import cv2 as cv
import numpy as np
import math
import wmi
import hashlib
import binascii
from ftplib import FTP
import ctypes as C
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from typing import List, Tuple, Union, Optional

# 弧度到度数的转换常量
R2D = 180.0 / math.pi

def Data_to_hex_relabled(Adress: str) -> str:
    Write_Data = Adress[-4:][2:4]+Adress[-4:][0:2]
    return Write_Data

def hexStr_to_str(hex_str: str) -> str:
    hex = hex_str.encode("utf-8")
    str_bin = binascii.unhexlify(hex)
    return str_bin.decode("utf-8")

def CircleCut(Img: np.ndarray, Center: Tuple[int, int], Radius: int, shape: str) -> np.ndarray:
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

def Creat_Block(size: Tuple[int, int], Cline: str, sp: int, kerf: int, corr: int, color: Tuple[int, int, int], current: int) -> np.ndarray:
    Img_Width = size[0]
    Img_Hight = size[1]
    white = (255,255,255)
    blue = (255,255,51)
    yellow =(0,255,255)
    pink = (203,0,255)
    gray = (150,150,150)
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

def Cutting_Info(size: Tuple[int, int], y_pos: List[List], selected_path: int, current_path: List[int]) -> np.ndarray:
    Img = 0
    block = 0
    count =0
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

def Animation_Y_POS(img_size: Tuple[int, int], y_pos: List[List], current_path_sp: List[int], current_x: int, selected_path: int, zoom_size: int, if_cut: int, shape: str, Scale: float) -> Tuple[np.ndarray, List[List]]:
    Img_Width = 1000
    Img_Hight = 1000
    Img_Center = (int(Img_Width/2),int(Img_Hight/2))
    Img = np.zeros((Img_Hight,Img_Width,3),np.uint8)
    white = (255,255,255)
    blue = (255,255,51)
    yellow =(0,255,255)
    pink = (203,0,255)
    gray = (150,150,150)
    black = (0,0,0)
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
        Y_dis = int(y_pos[i][0])
        Y_dis = int(Y_dis * Scale)
        Y_Loc = int(Img_Hight/2)+Y_dis
        X_dis = int(y_pos[i][4])
        X_dis = int(X_dis * Scale)
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
        Img = CircleCut(Img,(500,500),int((img_size[0]/2)*Scale)+10,shape)
    else:
        LU = (Img_Center[0] - int(img_size[0]/2)-10,Img_Center[1] - int(img_size[1]/2)-10)
        RD = (Img_Center[0] + int(img_size[0]/2)+10,Img_Center[1] + int(img_size[1]/2)+10)
        Img = CircleCut(Img,LU,RD,shape)


   
    if zoom_size != 1:
        Img_Center =int( 500+(y_pos[selected_path][0]* Scale))
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
            Y_dis = int(Y_dis * Scale)
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
                rect_y_pos = 500-(int((y_pos[selected_path][0]* Scale)-i[0])*zoom_size)
            else:
                continue
        else:
            rect_y_pos = i[0]+500
        cv.rectangle(Img,(1000-rect_width-shift,rect_y_pos-rect_hight),(1000-shift,rect_y_pos+rect_hight),(255,0,0),-1)
        cv.rectangle(Img,(shift,rect_y_pos-rect_hight),(shift+rect_width,rect_y_pos+rect_hight),(255,0,0),-1)
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

def Display_Devide(Img: np.ndarray, size: int, start_po: int, Img_Display: np.ndarray, border_swtich: bool, border_color: Tuple[int, int, int]) -> np.ndarray: 

    Img_Width = len(Img[0])
    Img_Hight = len(Img)  
    block_size = [int(Img_Width/8),int(Img_Hight/8)]
    start_y = 0
    start_x = 0
    border_size = 0
    
    # try:
    #     Img_Display= cv.cvtColor(Img_Display,cv.COLOR_GRAY2BGR)
    # except:
    #     pass
    # try:
    #     Img = cv.cvtColor(Img,cv.COLOR_GRAY2BGR)
    # except:
    #     pass

    if size == 0:
        border_size = 5
    if size == 16:
        border_size = 5
    if size == 4:
        border_size = 10
    if size == 1:
        border_size = 20
    
    if border_swtich == True:
        Img = cv.copyMakeBorder(Img,border_size,border_size,border_size,border_size,cv.BORDER_CONSTANT,value = border_color)
        Img = cv.resize(Img,(Img_Width,Img_Hight))
        
    if size == 0:
        Img_Display = Img
    if size == 16:
        Img = cv.resize(Img,(int(Img_Width/2),int(Img_Hight/2)))
        if start_po in [8,16,24,32,40,48,56,64]:
            start_y = int(start_po/8)-1
            start_x = (start_po%8+7)
        else:
            start_y = int(start_po/8)
            start_x = (start_po%8)-1
        location =(start_y*block_size[1],start_x*block_size[0])
        Img_Display[location[0] : location[0] + Img.shape[0], location[1] : location[1] + Img.shape[1], :] = Img

    if size == 4:
        Img = cv.resize(Img,(int(Img_Width/4),int(Img_Hight/4)))
        if start_po in [8,16,24,32,40,48,56,64]:
            start_y = int(start_po/8)-1
            start_x = (start_po%8+7)
        else:
            start_y = int(start_po/8)
            start_x = (start_po%8)-1
        Img_Display[(start_y*block_size[1]):(start_y*block_size[1])+int(Img_Hight/4),(start_x*block_size[0]):(start_x*block_size[0])+int(Img_Width/4)] = Img
    if size == 1:
        Img = cv.resize(Img,(block_size[0],block_size[1]))
        if start_po in [8,16,24,32,40,48,56,64]:
            start_y = int(start_po/8)-1
            start_x = (start_po%8+7)
        else:
            start_y = int(start_po/8)
            start_x = (start_po%8)-1
        Img_Display[(start_y*block_size[1]):(start_y*block_size[1])+int(Img_Hight/8),(start_x*block_size[0]):(start_x*block_size[0])+int(Img_Width/8)] = Img

    try:
        size = int(size)
        if size > 100:
            col = size%10
            row = int(size/10)-10
            if start_po in [8,16,24,32,40,48,56,64]:
                start_y = int(start_po/8)-1
                start_x = (start_po%8+7)
            else:
                start_y = int(start_po/8)
                start_x = (start_po%8)-1
            Img = cv.resize(Img,(block_size[0]*4,block_size[1]*2))
            Img_Display[(start_y*block_size[1]):((start_y+row)*block_size[1]),(start_x*block_size[0]):((start_x+col)*block_size[0])] = Img
    except:
        pass

    return Img_Display

def Mark_image(image: np.ndarray, marks: int, Command_Target_Window_Width: int, Command_Target_Window_Hight: int, Command_StandardLine_Hight: int, Command_CuttingLine_Hight: int) -> np.ndarray:
    center_cross = 0
    target_window = 0
    center_line = 0
    std_line = 0
    cutting_path_line =0
    
    if marks in(1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31):
        center_cross = 1
    if marks in(2,3,6,7,10,11,14,15,18,19,22,23,26,27,30,31):
        target_window =1
    if marks in(4,5,6,7,12,13,14,15,20,21,22,23,28,29,30,31):
        center_line = 1
    if marks in(8,9,10,11,12,13,14,15,24,25,26,27,28,29,30,31):
        std_line = 1
    if marks in(16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31):
        cutting_path_line =1 

    image_width = image.shape[1]
    image_hight = image.shape[0]
    image_center = [int(image_width/2),int(image_hight/2)]
    if center_cross == 1:
        if cutting_path_line == 1:
            cv.line(image,(image_center[0]-100,image_center[1]),(image_center[0]+100,image_center[1]),(0,255,0),2)
            cv.line(image,(image_center[0],image_center[1]-100),(image_center[0],image_center[1]+100),(0,255,0),2)
        else:
            cv.line(image,(0,image_center[1]),(image_width,image_center[1]),(0,255,0),2)
            cv.line(image,(image_center[0],0),(image_center[0],image_hight),(0,255,0),2)
    if target_window == 1:
        Target_Window_Width = int(Command_Target_Window_Width/2)
        Target_Window_Hight = int(Command_Target_Window_Hight/2)
        cv.rectangle(image,(image_center[0]-Target_Window_Width,image_center[1]-Target_Window_Hight),(image_center[0]+Target_Window_Width,image_center[1]+Target_Window_Hight),(0,255,0),2)              
    if center_line == 1:
        cv.line(image,(0,image_center[1]),(image_width,image_center[1]),(0,255,0),2,cv.LINE_AA)
    if std_line == 1:
        Std_Line_Hight = int(Command_StandardLine_Hight/2)
        if cutting_path_line == 1:
            dot_count = 0
            gap = 5
            for i in range(1,image_width//5):
                if dot_count == 0:
                    cv.line(image,(gap*(i-1),image_center[1]-Std_Line_Hight),(gap*i,image_center[1]-Std_Line_Hight),(0,255,0),2)
                    cv.line(image,(gap*(i-1),image_center[1]+Std_Line_Hight),(gap*i,image_center[1]+Std_Line_Hight),(0,255,0),2)
                    dot_count = 1
                    continue
                if dot_count == 1:
                    dot_count = 0
        else:                  
            cv.line(image,(0,image_center[1]-Std_Line_Hight),(image_width,image_center[1]-Std_Line_Hight),(0,255,0),2)         
            cv.line(image,(0,image_center[1]+Std_Line_Hight),(image_width,image_center[1]+Std_Line_Hight),(0,255,0),2)
    if cutting_path_line == 1:
        Cutting_Path_Line_Hight = int(Command_CuttingLine_Hight/2)
        cv.line(image,(0,image_center[1]-Cutting_Path_Line_Hight),(image_center[0]-75,image_center[1]-Cutting_Path_Line_Hight),(255,191,0),2)
        cv.line(image,(image_center[0]+75,image_center[1]-Cutting_Path_Line_Hight),(image_width,image_center[1]-Cutting_Path_Line_Hight),(255,191,0),2)  
        cv.line(image,(0,image_center[1]+Cutting_Path_Line_Hight),(image_center[0]-75,image_center[1]+Cutting_Path_Line_Hight),(255,191,0),2)
        cv.line(image,(image_center[0]+75,image_center[1]+Cutting_Path_Line_Hight),(image_width,image_center[1]+Cutting_Path_Line_Hight),(255,191,0),2)  
    
    
    return image

def Passcode_Check(input: str) -> bool:
    PassCode = wmi.WMI().Win32_Processor()[0].ProcessorId.strip() + "415263"  + wmi.WMI().Win32_DiskDrive()[0].SerialNumber.strip()
    PassCode_md5 = hashlib.md5(PassCode.encode("gb2312"))
    PassCode_md5 = PassCode_md5.hexdigest()

    if input == hashlib.md5((PassCode_md5[4:14]+"415263").encode("gb2312")).hexdigest():
        return True
    else:
        return False

def conn_ftp() -> Tuple[int, FTP]:
    ftp_ip = "192.168.1.5"
    ftp_port = 21
    ftp_user = "Qrobot"
    ftp_pw = "Qrobot123"                

    ftp = FTP()
    try:
        # 设置连接超时和传输超时
        ftp.connect(ftp_ip, ftp_port, timeout=10)
        ftp.login(ftp_user, ftp_pw)
        ftp.set_pasv(True)  # 使用被动模式
        print(ftp.getwelcome())
        return 1, ftp
    except Exception as e:
        print(f"FTP连接失败: {e}")
        try:
            ftp.quit()
        except:
            pass
        return 0, ftp

def download_file(ftp: FTP, remotepath: str, local_path: str, filename: str) -> str:
    bufsize = 2048
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 检查连接是否仍然有效
            ftp.voidcmd("NOOP")
            
            ftp.cwd(remotepath)
            local_path = local_path + "/" + filename
            
            with open(local_path, 'wb') as fp:
                ftp.retrbinary('RETR ' + filename, fp.write, bufsize)
            
            ftp.cwd("..")
            return "OK"
            
        except Exception as e:
            retry_count += 1
            print(f"FTP下载失败 (尝试 {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                try:
                    # 尝试重新连接
                    ftp.quit()
                except:
                    pass
                
                # 重新建立连接
                ret, ftp = conn_ftp()
                if ret == 0:
                    print("无法重新建立FTP连接")
                    return "NG"
            else:
                return "NG"
    
    return "NG"

def remove_duplicates(points: List[Tuple[int, int]], min_distance: int = 30)->Tuple[int, str, List[Tuple[int, int]]]:
    """
    去除重复的模板匹配点
    Args:
        points: 匹配点列表 [(x1,y1), (x2,y2), ...]
        min_distance: 最小距离阈值，小于此距离的点被认为是重复的
    Returns:
        (ret, retcontent, unique_points): 返回状态码、描述信息和去重后的点列表
    """
    try:
        if len(points) <= 1:
            return 0, "去重完成", points
        
        # 转换为numpy数组便于计算
        points_array = np.array(points)
        unique_points = []
        used_indices = set()
        
        for i, point in enumerate(points_array):
            if i in used_indices:
                continue
            # 计算当前点到所有其他点的距离
            distances = np.sqrt(np.sum((points_array - point)**2, axis=1))
            
            # 找到距离小于阈值的所有点
            close_indices = np.where(distances < min_distance)[0]
            
            # 如果只有一个点（自己），直接添加
            if len(close_indices) == 1:
                unique_points.append(tuple(point))
                used_indices.add(i)
            else:
                # 如果有多个相近的点，选择第一个（通常是置信度最高的）
                unique_points.append(tuple(point))
                used_indices.update(close_indices)
        
        return 0, "去重完成", unique_points
    except Exception as e:
        return 1, f"去重处理异常: {str(e)}", points

def points_to_2d_array(unique_points: List[Tuple[int, int]], template_width: int, template_height: int)->Tuple[int, str, np.ndarray]:
    """
    将去重后的匹配点转换为二维数组，按照模板的实际排列组织
    Args:
        unique_points: 去重后的匹配点列表 [(x1,y1), (x2,y2), ...]
        template_width: 模板宽度
        template_height: 模板高度
    Returns:
        (ret, retcontent, result_array): 返回状态码、描述信息和二维数组
    """
    try:
        if not unique_points:
            return 0, "转换完成", np.array([])
        
        # 按x坐标排序，找到最左边的点
        sorted_by_x = sorted(unique_points, key=lambda p: p[0])
        leftmost_x = sorted_by_x[0][0]
        
        # 按y坐标排序，找到最上边的点
        sorted_by_y = sorted(unique_points, key=lambda p: p[1])
        topmost_y = sorted_by_y[0][1]
        
        # 计算行间距和列间距
        # 允许y方向有1/3个模板大小的误差
        y_tolerance = template_height / 2
        
        # 按y坐标分组，相近的y坐标认为是同一行
        rows = []
        current_row = []
        current_y = None
        
        for point in sorted(unique_points, key=lambda p: p[1]):
            if current_y is None or abs(point[1] - current_y) <= y_tolerance:
                # 同一行
                current_row.append(point)
                current_y = point[1] if current_y is None else (current_y + point[1]) / 2
            else:
                # 新的一行
                if current_row:
                    rows.append(sorted(current_row, key=lambda p: p[0]))  # 按x坐标排序
                current_row = [point]
                current_y = point[1]
        
        # 添加最后一行
        if current_row:
            rows.append(sorted(current_row, key=lambda p: p[0]))
        
        # 计算列数（取最大行的列数）
        max_cols = max(len(row) for row in rows) if rows else 0
        
        # 创建二维数组
        result_array = np.full((len(rows), max_cols), None, dtype=object)
        
        # 填充二维数组
        for row_idx, row_points in enumerate(rows):
            for col_idx, point in enumerate(row_points):
                result_array[row_idx][col_idx] = point
        
        return 0, "转换完成", result_array
    except Exception as e:
        return 1, f"二维数组转换异常: {str(e)}", np.array([])

def calculate_image_rotation_angle(points_2d_array: np.ndarray, image_center_x: int, image_center_y: int)->Tuple[int, str, float]  :
    """
    根据最靠近图像中心的那一行计算图像整体偏移角度
    Args:
        points_2d_array: 二维数组，array[row][col] 表示对应位置的匹配点
        image_center_x: 图像中心X坐标
        image_center_y: 图像中心Y坐标
    Returns:
        (ret, retcontent, angle): 返回状态码、描述信息和图像偏移角度（度）
    """
    try:
        if points_2d_array.size == 0:
            return 0, "角度计算完成", 0.0
        
        # 找到最靠近图像中心的那一行
        min_distance = float('inf')
        center_row_index = -1
        
        for row in range(points_2d_array.shape[0]):
            # 计算该行所有点的平均Y坐标
            row_points = []
            for col in range(points_2d_array.shape[1]):
                if points_2d_array[row][col] is not None:
                    row_points.append(points_2d_array[row][col])
            
            if len(row_points) > 0:
                # 计算该行的平均Y坐标
                avg_y = sum(point[1] for point in row_points) / len(row_points)
                # 计算该行到图像中心的距离
                distance = abs(avg_y - image_center_y)
                
                if distance < min_distance:
                    min_distance = distance
                    center_row_index = row
        
        if center_row_index == -1:
            return 1, "无法找到有效的行来计算角度", 0.0
        
        # 获取最靠近中心的那一行的所有点
        center_row_points = []
        for col in range(points_2d_array.shape[1]):
            if points_2d_array[center_row_index][col] is not None:
                center_row_points.append(points_2d_array[center_row_index][col])
        
        if len(center_row_points) < 3:
            return 1, "最靠近中心的行点数不足，无法计算角度", 0.0
        
        # 按X坐标排序
        center_row_points.sort(key=lambda p: p[0])
        
        # 计算该行的角度
        angles = []
        for i in range(len(center_row_points) - 1):
            point1 = center_row_points[i]
            point2 = center_row_points[i + 1]
            
            # 计算两点间的角度
            # 以纵向中轴线为0度基准，逆时针为正，顺时针为负
            dx = point2[0] - point1[0]  # x方向差值
            dy = point2[1] - point1[1]  # y方向差值
            
            if dx != 0:  # 避免除零错误
                # 使用atan2计算角度，以纵向为0度基准
                angle = math.atan2(dx, dy) * R2D  # 转换为度
                angles.append(angle)
        
        # 计算平均角度，排除偏差过大的数据
        if angles:
            # 计算所有角度的平均值
            initial_avg = sum(angles) / len(angles)
            
            # 计算每个角度与平均值的偏差
            deviations = [abs(angle - initial_avg) for angle in angles]
            
            # 计算标准差
            variance = sum((angle - initial_avg) ** 2 for angle in angles) / len(angles)
            std_dev = math.sqrt(variance)
            
            # 排除偏差过大的数据（超过2倍标准差的数据）
            threshold = 2 * std_dev
            filtered_angles = []
            for i, angle in enumerate(angles):
                if deviations[i] <= threshold:
                    filtered_angles.append(angle)
            
            # 如果过滤后还有数据，使用过滤后的数据计算平均值
            if filtered_angles:
                avg_angle = sum(filtered_angles) / len(filtered_angles)
            else:
                # 如果所有数据都被过滤掉，使用原始平均值
                avg_angle = initial_avg
            
            # 角度修正：以纵向中轴线为0度基准
            corrected_angle = avg_angle - 90
            
            return 0, f"角度计算完成，使用第{center_row_index}行，该行点数: {len(center_row_points)}", corrected_angle
        else:
            return 1, "无法计算偏移角度：没有足够的点对数据", 0.0
    except Exception as e:
        return 1, f"角度计算异常: {str(e)}", 0.0

def template_match_multiple(image: np.ndarray,template: np.ndarray,template_standard: float,roi: Tuple[int, int])->Tuple[int, str, List[float]]:
    """
    多模板匹配函数
    Args:
        image: 输入图像
        template: 模板图像
        template_standard: 模板匹配阈值
        roi: ROI区域 [roi_x, roi_y]
    Returns:
        (ret, retcontent, result): 返回状态码、描述信息和匹配结果
    """
    try:
        closest_template = [0,0,0,0]
        
        # 保存原图中心坐标
        original_center_x = int(image.shape[1]/2)
        original_center_y = int(image.shape[0]/2)
        template_standard = template_standard/100
        # 提取ROI区域
        image = image[int(image.shape[0]/2)-roi[1]:int(image.shape[0]/2)+roi[1],int(image.shape[1]/2)-roi[0]:int(image.shape[1]/2)+roi[0]]
        image = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
        template = cv.cvtColor(template,cv.COLOR_BGR2GRAY)
        image_width = image.shape[1]
        image_hight = image.shape[0]
        roi_x = roi[0]
        roi_y = roi[1]
        template_width = template.shape[1]
        template_hight = template.shape[0]
        img_center = [int(image_width/2),int(image_hight/2)]
        points = []
        temp = 9999
        
        match_result = cv.matchTemplate(image,template,cv.TM_CCOEFF_NORMED)
        min_val,max_val,min_loc,max_loc = cv.minMaxLoc(match_result)
        loc = np.where(match_result >= template_standard)
        
        for i in zip(*loc[::-1]):
            points.append((i[0]+int(template_width/2),i[1]+int(template_hight/2)))
        if len(points) == 0:
            return 1,"无目标图像",closest_template
        if max_val<template_standard:
            closest_template[2] = max_val
            return 2, "无目标图像: Q值未达到设定值",closest_template
        
        # 应用去重算法
        ret_dup, retcontent_dup, unique_points = remove_duplicates(points, min_distance=max(template_width,template_hight)/3)
        if ret_dup != 0:
            return ret_dup, f"去重处理失败: {retcontent_dup}", closest_template
        
        # 将去重后的结果转换为二维数组
        ret_2d, retcontent_2d, points_2d_array = points_to_2d_array(unique_points, template_width, template_hight)
        if ret_2d != 0:
            return ret_2d, f"二维数组转换失败: {retcontent_2d}", closest_template
        
        # 计算图像整体偏移角度
        ret_angle, retcontent_angle, rotation_angle = calculate_image_rotation_angle(points_2d_array, img_center[0], img_center[1])
        if ret_angle != 0:
            # 角度计算失败不影响主流程，继续执行
            rotation_angle = 0.0
        
        # 找到距离中心点最近的模板
        best_template = None
        min_distance = float('inf')
        
        for each_template in unique_points:
            template_x = each_template[0]
            template_y = each_template[1]
            # 计算到图像中心的距离
            distance = np.sqrt((template_x - img_center[0])**2 + (template_y - img_center[1])**2)
            if distance < min_distance:
                min_distance = distance
                best_template = each_template
        
        # 返回距离中心点最近的模板信息，格式与template_dll_match保持一致
        # 将ROI坐标转换为原图坐标
        if best_template is not None:
            # 使用与template_dll_match相同的坐标转换方式
            original_x = (best_template[0] - roi_x) + original_center_x
            original_y = (best_template[1] - roi_y) + original_center_y
            result = [original_x, original_y, max_val, rotation_angle]
        else:
            result = [0, 0, max_val, rotation_angle]
        if ret_angle != 0:
            return 2,"角度计算失败",result
        return 0,"模板匹配成功",result
    except Exception as e:
        return 1, f"模板匹配异常: {str(e)}", [0,0,0,0]
    
def template_dll_match(image:np.ndarray,template:np.ndarray,roi_x:int,roi_y:int,dll:C.CDLL,template_standard:float) -> Tuple[int, str, List[float]]:
    result = []
    image = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    template = cv.cvtColor(template,cv.COLOR_BGR2GRAY)
    template_standard = template_standard/100
    image_width = image.shape[1]
    image_hight = image.shape[0]
    template_width = template.shape[1]
    template_hight = template.shape[0]
    img_center = [int(image_width/2),int(image_hight/2)]
    template_transfer = template.ctypes.data_as(C.POINTER(C.c_ubyte))
    image_transfer = image.ctypes.data_as(C.POINTER(C.c_ubyte))
    res = dll.Match(image_hight, image_width,image_transfer,template_hight, template_width, template_transfer,0,0.4,roi_x,roi_y)
    for i in range(0,20):
        try:
            result.append([res.contents[0+i*4],res.contents[1+i*4],res.contents[2+i*4],res.contents[3+i*4]])                                
        except:
            break
    #判断结果是否为空
    if len(result) == 0:
        return 1,"无目标图像",[0,0,0,0]
    
    # 在达到设定阈值的候选中，取距整幅图像中心最近的模板
    best_index = -1
    min_distance = float('inf')
    image_show = cv.cvtColor(image,cv.COLOR_GRAY2BGR)
    for idx, each_template in enumerate(result):
        if each_template[2] < template_standard:
            continue
        # 将候选点从ROI坐标映射到图像坐标后再比较与图像中心的距离
        cand_x_img = (each_template[0] - roi_x) + img_center[0]
        cand_y_img = (each_template[1] - roi_y) + img_center[1]
        # 检查坐标是否为有效值
        if np.isnan(cand_x_img) or np.isnan(cand_y_img) or \
           np.isinf(cand_x_img) or np.isinf(cand_y_img):
            continue
        cv.circle(image_show,(int(cand_x_img),int(cand_y_img)),5,(0,255,0),-1)
        distance = np.sqrt((cand_x_img - img_center[0])**2 + (cand_y_img - img_center[1])**2)
        if distance < min_distance:
            min_distance = distance
            best_index = idx

    if best_index == -1:
        max_q = max(r[2] for r in result)
        return 2, "无目标图像: Q值未达到设定值", [0, 0, max_q, 0]

    chosen = result[best_index][:]
    chosen[0] = (chosen[0] - roi_x) + img_center[0]
    chosen[1] = (chosen[1] - roi_y) + img_center[1]
    return 0,"模板匹配成功",chosen
      
def template_match(image: np.ndarray, template: np.ndarray, template_standard: float) -> Tuple[int, str, List[float]]:
    image = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    template = cv.cvtColor(template,cv.COLOR_BGR2GRAY)
    template_standard = template_standard/100
    image_width = image.shape[1]
    image_hight = image.shape[0]
    template_width = template.shape[1]
    template_hight = template.shape[0]
    img_center = [int(image_width/2),int(image_hight/2)]

    match_result = cv.matchTemplate(image,template,cv.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc = cv.minMaxLoc(match_result)

    if max_val < template_standard:
        return 2, "无目标图像: Q值未达到设定值", [0, 0, max_val, 0]

    best_point = None
    best_q = 0.0
    min_distance = float('inf')
    loc = np.where(match_result >= template_standard)

    for y, x in zip(*loc[::-1]):
        q = match_result[y, x]
        cx = x + int(template_width / 2)
        cy = y + int(template_hight / 2)
        distance = np.sqrt((cx - img_center[0])**2 + (cy - img_center[1])**2)
        if distance < min_distance:
            min_distance = distance
            best_point = (cx, cy)
            best_q = float(q)

    if best_point is None:
        return 1, "无目标图像", [0, 0, 0, 0]

    return 0, "模板匹配成功", [best_point[0], best_point[1], best_q, 0]

def insert_text(image: np.ndarray, text: Union[str, List], start_po: int, font_size: float, color: Tuple[int, int, int], mode: str, color_list: Optional[List[Tuple[int, int, int]]] = None) -> np.ndarray:

    image_width = image.shape[1]
    image_hight = image.shape[0]
    block_size = [int(image_width/8),int(image_hight/8)]
    if start_po in [8,16,24,32,40,48,56,64]:  
        start_y = int(start_po/8)-1
        start_x = (start_po%8+7)
    else:
        start_y = int(start_po/8)
        start_x = (start_po%8)-1
    text_pos = (start_x*block_size[0]+3,start_y*block_size[1]+3)

    if mode == "template":
        text_q = "Q:"+text[0]
        text_a = "Angel:"+text[1]
        text_x = "X:"+text[2]
        text_y = "Y:"+text[3]
        cv.rectangle(image,text_pos,(text_pos[0]+100,text_pos[1]+92),0,-1)
        cv.putText(image,text_q,(text_pos[0],text_pos[1]+23),cv.FONT_HERSHEY_TRIPLEX,font_size,color,1,cv.LINE_8)
        cv.putText(image,text_a,(text_pos[0],text_pos[1]+46),cv.FONT_HERSHEY_TRIPLEX,font_size,color,1,cv.LINE_8)
        cv.putText(image,text_x,(text_pos[0],text_pos[1]+69),cv.FONT_HERSHEY_TRIPLEX,font_size,color,1,cv.LINE_8)
        cv.putText(image,text_y,(text_pos[0],text_pos[1]+92),cv.FONT_HERSHEY_TRIPLEX,font_size ,color,1,cv.LINE_8)
    
    if mode == "cutting_path":
        text_center     = "Center =" + text[0]
        text_width      = "Width  =" + text[1]
        text_max_w      = "Max   W=" + text[2]
        text_half_w     = "Half  W=" + text[3]
        text_chip_max   = "ChipMax=" + text[4]
        text_c_area     = "C  Area=" + text[5] 

        cv.rectangle(image,text_pos,(text_pos[0]+300,text_pos[1]+170),0,-1)
        cv.rectangle(image,(text_pos[0],text_pos[1]+350),(text_pos[0]+300,text_pos[1]+450),0,-1)
        cv.putText(image,text_center,(text_pos[0],text_pos[1]+40),cv.FONT_HERSHEY_TRIPLEX,font_size,color_list[0],1,cv.LINE_8)
        cv.putText(image,text_width,(text_pos[0],text_pos[1]+80),cv.FONT_HERSHEY_TRIPLEX,font_size,color_list[1],1,cv.LINE_8)
        cv.putText(image,text_max_w,(text_pos[0],text_pos[1]+120),cv.FONT_HERSHEY_TRIPLEX,font_size,color_list[2],1,cv.LINE_8)
        cv.putText(image,text_half_w,(text_pos[0],text_pos[1]+160),cv.FONT_HERSHEY_TRIPLEX,font_size ,color_list[3],1,cv.LINE_8)
        cv.putText(image,text_chip_max,(text_pos[0],text_pos[1]+400),cv.FONT_HERSHEY_TRIPLEX,font_size,color_list[4],1,cv.LINE_8)
        cv.putText(image,text_c_area,(text_pos[0],text_pos[1]+440),cv.FONT_HERSHEY_TRIPLEX,font_size ,color_list[5],1,cv.LINE_8)
    return image

def Center_block(Img: np.ndarray, blockhight: int) -> np.ndarray:
    Img_return = cv.cvtColor(Img,cv.COLOR_BGR2GRAY)
    Img_Width = len(Img_return[0])
    Img_Hight = len(Img_return)
    Img_Center = [int(Img_Width/2),int(Img_Hight/2)]
    Img_block = np.zeros((2*blockhight,Img_Width),dtype=np.uint8)

    Img_return[Img_Center[1]-blockhight:Img_Center[1]+blockhight,0:Img_Width] = Img_block
    return Img_return

def Largest_contour(Img: np.ndarray, edge: str) -> Tuple[List, int]:
    Img_Contours,hec = cv.findContours(Img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    temp_area = 0
    max_index = 0
    for i in range(0,len(Img_Contours)):
        area = cv.contourArea(Img_Contours[i])
        box = cv.boundingRect(Img_Contours[i])
        if box[1] != 0 and edge == "down":
            continue
        if box[1]+box[3] != Img.shape[0] and edge == "up":
            continue
        if area >temp_area:
            max_index = i
            temp_area = area
    return Img_Contours,max_index

def Cross_Detection(Img_Up: np.ndarray, Img_Down: np.ndarray) -> Tuple[Optional[int], Optional[int], np.ndarray]:
    Img = np.vstack((Img_Up,Img_Down))
    Img_Width = len(Img[0])
    Img_Hight = len(Img) 
    Img_Center = [int(Img_Width/2),int(Img_Hight/2)]
    ver_val = []
    count = 0
    left_edge =0
    right_edge = 0
    for w in range(0,Img_Width):
        count =np.count_nonzero(Img[:,w])
        ver_val.append(count)
        count = 0

    if len(ver_val)<41:
        return None,None,Img
    
    for i in range(0,len(ver_val)-1):
        if ver_val[i] >= Img_Hight-2:
            left_edge = i
            break
    for i in range(len(ver_val)-1,0,-1):
        if ver_val[i] >= Img_Hight-2:
            right_edge = i
            break
    if left_edge == right_edge == 0:
        return None,None,Img
    else: 
        return left_edge-10,right_edge+10,Img

def cutting_path_detection(Img: np.ndarray) -> Tuple[int, str, np.ndarray, List[int]]:
    Cutting_Path_Parameters = [0,0,0,0,0,0]
    Img_Check = Img
    Img_Width_Check = len(Img_Check[0])
    Img_Hight_Check = len(Img_Check)
    Img_Center_Check = [int(Img_Width_Check/2),int(Img_Hight_Check/2)]
    Image_mean = np.mean(Img_Check)
    if Image_mean < 50:
        Img = cv.cvtColor(Img,cv.COLOR_GRAY2BGR)
        return 1,"整体亮度过低",Img,Cutting_Path_Parameters

    total = 0
    hor_val = []
    Cutting_Path_Edges = []

    for h in range(0,Img_Hight_Check):
        for w in range(0,Img_Width_Check):
            total += int(Img_Check[h,w] )      
        hor_val.append(total/Img_Width_Check)
        total = 0

    if len(hor_val) < 35: #if the image is too small
        Img = cv.cvtColor(Img,cv.COLOR_GRAY2BGR)
        return 2,"无法定位切割道:检测宽度过低",Img,Cutting_Path_Parameters
    
    flitered_array = [x for x in hor_val if 0<x<200] #count nonzero
    outlier = np.mean(flitered_array)
    flitered_array = [x for x in flitered_array if x<outlier] #cut off the outliers 
    lowest_degree = int(np.mean(flitered_array))

    if lowest_degree <40:
        lowest_degree = 40
    try:
        for i in range(int(len(hor_val)/2),20,-1):
            if i > int(len(hor_val)/2)-5 and i <int(len(hor_val)/2)+5 :
                continue
            curren_value = int(hor_val[i])
            if curren_value> lowest_degree*1.3: #and curren_value <lowest_degree+15:
                Cutting_Path_Edges.append(i)
                break
        for i in range(int(len(hor_val)/2),len(hor_val)-20):
            if i > int(len(hor_val)/2)-5 and i <int(len(hor_val)/2)+5 :
                continue
            curren_value = int(hor_val[i])
            if curren_value> lowest_degree*1.3: #and curren_value <lowest_degree+15:
                Cutting_Path_Edges.append(i)
                break
        
        Cutting_Path_Top , Cutting_Path_Bot = Cutting_Path_Edges
    except:
        Img = cv.cvtColor(Img,cv.COLOR_GRAY2BGR)
        return 2,"无法定位切割道",Img,Cutting_Path_Parameters

    if Cutting_Path_Top-30 <= 0 or Cutting_Path_Bot+30 >= Img_Center_Check[1]*2:
        Up_Crack_Max = 0
        
        Down_Crack_Max = 0
        Crack_Max = 0
        Crack_Area = 0

        Center_to_MaxDefect = 0
        Cutting_Path_Center = 0
        Img_Check = cv.cvtColor(Img_Check,cv.COLOR_GRAY2BGR)
    else:
        up_mean = np.mean(hor_val[Cutting_Path_Top+3:Cutting_Path_Top+10])
        down_mean = np.mean(hor_val[Cutting_Path_Bot-10:Cutting_Path_Bot-3])
        if up_mean == 0:
            up_mean = down_mean
        if down_mean == 0:
            down_mean = up_mean
        if up_mean == down_mean == 0:
            up_mean ,down_mean = 15 ,15

        try:
            Up_Crack = Img_Check[Cutting_Path_Top-30:Cutting_Path_Top+3, 0:Img_Width_Check]
            Down_Crack = Img_Check[Cutting_Path_Bot-3:Cutting_Path_Bot+30 ,0:Img_Width_Check]
        except Exception as e:
            Img = cv.cvtColor(Img,cv.COLOR_GRAY2BGR)
            print(e)
            return 2,"外遮罩过窄无法定位崩边",Img,Cutting_Path_Parameters
        
        crack_mean = 0
        if up_mean > down_mean:
            crack_mean = up_mean
        else:
            crack_mean = down_mean
        if crack_mean * 0.15<20:
            crack_mean = crack_mean+20
        else:
            crack_mean = crack_mean*1.15

        ret,Up_Crack_Thresh = cv.threshold(Up_Crack,crack_mean,255,cv.THRESH_BINARY_INV)
        ret,Down_Crack_Thresh = cv.threshold(Down_Crack,crack_mean,255,cv.THRESH_BINARY_INV)
        cv.line(Up_Crack,(0,33),(Img_Width_Check,33),0,3,cv.LINE_8)
        cv.line(Down_Crack,(0,1),(Img_Width_Check,1),0,3,cv.LINE_8)
        ret,Up_Crack_Thresh = cv.threshold(Up_Crack,crack_mean*1.15,255,cv.THRESH_BINARY_INV)
        ret,Down_Crack_Thresh = cv.threshold(Down_Crack,crack_mean*1.15,255,cv.THRESH_BINARY_INV)


        Left_Edge , Right_Edge,Crack_Img = Cross_Detection(Up_Crack_Thresh,Down_Crack_Thresh)
        if Left_Edge == Right_Edge == None:
            pass
        else:
            Left_Edge = Left_Edge - 10
            Right_Edge = Right_Edge +10
            cv.rectangle(Up_Crack_Thresh,(Left_Edge,0),(Right_Edge,30),0,-1,cv.LINE_8)
            cv.rectangle(Down_Crack_Thresh,(Left_Edge,3),(Right_Edge,33),0,-1,cv.LINE_8)
        Up_Crack_Contours, Up_Crack_Index =  Largest_contour(Up_Crack_Thresh,"up")
        Up_Crack = cv.cvtColor(Up_Crack,cv.COLOR_GRAY2BGR)
    
        Down_Crack_Contours,Down_Crack_Index =  Largest_contour(Down_Crack_Thresh,"down")
        Down_Crack = cv.cvtColor(Down_Crack,cv.COLOR_GRAY2BGR)

        Up_rect = cv.boundingRect(Up_Crack_Contours[Up_Crack_Index])
        Down_rect = cv.boundingRect(Down_Crack_Contours[Down_Crack_Index])
    

        cv.drawContours(Up_Crack,Up_Crack_Contours,Up_Crack_Index,(0,255,0),2,cv.LINE_8)
        cv.line(Up_Crack,(0,33),(Img_Width_Check,33),(0,0,0),3,cv.LINE_8)

        cv.drawContours(Down_Crack,Down_Crack_Contours,Down_Crack_Index,(0,255,0),2,cv.LINE_8)
        cv.line(Down_Crack,(0,0),(Img_Width_Check,0),(0,0,0),3,cv.LINE_8)

        Img_Check = cv.cvtColor(Img_Check,cv.COLOR_GRAY2BGR)
        Img_Check[Cutting_Path_Top-30:Cutting_Path_Top+3, 0:Img_Width_Check] = Up_Crack     
        Img_Check[Cutting_Path_Bot-3:Cutting_Path_Bot+30, 0:Img_Width_Check] = Down_Crack
        Up_Crack_Max = Up_rect[3]
        Down_Crack_Max = Down_rect[3]
        Cutting_Path_Center = int((Cutting_Path_Bot-Cutting_Path_Top)/2)+Cutting_Path_Top
        if Up_Crack_Max>=Down_Crack_Max :
            Center_to_MaxDefect = Cutting_Path_Center-Cutting_Path_Top + Up_Crack_Max
            Crack_Max = Up_Crack_Max
        else:
            Center_to_MaxDefect = Cutting_Path_Bot - Cutting_Path_Center + Down_Crack_Max
            Crack_Max = Down_Crack_Max
        Crack_Area =int( (np.count_nonzero(Up_Crack_Contours[Up_Crack_Index])+np.count_nonzero(Down_Crack_Contours[Down_Crack_Index]))/10 )



    cv.line(Img_Check,(0,Cutting_Path_Top),(Img_Width_Check,Cutting_Path_Top),(0,0,255),2,cv.LINE_8)
    cv.line(Img_Check,(0,Cutting_Path_Bot),(Img_Width_Check,Cutting_Path_Bot),(0,0,255),2,cv.LINE_8)

    
    Cutting_Path_Center_Shift = Cutting_Path_Center - Img_Center_Check[1]
    Cutting_Path_Width = Cutting_Path_Bot-Cutting_Path_Top
    Cutting_Path_Width_Total = Cutting_Path_Width+Up_Crack_Max+Down_Crack_Max
    if Cutting_Path_Width <= 10:
        Img = cv.cvtColor(Img,cv.COLOR_GRAY2BGR)
        return 3,"检测切割道过窄",Img,Cutting_Path_Parameters
    Cutting_Path_Parameters = [Cutting_Path_Center_Shift,Cutting_Path_Width,Cutting_Path_Width_Total,Center_to_MaxDefect,Crack_Max,Crack_Area]
    print("Detecting OUT")

    return 0,"切痕检查完成",Img_Check,Cutting_Path_Parameters

def cutting_path_reflection(Img: np.ndarray, roi: List[int], method: str = "std") -> Tuple[int, str, np.ndarray, List[int]]:
    """
    完善后的反射切割道检测函数，与cutting_path_detection保持一致的处理逻辑
    """
    
    Cutting_Path_Parameters = [0,0,0,0,0,0]
    image = Img.copy()
    # 灰度保护
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image_width = image.shape[1]
    image_hight = image.shape[0]
    image_center = [int(image_width/2),int(image_hight/2)]

    check_roi = roi 
    # 使用传入的roi参数
    image_check = image[image_center[1]-check_roi[1]:image_center[1]+check_roi[1], 
                  image_center[0]-check_roi[0]:image_center[0]+check_roi[0]]
    image_mean = np.mean(image_check)
    
    #将 image_mask 转换为 uint8 类型
    if method == "std":
        image_mask = np.where(image_check >= image_mean, 255, 0).astype(np.uint8)
    elif method == "reflection":
        image_mask = np.where(image_check <= image_mean-10, 255, 0).astype(np.uint8)
    
    # 使用掩码提取感兴趣区域
    image_check_masked = cv.bitwise_and(image_check, image_mask)
    
    # 计算水平投影值
    total = 0 
    hor_val = []
    for h in range(0,image_mask.shape[0]):
        for w in range(0,image_mask.shape[1]):
            total = total + int(image_mask[h,w])
        hor_val.append(total/image_mask.shape[1])
        total = 0 
    
    # 绘制投影图
    
    # 分析投影数据，找出切割道边界

    sorted_array = [x for x in hor_val if 0 < x < 200]
    if len(sorted_array) > 0:
        outlier = np.mean(sorted_array)
        sorted_array = [x for x in sorted_array if x < outlier]
        if len(sorted_array) > 0:
            lowest_degree = int(np.mean(sorted_array))
        else:
            lowest_degree = 40
    else:
        lowest_degree = 40
        
    if lowest_degree < 40:
        lowest_degree = 40
        
    Cutting_Path_Edges = []
    
    # 从中间向上查找上边界
    mid_ignore = check_roi[2]
    if mid_ignore<10:
        mid_ignore = 10
    for i in range(int(len(hor_val)/2), 5, -1):
        if i > int(len(hor_val)/2)-mid_ignore and i < int(len(hor_val)/2)+mid_ignore:
            continue
        if i < len(hor_val):
            current_value = int(hor_val[i])
            if current_value >= lowest_degree:
                Cutting_Path_Edges.append(i + 2)
                break
                
    # 从中间向下查找下边界
    for i in range(int(len(hor_val)/2)+5, len(hor_val) - 5):
        if i > int(len(hor_val)/2)-mid_ignore and i < int(len(hor_val)/2)+mid_ignore:
            continue

        if i < len(hor_val):
            current_value = int(hor_val[i])
            if current_value >= lowest_degree:
                Cutting_Path_Edges.append(i - 2)
                break
                
    # 检查是否成功找到两个边界
    try:
        Cutting_Path_Top, Cutting_Path_Bot = Cutting_Path_Edges
    except:
        Img_Color = Img.copy()
        if len(Img_Color.shape) == 2:
            Img_Color = cv.cvtColor(Img_Color, cv.COLOR_GRAY2BGR)
        return 1, "无法定位反射切割道", Img_Color, Cutting_Path_Parameters
    # 边界顺序保护
    if Cutting_Path_Top >= Cutting_Path_Bot:
        Img_Color = Img.copy()
        if len(Img_Color.shape) == 2:
            Img_Color = cv.cvtColor(Img_Color, cv.COLOR_GRAY2BGR)
        return 1, "切割道边界异常", Img_Color, Cutting_Path_Parameters

    # 计算切割道相关参数
    Cutting_Path_Center = int((Cutting_Path_Bot - Cutting_Path_Top) / 2) + Cutting_Path_Top
    Cutting_Path_Center_Shift = Cutting_Path_Center - check_roi[1]  # 相对于中心的偏移
    Cutting_Path_Width = Cutting_Path_Bot - Cutting_Path_Top
    
    # 完整的缺陷检测逻辑
    # 修改：根据实际切割道边缘进行自适应崩边检测
    up_detection_range = min(30, Cutting_Path_Top)
    down_detection_range = min(30, image_check.shape[0] - Cutting_Path_Bot)
    
    if up_detection_range >= 6 and down_detection_range >= 6:# 确保有检测区域
        # 提取上下裂纹区域

            
        # 修改：使用实际可用范围进行裂纹检测
        Up_Crack_ori = image_check[Cutting_Path_Top- up_detection_range + 3:Cutting_Path_Top+3, 0:image_check.shape[1]]
        Up_Crack = image_check[Cutting_Path_Top- up_detection_range + 3:Cutting_Path_Top+3, 0:image_check.shape[1]]
        Down_Crack_ori = image_check[Cutting_Path_Bot-3:Cutting_Path_Bot + down_detection_range - 3, 0:image_check.shape[1]]
        Down_Crack = image_check[Cutting_Path_Bot-3:Cutting_Path_Bot + down_detection_range - 3, 0:image_check.shape[1]]
        crack_mean = (cv.mean(Up_Crack)[0]+cv.mean(Down_Crack)[0])/2
        ret, Up_Crack_Thresh = cv.threshold(Up_Crack, crack_mean*0.5,255, cv.THRESH_BINARY_INV)
        ret, Down_Crack_Thresh = cv.threshold(Down_Crack, crack_mean*0.5, 255, cv.THRESH_BINARY_INV)
    
        # 添加边界线以避免边缘干扰
        #cv.line(Up_Crack_Thresh, (0, Up_Crack.shape[0]-1), (Up_Crack.shape[1], Up_Crack.shape[0]-1), 0, 1, cv.LINE_8)
        if Up_Crack_Thresh.shape[0] >= 4:
            cv.line(Up_Crack_Thresh, (0, Up_Crack.shape[0]-3), (Up_Crack.shape[1], Up_Crack.shape[0]-3), 255, 2, cv.LINE_8)
        #cv.line(Down_Crack_Thresh, (0, 1), (Down_Crack.shape[1], 1), 0, 1, cv.LINE_8)
        if Down_Crack_Thresh.shape[0] >= 4:
            cv.line(Down_Crack_Thresh, (0, 3), (Down_Crack.shape[1], 3), 255, 2, cv.LINE_8) 
        # 重新进行阈值处理以获得更清晰的结果

        # 检测横向裂纹并排除干扰
        Left_Edge, Right_Edge, Crack_Img = Cross_Detection(Up_Crack_Thresh, Down_Crack_Thresh)
        if Left_Edge is not None and Right_Edge is not None:
            cv.rectangle(Up_Crack_Thresh, (Left_Edge, 0), (Right_Edge, max(0, up_detection_range - 3)), 0, -1, cv.LINE_8)
            cv.rectangle(Down_Crack_Thresh, (Left_Edge, 3), (Right_Edge, down_detection_range), 0, -1, cv.LINE_8)

        # 查找最大轮廓
        try:
            Up_Crack_Contours, Up_Crack_Index = Largest_contour(Up_Crack_Thresh,"up")
            Down_Crack_Contours, Down_Crack_Index = Largest_contour(Down_Crack_Thresh,"down")
        except Exception:
            Up_Crack_Contours, Down_Crack_Contours = [], []
            Up_Crack_Index, Down_Crack_Index = 0, 0
        
        # 转换为彩色图像以便绘制
        Up_Crack_Color = cv.cvtColor(Up_Crack_ori, cv.COLOR_GRAY2BGR)
        Down_Crack_Color = cv.cvtColor(Down_Crack_ori, cv.COLOR_GRAY2BGR)

        # 获取边界框
        if len(Up_Crack_Contours) == 0 or len(Down_Crack_Contours) == 0:
            Up_rect = (0,0,0,0)
            Down_rect = (0,0,0,0)
        else:
            Up_rect = cv.boundingRect(Up_Crack_Contours[Up_Crack_Index])
            Down_rect = cv.boundingRect(Down_Crack_Contours[Down_Crack_Index])

        # 绘制轮廓
        if len(Up_Crack_Contours) > 0:
            cv.drawContours(Up_Crack_Color, Up_Crack_Contours, Up_Crack_Index, (0, 255, 0), 2, cv.LINE_8)
        if len(Down_Crack_Contours) > 0:
            cv.drawContours(Down_Crack_Color, Down_Crack_Contours, Down_Crack_Index, (0, 255, 0), 2, cv.LINE_8)
        cv.line(Up_Crack_Color, (0, Up_Crack.shape[0]-1), (Up_Crack.shape[1], Up_Crack.shape[0]-1), 0, 1, cv.LINE_8)
        cv.line(Down_Crack_Color, (0, 1), (Down_Crack.shape[1], 1), 0, 2, cv.LINE_8)
        # 添加边界线


        # 将处理后的裂纹区域放回原图
        image_check_result = image_check.copy()
        if len(image_check_result.shape) == 2:
            image_check_result = cv.cvtColor(image_check_result, cv.COLOR_GRAY2BGR)
        image_check_result[Cutting_Path_Top- up_detection_range + 3:Cutting_Path_Top+3, 0:image_check.shape[1]] = Up_Crack_Color     
        image_check_result[Cutting_Path_Bot-3:Cutting_Path_Bot + down_detection_range - 3, 0:image_check.shape[1]] = Down_Crack_Color
        
        # 计算裂纹参数
        Up_Crack_Max = Up_rect[3]
        Down_Crack_Max = Down_rect[3]
        
        # 确定最大裂纹和相关参数
        if Up_Crack_Max >= Down_Crack_Max:
            Center_to_MaxDefect = Cutting_Path_Center - Cutting_Path_Top + Up_Crack_Max
            Crack_Max = Up_Crack_Max-8
        else:
            Center_to_MaxDefect = Cutting_Path_Bot - Cutting_Path_Center + Down_Crack_Max
            Crack_Max = Down_Crack_Max-8
        if Crack_Max < 0:
            Crack_Max = 0
        # 计算裂纹总面积
        if len(Up_Crack_Contours) > 0 and len(Down_Crack_Contours) > 0:
            Crack_Area = int((cv.contourArea(Up_Crack_Contours[Up_Crack_Index]) + 
                         cv.contourArea(Down_Crack_Contours[Down_Crack_Index])) / 10)
        else:
            Crack_Area = 0
    else:
        Up_Crack_Max = 0
        Down_Crack_Max = 0
        Crack_Max = 0
        Crack_Area = 0
        Center_to_MaxDefect = 0
    
    # 在原图上绘制检测结果
    Img_Result = Img.copy()
    if len(Img_Result.shape) == 2:
        Img_Result = cv.cvtColor(Img_Result, cv.COLOR_GRAY2BGR)

    
    # 如果有缺陷检测结果，则叠加显示
    if 'image_check_result' in locals():
        Img_Result[image_center[1]-check_roi[1]:image_center[1]+check_roi[1], 
                  image_center[0]-check_roi[0]:image_center[0]+check_roi[0]] = image_check_result
    
    cv.line(Img_Result, (image_center[0]-check_roi[0], image_center[1]-check_roi[1]+Cutting_Path_Top), 
            (image_center[0]+check_roi[0], image_center[1]-check_roi[1]+Cutting_Path_Top), (0,0,255), 2, cv.LINE_8)
    cv.line(Img_Result, (image_center[0]-check_roi[0], image_center[1]-check_roi[1]+Cutting_Path_Bot), 
            (image_center[0]+check_roi[0], image_center[1]-check_roi[1]+Cutting_Path_Bot), (0,0,255), 2, cv.LINE_8)
    cv.rectangle(Img_Result, (image_center[0]-check_roi[0], image_center[1]-check_roi[1]), 
            (image_center[0]+check_roi[0], image_center[1]+check_roi[1]), (255,0,255), 2, cv.LINE_8)
    # 计算总宽度（包括缺陷）
    Cutting_Path_Width_Total = Cutting_Path_Width + Up_Crack_Max + Down_Crack_Max
    
    if Cutting_Path_Width <= 10:
        return 2, "检测反射切割道过窄", Img_Result, Cutting_Path_Parameters
        
    # 组装返回参数
    Cutting_Path_Parameters = [Cutting_Path_Center_Shift, Cutting_Path_Width, Cutting_Path_Width_Total, 
                              Center_to_MaxDefect, Crack_Max, Crack_Area]
    print("Reflection Detecting OUT")
    
    return 0, "反射切痕检查完成", Img_Result, Cutting_Path_Parameters

def auto_focal(image: np.ndarray) -> int:
    scharr_x = cv.Sobel(image,cv.CV_64F,1,0,ksize=-1)
    scharr_y = cv.Sobel(image,cv.CV_64F,0,1,ksize=-1)
    scharr_x = cv.convertScaleAbs(scharr_x)    
    scharr_y = cv.convertScaleAbs(scharr_y)
    scharr_xy = cv.addWeighted(scharr_x,0.5,scharr_y,0.5,0)
    
    kernel=cv.getStructuringElement(shape=cv.MORPH_RECT,ksize=(3,3))
    scharr_xy=cv.morphologyEx(src=scharr_xy,op=cv.MORPH_OPEN,kernel=kernel,iterations=1)
    image_clarity = int(cv.mean(scharr_xy)[0]*10)

    return image_clarity

def best_template(image: np.ndarray) -> np.ndarray:
    image = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    image_width_gap = int(len(image[0])/3)-1
    image_hight_gap = int(len(image)/3)-1 
    image_sub_list = []
    result = []
    for i in range(0,3):
        for j in range(0,3):
            image_sub_list.append(image[image_hight_gap*i:image_hight_gap*(i+1),image_width_gap*j:image_width_gap*(j+1)])
    for img in image_sub_list:
        result.append(auto_focal(img))

    loc = result.index(np.max(result))
    return image_sub_list[loc]

def image_preprocess(image: cv.typing.MatLike, image_angle_list: List[float], current_cam: int) -> np.ndarray:
    ## 预处理
    iamge_hight = image.shape[0]
    image_width = image.shape[1]
    for index,a in enumerate(image_angle_list):
        if a > 32767:
            image_angle_list[index] = (image_angle_list[index]-65536)/10000
        else:
            image_angle_list[index] = image_angle_list[index]/10000
    angle = image_angle_list[current_cam]
    rotate_matrix = cv.getRotationMatrix2D((image.shape[1]/2,image.shape[0]/2),angle,1)
    image = cv.warpAffine(image,rotate_matrix,(image.shape[1],image.shape[0]))
    image = image[20:image.shape[0]-20,20:image.shape[1]-20]
    image = cv.cvtColor(image,cv.COLOR_GRAY2BGR)
    return image
        
        









