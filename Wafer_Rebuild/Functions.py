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
import logging
import time


def Data_to_hex_relabled(Adress):
    Write_Data = Adress[-4:][2:4]+Adress[-4:][0:2]
    return Write_Data


def hexStr_to_str(hex_str):
    hex = hex_str.encode("utf-8")
    str_bin = binascii.unhexlify(hex)
    return str_bin.decode("utf-8")


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


def Animation_Y_POS(img_size,y_pos,current_path_sp,current_x,selected_path,zoom_size,if_cut,shape,Scale):
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


def Display_Devide(Img,size,start_po,Img_Display,border_swtich,border_color): 

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


def Mark_image(image:np.ndarray,marks,Command_Target_Window_Width,Command_Target_Window_Hight,Command_StandardLine_Hight,Command_CuttingLine_Hight):
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


def Passcode_Check(input):
    PassCode = wmi.WMI().Win32_Processor()[0].ProcessorId.strip() + "415263"  + wmi.WMI().Win32_DiskDrive()[0].SerialNumber.strip()
    PassCode_md5 = hashlib.md5(PassCode.encode("gb2312"))
    PassCode_md5 = PassCode_md5.hexdigest()

    if input == hashlib.md5((PassCode_md5[4:14]+"415263").encode("gb2312")).hexdigest():
        return True
    else:
        return False


def conn_ftp():
    ftp_ip = "192.168.1.5"
    ftp_port = 21
    ftp_user = "Qrobot"
    ftp_pw = "Qrobot123"                

    ftp = FTP()
    try:
        ftp.connect(ftp_ip,ftp_port)
        ftp.login(ftp_user,ftp_pw)
        print(ftp.getwelcome())
    except:
        return 0,ftp
    return 1,ftp

def download_file(ftp,remotepath,local_path,filename):
    bufsize = 2048
    try:
        ftp.cwd(remotepath)
        local_path = local_path+ "/"+ filename
        fp = open(local_path ,'wb')
        ftp.retrbinary('RETR '+filename,fp.write,bufsize)
        ftp.set_debuglevel(0)
        fp.close()
        ftp.cwd("..")
    except Exception as e:
        print("FTP not found: ",e)
        return "NG"
    return "OK"



def template_dll_match(image:np.ndarray,template:np.ndarray,roi_x:int,roi_y:int,dll:C.CDLL,template_standard:float):
    result = []
    closest_template = 0
    temp = 2000
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
        closest_template = [0,0,0,0]
        return 1,"无目标图像",closest_template
    
    #取最靠近的中心的模板
    for each_template in result:
        if each_template[2]<template_standard:
            continue
        distence = np.sqrt(math.pow(abs(each_template[0]-roi_x),2)+ math.pow(abs(each_template[1]-roi_y),2))
        if distence <= temp:
            temp = distence
            closest_template = each_template
            closest_template[0] = (closest_template[0] - roi_x) + img_center[0]
            closest_template[1] = (closest_template[1] - roi_y) + img_center[1]

    #判断是否全部模板都没有达到template_standard
    if closest_template == 0:
        closest_template = [0,0,result[0][2],0]
        return 2, "无目标图像: Q值未达到设定值",closest_template
    
    closest_template[3] = result[0][3]
    return 0,"模板匹配成功",closest_template
    
    
def template_match(image,template,template_standard):
    image = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    template = cv.cvtColor(template,cv.COLOR_BGR2GRAY)
    template_standard = template_standard/100
    image_width = image.shape[1]
    image_hight = image.shape[0]
    template_width = template.shape[1]
    template_hight = template.shape[0]
    img_center = [int(image_width/2),int(image_hight/2)]
    points = []
    closest_template = [0,0,0,0]
    temp = 9999

    match_result = cv.matchTemplate(image,template,cv.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc = cv.minMaxLoc(match_result)
    loc = np.where(match_result >= max_val-0.01)


    for i in zip(*loc[::-1]):
        points.append((i[0]+int(template_width/2),i[1]+int(template_hight/2)))
    if len(points) == 0:
        return 1,"无目标图像",closest_template
    if max_val<template_standard:
        closest_template[2] = max_val
        return 2, "无目标图像: Q值未达到设定值",closest_template
    # for each_template in points:
    #     distence = np.sqrt(math.pow(abs(each_template[0]-img_center[0]),2)+ math.pow(abs(each_template[1]-img_center[1]),2))
    #     if distence <= temp:
    #         temp = distence
    #         closest_template[0] = each_template[0]
    #         closest_template[1] = each_template[1]
    closest_template[0] = max_loc[0] + int(template_width/2)
    closest_template[1] = max_loc[1] + int(template_hight/2)
    closest_template[2] = max_val

    return 0,"模板匹配成功",closest_template


def insert_text(image,text,start_po,font_size,color,mode):

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
        cv.rectangle(image,text_pos,(text_pos[0]+300,text_pos[1]+250),0,-1)
        cv.putText(image,text_center,(text_pos[0],text_pos[1]+40),cv.FONT_HERSHEY_TRIPLEX,font_size,color,1,cv.LINE_8)
        cv.putText(image,text_width,(text_pos[0],text_pos[1]+80),cv.FONT_HERSHEY_TRIPLEX,font_size,color,1,cv.LINE_8)
        cv.putText(image,text_max_w,(text_pos[0],text_pos[1]+120),cv.FONT_HERSHEY_TRIPLEX,font_size,color,1,cv.LINE_8)
        cv.putText(image,text_half_w,(text_pos[0],text_pos[1]+160),cv.FONT_HERSHEY_TRIPLEX,font_size ,color,1,cv.LINE_8)
        cv.putText(image,text_chip_max,(text_pos[0],text_pos[1]+200),cv.FONT_HERSHEY_TRIPLEX,font_size,color,1,cv.LINE_8)
        cv.putText(image,text_c_area,(text_pos[0],text_pos[1]+240),cv.FONT_HERSHEY_TRIPLEX,font_size ,color,1,cv.LINE_8)
    return image


def Center_block(Img,blockhight):
    Img_return = cv.cvtColor(Img,cv.COLOR_BGR2GRAY)
    Img_Width = len(Img_return[0])
    Img_Hight = len(Img_return)
    Img_Center = [int(Img_Width/2),int(Img_Hight/2)]
    Img_block = np.zeros((2*blockhight,Img_Width),dtype=np.uint8)

    Img_return[Img_Center[1]-blockhight:Img_Center[1]+blockhight,0:Img_Width] = Img_block
    return Img_return


def Largest_contour(Img):
    Img_Contours,hec = cv.findContours(Img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    temp_area = 0
    max_index = 0
    for i in range(0,len(Img_Contours)):
        area = cv.contourArea(Img_Contours[i])
        if area >temp_area:
            max_index = i
            temp_area = area
    return Img_Contours,max_index#Finde the largest contour and return its index


def Cross_Detection(Img_Up,Img_Down):
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
    
    for i in range(20,len(ver_val)-20):
        if ver_val[i] > Img_Hight-20:
            left_edge = i
            break
    for i in range(len(ver_val)-20,20,-1):
        if ver_val[i] > Img_Hight-20:
            right_edge = i
            break
    if left_edge == right_edge == 0:
        return None,None,Img
    else: 
        return left_edge,right_edge,Img

def cutting_path_detection(Img:np.ndarray):
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
                Cutting_Path_Edges.append(i+2)
                break
        for i in range(int(len(hor_val)/2),len(hor_val)-20):
            if i > int(len(hor_val)/2)-5 and i <int(len(hor_val)/2)+5 :
                continue
            curren_value = int(hor_val[i])
            if curren_value> lowest_degree*1.3: #and curren_value <lowest_degree+15:
                Cutting_Path_Edges.append(i-2)
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
        Up_Crack_Contours, Up_Crack_Index =  Largest_contour(Up_Crack_Thresh)
        Up_Crack = cv.cvtColor(Up_Crack,cv.COLOR_GRAY2BGR)
    
        Down_Crack_Contours,Down_Crack_Index =  Largest_contour(Down_Crack_Thresh)
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


def auto_focal(image):
    scharr_x = cv.Sobel(image,cv.CV_64F,1,0,ksize=-1)
    scharr_y = cv.Sobel(image,cv.CV_64F,0,1,ksize=-1)
    scharr_x = cv.convertScaleAbs(scharr_x)    
    scharr_y = cv.convertScaleAbs(scharr_y)
    scharr_xy = cv.addWeighted(scharr_x,0.5,scharr_y,0.5,0)
    
    kernel=cv.getStructuringElement(shape=cv.MORPH_RECT,ksize=(3,3))
    scharr_xy=cv.morphologyEx(src=scharr_xy,op=cv.MORPH_OPEN,kernel=kernel,iterations=1)
    image_clarity = int(cv.mean(scharr_xy)[0]*10)

    return image_clarity


def best_template(image):
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


def image_preprocess(image:cv.typing.MatLike,image_angle_list,current_cam:int):
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
        
        









