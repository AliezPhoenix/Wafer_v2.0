from flask import Flask, render_template, Response
import cv2 as cv
import time
import csv
from MvCameraControl_class import *
import sys
sys.path.append("../MvImport")
sys.path.append("../DLL")
import numpy as np
def CameraSet(netIp, deviceIp):
    stDevInfo = MV_CC_DEVICE_INFO()
    stGigEDev = MV_GIGE_DEVICE_INFO()
    
    deviceIpList = deviceIp.split('.')# IP地址
    stGigEDev.nCurrentIp = (int(deviceIpList[0]) << 24) | (int(deviceIpList[1]) << 16) | (int(deviceIpList[2]) << 8) | int(deviceIpList[3])

    netIpList = netIp.split('.')# 网卡地址
    stGigEDev.nNetExport =  (int(netIpList[0]) << 24) | (int(netIpList[1]) << 16) | (int(netIpList[2]) << 8) | int(netIpList[3])

    stDevInfo.nTLayerType = MV_GIGE_DEVICE
    stDevInfo.SpecialInfo.stGigEInfo = stGigEDev
    
    cam = MvCamera()
    
    ret = cam.MV_CC_CreateHandle(stDevInfo)
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive,0)
    if stDevInfo.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = cam.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
                if ret != 0:
                    print ("Warning: Set Packet Size fail! ret[0x%x]" % ret)
            else:
                print ("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)
    ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    stParam =  MVCC_INTVALUE()
    memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
    ret = cam.MV_CC_GetIntValue("PayloadSize", stParam)
    ret = cam.MV_CC_StartGrabbing()

    nPayloadSize = stParam.nCurValue

    data_img = (c_ubyte * nPayloadSize)()
    pData = byref(data_img)
    nDataSize = nPayloadSize
    stFrameInfo = MV_FRAME_OUT_INFO_EX()
    memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))

    return [cam,data_img,pData,nDataSize,stFrameInfo]
def CircleCut(Img,Center,Radius,shape):
    mask = np.full((Img.shape[0], Img.shape[1]), 0, dtype=np.uint8) 
    # create circle mask, center, radius, fill color, size of the border
    if shape == "Circle":
        cv.circle(mask,Center, Radius, (255,255,255),-1)
    else:
        cv.rectangle(mask,Center,Radius,(255,255,255),-1)
    # get only the inside pixels
    fg = cv.bitwise_or(Img, Img, mask=mask)
    mask = cv.bitwise_not(mask)
    background = np.full(Img.shape, 150, dtype=np.uint8)
    bk = cv.bitwise_or(background, background, mask=mask)
    final = cv.bitwise_or(fg, bk)

    return final
def Creat_Block(size,Cline,sp,kerf,corr,color,current):
    Img_Width = size[0]
    Img_Hight = size[1]
    white = (255,255,255)
    blue = (51,255,255)
    yellow =(255,255,0)
    pink = (255,0,203)
    gray = (180,180,180)
    black = (0,0,0)
    y_dis = int(Img_Hight/2)
    x_dis = int(Img_Width/5)
    Locs = []
    block = np.zeros((Img_Hight,Img_Width,3),np.uint8)
    if current == 1:
        cv.rectangle(block,(0,0),(Img_Width,Img_Hight),(238,104,123),-1,cv.LINE_8)
    else:
        cv.rectangle(block,(0,0),(Img_Width,Img_Hight),gray,-1,cv.LINE_8)
    cv.rectangle(block,(0,0),(150,200),color,-1,cv.LINE_8)
    for h in range(1,3):
        for w in range(0,5):
            posi = [w*x_dis,y_dis*h]
            Locs.append(posi)
    if sp == 3:
        if kerf ==0 and corr == 0:
            cv.putText(block,"SP1",(Locs[1][0]+50,Locs[1][1]+20),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
            cv.putText(block,"SP2",(Locs[3][0]+50,Locs[3][1]+20),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
        else:
            cv.putText(block,"SP1",(Locs[1][0]+50,Locs[1][1]-30),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
            cv.putText(block,"SP2",(Locs[3][0]+50,Locs[3][1]-30),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
    if sp == 1:
        if kerf ==0 and corr == 0:
            cv.putText(block,"SP1",(Locs[1][0]+50,Locs[1][1]+20),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
        else:
            cv.putText(block,"SP1",(Locs[1][0]+50,Locs[1][1]-30),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
    if sp == 2:
        if kerf ==0 and corr == 0:
            cv.putText(block,"SP2",(Locs[3][0]+50,Locs[3][1]+20),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
        else:
            cv.putText(block,"SP2",(Locs[3][0]+50,Locs[3][1]-30),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
    if kerf != 0:
        cv.putText(block,"Kerf",(Locs[6][0]+50,Locs[6][1]-50),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
    if corr != 0:
        cv.putText(block,"Corr",(Locs[8][0]+50,Locs[8][1]-50),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
    cv.putText(block,Cline,(Locs[0][0]+15,Locs[0][1]+15),cv.FONT_HERSHEY_SIMPLEX,2,black,5,cv.LINE_8)
    cv.line(block,(150,0),(150,200),black,5,cv.LINE_8)
    cv.line(block,(0,0),(600,0),black,5,cv.LINE_8)
    cv.line(block,(0,200),(600,200),black,5,cv.LINE_8)
    cv.line(block,(0,0),(0,200),black,5,cv.LINE_8)
    return block
def Cutting_Info(size,y_pos,selected_path,current_path):
    Img_Width = size[0]
    Img_Hight = size[1]
    Img = 0
    block = 0
    count =0
    
    white = (255,255,255)
    blue = (255,255,51)
    yellow =(0,255,255)
    pink = (203,0,255)
    gray = (150,150,150)
    black = (0,0,0)
    sptext = 0
    try:
        staus = int(y_pos[i][5])
    except:
        staus = 0
    shift = 0
    for i in range(selected_path-5,selected_path+8):
        if selected_path-5 < 0:
            i= i+5
        if selected_path <5 and i >=selected_path:
            i = i-selected_path
        color = gray
        if_selected =0
        if count > 9:
            block = Creat_Block((600,200)," ",0,0,0,color,0)
            Img = np.vstack([Img,block])
            continue
        try:
            sp = int(y_pos[i][1])   
        except:
            block = Creat_Block((600,200)," ",0,0,0,color,0)
            Img = np.vstack([Img,block])
            continue
        if staus == 1 or  y_pos[i][1] == 5:
            color = blue
            sptext =1
        elif staus == 2 or staus == 3 or  y_pos[i][1] == 6:
            color = yellow
            sptext = 2
        else:
            sptext = sp
        if i == current_path[0] or i == current_path[1]:
            color = pink
        if i == selected_path:
            if_selected = 1
        kerf = int(y_pos[i][2])
        correct = int(y_pos[i][3])

        block = Creat_Block((600,200),str(i+1),sptext,kerf,correct,color,if_selected)
        if count == 0:
            Img = block
        else:
            Img = np.vstack([Img,block])
        count += 1
    Img = cv.resize(Img,size)
    return Img
def Animation_Y_POS(img_size,y_pos,current_path_sp,current_x,selected_path,zoom_size,if_cut,shape):
    Img_Width = 1000
    Img_Hight = 1000
    Img_Center = (int(Img_Width/2),int(Img_Hight/2))
    Img = np.zeros((Img_Hight,Img_Width,3),np.uint8)
    white = (255,255,255)
    blue = (255,255,51)
    yellow =(0,255,255)
    pink = (203,0,255)
    linesize = 0
    Range = int((Img_Hight/zoom_size)/2+1)
    kerf_loc = []
    corr_loc = []
    rect_pos = []
    for i in range(0,len(y_pos)):
        if i == selected_path:
            linesize = 2
        else:
            linesize = 1
        Y_dis = -int(y_pos[i][0])
        Y_dis = int(Y_dis * 0.3125)
        Y_Loc = int(Img_Hight/2)+Y_dis
        X_dis = int(y_pos[i][4])
        X_dis = int(X_dis * 0.3125)
        if X_dis == 0:
            X_Loc = 0
        else:
            X_Loc = int(Img_Width/2)+ X_dis
        kerf = int(y_pos[i][2])
        correct = int(y_pos[i][3])
        
        if kerf != 0 or correct != 0:
            rect_pos.append((Y_dis,kerf,correct,i))

        try:
            staus = int(y_pos[i][5])
        except:
            staus = 0
        if i == current_path_sp[0]:############  SP1              
            cv.line(Img,(0,Y_Loc),(Img_Width,Y_Loc),white,linesize,cv.LINE_8)       
            y_pos[i][1] = 5
            if if_cut == 1:
                cv.line(Img,(0,Y_Loc),(current_x,Y_Loc),pink,linesize,cv.LINE_8) 
        elif i == current_path_sp[1]:###############SP2
            cv.line(Img,(0,Y_Loc),(Img_Width,Y_Loc),white,linesize,cv.LINE_8)
            y_pos[i][1] = 6
            if if_cut == 1:
                cv.line(Img,(0,Y_Loc),(current_x,Y_Loc),pink,linesize,cv.LINE_8)                
        elif staus == 1 or y_pos[i][1] == 5:
            cv.line(Img,(0,Y_Loc),(Img_Width,Y_Loc),blue,linesize,cv.LINE_8)
        elif staus == 2 or staus == 3 or y_pos[i][1] == 6:
            cv.line(Img,(0,Y_Loc),(Img_Width,Y_Loc),yellow,linesize,cv.LINE_8)
        else:
            cv.line(Img,(0,Y_Loc),(Img_Width,Y_Loc),white,linesize,cv.LINE_8)
        if zoom_size !=1:
            cv.line(Img,(X_Loc,0),(X_Loc,Img_Hight),white,1,cv.LINE_8)
            cv.line(Img,(500,0),(500,Img_Hight),white,1,cv.LINE_8)
    Img_Center = (int(Img_Width/2),int(Img_Hight/2))
    if shape == "Circle":
        Img = CircleCut(Img,(500,500),int((img_size[0]/2)*0.3125)+10,shape)
    else:
        LU = (Img_Center[0] - int(img_size[0]/2)-10,Img_Center[1] - int(img_size[1]/2)-10)
        RD = (Img_Center[0] + int(img_size[0]/2)+10,Img_Center[1] + int(img_size[1]/2)+10)
        Img = CircleCut(Img,LU,RD,shape)


   
    if zoom_size != 1:
        Img_Center =int( 500-(y_pos[selected_path][0]* 0.3125))
        Display_Line = []
        Range = int(1000/zoom_size/2)
        if Img_Center - Range < 0 :
            Up_Limit = 0
        else:
            Up_Limit = Img_Center - Range
        if Img_Center + Range >Img_Hight:
            Down_Limit = 1000
        else:
            Down_Limit = Img_Center + Range
        for i in range(0,len(y_pos)):
            Y_dis = int(y_pos[i][0])
            Y_dis = int(Y_dis * 0.3125)
            loc = Y_dis + 500
            if loc <Down_Limit and loc>Up_Limit:
                Display_Line.append(i)


        Img = Img[Up_Limit:Down_Limit,500-Range:500+Range]
        Img = cv.resize(Img,(1000,1000))
    

    rect_width = 80
    rect_hight = 10
    shift = 5
    Font_size = 0.6
    for i in rect_pos:
        if zoom_size != 1 :
            if (i[3] in Display_Line):
                rect_y_pos = 500-(int((y_pos[selected_path][0]* 0.3125)-i[0])*zoom_size)
            else:
                continue
        else:
            rect_y_pos = i[0]+500


        cv.rectangle(Img,(1000-rect_width-shift,rect_y_pos-rect_hight),(1000-shift,rect_y_pos+rect_hight),(255,0,0),-1)
        if i[1] > 1 and i[2] != 0:
            cv.rectangle(Img,(shift,rect_y_pos-rect_hight),(shift+rect_width,rect_y_pos+rect_hight),(255,0,0),-1)
            
        if i[1] == 0 and i[2] == 1:
            cv.putText(Img,"   C1",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 0 and i[2] == 2:
            cv.putText(Img,"     ",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"   C2",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 0 and i[2] == 3:
            cv.putText(Img,"   C1",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"   C2",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)

        
        if i[1] == 1 and i[2] == 0:
            cv.putText(Img,"K1   ",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 1 and i[2] == 1:
            cv.putText(Img,"K1 C1",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 1 and i[2] == 2:
            cv.putText(Img,"K1   ",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"   C2",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 1 and i[2] == 3:
            cv.putText(Img,"K1 C1",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"   C2",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)

        if i[1] == 2 and i[2] == 0:
            cv.putText(Img,"     ",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"K2   ",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 2 and i[2] == 1:
            cv.putText(Img,"   C1",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"K2   ",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 2 and i[2] == 2:
            cv.putText(Img,"     ",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"K2 C2",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 2 and i[2] == 3:
            cv.putText(Img,"   C1",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"K2 C2",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)


        if i[1] == 3 and i[2] == 0:
            cv.putText(Img,"K1   ",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"K2   ",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 3 and i[2] == 1:
            cv.putText(Img,"K1 C1",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"K2   ",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 3 and i[2] == 2:
            cv.putText(Img,"K1   ",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"K2 C2",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
        if i[1] == 3 and i[2] == 3:
            cv.putText(Img,"K1 C1 ",(1000-rect_width-shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
            cv.putText(Img,"K2 C2",(shift+10,rect_y_pos+rect_hight-5),cv.FONT_HERSHEY_SIMPLEX,Font_size,(255,255,255),2)
    
    Img_Info = Cutting_Info((600,2000),y_pos,selected_path,current_path_sp)
    Img_Info = cv.resize(Img_Info,(int(Img_Width/3),Img_Hight))
    Img = np.hstack([Img,Img_Info])
    return Img,y_pos

class VideoCamera(object):
    def __init__(self):
        # 通过opencv获取实时视频流
        self.video = cv.VideoCapture(0)
        self.cam = CameraSet("192.168.1.91","192.168.1.1")

    def __del__(self):
        self.video.release()
        self.cam[0].MV_CC_StopGrabbing()
        self.cam[0].MV_CC_CloseDevice()

    def get_frame(self):
        success, image = self.video.read()
        ret = self.cam[0].MV_CC_GetOneFrameTimeout(self.cam[2], self.cam[3], self.cam[4], 1000)
        Img = np.array(self.cam[1],dtype = np.uint8)
        Img= Img.reshape((480,640),order = 'C')
        Img = cv.cvtColor(Img,cv.COLOR_GRAY2BGR)
        cv.line(Img,(320,0),(320,480),(0,255,0),1,cv.LINE_8)      
        cv.line(Img,(0,240),(640,240),(0,255,0),1,cv.LINE_8)  
        # 在这里处理视频帧
        #cv.putText(image, "hello", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0))
        #cv.line(image,(200,200),(400,200),(255,0,255),2,cv.LINE_8)
        cv.namedWindow("asd",cv.WINDOW_AUTOSIZE)
        cv.imshow("asd",Img)
        cv.waitKey( 20)
        # 因为opencv读取的图片并非jpeg格式，因此要用motion JPEG模式需要先将图片转码成jpg格式图片
        ret, jpeg = cv.imencode('.jpg', Img)
        
        return jpeg.tobytes()

class Animation(object):
    def __init__(self) -> None:
        self.Y_Pos = []
        with open('./Data_FTP/CutLineMap.CSV',encoding = 'utf-8-sig') as f:
            for row in csv.reader(f,skipinitialspace = True):
                try:
                    if int(row[0]) == int(row[1]) == 0:
                        continue
                    else:
                        for i in (0,len(row)-1):
                            row[i] = int(row[i])
                        self.Y_Pos.append(row)
                except Exception as e:
                    print(e)
                    continue
    def get_frame(self):
        diameter = abs(self.Y_Pos[0][0])+abs(self.Y_Pos[-1][0])
        Img_Size = [diameter,diameter]
        Current_Path_Sp = [5,25]
        Current_X = 0
        Img_Center = (int(diameter/2),int(diameter/2))
        Select_Path = 0
        Zoom_Size = 2

        Select_Path = np.random.random_integers(1,100)
        Current_X += 10
        Img,self.Y_Pos =Animation_Y_POS(Img_Size,self.Y_Pos,Current_Path_Sp,Current_X,Select_Path,Zoom_Size,1,"Circle")
        ret, jpeg = cv.imencode('.jpg', Img)
        return jpeg.tobytes()
            


app = Flask(__name__)

#app = Flask(__name__)
@app.route('/')  # 主页
def index():
    # jinja2模板，具体格式保存在index.html文件中
    return '<html>\n    <img src="/video_feed">\n  </body>\n</html>'
    #return render_template('templates/index.html')

def gen(camera):
    
    while True:      
        start_t=time.time()

        frame = camera.get_frame()
        print('{0}'.format(time.time()-start_t))
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/video_feed')  # 这个地址返回视频流响应
def video_feed():
    return Response(gen(Animation()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Animation1 = Animation()
    # Animation1.get_frame()
    app.run(host='0.0.0.0', debug=True, port=5000)
    

