from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, List

import pandas as pd


def records_to_dataframe(records: Iterable) -> pd.DataFrame:
    """Convert a list of dataclass records to DataFrame."""
    return pd.DataFrame([asdict(r) for r in records])


def summarize_latency(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-model latency summary."""
    if df.empty:
        return pd.DataFrame()
    
    # 按模型分组统计
    result_rows = []
    
    for model in df["model"].unique():
        model_df = df[df["model"] == model]
        success_df = model_df[model_df["error"].isna()]
        
        total_requests = len(model_df)
        success_count = len(success_df)
        error_count = total_requests - success_count
        error_rate = error_count / total_requests if total_requests > 0 else 0
        
        # 计算延迟统计（仅成功的请求）
        if len(success_df) > 0:
            latencies = success_df["latency_ms"]
            avg_latency = latencies.mean()
            # 只有在成功请求数>1时才显示最低/最高延迟
            if len(success_df) > 1:
                min_latency = latencies.min()
                max_latency = latencies.max()
            else:
                min_latency = max_latency = None
        else:
            avg_latency = min_latency = max_latency = None
        
        # 计算流式第一token延迟统计（仅有first_token_latency_ms数据的请求）
        first_token_avg = first_token_min = first_token_max = None
        if len(success_df) > 0 and "first_token_latency_ms" in success_df.columns:
            first_token_df = success_df[success_df["first_token_latency_ms"].notna()]
            if len(first_token_df) > 0:
                first_token_latencies = first_token_df["first_token_latency_ms"]
                first_token_avg = first_token_latencies.mean()
                if len(first_token_df) > 1:
                    first_token_min = first_token_latencies.min()
                    first_token_max = first_token_latencies.max()
                else:
                    first_token_min = first_token_max = None
        
        result_rows.append({
            "model": model,
            "avg_latency": avg_latency,
            "min_latency": min_latency,
            "max_latency": max_latency,
            "first_token_avg": first_token_avg,
            "first_token_min": first_token_min,
            "first_token_max": first_token_max,
            "error_rate": error_rate,
            "total_requests": total_requests,
            "success_count": success_count,
            "error_count": error_count,
        })
    
    return pd.DataFrame(result_rows)


def error_rate(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    agg = df.groupby("model")["error"].apply(lambda s: s.notna().mean()).reset_index()
    agg = agg.rename(columns={"error": "error_rate"})
    return agg
