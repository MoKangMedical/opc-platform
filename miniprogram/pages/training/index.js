const { courses } = require("../../utils/data");

Page({
  data: {
    courses,
    tracks: [
      "一人公司定位",
      "AI 生产系统",
      "知识资产商品化",
      "客户获取与交付",
      "可信声誉建设"
    ]
  },

  enroll(e) {
    wx.showToast({
      title: `已加入学习清单`,
      icon: "success"
    });
  }
});
