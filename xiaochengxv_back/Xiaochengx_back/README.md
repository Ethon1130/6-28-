# 升腾设备监控系统

这是一个基于Django Channels和微信小程序的实时监控系统，支持升腾设备图片流传输。

## 功能特性

- 🔄 实时图片流传输
- 📱 微信小程序前端界面
- 🔧 升腾设备配置管理
- 📊 实时FPS和状态监控
- 🎨 美观的用户界面
- 🔄 自动降级到模拟数据模式

## 系统架构

```
微信小程序 (前端)
    ↓ WebSocket
Django Channels (后端)
    ↓ HTTP API
升腾设备 (数据源)
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 数据库配置

确保MySQL数据库已启动，并在`settings.py`中配置正确的数据库连接信息。

### 3. 运行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 启动服务器

```bash
python manage.py runserver
```

## 使用方法

### 后端API

#### WebSocket连接
- URL: `ws://localhost:8000/ws/ascend/`
- 协议: WebSocket

#### 支持的消息类型

1. **开始流传输**
```json
{
    "type": "start_stream"
}
```

2. **停止流传输**
```json
{
    "type": "stop_stream"
}
```

3. **请求单帧图片**
```json
{
    "type": "request_frame"
}
```

4. **配置升腾设备**
```json
{
    "type": "configure_ascend",
    "config": {
        "device_ip": "192.168.1.100",
        "device_port": 8080,
        "fps": 10,
        "timeout": 10,
        "use_real_device": false
    }
}
```

#### 响应消息类型

1. **图片帧数据**
```json
{
    "type": "frame",
    "image_data": "data:image/jpeg;base64,...",
    "frame_index": 123,
    "timestamp": 1640995200.123,
    "fps": 10.5
}
```

2. **流状态**
```json
{
    "type": "stream_started",
    "message": "开始推送图片流 (模拟数据)"
}
```

3. **错误信息**
```json
{
    "type": "error",
    "message": "错误描述"
}
```

### 前端使用

1. 在微信开发者工具中打开小程序项目
2. 确保后端服务器正在运行
3. 在监控页面点击"连接"按钮
4. 系统会自动开始传输图片流

## 配置说明

### 升腾设备配置

在`consumers.py`中可以修改升腾设备的默认配置：

```python
self.ascend_config = {
    'device_ip': '192.168.1.100',  # 升腾设备IP
    'device_port': 8080,           # 升腾设备端口
    'timeout': 10,                 # 连接超时时间
    'fps': 10                      # 默认帧率
}
```

### 模拟数据模式

当升腾设备不可用时，系统会自动切换到模拟数据模式，生成彩色SVG图片作为测试数据。

## 测试

### WebSocket连接测试

运行测试脚本验证WebSocket功能：

```bash
python test_websocket.py
```

测试内容包括：
- WebSocket连接建立
- 开始/停止流传输
- 图片帧数据接收
- 设备配置
- 错误处理

## 故障排除

### 常见问题

1. **WebSocket连接失败**
   - 检查Django服务器是否正在运行
   - 确认端口8000未被占用
   - 检查防火墙设置

2. **升腾设备连接失败**
   - 确认设备IP和端口正确
   - 检查网络连接
   - 系统会自动切换到模拟数据模式

3. **图片显示异常**
   - 检查图片数据格式
   - 确认base64编码正确
   - 查看浏览器控制台错误信息

### 日志查看

Django服务器会输出详细的连接和错误日志，可以通过以下方式查看：

```bash
python manage.py runserver --verbosity=2
```

## 开发说明

### 添加新的消息类型

1. 在`consumers.py`的`receive`方法中添加新的消息处理逻辑
2. 在前端JavaScript中添加相应的消息发送代码
3. 更新前端UI以支持新功能

### 自定义图片源

可以通过修改`get_ascend_frame`方法来实现自定义的图片获取逻辑：

```python
async def get_ascend_frame(self):
    # 实现自定义图片获取逻辑
    # 返回base64编码的图片数据
    pass
```

## 许可证

本项目采用MIT许可证。 