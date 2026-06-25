import logging.handlers
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ctypes import *
#sys.path.append("../MvImport")
#sys.path.append("../DLL")
from MvCameraControl_class import *
import wmi
import hashlib
import Classes
import logging
import time
from Camera import CameraController



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

        record                  = logging.handlers.TimedRotatingFileHandler("log.txt",when = "d",interval= 2, backupCount=5)
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
        self.quit_thread()
        count = 1
        while(True):
            try:
                time.sleep(5)
                self.logger.info("尝试重启，重启次数：{}次".format(count))
                self.start_work_thread()
                break
            except:
                self.logger.warning("重启失败,尝试次数：{}次".format(count))
                count += 1
            

    def start_work_thread(self):
        try:
            del self.Work
        except:
            self.logger.warning("删除线程失败")
        self.Work = Classes.WorkThread(image_show_lable =  self.Label_Display, 
                                       logger = self.logger,
                                       Camlow = self.Camlow,
                                       Camlow2 = self.Camlow2,
                                       Camhigh = self.Camhigh,
                                       Camhigh2 = self.Camhigh2,)
        self.Work._shut_down_signal.connect(self.restart_thread)
        self.Work.start()
    
    def quit_thread(self):
        self.Work.quit()
        
        
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




