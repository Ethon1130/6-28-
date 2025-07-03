#!/usr/bin/env python3
"""
WebSocket 连接测试脚本
用于测试升腾设备监控的WebSocket功能
"""

import asyncio
import websockets
import json
import time

async def test_websocket():
    """测试WebSocket连接和消息处理"""
    uri = "ws://localhost:8000/ws/ascend/"
    
    try:
        print("正在连接WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("WebSocket连接成功!")
            
            # 测试1: 发送开始流请求
            print("\n测试1: 发送开始流请求")
            start_message = {
                "type": "start_stream"
            }
            await websocket.send(json.dumps(start_message))
            print(f"发送消息: {start_message}")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到响应: {data}")
            
            # 测试2: 接收几帧图片数据
            print("\n测试2: 接收图片帧数据")
            frame_count = 0
            start_time = time.time()
            
            while frame_count < 5:  # 接收5帧
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'frame':
                        frame_count += 1
                        print(f"收到第{frame_count}帧: 帧索引={data.get('frame_index')}, FPS={data.get('fps')}")
                        
                        # 检查图片数据
                        image_data = data.get('image_data', '')
                        if image_data.startswith('data:image'):
                            print(f"  图片数据: {len(image_data)} 字符")
                        else:
                            print(f"  图片数据格式错误: {image_data[:50]}...")
                    
                    elif data.get('type') == 'error':
                        print(f"收到错误: {data.get('message')}")
                        break
                        
                except asyncio.TimeoutError:
                    print("接收超时")
                    break
            
            elapsed_time = time.time() - start_time
            print(f"接收完成，耗时: {elapsed_time:.2f}秒")
            
            # 测试3: 发送停止流请求
            print("\n测试3: 发送停止流请求")
            stop_message = {
                "type": "stop_stream"
            }
            await websocket.send(json.dumps(stop_message))
            print(f"发送消息: {stop_message}")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到响应: {data}")
            
            # 测试4: 请求单帧图片
            print("\n测试4: 请求单帧图片")
            single_frame_message = {
                "type": "request_frame"
            }
            await websocket.send(json.dumps(single_frame_message))
            print(f"发送消息: {single_frame_message}")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到响应: {data}")
            
            # 测试5: 配置升腾设备
            print("\n测试5: 配置升腾设备")
            config_message = {
                "type": "configure_ascend",
                "config": {
                    "device_ip": "192.168.1.100",
                    "device_port": 8080,
                    "fps": 15,
                    "timeout": 5
                }
            }
            await websocket.send(json.dumps(config_message))
            print(f"发送消息: {config_message}")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"收到响应: {data}")
            
            print("\n所有测试完成!")
            
    except websockets.exceptions.ConnectionRefused:
        print("错误: 无法连接到WebSocket服务器")
        print("请确保Django服务器正在运行: python manage.py runserver")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    print("WebSocket 连接测试")
    print("=" * 50)
    asyncio.run(test_websocket()) 