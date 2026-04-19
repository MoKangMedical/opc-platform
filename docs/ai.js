// ============================================
// OPC Alliance — MIMO AI Integration
// ============================================

const MimoAI = (function() {
    'use strict';

    const CONFIG = {
        apiKey: 'sk-ccwzuzw9e1t42xjok84nfx7wrv4geuzc590ojipwfqga5uxl',
        baseUrl: 'https://api.xiaomimimo.com/v1',
        model: 'mimo-v2-pro'
    };

    // Legends knowledge base for system prompts
    const LEGENDS_WISDOM = buildLegendsWisdom();

    function buildLegendsWisdom() {
        if (typeof LEGENDS === 'undefined') return '';
        return LEGENDS.map(l => {
            const quotes = (l.philosophyZh || l.philosophy || []).slice(0, 3).join('；');
            return `${l.nameZh || l.name}（${l.roleZh || l.role}）：核心理念：${quotes}。名言："${l.quoteZh || l.quote}"`;
        }).join('\n');
    }

    async function chat(systemPrompt, userMessage, temperature = 0.7) {
        const body = {
            model: CONFIG.model,
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userMessage }
            ],
            temperature,
            max_tokens: 2000
        };

        // Strategy 1: Proxy (via Cloudflare Worker /v1/ path)
        const proxyBase = localStorage.getItem('opc_sm_proxy') || '';
        if (proxyBase) {
            try {
                // Worker proxy: /v1/chat/completions 直接转发到 MIMO
                const proxyUrl = proxyBase.replace(/\/?$/, '') + '/v1/chat/completions';
                const resp = await fetch(proxyUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const data = await resp.json();
                if (data.choices && data.choices[0]) {
                    return { ok: true, content: data.choices[0].message.content, via: 'proxy' };
                }
            } catch(e) { /* fall through to direct */ }
        }

        // Strategy 2: Direct call (if CORS extension installed)
        try {
            const resp = await fetch(`${CONFIG.baseUrl}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${CONFIG.apiKey}`
                },
                body: JSON.stringify(body)
            });
            const data = await resp.json();
            if (data.choices && data.choices[0]) {
                return { ok: true, content: data.choices[0].message.content, via: 'direct' };
            }
            return { ok: false, error: data.error?.message || 'API返回异常' };
        } catch(e) {
            return { ok: false, error: 'CORS_BLOCKED' };
        }
    }

    // ---- OPC AI Advisor ----
    async function askAdvisor(question) {
        const systemPrompt = `你是OPC创业者联盟的AI顾问，基于全球18位最成功的「一人公司」（One Person Company）创业者的商业智慧来回答问题。

你的知识库来自以下传奇人物的思维模式：
${LEGENDS_WISDOM}

回答要求：
1. 引用具体人物的观点和经验
2. 给出实操建议，不要空泛的鸡汤
3. 中文回答，简洁有力
4. 如果问题超出OPC范围，诚实说明
5. 每个回答控制在300字以内`;
        return chat(systemPrompt, question, 0.7);
    }

    // ---- Idea Evaluator ----
    async function evaluateIdea(idea) {
        const systemPrompt = `你是OPC创业者联盟的「想法评估器」。用户会提交一个创业想法，你需要从一人公司（OPC）的角度进行评估。

评估维度（每项1-10分）：
1. 🎯 一人可执行度：这个想法一个人能做吗？
2. 💰 变现潜力：能产生收入吗？边际成本如何？
3. 🚀 启动速度：能快速上线MVP吗？
4. 📈 可扩展性：有复利效应吗？
5. 🛡️ 护城河：有竞争优势吗？

输出格式（严格JSON）：
{
  "scores": { "solo": N, "revenue": N, "speed": N, "scale": N, "moat": N },
  "total": N,
  "verdict": "一句话总评",
  "strengths": ["优势1", "优势2"],
  "risks": ["风险1", "风险2"],
  "suggestions": ["建议1", "建议2"],
  "similarLegends": ["类似成功的人物名"]
}

参考的成功模式：${LEGENDS_WISDOM}

注意：total是5项平均分，保留1位小数。similarLegends从18位传奇人物中匹配。`;

        const result = await chat(systemPrompt, `请评估这个创业想法：\n\n${idea}`, 0.3);
        if (result.ok) {
            try {
                const jsonMatch = result.content.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    result.evaluation = JSON.parse(jsonMatch[0]);
                }
            } catch(e) { /* non-JSON is fine */ }
        }
        return result;
    }

    // ---- Daily AI Recommendation ----
    async function getDailyRecommendation() {
        const today = new Date().toISOString().slice(0, 10);
        const cached = localStorage.getItem('opc_daily_rec');
        if (cached) {
            try {
                const parsed = JSON.parse(cached);
                if (parsed.date === today) return { ok: true, content: parsed.content, cached: true };
            } catch(e) {}
        }

        const systemPrompt = `你是OPC创业者联盟的每日推荐官。每天为创业者推荐一个行动建议。

输出格式：
🔥 今日OPC建议
[一句话核心建议，来自某位传奇人物的方法论]

💡 行动步骤
1. [具体可执行的第一步]
2. [第二步]
3. [第三步]

📖 推荐资源
[一个相关工具/书籍/课程]

💭 今日思考
[一个引发思考的问题]

要求：每天内容不同，结合当前创业趋势，给出具体可执行的建议。控制在200字以内。`;

        const result = await chat(systemPrompt, `今天是${today}，请给出今日OPC创业建议。`, 0.9);
        if (result.ok) {
            localStorage.setItem('opc_daily_rec', JSON.stringify({ date: today, content: result.content }));
        }
        return result;
    }

    return { askAdvisor, evaluateIdea, getDailyRecommendation };
})();

window.MimoAI = MimoAI;
