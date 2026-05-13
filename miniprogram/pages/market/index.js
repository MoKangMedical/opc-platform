const { assets, services } = require("../../utils/data");

Page({
  data: {
    active: "asset",
    keyword: "",
    assets,
    services,
    filteredAssets: assets
  },

  switchMode(e) {
    this.setData({ active: e.currentTarget.dataset.mode });
  },

  onSearch(e) {
    const keyword = e.detail.value.trim().toLowerCase();
    const filteredAssets = assets.filter((asset) => {
      const haystack = [
        asset.title,
        asset.type,
        asset.seller,
        asset.promise,
        asset.tags.join(" ")
      ].join(" ").toLowerCase();
      return haystack.includes(keyword);
    });
    this.setData({ keyword, filteredAssets: keyword ? filteredAssets : assets });
  },

  openAsset(e) {
    wx.navigateTo({
      url: `/pages/asset-detail/index?id=${e.currentTarget.dataset.id}`
    });
  },

  createIntent(e) {
    const title = e.currentTarget.dataset.title;
    wx.showModal({
      title: "生成订阅意向",
      content: `已为「${title}」生成采购意向。真实付款请跳转 KnoVault H5 连接钱包完成。`,
      confirmText: "复制 H5",
      success(res) {
        if (res.confirm) {
          wx.setClipboardData({ data: "https://opcplatform.cn/knovault/" });
        }
      }
    });
  }
});
