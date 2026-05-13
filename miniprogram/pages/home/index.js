const { assets, courses, infos } = require("../../utils/data");

Page({
  data: {
    stats: [
      { value: "3类", label: "知识资产" },
      { value: "67", label: "AI 项目机会" },
      { value: "10143", label: "Monad Testnet" },
      { value: "2.5%", label: "演示平台费" }
    ],
    entries: [
      {
        title: "OPC 淘宝交易",
        desc: "报告、模板、数据包、方法论和服务能力的可信货架。",
        path: "/pages/market/index"
      },
      {
        title: "OPC 培训学院",
        desc: "从一人公司定位、AI 生产系统到知识资产定价。",
        path: "/pages/training/index"
      },
      {
        title: "OPC 信息平台",
        desc: "政策、案例、活动和项目机会聚合。",
        path: "/pages/info/index"
      }
    ],
    featuredAsset: assets[0],
    featuredCourse: courses[2],
    latestInfo: infos[0]
  },

  goTo(e) {
    wx.switchTab({ url: e.currentTarget.dataset.path });
  },

  openKnoVault() {
    wx.showModal({
      title: "打开 H5 交易 Demo",
      content: "真实 MON 订阅需要在 H5 连接钱包完成。请复制链接到浏览器打开：https://opcplatform.cn/knovault/",
      confirmText: "复制链接",
      success(res) {
        if (res.confirm) {
          wx.setClipboardData({ data: "https://opcplatform.cn/knovault/" });
        }
      }
    });
  }
});
