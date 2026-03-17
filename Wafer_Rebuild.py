import logging.handlers
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ctypes import *
from MvCameraControl_class import *
import wmi
import hashlib
import Classes
import logging
import time
from Camera import CameraController
from flask import Flask, render_template, Response
import queue
import threading
import numpy as np
import cv2 as cv
from Web_Display import set_work_thread
from Web_Display import app as web_display_app
import traceback



class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.Label_Display = QtWidgets.QLabel(self.groupBox)
        self.Label_Display.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.Label_Display.setObjectName("Label_Display")
        self.gridLayout.addWidget(self.Label_Display, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "显示画面"))
        self.Label_Display.setText(_translate("Dialog", "TextLabel"))


class LoginDlg(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent = None):       
        super(LoginDlg,self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Wafer")
        self.Label_Display.setScaledContents(True)

        self.logger             = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        stream                  = logging.StreamHandler()
        stream.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        stream.setLevel(logging.WARNING)

        record                  = logging.handlers.TimedRotatingFileHandler("log.txt",when = "d",interval= 7, backupCount=5)
        record.setLevel(logging.INFO)
        record.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(stream)
        self.logger.addHandler(record)
         
        self.Camlow             = MvCamera()
        self.Camlow2            = MvCamera()
        self.Camhigh            = MvCamera()
        self.Camhigh2           = MvCamera()
        self.Camlow2            = CameraController(self.Camlow2, "192.168.1.247","192.168.1.154")
        self.Camhigh2           = CameraController(self.Camhigh2,"192.168.1.248","192.168.1.155")   
        self.Camhigh            = CameraController(self.Camhigh, "192.168.1.249","192.168.1.156")
        self.Camlow             = CameraController(self.Camlow,  "192.168.1.250","192.168.1.157")

        # 网页同步显示相关初始化
        self.web_frame_queue = queue.Queue(maxsize=10)
        self.web_app = Flask("web_display")
        self.web_thread = None
        #######################密码检测#######################
        # 初始化一个标志变量，用于后续判断密码是否输入正确
        ifWrong = True
        # 通过WMI获取处理器ID和硬盘序列号，拼接成一个独特的PassCode
        PassCode = wmi.WMI().Win32_Processor()[0].ProcessorId.strip() + "415263"  + wmi.WMI().Win32_DiskDrive()[0].SerialNumber.strip()
        # 对PassCode进行MD5加密
        md5 = hashlib.md5(PassCode.encode("gb2312"))
        md5 = md5.hexdigest()
        # 尝试从文件中读取密码
        try:
            f = open('password.txt')
            Password = f.read()
            f.close()
        except:
            # 如果文件不存在或读取失败，通过对话框获取注册密码
            Password = QInputDialog.getText(self, "注册","软件id: "+ md5[4:14], text="请输入注册密码")
            # 将获取的密码写入文件
            file = open('password.txt','w')
            file.write(Password[0])
            file.close()
            # 再次读取文件以确保密码被正确设置
            file = open('password.txt','r')
            Password = file.read()
            file.close()
        # 循环检查密码是否正确
        while(ifWrong):
            # 检查读取的密码是否与计算的MD5值匹配
            if Password == hashlib.md5((md5[4:14]+"415263").encode("gb2312")).hexdigest():
                ifWrong = False
                break
            else:
                # 如果密码不正确，提示用户并允许重新输入
                self.logger.warning("密码错误")
                reply = QMessageBox.information(self,"警告","注册密码错误",QMessageBox.Yes | QMessageBox.No)
                Password = QInputDialog.getText(self, "注册","软件id: "+ md5[4:14], text="请输入注册密码")
                print(md5[4:14])
                # 更新文件中的密码
                file = open('password.txt','w')
                file.write(Password[0])
                file.close()
                # 重新读取文件中的密码以供检查
                file = open('password.txt','r')
                Password = file.read()
                file.close()
        self.start_work_thread()
        
    def restart_thread(self):
        """重启工作线程，带最大重试次数限制"""
        self.quit_thread()
        max_retries = 10  # 最大重试次数
        count = 1
        while count <= max_retries:
            try:
                time.sleep(5)
                self.logger.info("尝试重启，重启次数：{}/{}次".format(count, max_retries))
                self.start_work_thread()
                self.logger.info("线程重启成功")
                break
            except Exception as e:
                self.logger.warning("重启失败,尝试次数：{}/{}次，错误：{}".format(count, max_retries, str(e)))
                count += 1
                if count > max_retries:
                    self.logger.error("达到最大重试次数，停止重启尝试")
                    sys.exit()
            
    def start_work_thread(self):
        """启动工作线程"""
        # 确保旧线程已完全停止
        if hasattr(self, 'Work') and self.Work is not None:
            try:
                if self.Work.isRunning():
                    self.logger.warning("工作线程仍在运行，强制停止")
                    self.Work.terminate()
                    self.Work.wait(3000)  # 等待最多3秒
                del self.Work
            except Exception as e:
                self.logger.warning("清理旧线程失败: {}".format(str(e)))
        
        self.Work = Classes.WorkThread(image_show_lable =  self.Label_Display, 
                                       logger = self.logger,
                                       Camlow = self.Camlow,
                                       Camlow2 = self.Camlow2,
                                       Camhigh = self.Camhigh,
                                       Camhigh2 = self.Camhigh2,
                                       web_frame_queue = self.web_frame_queue,
                                       web_display_enabled = True)
        
        self.Work._shut_down_signal.connect(self.restart_thread)
        self.Work.start()
        
        # 启动Web服务器
        self.start_web_server()
            
    def quit_thread(self):
        """安全地停止工作线程"""
        if not hasattr(self, 'Work') or self.Work is None:
            return
        
        try:
            if self.Work.isRunning():
                self.logger.info("正在停止工作线程...")
                self.Work.quit()  # 请求线程退出
                # 等待线程正常退出，最多等待3秒
                if not self.Work.wait(3000):
                    self.logger.warning("线程未在3秒内退出，强制终止")
                    self.Work.terminate()
                    self.Work.wait(1000)  # 再等待1秒确保终止
                self.logger.info("工作线程已停止")
        except Exception as e:
            self.logger.error("停止工作线程时发生错误: {}".format(str(e)))
        
    def start_web_server(self):
        """启动Web服务器"""
        if self.web_thread is None or not self.web_thread.is_alive():
            # 设置WorkThread实例到Web_Display模块
            try:
                set_work_thread(self.Work)
                self.logger.info("WorkThread已设置到Web_Display模块")
                # 使用Web_Display模块的Flask应用
                self.web_app = web_display_app
                self.logger.info("使用Web_Display模块的Flask应用")
            except Exception as e:
                self.logger.warning(f"无法使用Web_Display模块: {e}，使用内置Web服务器")
                self.setup_builtin_web_server()

            # 启动Web服务器线程
            self.web_thread = threading.Thread(target=self.run_web_server, daemon=True)
            self.web_thread.start()
            self.logger.info("Web服务器已启动，访问地址: http://localhost:5000")
    
    def setup_builtin_web_server(self):
        """设置内置Web服务器路由"""
        @self.web_app.route('/')
        def index():
            return render_template('stream.html') if hasattr(self.web_app, 'template_folder') else '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>实时视频流</title>
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
                        image-rendering: pixelated;
                    }
                </style>
            </head>
            <body>
                <img src="/video_feed" id="video-stream">
                <script>
                    setInterval(() => {
                        const img = document.getElementById('video-stream');
                        if (img.naturalWidth === 0) {
                            console.log("重新连接视频流...");
                            img.src = img.src.split('?')[0] + '?t=' + new Date().getTime();
                        }
                    }, 5000);
                </script>
            </body>
            </html>
            '''
        
        @self.web_app.route('/video_feed')
        def video_feed():
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @self.web_app.route('/status')
        def status():
            status_info = {
                'work_thread_connected': hasattr(self, 'Work') and self.Work.isRunning(),
                'web_display_enabled': True,
                'display_mode': getattr(self.Work, 'display_mode', 'unknown') if hasattr(self, 'Work') else 'unknown',
                'queue_size': self.web_frame_queue.qsize()
            }
            return status_info
   
    def generate_frames(self):
        """生成器函数，持续从队列获取帧并推送"""
        while True:
            try:
                # 从WorkThread获取图像数据
                if hasattr(self, 'Work') and self.Work.web_display_enabled:
                    try:
                        frame_data = self.Work.web_frame_queue.get(timeout=0.5)
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                        continue
                    except queue.Empty:
                        pass
                
                # 发送空白图像
                blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
                ret, buffer = cv.imencode('.jpg', blank_img)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception as e:
                self.logger.error(f"生成帧数据错误: {e}")
                time.sleep(0.1)
    
    def run_web_server(self):
        """运行Web服务器"""
        try:
            self.logger.info(f"正在启动Web服务器，Flask应用: {self.web_app}")
            self.logger.info(f"Web应用路由: {[rule.rule for rule in self.web_app.url_map.iter_rules()]}")
            self.web_app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
        except Exception as e:
            print(f"Web服务器启动失败: {e}")
            self.logger.error(f"Web服务器启动失败: {e}")
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
       
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dlg = LoginDlg()
    dlg.showFullScreen()
    width = dlg.width()
    hight = dlg.height()
    dlg.setFixedWidth(width+20)
    dlg.setFixedHeight(hight+20)
    dlg.move(-10,-10)
    sys.exit(app.exec_())




