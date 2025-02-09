# backend.py
import pygame
import asyncio
import json
from aiohttp import web
import time

class GamepadController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        # 检查是否有可用的手柄
        if pygame.joystick.get_count() == 0:
            raise Exception("未检测到手柄")
            
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        
        # 打印手柄信息，用于调试
        print(f"检测到手柄: {self.joystick.get_name()}")
        print(f"轴数量: {self.joystick.get_numaxes()}")
        print(f"按钮数量: {self.joystick.get_numbuttons()}")
        
        self.left_intensity = 0
        self.right_intensity = 0

    def set_vibration(self, left, right):
        """设置振动强度"""
        try:
            # 尝试使用不同的振动方法
            # 方法1: 直接使用 rumble
            success = self.joystick.rumble(left, right, 0)
            if not success:
                # 方法2: 使用 set_vibration
                if hasattr(self.joystick, 'set_vibration'):
                    self.joystick.set_vibration(0, left, right)
                # 方法3: 使用 set_rumble
                elif hasattr(self.joystick, 'set_rumble'):
                    self.joystick.set_rumble(0, int(left * 65535))
                    self.joystick.set_rumble(1, int(right * 65535))
            
            self.left_intensity = left
            self.right_intensity = right
            
            # 打印调试信息
            print(f"设置振动: 左={left:.2f}, 右={right:.2f}")
            
        except Exception as e:
            print(f"设置振动时出错: {str(e)}")

    def stop_vibration(self):
        """停止振动"""
        try:
            self.joystick.stop_rumble()
        except:
            try:
                self.set_vibration(0, 0)
            except Exception as e:
                print(f"停止振动时出错: {str(e)}")
                
        self.left_intensity = 0
        self.right_intensity = 0

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    controller = request.app['controller']
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if 'left' in data and 'right' in data:
                    left = float(data['left'])
                    right = float(data['right'])
                    controller.set_vibration(left, right)
                elif data.get('action') == 'stop':
                    controller.stop_vibration()
    except Exception as e:
        print(f"WebSocket处理错误: {str(e)}")
    finally:
        controller.stop_vibration()
    
    return ws

async def index(request):
    with open('index.html', 'r', encoding='utf-8') as f:
        return web.Response(text=f.read(), content_type='text/html')

def main():
    try:
        app = web.Application()
        app['controller'] = GamepadController()
        
        app.router.add_get('/', index)
        app.router.add_get('/ws', websocket_handler)
        
        print("服务器启动在 http://localhost:8080")
        web.run_app(app, host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"程序启动错误: {str(e)}")

if __name__ == '__main__':
    main()
