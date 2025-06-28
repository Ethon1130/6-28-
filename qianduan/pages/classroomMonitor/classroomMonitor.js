// pages/classroomMonitor/classroomMonitor.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    user: {}
  },

  handleLoadUser() {
    wx.request({
      url: 'http://localhost:8000/index/',  // 请求的 URL
      method: 'GET',  // 请求方法
      data: {},  // 请求参数，如果没有可以留空
      header: {},  // 请求头部信息，可以留空
      success: (res) => {
        console.log(res.data);  // 打印返回的数据
        this.setData({
          user: res.data  // 修改为正确的拼写 `user`
        });
      },

      fail: (error) => {
        console.log(error);  // 打印错误信息
      }
    });
  }
});
