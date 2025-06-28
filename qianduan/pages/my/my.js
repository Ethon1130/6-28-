// pages/my/my.js
Page({
  data: {
    userInfo: null,
    nickname: '',   // 存储修改的昵称
    avatar: '',     // 存储修改的头像
  },

  onLoad: function () {
    // 获取用户信息，假设从缓存或其他地方获取
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo && userInfo.isLoggedIn) {
      this.setData({
        userInfo: userInfo,
        nickname: userInfo.nickName,
        avatar: userInfo.avatarUrl
      });
    }
  },

  // 修改头像
  changeAvatar() {
    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const avatar = res.tempFilePaths[0];
        this.setData({ avatar: avatar });

        // 上传头像至后端
        wx.uploadFile({
          url: 'https://your-backend-url/api/update-profile/',  // 后端更新用户资料的接口
          filePath: avatar,
          name: 'avatar',
          header: {
            'Authorization': `Bearer ${wx.getStorageSync('token')}` // 如果需要 Token 验证
          },
          success: (res) => {
            const data = JSON.parse(res.data);
            if (data.status === 'success') {
              this.setData({
                userInfo: data.user
              });
              wx.setStorageSync('userInfo', data.user);
            }
          }
        });
      }
    });
  },

  // 修改昵称
  editNickname() {
    wx.showModal({
      title: '修改昵称',
      content: '',
      editable: true,
      placeholderText: '请输入新昵称',
      success: (res) => {
        if (res.confirm && res.content) {
          this.setData({ nickname: res.content });

          // 发送修改昵称的请求到后端
          wx.request({
            url: 'https://your-backend-url/api/update-profile/',  // 后端更新用户资料的接口
            method: 'POST',
            data: { nickname: res.content },
            header: {
              'Authorization': `Bearer ${wx.getStorageSync('token')}`
            },
            success: (response) => {
              if (response.data.status === 'success') {
                this.setData({
                  userInfo: response.data.user
                });
                wx.setStorageSync('userInfo', response.data.user);
                wx.showToast({
                  title: '修改成功',
                  icon: 'success',
                  duration: 2000
                });
              } else {
                wx.showToast({
                  title: '修改失败',
                  icon: 'none',
                  duration: 2000
                });
              }
            }
          });
        }
      }
    });
  },


  onShow: function () {
    // 每次页面显示时检查登录状态
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo && userInfo.isLoggedIn) {
      this.setData({
        userInfo
      });
    }
  },

  goLogin: function () {
    // 跳转到登录页面
    wx.navigateTo({
      url: '/pages/login/login'
    });
  },

  onMenuTap: function (e) {
    const menu = e.currentTarget.dataset.menu;

    // 检查是否登录
    if (!this.data.userInfo) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      this.goLogin();
      return;
    }

    // 根据菜单项跳转到对应页面
    switch (menu) {
      case 'announcement':
        wx.navigateTo({ url: '/pages/announcement/announcement' });
        break;
      case 'message':
        wx.navigateTo({ url: '/pages/message/message' });
        break;
      case 'class-register':
        wx.navigateTo({ url: '/pages/class-register/class-register' });
        break;
      case 'evaluation':
        wx.navigateTo({ url: '/pages/evaluation/evaluation' });
        break;
      case 'leave':
        wx.navigateTo({ url: '/pages/leave/leave' });
        break;
      case 'attendance':
        wx.navigateTo({ url: '/pages/attendance/attendance' });
        break;
    }
  },

  onSettingTap: function () {
    wx.navigateTo({
      url: '/pages/settings/settings'
    });
  },

  onAboutTap: function () {
    wx.navigateTo({
      url: '/pages/about/about'
    });
  },

  logout: function () {
    // 退出登录
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除用户信息
          wx.removeStorageSync('userInfo');
          this.setData({
            userInfo: null
          });
          wx.showToast({
            title: '已退出登录',
            icon: 'none'
          });
        }
      }
    });
  }
});
