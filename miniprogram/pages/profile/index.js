const { orders } = require("../../utils/data");

Page({
  data: {
    orders,
    profile: {
      name: "Demo OPC Buyer",
      wallet: "0xad79...e137",
      verified: false,
      assets: 0,
      learning: 2
    }
  },

  copyH5() {
    wx.setClipboardData({ data: "https://opcplatform.cn/knovault/" });
  },

  applyVerify() {
    wx.showModal({
      title: "申请 Verified OPC",
      content: "生产版会提交钱包、作品样本和 Verification Pack。当前原型先展示入口。",
      showCancel: false
    });
  }
});
