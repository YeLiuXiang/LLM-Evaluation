// ==================== 全局状态 ====================

let availableModels = [];
let selectedModels = new Set();
let currentTaskId = null;
let eventSource = null;
let modelOutputs = {}; // 存储每个模型的输出内容
let modelStatus = {}; // 存储每个模型的状态
let modelParamSupport = {}; // 存储模型参数支持信息
let summaryData = null; // 存储统计摘要数据

// ==================== DOM 元素 ====================
const elements = {
    modelSelector: document.getElementById('model-selector'),
    questionInput: document.getElementById('question-input'),
    presetSelect: document.getElementById('preset-question-select'),
    concurrencyInput: document.getElementById('concurrency-input'),
    iterationsInput: document.getElementById('iterations-input'),
    maxTokensInput: document.getElementById('max-tokens-input'),
    temperatureInput: document.getElementById('temperature-input'),
    streamToggle: document.getElementById('stream-toggle'),
    startTestBtn: document.getElementById('start-test-btn'),
    stopTestBtn: document.getElementById('stop-test-btn'),
    clearAllBtn: document.getElementById('clear-all-btn'),
    downloadResultsBtn: document.getElementById('download-results-btn'),
    historyBtn: document.getElementById('history-btn'),
    testStatus: document.getElementById('test-status'),
    activeModels: document.getElementById('active-models'),
    modelsContainer: document.getElementById('models-container'),
    emptyState: document.getElementById('empty-state'),
    summarySection: document.getElementById('summary-section'),
    summaryTable: document.getElementById('summary-table'),
    latencyHelpBtn: document.getElementById('latency-help-btn'),
    toggleAddModelBtn: document.getElementById('toggle-add-model'),
    addModelForm: document.getElementById('add-model-form'),
    addModelBtn: document.getElementById('add-model-btn'),
    newModelNameInput: document.getElementById('new-model-name'),
    newModelEndpointInput: document.getElementById('new-model-endpoint'),
    newModelApiKeyInput: document.getElementById('new-model-api-key'),
    newModelApiVersionInput: document.getElementById('new-model-api-version'),
    newModelMaxTokensInput: document.getElementById('new-model-max-tokens'),
    newModelTemperatureInput: document.getElementById('new-model-temperature'),
    newModelConcurrencyInput: document.getElementById('new-model-concurrency'),
    newModelIterationsInput: document.getElementById('new-model-iterations'),
    newModelStreamToggle: document.getElementById('new-model-stream'),
    addModelMessage: document.getElementById('add-model-message'),
    historyPanel: document.getElementById('history-panel'),
    historyList: document.getElementById('history-list'),
    closeHistoryBtn: document.getElementById('close-history-btn'),
    refreshHistoryBtn: document.getElementById('refresh-history-btn'),
    clearHistoryBtn: document.getElementById('clear-history-btn'),
    historyDetailModal: document.getElementById('history-detail-modal'),
    historyDetailBody: document.getElementById('history-detail-body'),
    closeDetailModalBtn: document.getElementById('close-detail-modal-btn')
};

// ==================== 初始化 ====================
async function init() {
    // 初始化Markdown渲染器
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            gfm: true,
            breaks: true,
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) {}
                }
                return hljs.highlightAuto(code).value;
            }
        });
    }
    
    // 初始化配置参数
    initializeFormDefaults();
    
    resetModelForm();
    setModelFormMessage();
    await loadModels();
    setupEventListeners();
    
    // 初始化预设问题
    initializePresetQuestions();
}

// 初始化表单默认值
function initializeFormDefaults() {
    if (!window.AppConfig) {
        console.error('配置文件未加载');
        return;
    }
    
    const config = window.AppConfig.defaultParams;
    
    elements.concurrencyInput.value = config.concurrency;
    elements.iterationsInput.value = config.iterations;
    elements.maxTokensInput.value = config.maxTokens;
    elements.temperatureInput.value = config.temperature;
    elements.streamToggle.checked = config.stream;
}

// 初始化预设问题
function initializePresetQuestions() {
    if (!window.AppConfig) return;
    
    const questions = window.AppConfig.presetQuestions;
    elements.presetSelect.innerHTML = questions.map(q => 
        `<option value="${q.value}">${q.label}</option>`
    ).join('');
    
    // 设置默认问题
    if (questions.length > 0) {
        elements.presetSelect.value = questions[0].value;
        applyPreset(questions[0].value);
    }
}

// ==================== 加载模型列表 ====================
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        availableModels = data.models;
        
        // 保存模型参数支持信息
        modelParamSupport = {};
        availableModels.forEach(model => {
            modelParamSupport[model.name] = model.supported_params || {
                max_tokens: true,
                temperature: true,
                stream: true,
            };
        });
        
        renderModelSelector();
    } catch (error) {
        console.error('加载模型失败:', error);
        elements.modelSelector.innerHTML = `
            <div class="error-message" style="color: var(--error-color); padding: 12px;">
                ❌ 加载模型失败：${error.message}
            </div>
        `;
    }
}

// ==================== 渲染模型选择器 ====================
function renderModelSelector() {
    if (availableModels.length === 0) {
        elements.modelSelector.innerHTML = `
            <div class="loading">未找到可用模型</div>
        `;
        return;
    }

    elements.modelSelector.innerHTML = availableModels.map(model => `
        <div class="model-item" data-model="${model.name}">
            <input 
                type="checkbox" 
                id="model-${model.name}" 
                value="${model.name}"
                checked
            >
            <label for="model-${model.name}" class="model-name">${model.name}</label>
        </div>
    `).join('');

    // 默认全选
    availableModels.forEach(model => selectedModels.add(model.name));
    updateActiveModelsCount();
}

// ==================== 设置事件监听 ====================
function setupEventListeners() {
    // 模型选择
    elements.modelSelector.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            const modelName = e.target.value;
            const modelItem = e.target.closest('.model-item');
            
            if (e.target.checked) {
                selectedModels.add(modelName);
                modelItem.classList.add('selected');
            } else {
                selectedModels.delete(modelName);
                modelItem.classList.remove('selected');
            }
            updateActiveModelsCount();
            updateTestParamsVisibility();
        }
    });

    // 开始测试
    elements.startTestBtn.addEventListener('click', startTest);

    // 停止测试
    elements.stopTestBtn.addEventListener('click', stopTest);

    // 清空所有
    elements.clearAllBtn.addEventListener('click', clearAllOutputs);

    // 下载结果
    elements.downloadResultsBtn.addEventListener('click', downloadResults);

    // 预设问题
    if (elements.presetSelect) {
        elements.presetSelect.addEventListener('change', (e) => {
            applyPreset(e.target.value);
        });
    }

    if (elements.addModelBtn) {
        elements.addModelBtn.addEventListener('click', submitModelConfig);
    }

    // 添加模型表单展开/收起
    if (elements.toggleAddModelBtn && elements.addModelForm) {
        elements.toggleAddModelBtn.addEventListener('click', () => {
            elements.addModelForm.classList.toggle('collapsed');
        });
    }

    // 延迟帮助按钮
    if (elements.latencyHelpBtn) {
        elements.latencyHelpBtn.addEventListener('click', showLatencyHelpInfo);
    }

    // 历史记录相关
    if (elements.historyBtn) {
        elements.historyBtn.addEventListener('click', openHistoryPanel);
    }
    if (elements.closeHistoryBtn) {
        elements.closeHistoryBtn.addEventListener('click', closeHistoryPanel);
    }
    if (elements.refreshHistoryBtn) {
        elements.refreshHistoryBtn.addEventListener('click', loadHistoryList);
    }
    if (elements.clearHistoryBtn) {
        elements.clearHistoryBtn.addEventListener('click', clearAllHistory);
    }
    if (elements.closeDetailModalBtn) {
        elements.closeDetailModalBtn.addEventListener('click', closeHistoryDetail);
    }
    // 点击模态框背景关闭
    if (elements.historyDetailModal) {
        elements.historyDetailModal.addEventListener('click', (e) => {
            if (e.target === elements.historyDetailModal) {
                closeHistoryDetail();
            }
        });
    }
}

function applyPreset(prompt) {
    if (elements.questionInput) {
        elements.questionInput.value = prompt;
    }
}

// ==================== 更新活跃模型数量 ====================
function updateActiveModelsCount() {
    elements.activeModels.textContent = selectedModels.size;
}

// ==================== 根据选中的模型更新参数可见性 ====================
function updateTestParamsVisibility() {
    if (selectedModels.size === 0) {
        // 没有选中模型，显示所有参数
        showTestParam('max-tokens');
        showTestParam('temperature');
        showTestParam('stream');
        return;
    }
    
    // 检查所有选中模型的参数支持情况
    const selectedArray = [...selectedModels];
    const paramsSupport = {
        'max_tokens': true,
        'temperature': true,
        'stream': true,
    };
    
    selectedArray.forEach(modelName => {
        const modelSupport = modelParamSupport[modelName] || {};
        paramsSupport['max_tokens'] = paramsSupport['max_tokens'] && (modelSupport['max_tokens'] !== false);
        paramsSupport['temperature'] = paramsSupport['temperature'] && (modelSupport['temperature'] !== false);
        paramsSupport['stream'] = paramsSupport['stream'] && (modelSupport['stream'] !== false);
    });
    
    // 根据支持情况显示/隐藏参数
    paramsSupport['max_tokens'] ? showTestParam('max-tokens') : hideTestParam('max-tokens');
    paramsSupport['temperature'] ? showTestParam('temperature') : hideTestParam('temperature');
    paramsSupport['stream'] ? showTestParam('stream') : hideTestParam('stream');
}

function showTestParam(paramId) {
    const paramElements = getParamElements(paramId);
    if (paramElements.group) {
        paramElements.group.style.display = '';
    }
}

function hideTestParam(paramId) {
    const paramElements = getParamElements(paramId);
    if (paramElements.group) {
        paramElements.group.style.display = 'none';
    }
}

function getParamElements(paramId) {
    if (paramId === 'max-tokens') {
        return {
            group: document.querySelector('[data-param="max-tokens"]'),
            input: elements.maxTokensInput,
        };
    } else if (paramId === 'temperature') {
        return {
            group: document.querySelector('[data-param="temperature"]'),
            input: elements.temperatureInput,
        };
    } else if (paramId === 'stream') {
        return {
            group: document.querySelector('[data-param="stream"]'),
            input: elements.streamToggle,
        };
    }
    return {};
}

// ==================== 开始测试 ====================
async function startTest() {
    if (selectedModels.size === 0) {
        alert('请至少选择一个模型');
        return;
    }

    const question = elements.questionInput.value.trim();
    if (!question) {
        alert('请输入测试问题');
        return;
    }

    // 禁用开始按钮，启用停止按钮
    elements.startTestBtn.disabled = true;
    elements.stopTestBtn.disabled = false;
    elements.testStatus.textContent = '准备中...';
    
    // 隐藏统计摘要并清空之前的数据
    elements.summarySection.classList.add('hidden');
    displayedSummaryModels.clear();  // 清空已显示的模型统计
    summaryData = null;  // 清空统计数据

    // 清空之前的输出
    clearAllOutputs();

    // 为选中的模型创建卡片
    createModelCards([...selectedModels]);

    try {
        // 发起测试请求
        const response = await fetch('/api/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                models: [...selectedModels],
                question: question,
                concurrency: parseInt(elements.concurrencyInput.value),
                iterations: parseInt(elements.iterationsInput.value),
                max_tokens: parseInt(elements.maxTokensInput.value),
                temperature: parseFloat(elements.temperatureInput.value),
                stream: elements.streamToggle.checked
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        currentTaskId = data.task_id;

        elements.testStatus.textContent = '运行中...';

        // 建立 SSE 连接
        connectSSE(currentTaskId);

    } catch (error) {
        console.error('启动测试失败:', error);
        alert(`启动测试失败: ${error.message}`);
        resetUI();
    }
}

// ==================== 创建模型卡片 ====================
function createModelCards(models) {
    // 隐藏空状态
    elements.emptyState.classList.add('hidden');

    elements.modelsContainer.innerHTML = models.map(modelName => `
        <div class="model-card" data-model="${modelName}">
            <div class="card-header">${modelName}</div>
            <div class="card-body empty" id="output-${modelName}">
                等待响应中...
            </div>
            <div class="card-footer">
                <span class="status-badge connecting" id="status-${modelName}">连接中</span>
                <span class="duration-text" id="duration-${modelName}">-</span>
            </div>
        </div>
    `).join('');

    // 初始化状态
    models.forEach(modelName => {
        modelOutputs[modelName] = '';
        modelStatus[modelName] = { status: 'connecting', duration: null };
    });
}

// ==================== 连接 SSE ====================
function connectSSE(taskId) {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource(`/api/stream/${taskId}`);

    // 接收流式数据块
    eventSource.addEventListener('chunk', (event) => {
        const data = JSON.parse(event.data);
        handleStreamChunk(data);
    });

    // 接收统计摘要
    eventSource.addEventListener('summary', (event) => {
        console.log('=== 收到 summary 事件 ===');
        console.log('event.data:', event.data);
        try {
            const summaryData = JSON.parse(event.data);
            console.log('解析后的 summary:', summaryData);
            // 增量显示统计数据
            displaySummaryIncremental(summaryData);
        } catch (e) {
            console.error('解析 summary 数据失败:', e);
        }
    });
    
    // 接收完整的统计摘要（用于历史记录）
    eventSource.addEventListener('summary_complete', (event) => {
        console.log('=== 收到 summary_complete 事件 ===');
        try {
            const completeData = JSON.parse(event.data);
            console.log('完整统计数据:', completeData);
            // 保存完整的统计数据供下载使用
            summaryData = completeData;
        } catch (e) {
            console.error('解析完整统计数据失败:', e);
        }
    });

    // 测试完成
    eventSource.addEventListener('complete', (event) => {
        console.log('测试完成');
        handleTestComplete();
    });

    // 错误处理
    eventSource.addEventListener('error', (event) => {
        if (event.data) {
            const errorData = JSON.parse(event.data);
            console.error('测试错误:', errorData.error);
            alert(`测试错误: ${errorData.error}`);
        }
        handleTestComplete();
    });

    eventSource.onerror = (error) => {
        console.error('SSE 连接错误:', error);
        if (eventSource.readyState === EventSource.CLOSED) {
            console.log('SSE 连接已关闭');
        }
    };
}

// ==================== 处理流式数据块 ====================
let pendingUpdates = {};
let rafPending = false;

function handleStreamChunk(data) {
    const { model, chunk, status, duration } = data;

    // 累积输出内容
    if (chunk) {
        modelOutputs[model] = (modelOutputs[model] || '') + chunk;
        pendingUpdates[model] = true;
    }

    // 更新状态
    if (status) {
        updateModelStatus(model, status, duration);
    }

    // 使用 requestAnimationFrame 批量更新DOM，避免卡顿
    if (!rafPending) {
        rafPending = true;
        requestAnimationFrame(flushPendingUpdates);
    }
}

function flushPendingUpdates() {
    rafPending = false;
    
    for (const model in pendingUpdates) {
        const outputElement = document.getElementById(`output-${model}`);
        if (outputElement) {
            // 使用 marked 渲染 Markdown
            try {
                const rawContent = modelOutputs[model] || '';
                const htmlContent = marked.parse(rawContent, {
                    breaks: true,  // 支持换行
                    gfm: true,     // 启用 GitHub Flavored Markdown
                    highlight: function(code, lang) {
                        // 代码高亮
                        if (lang && hljs.getLanguage(lang)) {
                            try {
                                return hljs.highlight(code, { language: lang }).value;
                            } catch (e) {
                                console.error('Code highlight error:', e);
                            }
                        }
                        return hljs.highlightAuto(code).value;
                    }
                });
                outputElement.innerHTML = htmlContent;
            } catch (e) {
                console.error('Markdown 渲染失败:', e);
                // 如果渲染失败，使用原始文本
                outputElement.textContent = modelOutputs[model];
            }
            outputElement.classList.remove('empty');
            // 自动滚动到底部
            outputElement.scrollTop = outputElement.scrollHeight;
        }
    }
    pendingUpdates = {};
}

// ==================== 更新模型状态 ====================
function updateModelStatus(modelName, status, duration) {
    const statusElement = document.getElementById(`status-${modelName}`);
    const durationElement = document.getElementById(`duration-${modelName}`);

    if (statusElement) {
        statusElement.textContent = getStatusText(status);
        statusElement.className = `status-badge ${status}`;
    }

    if (durationElement && duration) {
        // 添加千分位逗号格式
        const formattedDuration = duration.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        durationElement.textContent = `${formattedDuration}ms`;
    }

    modelStatus[modelName] = { status, duration };
}

// ==================== 获取状态文本 ====================
function getStatusText(status) {
    const statusMap = {
        'connecting': '连接中',
        'streaming': '流式输出',
        'completed': '已完成',
        'error': '错误'
    };
    return statusMap[status] || status;
}

// ==================== 增量显示统计摘要 ====================
// 用于存储已显示的模型统计
let displayedSummaryModels = new Map();

function displaySummaryIncremental(summaryDataList) {
    console.log('=== displaySummaryIncremental 被调用 ===');
    console.log('summaryDataList:', summaryDataList);
    
    // 检查是否是字符串（可能是 JSON 字符串）
    if (typeof summaryDataList === 'string') {
        try {
            summaryDataList = JSON.parse(summaryDataList);
        } catch (e) {
            console.error('解析 JSON 失败:', e);
            return;
        }
    }
    
    // 检查是否为数组
    if (!Array.isArray(summaryDataList)) {
        console.error('统计数据不是数组：', summaryDataList);
        return;
    }
    
    if (summaryDataList.length === 0) {
        console.log('统计数据为空');
        return;
    }
    
    // 显示统计部分
    elements.summarySection.classList.remove('hidden');
    
    // 如果表格还不存在，创建表格结构
    if (!elements.summaryTable.querySelector('table')) {
        elements.summaryTable.innerHTML = `
            <table class="summary-table">
                <thead>
                    <tr>
                        <th>模型</th>
                        <th>平均延迟 (ms)</th>
                        <th>最低延迟 (ms)</th>
                        <th>最高延迟 (ms)</th>
                        <th>流式首Token平均 (ms)</th>
                        <th>流式首Token最低 (ms)</th>
                        <th>流式首Token最高 (ms)</th>
                        <th>错误率</th>
                        <th>成功/总数</th>
                    </tr>
                </thead>
                <tbody id="summary-tbody">
                </tbody>
            </table>
            <div class="summary-note">
                💡 <strong>说明：</strong>最低/最高延迟仅在并发数大于1时显示。Token统计基于API返回的usage信息。
            </div>
        `;
    }
    
    const tbody = document.getElementById('summary-tbody');
    
    // 格式化延迟值
    const formatLatency = (value) => {
        if (value == null || value === undefined || isNaN(value)) return '-';
        return parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    };
    
    // 为每个模型添加或更新行
    summaryDataList.forEach(row => {
        const modelName = row.model;
        
        // 检查是否已经显示过这个模型
        if (displayedSummaryModels.has(modelName)) {
            // 更新现有行
            const existingRow = document.getElementById(`summary-row-${modelName}`);
            if (existingRow) {
                existingRow.innerHTML = `
                    <td><strong>${modelName || '-'}</strong></td>
                    <td>${formatLatency(row.avg_latency)}</td>
                    <td>${formatLatency(row.min_latency)}</td>
                    <td>${formatLatency(row.max_latency)}</td>
                    <td>${formatLatency(row.first_token_avg)}</td>
                    <td>${formatLatency(row.first_token_min)}</td>
                    <td>${formatLatency(row.first_token_max)}</td>
                    <td>${row.error_rate != null ? (row.error_rate * 100).toFixed(2) + '%' : '0%'}</td>
                    <td>${row.success_count || 0}/${row.total_requests || 0}</td>
                `;
            }
        } else {
            // 添加新行
            const newRow = document.createElement('tr');
            newRow.id = `summary-row-${modelName}`;
            newRow.innerHTML = `
                <td><strong>${modelName || '-'}</strong></td>
                <td>${formatLatency(row.avg_latency)}</td>
                <td>${formatLatency(row.min_latency)}</td>
                <td>${formatLatency(row.max_latency)}</td>
                <td>${formatLatency(row.first_token_avg)}</td>
                <td>${formatLatency(row.first_token_min)}</td>
                <td>${formatLatency(row.first_token_max)}</td>
                <td>${row.error_rate != null ? (row.error_rate * 100).toFixed(2) + '%' : '0%'}</td>
                <td>${row.success_count || 0}/${row.total_requests || 0}</td>
            `;
            tbody.appendChild(newRow);
            displayedSummaryModels.set(modelName, row);
            
            // 添加淡入动画
            newRow.style.opacity = '0';
            requestAnimationFrame(() => {
                newRow.style.transition = 'opacity 0.3s ease-in';
                newRow.style.opacity = '1';
            });
        }
    });
}

// ==================== 显示统计摘要（保留用于历史记录） ====================
function displaySummary(summaryDataList) {
    console.log('=== displaySummary 被调用 ===');
    console.log('summaryDataList type:', typeof summaryDataList);
    console.log('summaryDataList value:', summaryDataList);
    
    // 检查是否是字符串（可能是 JSON 字符串）
    if (typeof summaryDataList === 'string') {
        console.log('検测到 JSON 字符串，正在解析');
        try {
            summaryDataList = JSON.parse(summaryDataList);
        } catch (e) {
            console.error('解析 JSON 失败:', e);
            return;
        }
    }
    
    // 检查是否为数组
    if (!Array.isArray(summaryDataList)) {
        console.error('统计数据不是数组：', summaryDataList);
        return;
    }
    
    if (summaryDataList.length === 0) {
        console.log('统计数据为空');
        return;
    }

    // 保存统计摘要数据供下载使用
    summaryData = summaryDataList;
    
    console.log('Displaying summary with', summaryDataList.length, 'rows');
    elements.summarySection.classList.remove('hidden');

    const tableHTML = `
        <table class="summary-table">
            <thead>
                <tr>
                    <th>模型</th>
                    <th>平均延迟 (ms)</th>
                    <th>最低延迟 (ms)</th>
                    <th>最高延迟 (ms)</th>
                    <th>流式首Token平均 (ms)</th>
                    <th>流式首Token最低 (ms)</th>
                    <th>流式首Token最高 (ms)</th>
                    <th>错误率</th>
                    <th>成功/总数</th>
                </tr>
            </thead>
            <tbody>
                ${summaryDataList.map(row => {
                    const formatLatency = (value) => {
                        if (value == null || value === undefined || isNaN(value)) return '-';
                        return parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
                    };
                    
                    return `
                        <tr>
                            <td><strong>${row.model || '-'}</strong></td>
                            <td>${formatLatency(row.avg_latency)}</td>
                            <td>${formatLatency(row.min_latency)}</td>
                            <td>${formatLatency(row.max_latency)}</td>
                            <td>${formatLatency(row.first_token_avg)}</td>
                            <td>${formatLatency(row.first_token_min)}</td>
                            <td>${formatLatency(row.first_token_max)}</td>
                            <td>${row.error_rate != null ? (row.error_rate * 100).toFixed(2) + '%' : '0%'}</td>
                            <td>${row.success_count || 0}/${row.total_requests || 0}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
        <div class="summary-note">
            💡 <strong>说明：</strong>最低/最高延迟仅在并发数大于1时显示。Token统计基于API返回的usage信息。
        </div>
    `;

    elements.summaryTable.innerHTML = tableHTML;
}

// ==================== 显示延迟统计说明 ====================
function showLatencyHelpInfo() {
    const helpText = `
📊 延迟统计说明

【完整延迟】(平均/最低/最高)
  • 定义：从请求发送开始到接收完整个响应的总时间
  • 包含：网络往返时间 + 服务器处理时间 + 数据传输时间
  • 适用于：所有请求类型（流式和非流式）
  • 用途：评估模型的整体响应速度

【流式首Token延迟】(平均/最低/最高)
  • 定义：从请求发送开始到接收第一个有效token的时间
  • 应用场景：流式响应才会记录（非流式显示为 - ）
  • 用途：评估模型的响应快速性和流式体验
  • 价值：体现服务端返回首个token的速度

【其他指标】
  • 错误率：失败请求数 / 总请求数
  • 成功/总数：成功请求数 / 总并发请求数
  • 注意：最低/最高延迟在并发数 > 1 时才显示
    `;
    alert(helpText);
}

// ==================== 测试完成处理 ====================
function handleTestComplete() {
    elements.testStatus.textContent = '已完成';
    
    // 更新所有未完成模型的状态为已完成
    Object.keys(modelStatus).forEach(modelName => {
        if (modelStatus[modelName].status === 'streaming' || 
            modelStatus[modelName].status === 'connecting') {
            updateModelStatus(modelName, 'completed', modelStatus[modelName].duration);
        }
    });

    // 关闭 SSE 连接
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }

    resetUI();
    elements.downloadResultsBtn.disabled = false;
}

// ==================== 停止测试 ====================
function stopTest() {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }

    elements.testStatus.textContent = '已停止';
    resetUI();
}

// ==================== 重置 UI ====================
function resetUI() {
    elements.startTestBtn.disabled = false;
    elements.stopTestBtn.disabled = true;
}

// ==================== 清空所有输出 ====================
function clearAllOutputs() {
    modelOutputs = {};
    modelStatus = {};
    summaryData = null;
    elements.modelsContainer.innerHTML = '';
    elements.emptyState.classList.remove('hidden');
    elements.summarySection.classList.add('hidden');
    elements.summaryTable.innerHTML = ''; // 清空统计表格
    elements.downloadResultsBtn.disabled = true;
}

// ==================== 下载结果 ====================
function downloadResults() {
    if (!summaryData || summaryData.length === 0) {
        alert('暂无统计数据，请先完成测试');
        return;
    }

    // 构建 CSV 内容（只包含统计摘要表数据）
    const headers = ['模型', '平均延迟(ms)', '最低延迟(ms)', '最高延迟(ms)', '流式首Token平均(ms)', '流式首Token最低(ms)', '流式首Token最高(ms)', '错误率', '成功/总数'];
    
    // 使用 BOM 以便 Excel 正常软件正常软件转换中文
    let csvContent = '\ufeff'; // UTF-8 BOM
    csvContent += headers.join(',') + '\n';
    
    summaryData.forEach(row => {
        const formatValue = (value) => {
            if (value == null || value === undefined) return '-';
            if (typeof value === 'number') {
                // 如果是延迟数据，保留2位小数
                if (value > 100) {
                    return value.toFixed(2);
                }
                return value.toString();
            }
            return value.toString();
        };
        
        const modelName = row.model || '-';
        const avgLatency = formatValue(row.avg_latency);
        const minLatency = formatValue(row.min_latency);
        const maxLatency = formatValue(row.max_latency);
        const firstTokenAvg = formatValue(row.first_token_avg);
        const firstTokenMin = formatValue(row.first_token_min);
        const firstTokenMax = formatValue(row.first_token_max);
        const errorRate = row.error_rate != null ? (row.error_rate * 100).toFixed(2) + '%' : '0%';
        const successCount = `${row.success_count || 0}/${row.total_requests || 0}`;
        
        csvContent += `${modelName},${avgLatency},${minLatency},${maxLatency},${firstTokenAvg},${firstTokenMin},${firstTokenMax},${errorRate},${successCount}\n`;
    });

    // 创建下载链接
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `llm_test_summary_${Date.now()}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


async function submitModelConfig() {
    if (!elements.addModelBtn) return;
    setModelFormMessage();
    const payload = {
        name: elements.newModelNameInput?.value.trim() || '',
        endpoint: elements.newModelEndpointInput?.value.trim() || '',
        api_key: elements.newModelApiKeyInput?.value.trim() || '',
        api_version: elements.newModelApiVersionInput?.value.trim() || '',
    };

    if (!payload.name || !payload.endpoint || !payload.api_key || !payload.api_version) {
        setModelFormMessage('请输入名称、Endpoint、API Key 和 API Version', 'error');
        return;
    }

    elements.addModelBtn.disabled = true;
    try {
        const response = await fetch('/api/models', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        let data = {};
        try {
            data = await response.json();
        } catch (err) {
            data = {};
        }

        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}`);
        }

        resetModelForm();
        setModelFormMessage(data.detail || `模型 '${payload.name}' 已保存`, 'success');
        await loadModels();
    } catch (error) {
        setModelFormMessage(error.message, 'error');
    } finally {
        elements.addModelBtn.disabled = false;
    }
}

function parseNumericInput(input, fallback) {
    if (!input) {
        return fallback;
    }
    const value = Number(input.value);
    return Number.isFinite(value) ? value : fallback;
}

function setModelFormMessage(text = '', type = '') {
    if (!elements.addModelMessage) return;
    elements.addModelMessage.textContent = text;
    elements.addModelMessage.classList.remove('success', 'error');
    if (type) {
        elements.addModelMessage.classList.add(type);
    }
}

function resetModelForm() {
    if (!elements.newModelNameInput) return;
    
    if (window.AppConfig) {
        const defaults = window.AppConfig.newModelDefaults;
        elements.newModelNameInput.value = '';
        if (elements.newModelEndpointInput) {
            elements.newModelEndpointInput.value = defaults.baseUrl;
        }
        if (elements.newModelApiKeyInput) {
            elements.newModelApiKeyInput.value = '';
        }
        if (elements.newModelApiVersionInput) {
            elements.newModelApiVersionInput.value = defaults.apiVersion;
        }
        if (elements.newModelMaxTokensInput) {
            elements.newModelMaxTokensInput.value = defaults.maxTokens;
        }
        if (elements.newModelTemperatureInput) {
            elements.newModelTemperatureInput.value = defaults.temperature;
        }
    } else {
        // 兜底默认值
        elements.newModelNameInput.value = '';
        if (elements.newModelEndpointInput) {
            elements.newModelEndpointInput.value = '';
        }
        if (elements.newModelApiKeyInput) {
            elements.newModelApiKeyInput.value = '';
        }
        if (elements.newModelApiVersionInput) {
            elements.newModelApiVersionInput.value = '2024-12-01-preview';
        }
        if (elements.newModelMaxTokensInput) {
            elements.newModelMaxTokensInput.value = '1000';
        }
        if (elements.newModelTemperatureInput) {
            elements.newModelTemperatureInput.value = '0.7';
        }
    }
    if (elements.newModelConcurrencyInput) {
        const concurrency = window.AppConfig ? window.AppConfig.defaultParams.concurrency : 3;
        elements.newModelConcurrencyInput.value = concurrency;
    }
    if (elements.newModelIterationsInput) {
        elements.newModelIterationsInput.value = '1';
    }
    if (elements.newModelStreamToggle) {
        elements.newModelStreamToggle.checked = true;
    }
}

// ==================== 历史记录功能 ====================
async function openHistoryPanel() {
    elements.historyPanel.classList.remove('hidden');
    await loadHistoryList();
}

function closeHistoryPanel() {
    elements.historyPanel.classList.add('hidden');
}

async function loadHistoryList() {
    try {
        elements.historyList.innerHTML = '<div class="loading">加载中...</div>';
        
        const response = await fetch('/api/history?limit=50');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '加载历史记录失败');
        }
        
        if (!data.records || data.records.length === 0) {
            elements.historyList.innerHTML = '<div class="empty-state"><p>暂无历史记录</p></div>';
            return;
        }
        
        renderHistoryList(data.records);
    } catch (error) {
        console.error('加载历史记录失败:', error);
        elements.historyList.innerHTML = `<div class="empty-state"><p>加载失败: ${error.message}</p></div>`;
    }
}

function renderHistoryList(records) {
    const html = records.map(record => {
        const date = new Date(record.timestamp);
        const timeStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
        
        return `
            <div class="history-item" data-id="${record.id}">
                <div class="history-item-header">
                    <span class="history-item-time">${timeStr}</span>
                    <button class="history-item-delete" onclick="deleteHistoryRecord('${record.id}', event)">删除</button>
                </div>
                <div class="history-item-question">${record.question || '未指定问题'}</div>
                <div class="history-item-meta">
                    <span>📊 ${record.model_count} 个模型</span>
                </div>
                <div class="history-item-models">
                    ${(record.models || []).slice(0, 3).map(m => `<span class="history-model-tag">${m}</span>`).join('')}
                    ${record.models && record.models.length > 3 ? `<span class="history-model-tag">+${record.models.length - 3}</span>` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    elements.historyList.innerHTML = html;
    
    // 添加点击事件
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (!e.target.classList.contains('history-item-delete')) {
                showHistoryDetail(item.dataset.id);
            }
        });
    });
}

async function showHistoryDetail(recordId) {
    try {
        elements.historyDetailModal.classList.remove('hidden');
        elements.historyDetailBody.innerHTML = '<div class="loading">加载中...</div>';
        
        const response = await fetch(`/api/history/${recordId}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '加载记录详情失败');
        }
        
        renderHistoryDetail(data.record);
    } catch (error) {
        console.error('加载记录详情失败:', error);
        elements.historyDetailBody.innerHTML = `<div class="empty-state"><p>加载失败: ${error.message}</p></div>`;
    }
}

function renderHistoryDetail(record) {
    const date = new Date(record.timestamp);
    const timeStr = date.toLocaleString('zh-CN');
    const config = record.test_config || {};
    
    let html = `
        <div class="detail-section">
            <h4>⏰ 测试时间</h4>
            <div class="detail-info">${timeStr}</div>
        </div>
        
        <div class="detail-section">
            <h4>⚙️ 测试配置</h4>
            <div class="detail-info">
                <div class="detail-info-row">
                    <span class="detail-info-label">问题：</span>
                    <span class="detail-info-value">${config.question || '-'}</span>
                </div>
                <div class="detail-info-row">
                    <span class="detail-info-label">并发数：</span>
                    <span class="detail-info-value">${config.concurrency || '-'}</span>
                </div>
                <div class="detail-info-row">
                    <span class="detail-info-label">迭代次数：</span>
                    <span class="detail-info-value">${config.iterations || '-'}</span>
                </div>
                <div class="detail-info-row">
                    <span class="detail-info-label">Max Tokens：</span>
                    <span class="detail-info-value">${config.max_tokens || '-'}</span>
                </div>
                <div class="detail-info-row">
                    <span class="detail-info-label">Temperature：</span>
                    <span class="detail-info-value">${config.temperature || '-'}</span>
                </div>
                <div class="detail-info-row">
                    <span class="detail-info-label">流式模式：</span>
                    <span class="detail-info-value">${config.stream ? '是' : '否'}</span>
                </div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>📊 统计结果</h4>
    `;
    
    // 生成统计表格
    html += `
        <table class="summary-table">
            <thead>
                <tr>
                    <th>模型</th>
                    <th>平均延迟 (ms)</th>
                    <th>最低延迟 (ms)</th>
                    <th>最高延迟 (ms)</th>
                    <th>流式首Token平均 (ms)</th>
                    <th>流式首Token最低 (ms)</th>
                    <th>流式首Token最高 (ms)</th>
                    <th>错误率</th>
                    <th>成功/总数</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    (record.summary || []).forEach(row => {
        const formatLatency = (value) => {
            if (value == null || value === undefined || isNaN(value)) return '-';
            return parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        };
        
        html += `
            <tr>
                <td><strong>${row.model || '-'}</strong></td>
                <td>${formatLatency(row.avg_latency)}</td>
                <td>${formatLatency(row.min_latency)}</td>
                <td>${formatLatency(row.max_latency)}</td>
                <td>${formatLatency(row.first_token_avg)}</td>
                <td>${formatLatency(row.first_token_min)}</td>
                <td>${formatLatency(row.first_token_max)}</td>
                <td>${row.error_rate != null ? (row.error_rate * 100).toFixed(2) + '%' : '0%'}</td>
                <td>${row.success_count || 0}/${row.total_requests || 0}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        </div>
    `;
    
    elements.historyDetailBody.innerHTML = html;
}

function closeHistoryDetail() {
    elements.historyDetailModal.classList.add('hidden');
}

async function deleteHistoryRecord(recordId, event) {
    event.stopPropagation();
    
    if (!confirm('确定要删除这条历史记录吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/history/${recordId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '删除失败');
        }
        
        // 重新加载列表
        await loadHistoryList();
    } catch (error) {
        console.error('删除历史记录失败:', error);
        alert(`删除失败: ${error.message}`);
    }
}

async function clearAllHistory() {
    if (!confirm('确定要清空所有历史记录吗？此操作不可恢复！')) {
        return;
    }
    
    try {
        const response = await fetch('/api/history', {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '清空失败');
        }
        
        // 重新加载列表
        await loadHistoryList();
    } catch (error) {
        console.error('清空历史记录失败:', error);
        alert(`清空失败: ${error.message}`);
    }
}

// 将deleteHistoryRecord暴露到全局作用域，供onclick使用
window.deleteHistoryRecord = deleteHistoryRecord;

// ==================== 页面加载完成后初始化 ====================
document.addEventListener('DOMContentLoaded', init);
