const { infos } = require("../../utils/data");

Page({
  data: {
    infos,
    categories: ["全部", "政策", "案例", "活动", "项目", "工具"],
    activeCategory: "全部"
  },

  selectCategory(e) {
    const activeCategory = e.currentTarget.dataset.category;
    this.setData({ activeCategory });
  }
});
