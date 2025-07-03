# your_app_name/consumers.py
import json
import asyncio
import base64
import aiohttp
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class ImageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """WebSocket 连接建立时的处理"""
        self.room_group_name = "ascend_monitor"
        self.is_streaming = False
        self.ascend_client = None
        self.frame_count = 0
        self.last_frame_time = 0
        
        # 昇腾设备配置
        self.ascend_config = {
            'device_ip': '192.168.1.100',
            'device_port': 8080,
            'timeout': 10,
            'fps': 10
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
        
        # 关闭昇腾设备连接
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
                
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except Exception as e:
            print(f"Error processing message: {e}")

    async def start_image_stream(self):
        """开始实时图片流推送"""
        try:
            # 初始化昇腾设备连接
            if not await self.init_ascend_connection():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': '昇腾设备连接失败'
                }))
                return
            
            self.is_streaming = True
            await self.send(text_data=json.dumps({
                'type': 'stream_started',
                'message': '开始推送图片流'
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
        
        # 关闭昇腾设备连接
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
                # 从昇腾设备获取图片数据
                image_data = await self.get_ascend_frame()
                
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

    async def init_ascend_connection(self):
        """初始化昇腾设备连接"""
        try:
            # 创建HTTP客户端会话
            self.ascend_client = aiohttp.ClientSession()
            
            # 构建测试URL
            test_url = f"http://{self.ascend_config['device_ip']}:{self.ascend_config['device_port']}/status"
            
            # 测试连接
            async with self.ascend_client.get(test_url, timeout=self.ascend_config['timeout']) as response:
                if response.status == 200:
                    print("昇腾设备连接成功")
                    return True
                else:
                    print(f"昇腾设备连接失败，状态码: {response.status}")
                    return False
                    
        except asyncio.TimeoutError:
            print("昇腾设备连接超时")
            return False
        except Exception as e:
            print(f"初始化昇腾设备连接失败: {e}")
            return False

    async def close_ascend_connection(self):
        """关闭昇腾设备连接"""
        try:
            if self.ascend_client:
                await self.ascend_client.close()
                self.ascend_client = None
                print("昇腾设备连接已关闭")
        except Exception as e:
            print(f"关闭昇腾设备连接失败: {e}")

    async def get_ascend_frame(self):
        """从昇腾设备获取图片帧"""
        try:
            if not self.ascend_client:
                print("昇腾设备未连接")
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
                    print(f"获取昇腾设备图片失败，状态码: {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            print("获取昇腾设备图片超时")
            return None
        except Exception as e:
            print(f"获取昇腾设备图片失败: {e}")
            return None
