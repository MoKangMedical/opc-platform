const { assets } = require("../../utils/data");

Page({
  data: {
    asset: null,
    contract: "0x7BF016e8f9bBC6998BB15Ed8238052ed94d44C56",
    events: [
      "AssetRegistered",
      "AssetVersionPublished",
      "SubscriptionCreated",
      "FeedbackSubmitted",
      "FirstTermApproved"
    ]
  },

  onLoad(query) {
    const asset = assets.find((item) => item.id === query.id) || assets[0];
    this.setData({ asset });
  },

  createIntent() {
    const title = this.data.asset.title;
    wx.showModal({
      title: "订阅当前版本",
      content: `你将订阅「${title}」当前有效版本。真实 MON 支付需要跳转 H5 连接钱包完成。`,
      confirmText: "复制 H5",
      success(res) {
        if (res.confirm) {
          wx.setClipboardData({ data: "https://opcplatform.cn/knovault/" });
        }
      }
    });
  }
});
