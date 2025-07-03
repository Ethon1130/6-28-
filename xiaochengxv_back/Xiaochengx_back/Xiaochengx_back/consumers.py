# your_app_name/consumers.py
import json
import asyncio
import base64
import aiohttp
import time
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from django.conf import settings


class ImageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """WebSocket 连接建立时的处理"""
        self.room_group_name = "ascend_monitor"
        self.is_streaming = False
        self.ascend_client = None  # 升腾设备客户端
        self.frame_count = 0
        self.last_frame_time = 0
        self.use_mock_data = True  # 默认使用模拟数据
        self.ascend_config = {
            'device_ip': '192.168.1.100',  # 升腾设备IP
            'device_port': 8080,  # 升腾设备端口
            'timeout': 10,  # 连接超时时间
            'fps': 10  # 默认帧率
        }
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        print(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        """WebSocket 断开连接时的处理"""
        self.is_streaming = False
        
        # 关闭升腾设备连接
        if self.ascend_client:
            await self.close_ascend_connection()
        
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        print(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """接收前端消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')
            
            if message_type == 'start_stream':
                # 开始推送图片流
                await self.start_image_stream()
            elif message_type == 'stop_stream':
                # 停止推送图片流
                await self.stop_image_stream()
            elif message_type == 'request_frame':
                # 请求单帧图片
                await self.send_single_frame()
            elif message_type == 'configure_ascend':
                # 配置升腾设备参数
                await self.configure_ascend_device(data.get('config', {}))
                
        except json.JSONDecodeError:
            print("Invalid JSON received")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '无效的JSON格式'
            }))
        except Exception as e:
            print(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'消息处理失败: {str(e)}'
            }))

    async def start_image_stream(self):
        """开始实时图片流推送"""
        try:
            # 尝试初始化升腾设备连接
            if not self.use_mock_data:
                if not await self.init_ascend_connection():
                    # 如果升腾设备连接失败，切换到模拟数据模式
                    self.use_mock_data = True
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': '升腾设备连接失败，已切换到模拟数据模式'
                    }))
            
            self.is_streaming = True
            await self.send(text_data=json.dumps({
                'type': 'stream_started',
                'message': f'开始推送图片流 ({("模拟数据" if self.use_mock_data else "升腾设备")})'
            }))
            
            # 启动图片推送循环
            asyncio.create_task(self.image_stream_loop())
            
        except Exception as e:
            print(f"Error starting image stream: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'启动流失败: {str(e)}'
            }))

    async def stop_image_stream(self):
        """停止实时图片流推送"""
        self.is_streaming = False
        
        # 关闭升腾设备连接
        if self.ascend_client:
            await self.close_ascend_connection()
        
        await self.send(text_data=json.dumps({
            'type': 'stream_stopped',
            'message': '停止推送图片流'
        }))

    async def image_stream_loop(self):
        """图片流推送循环"""
        while self.is_streaming:
            try:
                # 获取图片数据
                image_data = await self.get_frame()
                
                if image_data:
                    current_time = time.time()
                    fps = 1.0 / (current_time - self.last_frame_time) if self.last_frame_time > 0 else 0
                    self.last_frame_time = current_time
                    
                    await self.send(text_data=json.dumps({
                        'type': 'frame',
                        'image_data': image_data,
                        'frame_index': self.frame_count,
                        'timestamp': current_time,
                        'fps': round(fps, 1)
                    }))
                    
                    self.frame_count += 1
                
                # 控制推送频率
                sleep_time = 1.0 / self.ascend_config['fps']
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                print(f"Error in image stream loop: {e}")
                await asyncio.sleep(1)

    async def send_single_frame(self):
        """发送单帧图片"""
        try:
            image_data = await self.get_frame()
            if image_data:
                await self.send(text_data=json.dumps({
                    'type': 'single_frame',
                    'image_data': image_data,
                    'timestamp': time.time()
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': '无法获取图片数据'
                }))
        except Exception as e:
            print(f"Error sending single frame: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'获取单帧失败: {str(e)}'
            }))

    async def get_frame(self):
        """获取图片帧（升腾设备或模拟数据）"""
        if self.use_mock_data:
            return await self.get_mock_frame()
        else:
            return await self.get_ascend_frame()

    async def get_mock_frame(self):
        """获取模拟图片帧"""
        try:
            # 方案1: 尝试从本地图片文件读取
            mock_images = [
                'frame1.jpg', 'frame2.jpg', 'frame3.jpg', 
                'frame4.jpg', 'frame5.jpg', 'frame1.png', 
                'frame2.png', 'frame3.png'
            ]
            
            # 检查多个可能的路径
            possible_paths = [
                os.path.join(settings.MEDIA_ROOT, 'images', 'monitor'),
                os.path.join(settings.MEDIA_ROOT, 'images'),
                os.path.join(settings.BASE_DIR, 'static', 'images'),
                os.path.join(settings.BASE_DIR, 'media', 'images')
            ]
            
            frame_index = self.frame_count % len(mock_images)
            image_name = mock_images[frame_index]
            
            for base_path in possible_paths:
                image_path = os.path.join(base_path, image_name)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        image_bytes = f.read()
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        return f"data:image/jpeg;base64,{image_base64}"
            
            # 方案2: 生成纯色图片
            return await self.generate_color_frame(frame_index)
            
        except Exception as e:
            print(f"Error getting mock frame: {e}")
            return await self.generate_color_frame(self.frame_count)

    async def generate_color_frame(self, frame_index):
        """生成纯色图片帧"""
        try:
            # 根据帧索引生成不同颜色的图片
            colors = [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
            ]
            color = colors[frame_index % len(colors)]
            
            # 创建一个简单的SVG图片
            svg_content = f'''
            <svg width="640" height="480" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="{color}"/>
                <text x="50%" y="50%" font-family="Arial" font-size="48" 
                      fill="white" text-anchor="middle" dominant-baseline="middle">
                    模拟帧 {frame_index + 1}
                </text>
                <text x="50%" y="70%" font-family="Arial" font-size="24" 
                      fill="white" text-anchor="middle" dominant-baseline="middle">
                    升腾设备模拟数据
                </text>
            </svg>
            '''
            
            # 将SVG转换为base64
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            return f"data:image/svg+xml;base64,{svg_base64}"
            
        except Exception as e:
            print(f"Error generating color frame: {e}")
            # 返回一个最小的base64图片
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    async def init_ascend_connection(self):
        """初始化升腾设备连接"""
        try:
            # 创建HTTP客户端会话
            self.ascend_client = aiohttp.ClientSession()
            
            # 构建测试URL
            test_url = f"http://{self.ascend_config['device_ip']}:{self.ascend_config['device_port']}/status"
            
            # 测试连接
            async with self.ascend_client.get(test_url, timeout=self.ascend_config['timeout']) as response:
                if response.status == 200:
                    print("升腾设备连接成功")
                    return True
                else:
                    print(f"升腾设备连接失败，状态码: {response.status}")
                    return False
                    
        except asyncio.TimeoutError:
            print("升腾设备连接超时")
            return False
        except Exception as e:
            print(f"初始化升腾设备连接失败: {e}")
            return False

    async def close_ascend_connection(self):
        """关闭升腾设备连接"""
        try:
            if self.ascend_client:
                await self.ascend_client.close()
                self.ascend_client = None
                print("升腾设备连接已关闭")
        except Exception as e:
            print(f"关闭升腾设备连接失败: {e}")

    async def get_ascend_frame(self):
        """从升腾设备获取图片帧"""
        try:
            if not self.ascend_client:
                print("升腾设备未连接")
                return None
            
            # 构建图片获取URL
            image_url = f"http://{self.ascend_config['device_ip']}:{self.ascend_config['device_port']}/capture"
            
            async with self.ascend_client.get(image_url, timeout=self.ascend_config['timeout']) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    # 根据图片格式返回正确的MIME类型
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    return f"data:{content_type};base64,{image_base64}"
                else:
                    print(f"获取升腾设备图片失败，状态码: {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            print("获取升腾设备图片超时")
            return None
        except Exception as e:
            print(f"获取升腾设备图片失败: {e}")
            return None

    async def configure_ascend_device(self, config):
        """配置升腾设备参数"""
        try:
            # 更新配置
            if 'device_ip' in config:
                self.ascend_config['device_ip'] = config['device_ip']
            if 'device_port' in config:
                self.ascend_config['device_port'] = config['device_port']
            if 'fps' in config:
                self.ascend_config['fps'] = config['fps']
            if 'timeout' in config:
                self.ascend_config['timeout'] = config['timeout']
            
            # 如果指定了使用真实设备，尝试连接
            if config.get('use_real_device', False):
                self.use_mock_data = False
                if await self.init_ascend_connection():
                    await self.send(text_data=json.dumps({
                        'type': 'config_success',
                        'message': '升腾设备配置成功并连接'
                    }))
                else:
                    self.use_mock_data = True
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': '升腾设备连接失败，已切换到模拟数据模式'
                    }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'config_success',
                    'message': '升腾设备配置已更新'
                }))
                    
        except Exception as e:
            print(f"配置升腾设备失败: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'配置失败: {str(e)}'
            }))

    async def send_image_to_group(self, image_data, frame_index):
        """向房间组发送图片"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_image',
                'image_data': image_data,
                'frame_index': frame_index
            }
        )

    async def broadcast_image(self, event):
        """广播图片到所有连接的客户端"""
        await self.send(text_data=json.dumps({
            'type': 'frame',
            'image_data': event['image_data'],
            'frame_index': event['frame_index']
        }))
