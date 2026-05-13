# OPC Platform 微信小程序

定位：OPC 的淘宝交易、培训和信息平台。

这个小程序是 OPC Platform 的移动端入口，面向 AI 时代的一人公司。它把三类能力放到同一个微信内体验里：

1. **OPC 淘宝交易**：报告、模板、数据包、方法论、服务能力的可信货架。
2. **OPC 培训学院**：一人公司定位、AI 生产系统、知识资产商品化和交易能力训练。
3. **OPC 信息平台**：政策、案例、活动、项目机会和工具清单聚合。

## 当前版本

当前为原生微信小程序 MVP，可直接用微信开发者工具导入 `miniprogram/` 目录预览。

默认使用 `touristappid`。拿到正式小程序 AppID 后，修改 `project.config.json`：

```json
{
  "appid": "你的微信小程序 AppID"
}
```

## 页面结构

- `pages/home/index`：首页，展示定位、三大入口和重点资产。
- `pages/market/index`：交易广场，包含知识资产和服务能力。
- `pages/asset-detail/index`：资产详情，展示预览、版本、权益和 Monad Trust Events。
- `pages/training/index`：OPC 学院，展示学习路径和课程。
- `pages/info/index`：信息平台，展示政策、案例、活动和项目机会。
- `pages/profile/index`：我的 OPC，展示订阅记录、认证入口和 H5 交易链接。

## 交易设计

微信小程序不直接假设 MetaMask / injected wallet。当前交易路径是：

1. 小程序内发现资产、查看预览、生成订阅意向。
2. 复制或跳转到 `https://opcplatform.cn/knovault/`。
3. 在 H5 页面连接钱包，切换 Monad Testnet，完成 MON 订阅。
4. 后续由后端/indexer 同步 Monad Trust Events，再回显到小程序订单和声誉页。

当前 H5：

```text
https://opcplatform.cn/knovault/
```

Monad Testnet：

```text
Chain ID: 10143
Contract: 0x7BF016e8f9bBC6998BB15Ed8238052ed94d44C56
```

## 后续接入

生产版建议补齐：

- 微信登录与用户 openid。
- 后端 API：资产列表、课程列表、信息流、订阅意向单。
- Monad indexer：同步 `AssetRegistered`、`AssetVersionPublished`、`SubscriptionCreated`、`FeedbackSubmitted`。
- H5 支付回跳或轮询交易状态。
- 内容访问控制：订阅后展示访问说明、下载链接或受控内容页。
- OPC 认证流程：提交钱包、作品样本和 Verification Pack。

## 开发者工具导入

1. 打开微信开发者工具。
2. 选择「导入项目」。
3. 项目目录选择本目录：`miniprogram/`。
4. AppID 暂时选择测试号或使用 `touristappid`。
5. 编译运行。

## 设计口径

这不是单纯内容平台，也不是招聘平台。

OPC Platform 小程序的核心是让一人公司形成可交易能力：

- 知识资产能被上架。
- 买家能看预览和可信记录。
- 课程帮助 OPC 学会资产化。
- 信息流帮助 OPC 找政策、机会和案例。
- Monad 作为可信交易和声誉事件层。
