Page({
  data: {
    phone: '',
    code: '',
    password: '',
    nickname: '',
    phoneFocus: false,
    codeFocus: false,
    passwordFocus: false,
    nicknameFocus: false,
    countdownText: '获取验证码',
    countdown: 0
  },

  inputPhone: function (e) {
    this.setData({
      phone: e.detail.value
    });
  },

  inputCode: function (e) {
    this.setData({
      code: e.detail.value
    });
  },

  inputPassword: function (e) {
    this.setData({
      password: e.detail.value
    });
  },

  inputNickname: function (e) {
    this.setData({
      nickname: e.detail.value
    });
  },

  clearPhone: function () {
    this.setData({
      phone: '',
      phoneFocus: true
    });
  },

  clearCode: function () {
    this.setData({
      code: '',
      codeFocus: true
    });
  },

  clearPassword: function () {
    this.setData({
      password: '',
      passwordFocus: true
    });
  },

  clearNickname: function () {
    this.setData({
      nickname: '',
      nicknameFocus: true
    });
  },

  onPhoneFocus: function () {
    this.setData({ phoneFocus: true });
  },

  onCodeFocus: function () {
    this.setData({ codeFocus: true });
  },

  onPasswordFocus: function () {
    this.setData({ passwordFocus: true });
  },

  onNicknameFocus: function () {
    this.setData({ nicknameFocus: true });
  },

  onPhoneBlur: function () {
    this.setData({ phoneFocus: false });
  },

  onCodeBlur: function () {
    this.setData({ codeFocus: false });
  },

  onPasswordBlur: function () {
    this.setData({ passwordFocus: false });
  },

  onNicknameBlur: function () {
    this.setData({ nicknameFocus: false });
  },

  sendVerificationCode: function () {
    const { phone, countdown } = this.data;

    // 验证手机号
    if (!phone || phone.length !== 11) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      });
      return;
    }

    // 防止重复发送
    if (countdown > 0) return;

    wx.showLoading({
      title: '发送中...',
      mask: true
    });

    wx.request({
      url: 'http://localhost:8000/send_code/',
      method: 'POST',
      data: { phone: phone },
      success: (res) => {
        wx.hideLoading();
        if (res.data.status === 'success') {
          wx.showToast({
            title: '验证码已发送',
            icon: 'success'
          });

          // 开始倒计时
          this.startCountdown();
        } else {
          wx.showToast({
            title: res.data.message || '发送失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      }
    });
  },

  startCountdown: function () {
    let countdown = 60;
    const timer = setInterval(() => {
      countdown--;
      this.setData({
        countdown: countdown,
        countdownText: countdown > 0 ? `${countdown}s` : '获取验证码'
      });

      if (countdown <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  },

  register: function () {
    const { phone, code, password, nickname } = this.data;

    // 表单验证
    if (!phone || phone.length !== 11) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      });
      return;
    }

    if (!code || code.length !== 6) {
      wx.showToast({
        title: '请输入6位验证码',
        icon: 'none'
      });
      return;
    }

    if (!password) {
      wx.showToast({
        title: '请设置密码',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '注册中...',
      mask: true
    });

    wx.request({
      url: 'http://localhost:8000/register/',
      method: 'POST',
      data: {
        phone: phone,
        code: code,
        password: password,
        nickname: nickname
      },
      success: (res) => {
        wx.hideLoading();
        if (res.data.status === 'success') {
          wx.showToast({
            title: '注册成功',
            icon: 'success',
            duration: 2000,
            success: () => {
              // 跳转到登录页面
              wx.redirectTo({
                url: '/pages/login/login'
              });
            }
          });
        } else {
          wx.showToast({
            title: res.data.message || '注册失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      }
    });
  },

  onLoad: function () {
    // 检查是否已登录
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo && userInfo.isLoggedIn) {
      wx.switchTab({
        url: '/pages/my/my'
      });
    }
  }
}); 