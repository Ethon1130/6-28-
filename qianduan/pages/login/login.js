Page({
  data: {
    username: '',
    password: '',
    usernameFocus: false,
    passwordFocus: false
  },

  inputUsername: function (e) {
    this.setData({
      username: e.detail.value
    });
  },

  inputPassword: function (e) {
    this.setData({
      password: e.detail.value
    });
  },

  clearUsername: function () {
    this.setData({
      username: '',
      usernameFocus: true
    });
  },

  clearPassword: function () {
    this.setData({
      password: '',
      passwordFocus: true
    });
  },

  onUsernameConfirm: function () {
    this.setData({
      passwordFocus: true
    });
  },

  onPasswordFocus: function () {
    this.setData({
      passwordFocus: true
    });
  },

  onUsernameFocus: function () {
    this.setData({
      usernameFocus: true
    });
  },

  onUsernameBlur: function () {
    this.setData({
      usernameFocus: false
    });
  },

  onPasswordBlur: function () {
    this.setData({
      passwordFocus: false
    });
  },

  login: function () {
    const { username, password } = this.data;

    if (!username) {
      wx.showToast({
        title: '请输入用户名',
        icon: 'none'
      });
      return;
    }

    if (!password) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '登录中...',
      mask: true
    });

    // 真实的网络请求
    wx.request({
      url: 'http://localhost:8000/login/', // 后端登录接口
      method: 'POST',
      data: {
        username: username,
        password: password
      },
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        wx.hideLoading();

        if (res.data.status === 'success') {
          wx.setStorageSync('userInfo', {
            nickName: res.data.user.username,
            avatarUrl: '/images/avatar1.png',
            isLoggedIn: true
          });
          wx.switchTab({
            url: '/pages/my/my'
          });
        } else {
          wx.showToast({
            title: res.data.message || '登录失败',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none',
          duration: 2000
        });
      }
    });
  },

  onLoad: function () {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo && userInfo.isLoggedIn) {
      wx.switchTab({
        url: '/pages/my/my'
      });
    }
  }
});
