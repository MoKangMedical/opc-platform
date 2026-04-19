// ============================================
// OPC Legends — Data (Bilingual + Cartoon Avatars)
// ============================================

// Generate unique cartoon SVG avatar for each legend
function cartoonAvatar(seed, hue1, hue2) {
    // Deterministic pseudo-random from seed
    let h = 0;
    for (let i = 0; i < seed.length; i++) { h = ((h << 5) - h + seed.charCodeAt(i)) | 0; }
    const r = (n) => Math.abs((h = (h * 16807 + n) % 2147483647) % 100) / 100;
    
    const skinTones = ['#FFDBAC', '#F1C27D', '#E0AC69', '#C68642', '#8D5524', '#FFD5B8', '#F4C19B'];
    const skin = skinTones[Math.floor(r(1) * skinTones.length)];
    const hairColors = ['#2C1B0E', '#4A3728', '#6B4423', '#8B6914', '#D4A843', '#1A1A2E', '#C0392B', '#8E44AD'];
    const hair = hairColors[Math.floor(r(2) * hairColors.length)];
    const hasGlasses = r(3) > 0.5;
    const hasBeard = r(4) > 0.65;
    const hasHat = r(5) > 0.75;
    const eyeStyle = Math.floor(r(6) * 3); // 0=normal, 1=happy, 2=cool
    const mouthStyle = Math.floor(r(7) * 3); // 0=smile, 1=grin, 2=smirk
    const bgAngle = Math.floor(r(8) * 360);
    
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
      <defs>
        <linearGradient id="bg-${seed}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="${hue1}"/>
          <stop offset="100%" stop-color="${hue2}"/>
        </linearGradient>
        <clipPath id="round-${seed}"><rect width="200" height="200" rx="40"/></clipPath>
      </defs>
      <rect width="200" height="200" rx="40" fill="url(#bg-${seed})"/>
      <g clip-path="url(#round-${seed})">`;
    
    // Hat
    if (hasHat) {
        svg += `<rect x="55" y="28" width="90" height="18" rx="9" fill="${hair}" opacity="0.9"/>
                <rect x="65" y="10" width="70" height="25" rx="12" fill="${hair}"/>`;
    }
    
    // Hair back
    if (!hasHat) {
        svg += `<ellipse cx="100" cy="72" rx="52" ry="48" fill="${hair}"/>`;
    }
    
    // Face
    svg += `<ellipse cx="100" cy="85" rx="44" ry="46" fill="${skin}"/>`;
    
    // Ears
    svg += `<ellipse cx="56" cy="85" rx="8" ry="12" fill="${skin}"/>
            <ellipse cx="144" cy="85" rx="8" ry="12" fill="${skin}"/>`;
    
    // Hair front
    if (!hasHat) {
        svg += `<path d="M56 65 Q60 40 80 45 Q90 30 100 38 Q110 30 120 45 Q140 40 144 65" fill="${hair}"/>`;
        // Side hair
        svg += `<path d="M56 65 Q52 80 55 95" stroke="${hair}" stroke-width="6" fill="none" stroke-linecap="round"/>
                <path d="M144 65 Q148 80 145 95" stroke="${hair}" stroke-width="6" fill="none" stroke-linecap="round"/>`;
    }
    
    // Eyebrows
    svg += `<path d="M72 70 Q82 64 92 70" stroke="${hair}" stroke-width="3" fill="none" stroke-linecap="round"/>
            <path d="M108 70 Q118 64 128 70" stroke="${hair}" stroke-width="3" fill="none" stroke-linecap="round"/>`;
    
    // Eyes
    if (eyeStyle === 0) {
        // Normal
        svg += `<ellipse cx="82" cy="82" rx="8" ry="9" fill="white"/>
                <ellipse cx="118" cy="82" rx="8" ry="9" fill="white"/>
                <circle cx="84" cy="83" r="5" fill="#2C3E50"/>
                <circle cx="120" cy="83" r="5" fill="#2C3E50"/>
                <circle cx="86" cy="81" r="2" fill="white"/>
                <circle cx="122" cy="81" r="2" fill="white"/>`;
    } else if (eyeStyle === 1) {
        // Happy squint
        svg += `<path d="M72 82 Q82 76 92 82" stroke="#2C3E50" stroke-width="3.5" fill="none" stroke-linecap="round"/>
                <path d="M108 82 Q118 76 128 82" stroke="#2C3E50" stroke-width="3.5" fill="none" stroke-linecap="round"/>`;
    } else {
        // Cool / confident
        svg += `<ellipse cx="82" cy="82" rx="9" ry="8" fill="white"/>
                <ellipse cx="118" cy="82" rx="9" ry="8" fill="white"/>
                <circle cx="85" cy="83" r="5" fill="#2C3E50"/>
                <circle cx="121" cy="83" r="5" fill="#2C3E50"/>
                <circle cx="87" cy="81" r="1.5" fill="white"/>
                <circle cx="123" cy="81" r="1.5" fill="white"/>`;
    }
    
    // Glasses
    if (hasGlasses) {
        svg += `<rect x="68" y="72" width="28" height="22" rx="6" stroke="#333" stroke-width="2.5" fill="none"/>
                <rect x="104" y="72" width="28" height="22" rx="6" stroke="#333" stroke-width="2.5" fill="none"/>
                <line x1="96" y1="82" x2="104" y2="82" stroke="#333" stroke-width="2.5"/>`;
    }
    
    // Nose
    svg += `<path d="M100 88 Q96 96 100 100 Q104 96 100 88" fill="${skin}" stroke="${skin}" stroke-width="1" opacity="0.7"/>`;
    
    // Mouth
    if (mouthStyle === 0) {
        svg += `<path d="M85 108 Q100 120 115 108" stroke="#C0392B" stroke-width="3" fill="none" stroke-linecap="round"/>`;
    } else if (mouthStyle === 1) {
        svg += `<path d="M82 106 Q100 124 118 106" fill="#C0392B" stroke="none"/>
                <path d="M85 112 Q100 108 115 112" fill="white"/>`;
    } else {
        svg += `<path d="M88 110 Q100 116 115 108" stroke="#C0392B" stroke-width="3" fill="none" stroke-linecap="round"/>`;
    }
    
    // Beard
    if (hasBeard) {
        svg += `<path d="M70 105 Q75 130 100 135 Q125 130 130 105" fill="${hair}" opacity="0.6"/>`;
    }
    
    // Body / shirt collar
    svg += `<path d="M60 145 Q100 160 140 145 L150 200 L50 200 Z" fill="${hue1}" opacity="0.8"/>
            <path d="M85 145 L100 165 L115 145" fill="${skin}"/>`;
    
    svg += `</g></svg>`;
    return svg;
}

const LEGENDS = [
    {
        id: "pieter-levels",
        name: "Pieter Levels",
        nameZh: "皮特·莱弗尔斯",
        role: "Serial Shipper • Nomad Founder",
        roleZh: "连续发者 • 数字游民创始人",
        category: ["saas"],
        avatar: cartoonAvatar("pieter", "#6c5ce7", "#a29bfe"),
        avatarBg: "linear-gradient(135deg, #6c5ce7, #a29bfe)",
        bio: "Dutch developer who built 70+ products as a one-person company. Revenue, Nomad List, Remote OK, and Photo AI generate $3.5M+/year. The godfather of the build-in-public movement.",
        bioZh: "荷兰开发者，以一人公司模式打造了70+个产品。Revenue、Nomad List、Remote OK和Photo AI年收入超过350万美元。'公开构建'运动的教父。",
        metrics: [
            { value: "$3.5M+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "70+", label: "Products Shipped", labelZh: "已发布产品" },
            { value: "4", label: "$1M+ Products", labelZh: "百万级产品" },
            { value: "0", label: "Employees", labelZh: "员工数" }
        ],
        website: "https://levels.io",
        twitter: "https://twitter.com/levelsio",
        quote: "The best marketing is shipping fast and being transparent about it.",
        quoteZh: "最好的营销就是快速发布，并且保持透明。",
        philosophy: [
            "Ship fast, iterate faster — launch a new product every week",
            "Build in public: share revenue, metrics, and mistakes",
            "One person + code + AI = unlimited leverage",
            "Don't hire unless you absolutely have to",
            "Solve your own problems first, then monetize"
        ],
        philosophyZh: [
            "快速发布，快速迭代——每周上线一个新产品",
            "公开构建：分享收入、数据和错误",
            "一个人 + 代码 + AI = 无限杠杆",
            "除非万不得已，不要招人",
            "先解决自己的问题，再考虑变现"
        ],
        keyInsight: "Pieter proves that volume wins in the product game. By shipping 70+ products, he found 4 hits. Most founders ship 1 product and pray. The math is simple: more attempts = more chances of success.",
        keyInsightZh: "皮特证明了在产品游戏中，数量制胜。通过发布70+个产品，他找到了4个爆款。大多数创业者只做一个产品然后祈祷。数学很简单：尝试越多 = 成功概率越大。",
        businessModel: "SaaS + Marketplace",
        businessModelZh: "SaaS + 市场平台",
        tags: ["Build in Public", "Ship Fast", "Nomad", "AI Products"]
    },
    {
        id: "naval-ravikant",
        name: "Naval Ravikant",
        nameZh: "纳瓦尔·拉维坎特",
        role: "Philosopher • Investor • AngelList Founder",
        roleZh: "哲学家 • 投资人 • AngelList创始人",
        category: ["finance"],
        avatar: cartoonAvatar("naval", "#f0c040", "#e17055"),
        avatarBg: "linear-gradient(135deg, #f0c040, #e17055)",
        bio: "AngelList co-founder who codified wealth creation into a philosophy. His 'How to Get Rich Without Getting Lucky' tweetstorm became the most-shared business text of the decade.",
        bioZh: "AngelList联合创始人，将财富创造编码成一套哲学。他的推文风暴《如何在不靠运气的情况下致富》成为十年内被分享最多的商业文本。",
        metrics: [
            { value: "$1B+", label: "Net Worth", labelZh: "净资产" },
            { value: "100+", label: "Angel Investments", labelZh: "天使投资" },
            { value: "10M+", label: "Almanack Readers", labelZh: "年鉴读者" },
            { value: "∞", label: "Leverage", labelZh: "杠杆" }
        ],
        website: "https://nav.al",
        twitter: "https://twitter.com/naval",
        quote: "Seek wealth, not money or status. Wealth is having assets that earn while you sleep.",
        quoteZh: "追求财富，而非金钱或地位。财富是那些在你睡觉时仍在为你赚钱的资产。",
        philosophy: [
            "Specific knowledge: what you'd do for free is your superpower",
            "Leverage comes in three forms: labor, capital, and code",
            "Play long-term games with long-term people",
            "Happiness is a skill you can learn and practice",
            "Desire is a contract you make with yourself to be unhappy"
        ],
        philosophyZh: [
            "特定知识：你愿意免费做的事就是你的超能力",
            "杠杆有三种形式：劳动力、资本和代码",
            "和长期主义者玩长期游戏",
            "幸福是一种可以学习和练习的技能",
            "欲望是你与自己签订的不快乐契约"
        ],
        keyInsight: "Naval's greatest product is his thinking. He turned philosophy into a scalable asset — the Almanack is free, yet it generated billions in influence and deal flow. His framework: think deeply, share generously, monetize indirectly.",
        keyInsightZh: "纳瓦尔最伟大的产品是他的思想。他将哲学变成了可扩展的资产——年鉴是免费的，却产生了数十亿的影响力和交易流。他的框架：深度思考、慷慨分享、间接变现。",
        businessModel: "Investing + Philosophy",
        businessModelZh: "投资 + 哲学",
        tags: ["Leverage", "Philosophy", "Angel Investing", "Specific Knowledge"]
    },
    {
        id: "james-clear",
        name: "James Clear",
        nameZh: "詹姆斯·克利尔",
        role: "Author • Habit Architect",
        roleZh: "作家 • 习惯架构师",
        category: ["content"],
        avatar: cartoonAvatar("james", "#00d68f", "#4ecdc4"),
        avatarBg: "linear-gradient(135deg, #00d68f, #4ecdc4)",
        bio: "Turned a personal blog about habits into Atomic Habits — 15M+ copies sold, $10M+/year. The 3-2-1 Newsletter reaches 2M+ subscribers. Pure content compounding.",
        bioZh: "将一个关于习惯的个人博客变成了《掌控习惯》（Atomic Habits）——销量超过1500万册，年收入超1000万美元。3-2-1通讯覆盖200万+订阅者。纯粹的内容复利。",
        metrics: [
            { value: "15M+", label: "Books Sold", labelZh: "销量" },
            { value: "$10M+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "2M+", label: "Newsletter Subs", labelZh: "通讯订阅" },
            { value: "1", label: "Book", labelZh: "一本书" }
        ],
        website: "https://jamesclear.com",
        twitter: "https://twitter.com/JamesClear",
        quote: "You do not rise to the level of your goals. You fall to the level of your systems.",
        quoteZh: "你不会上升到目标的高度，你会跌落到系统的水平。",
        philosophy: [
            "Systems over goals — focus on the process, not the outcome",
            "Content compounds — every article is an asset forever",
            "Email list is the most valuable asset in the internet age",
            "Write for one specific reader, not a vague audience",
            "Consistency beats intensity every single time"
        ],
        philosophyZh: [
            "系统优于目标——关注过程，而非结果",
            "内容会复利增长——每篇文章都是永久资产",
            "邮件列表是互联网时代最有价值的资产",
            "为一个具体的读者写作，而非模糊的受众",
            "一致性每次都能击败强度"
        ],
        keyInsight: "James spent 3 years building his email list before publishing Atomic Habits. By launch day, he had 500K+ subscribers ready to buy. The book didn't create his audience — the audience created the book's success.",
        keyInsightZh: "詹姆斯在出版《掌控习惯》之前花了3年时间建立邮件列表。到发布日，他已经有50万+订阅者等着购买。书没有创造受众——是受众创造了书的成功。",
        businessModel: "Books + Newsletter + Speaking",
        businessModelZh: "书籍 + 通讯 + 演讲",
        tags: ["Habits", "Writing", "Newsletter", "Compounding"]
    },
    {
        id: "jason-fried",
        name: "Jason Fried & DHH",
        nameZh: "杰森·弗里德 & DHH",
        role: "Basecamp/37signals Founders",
        roleZh: "Basecamp/37signals 创始人",
        category: ["saas"],
        avatar: cartoonAvatar("jason", "#e17055", "#fdcb6e"),
        avatarBg: "linear-gradient(135deg, #e17055, #fdcb6e)",
        bio: "Built Basecamp into $30M+ ARR with radical anti-VC principles. Wrote 'Rework' which redefined startup culture. Proved that calm companies beat growth-obsessed startups.",
        bioZh: "以激进的反风投原则将Basecamp打造成年收入3000万+的产品。撰写了重新定义创业文化的《重来》（Rework）。证明了平静的公司胜过痴迷增长的创业公司。",
        metrics: [
            { value: "$30M+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "100K+", label: "Paying Companies", labelZh: "付费企业" },
            { value: "7", label: "Books Written", labelZh: "已出版书籍" },
            { value: "20+", label: "Years Profitable", labelZh: "盈利年数" }
        ],
        website: "https://basecamp.com",
        twitter: "https://twitter.com/jasonfried",
        quote: "You can work 40 hours a week and be just as productive as someone working 80.",
        quoteZh: "每周工作40小时，可以和每周工作80小时的人一样高效。",
        philosophy: [
            "No VC, no board, no growth pressure — profitable from month one",
            "Work 40 hours, not 80 — burnout is a bug, not a feature",
            "Opinionated software: we decide for the customer",
            "Meetings are toxic — use writing instead",
            "Small team, big impact — 70 people, $30M+ revenue"
        ],
        philosophyZh: [
            "不拿风投、不设董事会、没有增长压力——第一个月就盈利",
            "每周40小时，不是80——倦怠是bug，不是feature",
            "有态度的软件：我们替用户做决定",
            "会议有毒——用写作代替",
            "小团队大影响——70人创造3000万+收入"
        ],
        keyInsight: "37signals proved that 'small' is a strategy. By rejecting VC, they kept 100% ownership and made decisions based on product quality, not investor pressure. Rework became the bible for bootstrapped founders.",
        keyInsightZh: "37signals证明了'小'是一种战略。通过拒绝风投，他们保持了100%所有权，基于产品质量而非投资人压力做决策。《重来》成为自力更生创业者的圣经。",
        businessModel: "SaaS + Books",
        businessModelZh: "SaaS + 书籍",
        tags: ["Bootstrapped", "Anti-VC", "Calm Company", "Writing"]
    },
    {
        id: "sahil-lavingia",
        name: "Sahil Lavingia",
        nameZh: "萨希尔·拉文吉亚",
        role: "Gumroad Founder • Minimalist",
        roleZh: "Gumroad创始人 • 极简主义者",
        category: ["saas", "creator"],
        avatar: cartoonAvatar("sahil", "#fd79a8", "#e84393"),
        avatarBg: "linear-gradient(135deg, #fd79a8, #e84393)",
        bio: "Built Gumroad, failed to raise VC, then rebuilt it as a profitable calm company. The anti-hustle founder who does SaaS, writing, painting, and investing simultaneously.",
        bioZh: "打造了Gumroad，融资失败后将其重建为盈利的平静公司。反内卷创始人，同时做SaaS、写作、绘画和天使投资。",
        metrics: [
            { value: "$10M+", label: "Gumroad GMV", labelZh: "平台交易额" },
            { value: "$2M+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "50K+", label: "Creators Served", labelZh: "服务创作者" },
            { value: "1", label: "Full-time Person", labelZh: "全职人员" }
        ],
        website: "https://sahillavingia.com",
        twitter: "https://twitter.com/shl",
        quote: "The best work happens when you're relaxed, not when you're stressed.",
        quoteZh: "最好的工作发生在你放松的时候，而不是紧张的时候。",
        philosophy: [
            "Small is beautiful — you don't need to be a unicorn",
            "Multihyphenate: founder + writer + painter + investor",
            "Profitability > Growth at all costs",
            "Vulnerability is a competitive advantage",
            "Work on what excites you, not what maximizes revenue"
        ],
        philosophyZh: [
            "小即是美——你不需要成为独角兽",
            "多重身份：创始人+作家+画家+投资人",
            "盈利 > 不惜一切代价的增长",
            "脆弱性是竞争优势",
            "做让你兴奋的事，而非收入最大化的事"
        ],
        keyInsight: "After raising $8M and being told to grow aggressively, Sahil laid off 75% of his team, went solo, and made Gumroad profitable. Sometimes the best business decision is to shrink.",
        keyInsightZh: "在融资800万美元并被要求激进增长后，萨希尔裁掉了75%的团队，独自运营，让Gumroad盈利了。有时候最好的商业决策是缩小规模。",
        businessModel: "Marketplace + Creator Economy",
        businessModelZh: "平台 + 创作者经济",
        tags: ["Minimalism", "Resilience", "Creator Economy", "Pivot"]
    },
    {
        id: "jack-butcher",
        name: "Jack Butcher",
        nameZh: "杰克·布彻",
        role: "Visualize Value Founder",
        roleZh: "Visualize Value 创始人",
        category: ["creator"],
        avatar: cartoonAvatar("jack", "#2d3436", "#636e72"),
        avatarBg: "linear-gradient(135deg, #2d3436, #636e72)",
        bio: "From agency designer to one-person visual thinking empire. Visualize Value, Checks VV, and Opepen generated $5M+ through courses, NFTs, and visual frameworks.",
        bioZh: "从广告公司设计师到一人视觉思维帝国。Visualize Value、Checks VV和Opepen通过课程、NFT和视觉框架创造了500万+美元收入。",
        metrics: [
            { value: "$5M+", label: "Total Revenue", labelZh: "总收入" },
            { value: "500K+", label: "Twitter Followers", labelZh: "推特粉丝" },
            { value: "100+", label: "Visual Frameworks", labelZh: "视觉框架" },
            { value: "0", label: "Employees", labelZh: "员工数" }
        ],
        website: "https://visualizevalue.com",
        twitter: "https://twitter.com/jackbutcher",
        quote: "What if your work could work for you while you sleep?",
        quoteZh: "如果你的作品能在你睡觉时为你工作呢？",
        philosophy: [
            "Visual thinking: distill complex ideas into simple visuals",
            "One product, multiple monetization layers",
            "Aesthetic is a moat — good design = instant credibility",
            "NFTs as a distribution channel for digital art",
            "Simplicity is the ultimate sophistication"
        ],
        philosophyZh: [
            "视觉思维：将复杂想法提炼为简单图形",
            "一个产品，多层变现",
            "审美即护城河——好的设计=即时可信度",
            "NFT作为数字艺术的分发渠道",
            "简约是终极的精致"
        ],
        keyInsight: "Jack's entire business runs on visual frameworks — simple diagrams that explain complex ideas. He creates once on Figma, then sells as courses, NFTs, and frameworks. Zero marginal cost, infinite distribution.",
        keyInsightZh: "杰克的整个业务建立在视觉框架之上——用简单图表解释复杂想法。他在Figma上创建一次，然后作为课程、NFT和框架出售。零边际成本，无限分发。",
        businessModel: "Digital Products + NFTs + Courses",
        businessModelZh: "数字产品 + NFT + 课程",
        tags: ["Visual Thinking", "Web3", "Design", "One Product"]
    },
    {
        id: "derek-sivers",
        name: "Derek Sivers",
        nameZh: "德里克·西弗斯",
        role: "CD Baby Founder • Author",
        roleZh: "CD Baby创始人 • 作家",
        category: ["content", "consulting"],
        avatar: cartoonAvatar("derek", "#0984e3", "#74b9ff"),
        avatarBg: "linear-gradient(135deg, #0984e3, #74b9ff)",
        bio: "Founded CD Baby, sold it for $22M, gave it all to charity. Now writes books and essays that influence millions. Proves that wealth isn't the goal — freedom is.",
        bioZh: "创立CD Baby，以2200万美元卖出，全部捐给慈善机构。现在撰写影响数百万人的书籍和散文。证明财富不是目标——自由才是。",
        metrics: [
            { value: "$22M", label: "CD Baby Sale", labelZh: "出售价格" },
            { value: "3", label: "Bestselling Books", labelZh: "畅销书" },
            { value: "1M+", label: "Book Readers", labelZh: "读者" },
            { value: "$0", label: "Kept from Sale", labelZh: "自留金额" }
        ],
        website: "https://sive.rs",
        twitter: "https://twitter.com/sivers",
        quote: "Success is when you can stop doing what you dislike.",
        quoteZh: "成功就是你可以停止做自己不喜欢的事。",
        philosophy: [
            "Hell yes or no — if it's not a clear yes, it's a no",
            "Ideas are just multipliers — execution is worth millions",
            "Keep your day job until your passion pays",
            "Teach everything you know for free — it comes back",
            "The purpose of business is freedom, not money"
        ],
        philosophyZh: [
            "要么绝对愿意，要么直接拒绝——不是明确的'是'就是'不'",
            "想法只是乘数——执行力才值百万",
            "在副业能养活你之前，保住主业",
            "免费教你所知道的一切——它会回来的",
            "商业的目的是自由，而非金钱"
        ],
        keyInsight: "Derek's 'Ideas vs Execution' framework: an idea is worth $1 without execution, but $20M with great execution. He also showed that giving away $22M didn't make him poorer — it made him freer.",
        keyInsightZh: "德里克的'想法vs执行'框架：没有执行力的想法只值1美元，但出色的执行力能让它值2000万。他还证明了捐出2200万并没有让他更穷——而是让他更自由。",
        businessModel: "Books + Speaking + Teaching",
        businessModelZh: "书籍 + 演讲 + 教学",
        tags: ["Philosophy", "Music", "Generosity", "Freedom"]
    },
    {
        id: "tim-ferriss",
        name: "Tim Ferriss",
        nameZh: "蒂姆·费里斯",
        role: "Author • Investor • Experimenter",
        roleZh: "作家 • 投资人 • 实验家",
        category: ["content", "finance"],
        avatar: cartoonAvatar("tim", "#00b894", "#55efc4"),
        avatarBg: "linear-gradient(135deg, #00b894, #55efc4)",
        bio: "4-Hour Workweek created the 'lifestyle design' movement. Podcast has 900M+ downloads. Angel investor in Uber, Twitter, Shopify. The original solopreneur thought leader.",
        bioZh: "《每周工作4小时》开创了'生活方式设计'运动。播客下载量超过9亿次。Uber、Twitter、Shopify的天使投资人。初代独立创业者思想领袖。",
        metrics: [
            { value: "2M+", label: "Books Sold", labelZh: "销量" },
            { value: "900M+", label: "Podcast Downloads", labelZh: "播客下载" },
            { value: "60+", label: "Angel Investments", labelZh: "天使投资" },
            { value: "$100M+", label: "Portfolio Value", labelZh: "投资组合" }
        ],
        website: "https://tim.blog",
        twitter: "https://twitter.com/tferriss",
        quote: "Focus on being productive instead of busy.",
        quoteZh: "专注于高效，而非忙碌。",
        philosophy: [
            "Lifestyle design: build a business that serves your life",
            "80/20 everything — focus on the vital few",
            "Outsource and automate relentlessly",
            "The podcast as a learning tool — interview the best",
            "Angel investing = paid education with upside"
        ],
        philosophyZh: [
            "生活方式设计：打造一个服务于你人生的事业",
            "80/20法则一切——关注关键少数",
            "无限制地外包和自动化",
            "播客作为学习工具——采访最优秀的人",
            "天使投资=带上升空间的付费教育"
        ],
        keyInsight: "The 4-Hour Workweek created an entire industry of remote work, outsourcing, and lifestyle business. Tim's insight: the book IS the marketing engine for everything else he does.",
        keyInsightZh: "《每周工作4小时》创造了远程办公、外包和生活方式商业的整个产业。蒂姆的洞见：书本身就是其他一切的营销引擎。",
        businessModel: "Books + Podcast + Angel Investing",
        businessModelZh: "书籍 + 播客 + 天使投资",
        tags: ["4-Hour", "Podcasting", "Lifestyle Design", "Investing"]
    },
    {
        id: "marc-lou",
        name: "Marc Lou",
        nameZh: "马克·卢",
        role: "Serial Shipper • Vibe Coder",
        roleZh: "连续发布者 • 氛围编码者",
        category: ["saas"],
        avatar: cartoonAvatar("marc", "#fdcb6e", "#e17055"),
        avatarBg: "linear-gradient(135deg, #fdcb6e, #e17055)",
        bio: "French developer who launched 20+ SaaS products in 2 years as a solo founder. Ships faster than anyone alive.",
        bioZh: "法国开发者，2年内以个人创始人身份发布20+个SaaS产品。发布速度无人能及。",
        metrics: [
            { value: "$500K+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "20+", label: "Products Shipped", labelZh: "已发布产品" },
            { value: "100K+", label: "Twitter Followers", labelZh: "推特粉丝" },
            { value: "0", label: "Employees", labelZh: "员工数" }
        ],
        website: "https://marclou.beehiiv.com",
        twitter: "https://twitter.com/marc_louvion",
        quote: "Ship fast. The internet forgets your failures but remembers your wins.",
        quoteZh: "快速发布。互联网会忘记你的失败，但会记住你的成功。",
        philosophy: [
            "Ship in days, not months — velocity beats perfection",
            "Multiple small products > one big product",
            "AI is the ultimate co-pilot for solo founders",
            "Build in public: every launch is marketing",
            "Revenue validates; opinions don't"
        ],
        philosophyZh: [
            "几天内发布，而非几个月——速度胜过完美",
            "多个小产品 > 一个大产品",
            "AI是独立创始人的终极副驾驶",
            "公开构建：每次发布都是营销",
            "收入验证一切，观点不值钱"
        ],
        keyInsight: "Marc's 'vibe coding' approach means using AI to build entire products in hours. The barrier to launching SaaS has dropped to nearly zero. The game is now speed of iteration, not quality of code.",
        keyInsightZh: "马克的'氛围编码'方法意味着用AI在几小时内构建完整产品。发布SaaS的门槛已降至接近零。现在的游戏是迭代速度，而非代码质量。",
        businessModel: "SaaS Portfolio",
        businessModelZh: "SaaS组合",
        tags: ["Ship Fast", "AI Native", "Vibe Coding", "Portfolio"]
    },
    {
        id: "daniel-vassallo",
        name: "Daniel Vassallo",
        nameZh: "丹尼尔·瓦萨洛",
        role: "AWS Defector • Small Bets Founder",
        roleZh: "AWS叛逃者 • 小赌注创始人",
        category: ["saas", "consulting"],
        avatar: cartoonAvatar("daniel", "#a29bfe", "#fd79a8"),
        avatarBg: "linear-gradient(135deg, #a29bfe, #fd79a8)",
        bio: "Left a $500K/year AWS job to build small bets. Now runs a portfolio of tiny products generating $500K+/year. Proves that many small bets beat one big bet.",
        bioZh: "放弃了年薪50万美元的AWS工作去做小赌注。现在运营着一个年收入50万+的小产品组合。证明许多小赌注胜过一个大赌注。",
        metrics: [
            { value: "$500K+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "5+", label: "Small Products", labelZh: "小产品" },
            { value: "30K+", label: "Twitter Followers", labelZh: "推特粉丝" },
            { value: "$500K", label: "Salary Left", labelZh: "放弃的薪资" }
        ],
        website: "https://danielvassallo.com",
        twitter: "https://twitter.com/dvassallo",
        quote: "Most of my products make less than $2K/month. Combined, they make more than my AWS salary.",
        quoteZh: "我的大多数产品每月赚不到2000美元。但加起来，比我在AWS的工资还多。",
        philosophy: [
            "Small bets: diversify across many tiny products",
            "The probability of one big hit is low — spread risk",
            "Usefulness > polish — solve a tiny problem well",
            "Income diversification as a solo founder",
            "Quit the golden handcuffs — freedom > salary"
        ],
        philosophyZh: [
            "小赌注：分散投资多个小产品",
            "一个大成功的概率很低——分散风险",
            "有用 > 精致——把一个小问题解决好",
            "作为独立创始人的收入多元化",
            "挣脱金手铐——自由 > 薪水"
        ],
        keyInsight: "Daniel's 'Small Bets' philosophy is the anti-unicorn thesis. Instead of betting everything on one product, launch many small ones. His portfolio of 'unimpressive' products adds up to more than his AWS salary.",
        keyInsightZh: "丹尼尔的'小赌注'哲学是反独角兽论。与其把所有赌注压在一个产品上，不如发布许多小产品。他那些'不起眼'的产品组合加起来比AWS工资还多。",
        businessModel: "SaaS Portfolio + Courses",
        businessModelZh: "SaaS组合 + 课程",
        tags: ["Small Bets", "Portfolio", "AWS", "Risk Management"]
    },
    {
        id: "jon-yongfook",
        name: "Jon Yongfook",
        nameZh: "乔恩·永福",
        role: "Bannerbear Founder",
        roleZh: "Bannerbear 创始人",
        category: ["saas"],
        avatar: cartoonAvatar("jon", "#636e72", "#2d3436"),
        avatarBg: "linear-gradient(135deg, #636e72, #2d3436)",
        bio: "Solo SaaS founder living in Japan. Bannerbear (automated image/video generation API) runs as a one-person company at $25K+/MRR. The quiet achiever.",
        bioZh: "居住在日本的独立SaaS创始人。Bannerbear（自动化图片/视频生成API）以一人公司模式运营，月收入2.5万+美元。安静的成就者。",
        metrics: [
            { value: "$25K+", label: "Monthly Revenue", labelZh: "月收入" },
            { value: "1", label: "Product", labelZh: "一个产品" },
            { value: "3", label: "Years Solo", labelZh: "独立年数" },
            { value: "0", label: "Meetings/Week", labelZh: "每周会议" }
        ],
        website: "https://yongfook.com",
        twitter: "https://twitter.com/yongfook",
        quote: "You don't need a big team to build a useful API product.",
        quoteZh: "你不需要一个大团队来打造一个有用的API产品。",
        philosophy: [
            "One product, deeply maintained — no feature bloat",
            "API-first: let developers build on your infrastructure",
            "Automate everything — from billing to support",
            "Live where you want — geographic freedom",
            "Quiet growth > loud growth"
        ],
        philosophyZh: [
            "一个产品，深度维护——不做功能膨胀",
            "API优先：让开发者在你的基础设施上构建",
            "自动化一切——从计费到客服",
            "住在你想住的地方——地理自由",
            "安静增长 > 喧嚣增长"
        ],
        keyInsight: "Bannerbear proves that B2B API products are the perfect OPC model. Developers self-serve, documentation replaces sales, and the product literally prints money while you sleep.",
        keyInsightZh: "Bannerbear证明了B2B API产品是完美的OPC模式。开发者自助服务，文档取代销售，产品在你睡觉时自动赚钱。",
        businessModel: "SaaS (API)",
        businessModelZh: "SaaS（API服务）",
        tags: ["API", "Japan", "Automation", "Quiet Growth"]
    },
    {
        id: "tony-dinh",
        name: "Tony Dinh",
        nameZh: "丁德胜",
        role: "Indie Maker • Vietnam",
        roleZh: "独立创造者 • 越南",
        category: ["saas"],
        avatar: cartoonAvatar("tony", "#e17055", "#fdcb6e"),
        avatarBg: "linear-gradient(135deg, #e17055, #fdcb6e)",
        bio: "Vietnamese developer who left his job to build TypingMind, BlackMagic.so, and other tools. $40K+/MRR as a solo founder. Asia's top indie maker.",
        bioZh: "越南开发者，离职后打造了TypingMind、BlackMagic.so等工具。以独立创始人身份实现月收入4万+美元。亚洲顶级独立创造者。",
        metrics: [
            { value: "$40K+", label: "Monthly Revenue", labelZh: "月收入" },
            { value: "5+", label: "Products", labelZh: "产品数" },
            { value: "100K+", label: "Users", labelZh: "用户数" },
            { value: "0", label: "Employees", labelZh: "员工数" }
        ],
        website: "https://twitter.com/meablosstony",
        twitter: "https://twitter.com/meablosstony",
        quote: "Build for developers. They understand the value and pay without sales calls.",
        quoteZh: "为开发者构建。他们理解价值，不需要销售电话就会付费。",
        philosophy: [
            "Build developer tools — high willingness to pay",
            "Lifetime deals as initial validation + cash flow",
            "Asia-based, global market — cost arbitrage advantage",
            "One product funds the next — bootstrap chain",
            "Community-driven development"
        ],
        philosophyZh: [
            "构建开发者工具——付费意愿高",
            "终身买断作为初始验证+现金流",
            "立足亚洲，面向全球——成本套利优势",
            "一个产品为下一个产品提供资金——自力更生链",
            "社区驱动开发"
        ],
        keyInsight: "Tony's strategy is pure cost arbitrage: live in Vietnam, sell globally, keep costs near zero. His $40K MRR goes 5x further than in San Francisco.",
        keyInsightZh: "丁德胜的策略是纯粹的成本套利：住在越南，全球销售，成本接近零。他的4万美元月收入在越南的购买力是旧金山的5倍。",
        businessModel: "SaaS + Lifetime Deals",
        businessModelZh: "SaaS + 终身买断",
        tags: ["Vietnam", "DevTools", "Lifetime Deals", "Bootstrapped"]
    },
    {
        id: "andrew-wilkinson",
        name: "Andrew Wilkinson",
        nameZh: "安德鲁·威尔金森",
        role: "Tiny.com Founder • Investor",
        roleZh: "Tiny.com创始人 • 投资人",
        category: ["finance", "consulting"],
        avatar: cartoonAvatar("andrew", "#0984e3", "#6c5ce7"),
        avatarBg: "linear-gradient(135deg, #0984e3, #6c5ce7)",
        bio: "Founded MetaLab (design agency), then Tiny.com (holding company). Bought 30+ businesses. Proves that buying > building for many solopreneurs.",
        bioZh: "创立了MetaLab（设计公司），然后是Tiny.com（控股公司）。收购了30+家企业。证明对很多独立创业者来说，买比建更好。",
        metrics: [
            { value: "$100M+", label: "Portfolio Revenue", labelZh: "组合收入" },
            { value: "30+", label: "Companies Acquired", labelZh: "收购企业" },
            { value: "20+", label: "Years in Business", labelZh: "商业年数" },
            { value: "$50M+", label: "Personal Net Worth", labelZh: "个人净资产" }
        ],
        website: "https://tiny.com",
        twitter: "https://twitter.com/awilkinson",
        quote: "Don't build a business. Buy a boring business and make it better.",
        quoteZh: "不要创建企业。买一个无聊的生意，然后把它做得更好。",
        philosophy: [
            "Acquisition entrepreneurship: buy, don't build",
            "Boring businesses are the best investments",
            "Design as a competitive moat",
            "Hold forever — don't flip",
            "Cash flow > Growth"
        ],
        philosophyZh: [
            "收购式创业：买，不要建",
            "无聊的生意是最好的投资",
            "设计作为竞争护城河",
            "永远持有——不要转手",
            "现金流 > 增长"
        ],
        keyInsight: "Why build from zero when you can buy a profitable business for 3-5x earnings? The OPC playbook: buy a small business, run it solo, live well.",
        keyInsightZh: "当你能以3-5倍利润买下一家盈利企业时，为什么要从零开始？OPC剧本：买一个小生意，独自运营，活得很好。",
        businessModel: "Acquisitions + Holding Company",
        businessModelZh: "收购 + 控股公司",
        tags: ["Acquisitions", "Boring Business", "Design", "Cash Flow"]
    },
    {
        id: "paul-jarvis",
        name: "Paul Jarvis",
        nameZh: "保罗·贾维斯",
        role: "Company of One • Author",
        roleZh: "一人公司 • 作家",
        category: ["content", "saas"],
        avatar: cartoonAvatar("paul", "#55efc4", "#00b894"),
        avatarBg: "linear-gradient(135deg, #55efc4, #00b894)",
        bio: "Built a one-person company around writing, courses, and Fathom Analytics (privacy-focused web analytics). Proves that ethics + profit can coexist.",
        bioZh: "围绕写作、课程和Fathom Analytics（隐私优先的网站分析）打造了一人公司。证明了道德+利润可以共存。",
        metrics: [
            { value: "$1M+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "50K+", label: "Newsletter Subs", labelZh: "通讯订阅" },
            { value: "10K+", label: "Fathom Users", labelZh: "Fathom用户" },
            { value: "1", label: "Company of One", labelZh: "一人公司" }
        ],
        website: "https://pjrvs.com",
        twitter: "https://twitter.com/pjrvs",
        quote: "What if the goal isn't to grow, but to stay small and profitable?",
        quoteZh: "如果目标不是增长，而是保持小而盈利呢？",
        philosophy: [
            "Company of One: staying small as a deliberate choice",
            "Privacy as a product — Fathom vs Google Analytics",
            "Write for the person you were 5 years ago",
            "Courses scale knowledge without scaling headcount",
            "Ethical business is good business"
        ],
        philosophyZh: [
            "一人公司：刻意选择保持小规模",
            "隐私即产品——Fathom vs Google Analytics",
            "为5年前的自己写作",
            "课程可以规模化知识而不增加人数",
            "道德的生意就是好生意"
        ],
        keyInsight: "Paul's 'Company of One' is the philosophical foundation of the OPC movement. Growth isn't always the answer. Some businesses are better at 1 person than at 10.",
        keyInsightZh: "保罗的'一人公司'是OPC运动的哲学基础。增长并不总是答案。有些企业一个人比十个人更好。",
        businessModel: "SaaS + Books + Courses",
        businessModelZh: "SaaS + 书籍 + 课程",
        tags: ["Privacy", "Company of One", "Ethics", "Writing"]
    },
    {
        id: "justin-welsh",
        name: "Justin Welsh",
        nameZh: "贾斯汀·威尔士",
        role: "LinkedIn Empire • Solopreneur",
        roleZh: "LinkedIn帝国 • 独立创业者",
        category: ["content", "saas"],
        avatar: cartoonAvatar("justin", "#0984e3", "#74b9ff"),
        avatarBg: "linear-gradient(135deg, #0984e3, #74b9ff)",
        bio: "Left a VP role to build a solopreneur empire. LinkedIn audience of 500K+, courses, newsletter, and SaaS tools. $5M+ in revenue as a one-person company.",
        bioZh: "辞去VP职位打造独立创业者帝国。LinkedIn受众50万+，课程、通讯和SaaS工具。以一人公司创造了500万+美元收入。",
        metrics: [
            { value: "$5M+", label: "Total Revenue", labelZh: "总收入" },
            { value: "500K+", label: "LinkedIn Followers", labelZh: "LinkedIn粉丝" },
            { value: "100K+", label: "Newsletter Subs", labelZh: "通讯订阅" },
            { value: "0", label: "Employees", labelZh: "员工数" }
        ],
        website: "https://justinwelsh.com",
        twitter: "https://twitter.com/thejustinwelsh",
        quote: "I built a $5M+ business with no employees, no investors, and no office.",
        quoteZh: "我用零员工、零投资、零办公室打造了一个500万+美元的生意。",
        philosophy: [
            "LinkedIn is the most underrated platform for solopreneurs",
            "Content systems: batch-create, schedule, engage",
            "Digital products scale infinitely — courses, templates, guides",
            "One audience, multiple monetization layers",
            "Systematize everything — SOPs for solo founders"
        ],
        philosophyZh: [
            "LinkedIn是独立创业者最被低估的平台",
            "内容系统：批量创建、定时发布、互动",
            "数字产品无限扩展——课程、模板、指南",
            "一个受众，多层变现",
            "系统化一切——独立创始人的SOP"
        ],
        keyInsight: "Justin's playbook is repeatable: build a LinkedIn audience (free), create a newsletter (free), sell courses and templates (high margin). Total cost to start: $0.",
        keyInsightZh: "贾斯汀的剧本是可复制的：建立LinkedIn受众（免费），创建通讯（免费），销售课程和模板（高利润）。启动总成本：0美元。",
        businessModel: "Courses + Newsletter + SaaS",
        businessModelZh: "课程 + 通讯 + SaaS",
        tags: ["LinkedIn", "Newsletter", "Courses", "Systems"]
    },
    {
        id: "greg-isenberg",
        name: "Greg Isenberg",
        nameZh: "格雷格·伊森伯格",
        role: "Community Builder • Investor",
        roleZh: "社群构建者 • 投资人",
        category: ["consulting", "content"],
        avatar: cartoonAvatar("greg", "#6c5ce7", "#fd79a8"),
        avatarBg: "linear-gradient(135deg, #6c5ce7, #fd79a8)",
        bio: "Founded Late Checkout (community design agency), advisor to Reddit and TikTok. Turns community thinking into business strategy. The OPC consultant archetype.",
        bioZh: "创立Late Checkout（社群设计公司），Reddit和TikTok顾问。将社群思维转化为商业战略。OPC咨询师的典范。",
        metrics: [
            { value: "$10M+", label: "Agency Revenue", labelZh: "公司收入" },
            { value: "50+", label: "Brand Clients", labelZh: "品牌客户" },
            { value: "200K+", label: "Twitter Followers", labelZh: "推特粉丝" },
            { value: "10+", label: "Angel Investments", labelZh: "天使投资" }
        ],
        website: "https://gregerm.com",
        twitter: "https://twitter.com/gregisenberg",
        quote: "The best businesses are communities with a product attached.",
        quoteZh: "最好的生意是带着产品的社群。",
        philosophy: [
            "Community-first: build the tribe before the product",
            "The future is niche communities, not mass platforms",
            "Content as a service — your thinking IS the product",
            "Advisory as a business model — high margin, low effort",
            "Every business should have a community layer"
        ],
        philosophyZh: [
            "社群优先：在产品之前建立部落",
            "未来是垂直社群，而非大众平台",
            "内容即服务——你的思考就是产品",
            "咨询作为商业模式——高利润，低投入",
            "每个企业都应该有社群层"
        ],
        keyInsight: "Greg proves that OPC consulting is the fastest path to high income. The playbook: free content → audience → inbound leads → premium consulting.",
        keyInsightZh: "格雷格证明了OPC咨询是通往高收入的最快路径。剧本：免费内容 → 受众 → 主动询盘 → 高端咨询。",
        businessModel: "Consulting + Agency + Investing",
        businessModelZh: "咨询 + 公司 + 投资",
        tags: ["Community", "Consulting", "Twitter", "Advisory"]
    },
    {
        id: "pat-flynn",
        name: "Pat Flynn",
        nameZh: "帕特·弗林",
        role: "Smart Passive Income Founder",
        roleZh: "Smart Passive Income 创始人",
        category: ["content"],
        avatar: cartoonAvatar("pat", "#fdcb6e", "#00b894"),
        avatarBg: "linear-gradient(135deg, #fdcb6e, #00b894)",
        bio: "Laid off in 2008, built Smart Passive Income into a multi-million dollar media business. Podcast pioneer, affiliate marketing expert, and the OG online educator.",
        bioZh: "2008年被裁员后，将Smart Passive Income打造成数百万美元的媒体业务。播客先驱、联盟营销专家、初代在线教育者。",
        metrics: [
            { value: "$3M+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "15+", label: "Years Podcasting", labelZh: "播客年数" },
            { value: "100K+", label: "Email Subscribers", labelZh: "邮件订阅" },
            { value: "0", label: "Boss", labelZh: "老板" }
        ],
        website: "https://smartpassiveincome.com",
        twitter: "https://twitter.com/PatFlynn",
        quote: "I made more money being honest about what I didn't know than pretending I knew everything.",
        quoteZh: "诚实地承认自己不懂的东西，比假装什么都懂赚了更多的钱。",
        philosophy: [
            "Be everywhere — podcast, YouTube, blog, social",
            "Transparency reports: share exact revenue numbers",
            "Multiple income streams — never depend on one",
            "Serve first, sell second — lead with value",
            "The audience is the asset, not the products"
        ],
        philosophyZh: [
            "无处不在——播客、YouTube、博客、社交媒体",
            "透明报告：分享精确的收入数字",
            "多条收入流——永远不要依赖单一来源",
            "先服务，后销售——用价值引领",
            "受众才是资产，不是产品"
        ],
        keyInsight: "Pat's monthly income reports were revolutionary. By sharing exact numbers, he built massive trust. Vulnerability and transparency are the most powerful marketing tools.",
        keyInsightZh: "帕特的月度收入报告是革命性的。通过分享精确数字，他建立了巨大的信任。脆弱性和透明度是最强大的营销工具。",
        businessModel: "Affiliate + Courses + Podcast Sponsorship",
        businessModelZh: "联盟营销 + 课程 + 播客赞助",
        tags: ["Podcasting", "Affiliate", "Transparency", "SPI"]
    },
    // ===== 亚洲 / 中国代表 =====
    {
        id: "tiny-fool",
        name: "Tiny (tinyfool)",
        nameZh: "Tiny（tinyfool）",
        role: "Developer Community Builder",
        roleZh: "独立开发者社区缔造者",
        category: ["saas", "creator"],
        avatar: cartoonAvatar("tiny", "#e17055", "#fdcb6e"),
        avatarBg: "linear-gradient(135deg, #e17055, #fdcb6e)",
        bio: "Chinese indie developer who built a developer community platform generating $100K+/year. Proves that solo founders in China can build global products.",
        bioZh: "中国独立开发者，一人打造开发者社区平台，年收入超10万美元。证明中国的独立创业者也能做出全球化产品。",
        metrics: [
            { value: "$100K+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "5+", label: "Products", labelZh: "产品数" },
            { value: "10+", label: "Years Solo", labelZh: "独立年数" },
            { value: "1", label: "Person", labelZh: "一个人" }
        ],
        website: "https://blog.tinyfool.org",
        twitter: "",
        quote: "独立开发最重要的是找到自己的节奏，不要被风口带跑。",
        quoteZh: "独立开发最重要的是找到自己的节奏，不要被风口带跑。",
        philosophy: [
            "找到自己的技术优势，不要盲目追热点",
            "一个人最大的优势是决策速度——没有会议、没有审批",
            "用技术壁垒替代资金壁垒",
            "持续输出内容建立个人品牌",
            "中国创业者出海是巨大机会"
        ],
        philosophyZh: [
            "找到自己的技术优势，不要盲目追热点",
            "一个人最大的优势是决策速度——没有会议、没有审批",
            "用技术壁垒替代资金壁垒",
            "持续输出内容建立个人品牌",
            "中国创业者出海是巨大机会"
        ],
        keyInsight: "Tiny证明了在中国做独立开发是可行的。关键洞察：不要和巨头硬碰硬，找垂直领域深耕。一个人+技术壁垒=可持续的商业模式。",
        keyInsightZh: "Tiny证明了在中国做独立开发是可行的。关键洞察：不要和巨头硬碰硬，找垂直领域深耕。一个人+技术壁垒=可持续的商业模式。",
        businessModel: "Community + SaaS + Content",
        businessModelZh: "社区 + SaaS + 内容",
        tags: ["中国", "独立开发", "社区", "出海"]
    },
    {
        id: "clay-he",
        name: "何夕 (Clay He)",
        nameZh: "何夕",
        role: "YC Partner • Indie Hacker Advocate",
        roleZh: "YC中国合伙人 • 独立开发者布道者",
        category: ["consulting", "content"],
        avatar: cartoonAvatar("clay", "#6c5ce7", "#a29bfe"),
        avatarBg: "linear-gradient(135deg, #6c5ce7, #a29bfe)",
        bio: "Former YC China partner who champions Chinese indie hackers. Turned his personal brand into a bridge between Chinese builders and global startup ecosystem.",
        bioZh: "前YC中国合伙人，中国独立开发者的支持者。将个人品牌打造成中国创业者与全球创业生态的桥梁。",
        metrics: [
            { value: "100K+", label: "Followers", labelZh: "关注者" },
            { value: "50+", label: "Companies Advised", labelZh: "辅导企业" },
            { value: "10+", label: "Years in Tech", labelZh: "科技行业年数" },
            { value: "1", label: "Voice", labelZh: "一个声音" }
        ],
        website: "https://twitter.com/clayhe",
        twitter: "https://twitter.com/clayhe",
        quote: "中国不缺好的工程师，缺的是好的独立创业者。",
        quoteZh: "中国不缺好的工程师，缺的是好的独立创业者。",
        philosophy: [
            "个人品牌是最好的杠杆——免费、不可替代",
            "独立创业的核心是「想清楚自己要什么」",
            "中国开发者出海的优势是工程能力+成本效率",
            "用内容吸引同频的人，比销售有效100倍",
            "做有复利的事情：写文章、建社区、投资"
        ],
        philosophyZh: [
            "个人品牌是最好的杠杆——免费、不可替代",
            "独立创业的核心是「想清楚自己要什么」",
            "中国开发者出海的优势是工程能力+成本效率",
            "用内容吸引同频的人，比销售有效100倍",
            "做有复利的事情：写文章、建社区、投资"
        ],
        keyInsight: "何夕的影响力来自于持续输出：他每天在社交媒体分享创业思考，建立了一个以他为中心的独立创业者网络。这证明了在中国，个人品牌+技术背景=无限可能。",
        keyInsightZh: "何夕的影响力来自于持续输出：他每天在社交媒体分享创业思考，建立了一个以他为中心的独立创业者网络。这证明了在中国，个人品牌+技术背景=无限可能。",
        businessModel: "Advisory + Investing + Content",
        businessModelZh: "咨询 + 投资 + 内容",
        tags: ["中国", "YC", "个人品牌", "投资"]
    },
    {
        id: "susan-su",
        name: "Susan Su",
        nameZh: "苏珊·苏",
        role: "Portfolio Partner • Solopreneur Creator",
        roleZh: "投资合伙人 • 独立创业者创作者",
        category: ["finance", "content"],
        avatar: cartoonAvatar("susan", "#fd79a8", "#e84393"),
        avatarBg: "linear-gradient(135deg, #fd79a8, #e84393)",
        bio: "Sound Ventures partner who built a massive Twitter following by sharing startup growth insights. Asian-American woman proving that diverse founders can build world-class brands.",
        bioZh: "Sound Ventures合伙人，通过分享创业增长见解建立了大量推特粉丝。亚裔女性证明了多元背景的创始人也能打造世界级品牌。",
        metrics: [
            { value: "200K+", label: "Twitter Followers", labelZh: "推特粉丝" },
            { value: "$1B+", label: "Fund AUM", labelZh: "基金管理规模" },
            { value: "100+", label: "Companies Advised", labelZh: "辅导企业" },
            { value: "0", label: "Co-founders", labelZh: "联合创始人" }
        ],
        website: "https://twitter.com/susanthesuark",
        twitter: "https://twitter.com/susanthesuark",
        quote: "Build your brand before you need it.",
        quoteZh: "在你需要个人品牌之前就先建立它。",
        philosophy: [
            "个人品牌是0成本的最强杠杆",
            "增长黑客思维应用于个人品牌建设",
            "亚洲创业者需要在西方建立话语权",
            "免费分享知识→建立信任→获得机会",
            "多样性不是口号，是竞争优势"
        ],
        philosophyZh: [
            "个人品牌是0成本的最强杠杆",
            "增长黑客思维应用于个人品牌建设",
            "亚洲创业者需要在西方建立话语权",
            "免费分享知识→建立信任→获得机会",
            "多样性不是口号，是竞争优势"
        ],
        keyInsight: "Susan证明了在投资圈，个人品牌的影响力可以超越机构品牌。她的推特影响力让她获得了比传统VC合伙人更多的deal flow。对OPC的启示：你不需要一个公司来拥有影响力。",
        keyInsightZh: "Susan证明了在投资圈，个人品牌的影响力可以超越机构品牌。她的推特影响力让她获得了比传统VC合伙人更多的deal flow。对OPC的启示：你不需要一个公司来拥有影响力。",
        businessModel: "VC + Content + Advisory",
        businessModelZh: "风投 + 内容 + 咨询",
        tags: ["投资", "增长", "个人品牌", "多样性"]
    },
    {
        id: "kong-fanli",
        name: "孔繁利",
        nameZh: "孔繁利",
        role: "Indie SaaS Founder • China",
        roleZh: "独立SaaS创始人 • 中国",
        category: ["saas"],
        avatar: cartoonAvatar("kong", "#00d68f", "#4ecdc4"),
        avatarBg: "linear-gradient(135deg, #00d68f, #4ecdc4)",
        bio: "Chinese developer who built profitable SaaS products serving global markets from China. Demonstrates that geographic arbitrage + technical skills = OPC success.",
        bioZh: "中国开发者，从中国服务全球市场打造了盈利的SaaS产品。证明了地理套利+技术能力=OPC成功。",
        metrics: [
            { value: "$50K+", label: "Monthly Revenue", labelZh: "月收入" },
            { value: "3", label: "SaaS Products", labelZh: "SaaS产品" },
            { value: "50+", label: "Countries Served", labelZh: "服务国家" },
            { value: "1", label: "Founder", labelZh: "创始人" }
        ],
        website: "#",
        twitter: "",
        quote: "在中国做SaaS，面向全球市场，一个人就够了。",
        quoteZh: "在中国做SaaS，面向全球市场，一个人就够了。",
        philosophy: [
            "中国开发者出海的黄金时代",
            "选对市场比做对产品更重要",
            "Stripe Atlas + Vercel = 全球化基础设施",
            "用英文内容获取海外用户",
            "一个人=零沟通成本=极致效率"
        ],
        philosophyZh: [
            "中国开发者出海的黄金时代",
            "选对市场比做对产品更重要",
            "Stripe Atlas + Vercel = 全球化基础设施",
            "用英文内容获取海外用户",
            "一个人=零沟通成本=极致效率"
        ],
        keyInsight: "孔繁利代表了一类新兴的中国OPC创业者：在国内开发，面向全球市场，用Stripe收款，用Vercel部署。这种模式的优势：中国的生活成本 + 全球的付费能力 = 极高利润率。",
        keyInsightZh: "孔繁利代表了一类新兴的中国OPC创业者：在国内开发，面向全球市场，用Stripe收款，用Vercel部署。这种模式的优势：中国的生活成本 + 全球的付费能力 = 极高利润率。",
        businessModel: "SaaS (Global Market)",
        businessModelZh: "SaaS（全球市场）",
        tags: ["中国", "出海", "SaaS", "地理套利"]
    },
    {
        id: "junyu-wu",
        name: "吴俊宇",
        nameZh: "吴俊宇",
        role: "Tech Writer • Independent Analyst",
        roleZh: "科技作者 • 独立分析师",
        category: ["content"],
        avatar: cartoonAvatar("junyu", "#0984e3", "#74b9ff"),
        avatarBg: "linear-gradient(135deg, #0984e3, #74b9ff)",
        bio: "Independent Chinese tech writer who built a premium newsletter and consulting practice through deep industry analysis. Proves that content alone can sustain a one-person company.",
        bioZh: "独立中国科技作者，通过深度行业分析打造了付费通讯和咨询业务。证明了内容本身就能支撑一人公司。",
        metrics: [
            { value: "¥100万+", label: "Annual Revenue", labelZh: "年收入" },
            { value: "10万+", label: "Subscribers", labelZh: "订阅者" },
            { value: "5+", label: "Years Writing", labelZh: "写作年数" },
            { value: "0", label: "Employees", labelZh: "员工" }
        ],
        website: "#",
        twitter: "",
        quote: "深度内容永远有市场，关键是找到你的受众。",
        quoteZh: "深度内容永远有市场，关键是找到你的受众。",
        philosophy: [
            "在中国做付费内容是可行的——关键是深度",
            "微信公众号+知识星球=中国的内容变现闭环",
            "独立分析的价值在于没有利益冲突",
            "写作是最好的思考工具",
            "个人品牌建立后，变现方式自然出现"
        ],
        philosophyZh: [
            "在中国做付费内容是可行的——关键是深度",
            "微信公众号+知识星球=中国的内容变现闭环",
            "独立分析的价值在于没有利益冲突",
            "写作是最好的思考工具",
            "个人品牌建立后，变现方式自然出现"
        ],
        keyInsight: "吴俊宇代表了中国版的James Clear——通过持续输出高质量行业分析，建立了付费读者群。他的模式：免费文章引流→知识星球付费→企业咨询变现。一套完整的内容OPC闭环。",
        keyInsightZh: "吴俊宇代表了中国版的James Clear——通过持续输出高质量行业分析，建立了付费读者群。他的模式：免费文章引流→知识星球付费→企业咨询变现。一套完整的内容OPC闭环。",
        businessModel: "Newsletter + Consulting + Community",
        businessModelZh: "通讯 + 咨询 + 社群",
        tags: ["中国", "内容", "写作", "付费订阅"]
    },
    {
        id: "liu-xiaopai",
        name: "刘小排",
        nameZh: "刘小排",
        role: "Indie Developer • Vibe Coding Pioneer",
        roleZh: "独立开发者 • 氛围编码先驱",
        category: ["saas", "creator"],
        avatar: cartoonAvatar("liuxp", "#fdcb6e", "#e17055"),
        avatarBg: "linear-gradient(135deg, #fdcb6e, #e17055)",
        bio: "Chinese indie developer who champions the 'vibe coding' movement. Builds and ships products rapidly using AI, proving that speed of iteration is the new competitive advantage.",
        bioZh: "中国独立开发者，'氛围编码'运动的倡导者。使用AI快速构建和发布产品，证明迭代速度是新的竞争优势。",
        metrics: [
            { value: "¥30K+", label: "Monthly Revenue", labelZh: "月收入" },
            { value: "10+", label: "Products Shipped", labelZh: "已发布产品" },
            { value: "100K+", label: "Followers", labelZh: "关注者" },
            { value: "0", label: "Team Members", labelZh: "团队成员" }
        ],
        website: "#",
        twitter: "",
        quote: "用AI写代码，用直觉做产品，用速度打败一切。",
        quoteZh: "用AI写代码，用直觉做产品，用速度打败一切。",
        philosophy: [
            "AI时代，一个人=一个团队",
            "vibe coding:不写完美代码，写能跑的代码",
            "每周发布一个产品，用数量换质量",
            "中国市场的机会在垂直场景",
            "公开构建是最好的营销——免费、真实、有效"
        ],
        philosophyZh: [
            "AI时代，一个人=一个团队",
            "vibe coding:不写完美代码，写能跑的代码",
            "每周发布一个产品，用数量换质量",
            "中国市场的机会在垂直场景",
            "公开构建是最好的营销——免费、真实、有效"
        ],
        keyInsight: "刘小排代表了中国版的Marc Lou——用AI工具（Cursor/Claude）极快速地构建产品。他的哲学：在AI时代，代码不再是壁垒，速度和洞察力才是。一个人用AI一天能做完过去一个团队一周的工作。",
        keyInsightZh: "刘小排代表了中国版的Marc Lou——用AI工具（Cursor/Claude）极快速地构建产品。他的哲学：在AI时代，代码不再是壁垒，速度和洞察力才是。一个人用AI一天能做完过去一个团队一周的工作。",
        businessModel: "SaaS Portfolio + AI Tools",
        businessModelZh: "SaaS组合 + AI工具",
        tags: ["中国", "AI", "氛围编码", "Ship Fast"]
    }
];

// Language state
let currentLang = 'en';

function setLang(lang) {
    currentLang = lang;
    document.documentElement.setAttribute('lang', lang === 'zh' ? 'zh-CN' : 'en');
}

function t(enVal, zhVal) {
    return currentLang === 'zh' ? (zhVal || enVal) : enVal;
}

window.LEGENDS = LEGENDS;
window.setLang = setLang;
window.t = t;
window.currentLang = () => currentLang;
