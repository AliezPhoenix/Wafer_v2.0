from flask import Flask, Response
import cv2 as cv
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import queue
from PyQt5.QtCore import *
import socket
import time
app = Flask(__name__)
# 线程安全的帧队列 - 进一步增大队列以提高帧率
frame_queue = queue.Queue(maxsize=50)
# 全局变量存储WorkThread实例
work_thread_instance = None
def set_work_thread(work_thread):
    """设置WorkThread实例，用于网页同步显示"""
    global work_thread_instance
    work_thread_instance = work_thread

def add_frame_to_queue(frame_data, max_retries=3):
    """添加帧到队列，支持丢帧以提高帧率"""
    try:
        # 如果队列已满，丢弃最旧的帧
        if frame_queue.full():
            try:
                frame_queue.get_nowait()  # 丢弃最旧的帧
            except queue.Empty:
                pass
        
        # 添加新帧
        frame_queue.put(frame_data, block=False)
        return True
    except queue.Full:
        # 如果还是满的，强制丢弃一帧
        try:
            frame_queue.get_nowait()
            frame_queue.put(frame_data, block=False)
            return True
        except:
            return False
    except Exception as e:
        print(f"添加帧到队列失败: {e}")
        return False

def add_encoded_frame_to_queue(image_array):
    """添加编码后的帧到队列，提高效率"""
    try:
        # 高质量编码
        encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 95]
        ret, buffer = cv.imencode('.jpg', image_array, encode_param)
        if ret:
            return add_frame_to_queue(buffer.tobytes())
        return False
    except Exception as e:
        print(f"编码帧失败: {e}")
        return False

@app.route('/')
def index():
    """视频流主页"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>实时视频流</title>
        <meta charset="utf-8">
        <style>
            body { 
                margin: 0; 
                padding: 0; 
                background-color: black; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                overflow: hidden;
            }
            img { 
                max-width: 100vw; 
                max-height: 100vh; 
                object-fit: contain;
            }
        </style>
    </head>
    <body>
        <img src="/video_feed" id="video-stream">
        <script>
            setInterval(() => {
                const img = document.getElementById('video-stream');
                if (img.naturalWidth === 0) {
                    img.src = img.src.split('?')[0] + '?t=' + new Date().getTime();
                }
            }, 5000);
        </script>
    </body>
    </html>
    """
    return html_content

@app.route('/video_feed')
def video_feed():
    """视频流路由，生成MJPEG流"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_frames():
    """生成器函数，持续从队列获取帧并推送"""
    # JPEG编码参数 - 保持高质量
    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 95]  # 保持高质量
    
    while True:
        try:
            # 优先从WorkThread获取图像数据
            if work_thread_instance and work_thread_instance.web_display_enabled:
                try:
                    # 进一步减少超时时间以提高响应速度
                    frame_data = work_thread_instance.web_frame_queue.get(timeout=0.05)
                    if frame_data is not None:
                        # 如果frame_data已经是编码后的字节数据，直接使用
                        if isinstance(frame_data, bytes):
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                        else:
                            # 如果frame_data是图像数组，需要编码
                            ret, buffer = cv.imencode('.jpg', frame_data, encode_param)
                            if ret:
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    continue
                except queue.Empty:
                    # 队列为空时不打印，减少日志输出
                    pass
            
            # 如果WorkThread不可用，使用原有的Animation队列
            try:
                frame_data = frame_queue.get(timeout=0.05)  # 进一步减少超时时间
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            except queue.Empty:
                # 如果所有队列都为空，发送空白图像但降低频率
                blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
                cv.putText(blank_img, "No Data", (150, 300), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                ret, buffer = cv.imencode('.jpg', blank_img, encode_param)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    # 当没有数据时，减少延迟以提高响应性
                    time.sleep(0.01)  # 10ms延迟
                    
        except Exception as e:
            print(f"视频流生成错误: {e}")
            # 发送错误图像
            error_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv.putText(error_img, "Error", (200, 300), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv.imencode('.jpg', error_img, encode_param)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
# if __name__ == '__main__':
#     # 启动Flask应用（启用多线程模式）
#     work = Animation()
#     work.start()
#     app.run(host='0.0.0.0', port=5000, threaded=True)