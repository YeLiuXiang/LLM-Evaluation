from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, replace
from typing import Any, Callable, Dict, Iterable, List, Optional

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

StreamCallback = Callable[[str, int, str], None]  # model_name, request_id, chunk

# 模型参数兼容性配置
MODEL_PARAM_OVERRIDES = {
    "gpt-5-mini": {
        "temperature": 1.0,  # gpt-5-mini 仅支持 temperature=1
    }
}

# 模型参数支持配置 (哪些参数该模型支持)
MODEL_PARAM_SUPPORT = {
    # 默认配置：通用 chat 模型
    "default": {
        "max_tokens": True,
        "temperature": True,
        "stream": True,
    },
    # 特殊模型配置可在此添加
    "gpt-5-mini": {
        "max_tokens": True,
        "temperature": True,  # 虽然支持，但只接受1
        "stream": True,
    }
}


@dataclass
class ModelConfig:
    name: str
    endpoint: str
    api_key: str
    api_version: str
    prompt: str
    # 对 chat 模型使用 max_completion_tokens，对 codex 使用 max_tokens
    max_tokens: int = 1000
    temperature: float = 0.7
    concurrency: int = 1
    iterations: int = 1
    stream: bool = False

    def with_overrides(
        self,
        prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        concurrency: Optional[int] = None,
        iterations: Optional[int] = None,
        stream: Optional[bool] = None,
    ) -> "ModelConfig":
        return replace(
            self,
            prompt=prompt if prompt is not None else self.prompt,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            concurrency=concurrency if concurrency is not None else self.concurrency,
            iterations=iterations if iterations is not None else self.iterations,
            stream=stream if stream is not None else self.stream,
        )


@dataclass
class RequestRecord:
    model: str
    request_id: int
    start_time: float
    end_time: float
    latency_ms: float
    status: Optional[int]
    error: Optional[str]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    response_text: Optional[str]
    first_token_latency_ms: Optional[float] = None  # 流式情况下第一个token的延迟


class LatencyTester:
    def __init__(self, request_timeout: float = 60.0):
        self.request_timeout = request_timeout

    async def run_models(
        self,
        configs: Iterable[ModelConfig],
        question: Optional[str] = None,
        stream_callback: Optional[StreamCallback] = None,
    ) -> List[RequestRecord]:
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [
                asyncio.create_task(self._run_model(config, question, session, stream_callback))
                for config in configs
            ]
            results_nested = await asyncio.gather(*tasks)
        return [r for sub in results_nested for r in sub]

    async def _run_model(
        self,
        config: ModelConfig,
        question: Optional[str],
        session: aiohttp.ClientSession,
        stream_callback: Optional[StreamCallback],
    ) -> List[RequestRecord]:
        records: List[RequestRecord] = []
        sem = asyncio.Semaphore(max(1, config.concurrency))

        async def worker(request_id: int):
            async with sem:
                record = await self._single_request(
                    config=config,
                    question=question,
                    session=session,
                    request_id=request_id,
                    stream_callback=stream_callback,
                )
                records.append(record)

        # 总请求数 = 并发数 * 迭代次数
        total_requests = config.concurrency * config.iterations
        tasks = [asyncio.create_task(worker(i)) for i in range(total_requests)]
        await asyncio.gather(*tasks)
        return records

    async def _single_request(
        self,
        config: ModelConfig,
        question: Optional[str],
        session: aiohttp.ClientSession,
        request_id: int,
        stream_callback: Optional[StreamCallback],
    ) -> RequestRecord:
        is_codex = "codex" in config.name.lower()

        # 获取模型特定的参数覆盖
        param_overrides = MODEL_PARAM_OVERRIDES.get(config.name, {})
        temperature = param_overrides.get("temperature", config.temperature)

        # 路径与 payload 根据模型类型区分（codex 用 completions，其他用 chat）
        url = f"{config.endpoint.rstrip('/')}/openai/deployments/{config.name}/chat/completions"
        if is_codex:
            url = f"{config.endpoint.rstrip('/')}/openai/deployments/{config.name}/completions"
            payload: Dict[str, Any] = {
                "prompt": [question or config.prompt],
                "max_tokens": config.max_tokens,
                "temperature": temperature,
                "stream": config.stream,
            }
        else:
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question or config.prompt},
                ],
                # chat 模型用 max_completion_tokens，避免新版模型报 unsupported_parameter
                "max_completion_tokens": config.max_tokens,
                "temperature": temperature,
                "stream": config.stream,
            }

        params = {"api-version": config.api_version}
        headers = {
            "api-key": config.api_key,
            "Content-Type": "application/json",
        }

        logger.info(f"[{config.name}] Request #{request_id}: POST {url} with api-version={config.api_version}")
        
        start = time.perf_counter()
        status: Optional[int] = None
        error: Optional[str] = None
        prompt_tokens = completion_tokens = total_tokens = None
        response_text_parts: List[str] = []
        first_token_time: Optional[float] = None  # 第一个token到达时间

        try:
            async with session.post(url, headers=headers, params=params, json=payload) as resp:
                status = resp.status
                logger.info(f"[{config.name}] Request #{request_id}: Status {status}")
                
                if status >= 400:
                    try:
                        err_json = await resp.json(content_type=None)
                        err_detail = err_json.get("error") or err_json
                        error = f"HTTP {status}: {err_detail}"
                        logger.error(f"[{config.name}] Request #{request_id} error: {error}")
                    except Exception:
                        error = f"HTTP {status}"
                        logger.error(f"[{config.name}] Request #{request_id}: {error}")
                elif config.stream:
                    async for raw_line in resp.content:
                        line = raw_line.decode(errors="ignore").strip()
                        if not line or not line.startswith("data:"):
                            continue
                        data_str = line[len("data:") :].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue
                        choices = data.get("choices") or []
                        if not choices:
                            continue
                        if is_codex:
                            delta = choices[0].get("text")
                            if delta:
                                # 记录第一个token的时间
                                if first_token_time is None:
                                    first_token_time = time.perf_counter()
                                response_text_parts.append(delta)
                                if stream_callback:
                                    stream_callback(config.name, request_id, delta)
                        else:
                            delta = choices[0].get("delta", {}).get("content")
                            if delta:
                                # 记录第一个token的时间
                                if first_token_time is None:
                                    first_token_time = time.perf_counter()
                                response_text_parts.append(delta)
                                if stream_callback:
                                    stream_callback(config.name, request_id, delta)
                        usage = data.get("usage")
                        if usage:
                            prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
                            completion_tokens = usage.get("completion_tokens", completion_tokens)
                            total_tokens = usage.get("total_tokens", total_tokens)
                else:
                    data = await resp.json(content_type=None)
                    choices = data.get("choices") or []
                    if not choices:
                        error_detail = data.get("error") or data
                        error = f"No choices in response: {error_detail}"
                    else:
                        if is_codex:
                            content = choices[0].get("text") or ""
                        else:
                            message = choices[0].get("message", {})
                            content = message.get("content") or ""
                        response_text_parts.append(content)
                    usage = data.get("usage", {})
                    prompt_tokens = usage.get("prompt_tokens")
                    completion_tokens = usage.get("completion_tokens")
                    total_tokens = usage.get("total_tokens")
                if status and status >= 400:
                    if not error:
                        try:
                            err_json = await resp.json(content_type=None)
                            err_detail = err_json.get("error") or err_json
                            error = f"HTTP {status}: {err_detail}"
                        except Exception:
                            error = f"HTTP {status}"
        except Exception as exc:  # noqa: BLE001
            error = str(exc)

        end = time.perf_counter()
        latency_ms = (end - start) * 1000
        
        # 计算第一个token延迟（仅流式且有实际内容时）
        first_token_latency_ms = None
        if config.stream and first_token_time is not None:
            first_token_latency_ms = (first_token_time - start) * 1000
        
        return RequestRecord(
            model=config.name,
            request_id=request_id,
            start_time=start,
            end_time=end,
            latency_ms=latency_ms,
            status=status,
            error=error,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            response_text="".join(response_text_parts) if response_text_parts else None,
            first_token_latency_ms=first_token_latency_ms,
        )
