# app.py（后端）
from flask import Flask, render_template, request
import pygame
import time

app = Flask(__name__)

# 初始化手柄
pygame.init()
pygame.joystick.init()

# 检查手柄连接
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"已连接手柄: {joystick.get_name()}")
except:
    joystick = None
    print("未检测到手柄")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vibrate', methods=['POST'])
def vibrate():
    if not joystick:
        return "错误：未检测到手柄", 400
        
    data = request.get_json()
    intensity = float(data['intensity'])
    duration = float(data['duration'])
    
    try:
        joystick.rumble(intensity, intensity, int(duration * 1000))
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
