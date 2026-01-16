// 前端配置文件
window.AppConfig = {
    // 预设问题列表
    presetQuestions: [
        {
            label: "入门：how to learn english",
            value: "how to learn english"
        },
        {
            label: "基础：Explain how transformer attention works at a high level",
            value: "Explain how transformer attention works at a high level"
        },
        {
            label: "进阶：Compare gpt-4.1 and gpt-4o in terms of reasoning and hallucination tendencies",
            value: "Compare gpt-5.1 and gpt-4o in terms of reasoning and hallucination tendencies"
        },
        {
            label: "高级：Design a roadmap for building an autonomous AI agent that handles multi-turn customer support",
            value: "Design a roadmap for building an autonomous AI agent that handles multi-turn customer support"
        },
        {
            label: "专家：Estimate the trade-offs between RLHF and constitutional AI when fine-tuning large models",
            value: "Estimate the trade-offs between RLHF and constitutional AI when fine-tuning large models"
        }
    ],
    
    // 默认测试参数
    defaultParams: {
        concurrency: 3,          // 默认并发数
        iterations: 1,           // 默认迭代次数
        maxTokens: 1000,         // 默认最大Token数
        temperature: 0.7,        // 默认温度
        stream: true             // 默认启用流式响应
    },
    
    // 参数范围限制
    limits: {
        concurrency: { min: 1, max: 20 },
        iterations: { min: 1, max: 50 },
        maxTokens: { min: 10, max: 4000, step: 10 },
        temperature: { min: 0, max: 2, step: 0.1 }
    },
    
    // 新增模型的默认配置
    newModelDefaults: {
        maxTokens: 1000,
        temperature: 0.7,
        concurrency: 1,
        iterations: 1,
        stream: true,
        apiVersion: "2024-12-01-preview"
    }
};