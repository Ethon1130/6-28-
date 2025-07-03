// pages/classroomMonitor/classroomMonitor.js
Page({
  /**
   * 页面的初始数据
   */
  data: {
    isConnected: false,
    isPlaying: false,
    currentFrame: '',
    pauseFrame: '',
    mockFrames: [
      '/images/monitor/frame1.jpg',
      '/images/monitor/frame2.jpg',
      '/images/monitor/frame3.jpg',
      '/images/monitor/frame4.jpg',
      '/images/monitor/frame5.jpg'
    ],
    mockInterval: null,
    frameIndex: 0,
    fps: 0,
    user: {},
    ws: null,
    connectionStatus: '未连接', // 连接状态
    errorMessage: '', // 错误信息
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    console.log('监控页面加载');
    // 设置默认图片
    this.setData({
      currentFrame: this.data.mockFrames[0]
    });
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    console.log('监控页面显示');
  },

  /**
   * 开始/停止监控
   */
  toggleConnection: function () {
    if (this.data.isConnected) {
      // 断开WebSocket
      if (this.data.ws) {
        this.data.ws.close();
      }
      this.setData({
        isConnected: false,
        isPlaying: false,
        currentFrame: '',
        ws: null,
        connectionStatus: '已断开',
        errorMessage: ''
      });
      wx.showToast({ title: '监控已停止', icon: 'success' });
    } else {
      // 建立WebSocket连接
      this.setData({
        connectionStatus: '连接中...',
        errorMessage: ''
      });

      const ws = wx.connectSocket({
        url: 'ws://127.0.0.1:8000/ws/ascend/',
      });

      ws.onOpen(() => {
        console.log('WebSocket connected');
        this.setData({
          isConnected: true,
          isPlaying: true,
          connectionStatus: '已连接'
        });
        wx.showToast({ title: '监控已启动', icon: 'success' });

        // 连接成功后，发送开始流请求
        ws.send({
          data: JSON.stringify({
            type: 'start_stream'
          })
        });
      });

      ws.onMessage((msg) => {
        try {
          const data = JSON.parse(msg.data);
          console.log('收到WebSocket消息:', data.type);

          if (data.type === 'frame') {
            // 接收到图片帧数据
            this.setData({
              currentFrame: data.image_data,
              frameIndex: data.frame_index,
              fps: data.fps || 0
            });
          } else if (data.type === 'stream_started') {
            console.log('Stream started:', data.message);
            this.setData({
              connectionStatus: '流传输中',
              errorMessage: ''
            });
          } else if (data.type === 'stream_stopped') {
            console.log('Stream stopped:', data.message);
            this.setData({
              connectionStatus: '流已停止',
              isPlaying: false
            });
          } else if (data.type === 'single_frame') {
            // 接收到单帧图片
            this.setData({
              currentFrame: data.image_data,
              timestamp: data.timestamp
            });
          } else if (data.type === 'error') {
            // 处理错误消息
            console.error('后端错误:', data.message);
            this.setData({
              errorMessage: data.message,
              connectionStatus: '连接错误'
            });
            wx.showToast({
              title: data.message,
              icon: 'none',
              duration: 3000
            });
          } else if (data.type === 'config_success') {
            // 配置成功
            wx.showToast({
              title: data.message,
              icon: 'success'
            });
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
          this.setData({
            errorMessage: '消息解析失败',
            connectionStatus: '数据错误'
          });
        }
      });

      ws.onClose(() => {
        console.log('WebSocket closed');
        this.setData({
          isConnected: false,
          isPlaying: false,
          ws: null,
          connectionStatus: '连接已关闭',
          errorMessage: ''
        });
      });

      ws.onError((error) => {
        console.error('WebSocket error:', error);
        this.setData({
          isConnected: false,
          isPlaying: false,
          ws: null,
          connectionStatus: '连接失败',
          errorMessage: '网络连接错误'
        });
        wx.showToast({ title: '连接失败', icon: 'none' });
      });

      this.setData({ ws });
    }
  },

  /**
   * 播放/暂停控制
   */
  togglePlayback: function () {
    if (!this.data.isConnected) {
      wx.showToast({ title: '请先连接升腾设备', icon: 'none' });
      return;
    }

    if (this.data.isPlaying) {
      // 暂停流
      if (this.data.ws) {
        this.data.ws.send({
          data: JSON.stringify({
            type: 'stop_stream'
          })
        });
      }
      this.setData({ isPlaying: false });
      wx.showToast({ title: '已暂停', icon: 'success' });
    } else {
      // 恢复流
      if (this.data.ws) {
        this.data.ws.send({
          data: JSON.stringify({
            type: 'start_stream'
          })
        });
      }
      this.setData({ isPlaying: true });
      wx.showToast({ title: '已恢复', icon: 'success' });
    }
  },

  /**
   * 请求单帧图片
   */
  requestSingleFrame: function () {
    if (!this.data.isConnected) {
      wx.showToast({ title: '请先连接升腾设备', icon: 'none' });
      return;
    }

    if (this.data.ws) {
      this.data.ws.send({
        data: JSON.stringify({
          type: 'request_frame'
        })
      });
      wx.showToast({ title: '正在获取图片...', icon: 'loading' });
    }
  },

  /**
   * 配置升腾设备
   */
  configureAscendDevice: function () {
    if (!this.data.isConnected) {
      wx.showToast({ title: '请先连接升腾设备', icon: 'none' });
      return;
    }

    // 显示配置对话框
    wx.showModal({
      title: '配置升腾设备',
      content: '是否要配置升腾设备参数？',
      success: (res) => {
        if (res.confirm) {
          // 发送配置请求
          if (this.data.ws) {
            this.data.ws.send({
              data: JSON.stringify({
                type: 'configure_ascend',
                config: {
                  resolution: '1920x1080',
                  fps: 10,
                  quality: 'high'
                }
              })
            });
          }
        }
      }
    });
  },

  /**
   * 查看历史记录
   */
  viewHistory: function () {
    wx.showToast({
      title: '历史记录功能暂未开放',
      icon: 'none',
      duration: 2000
    });
  },

  /**
   * 启动模拟监控
   */
  startMockMonitor: function () {
    const that = this;
    const mockInterval = setInterval(() => {
      let index = this.data.frameIndex;
      index = (index + 1) % this.data.mockFrames.length;

      that.setData({
        frameIndex: index,
        currentFrame: that.data.mockFrames[index]
      });
    }, 1000); // 每秒切换一次图片

    this.setData({
      mockInterval: mockInterval
    });
  },

  /**
   * 停止模拟监控
   */
  stopMockMonitor: function () {
    if (this.data.mockInterval) {
      clearInterval(this.data.mockInterval);
      this.setData({
        mockInterval: null
      });
    }
  },

  /**
   * 获取用户信息
   */
  handleLoadUser: function () {
    wx.request({
      url: 'http://localhost:8000/index/',
      method: 'GET',
      data: {},
      header: {},
      success: (res) => {
        console.log('用户数据:', res.data);
        this.setData({
          user: res.data
        });
      },
      fail: (error) => {
        console.error('获取用户信息失败:', error);
        wx.showToast({
          title: '获取用户信息失败',
          icon: 'none',
          duration: 2000
        });
      }
    });
  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {
    // 页面卸载时清除定时器
    this.stopMockMonitor();
    console.log('监控页面卸载');
    if (this.data.ws) this.data.ws.close();
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {
    console.log('下拉刷新');
    wx.stopPullDownRefresh();
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {
    console.log('上拉触底');
  }
}); 
