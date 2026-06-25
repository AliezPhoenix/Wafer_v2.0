import cv2 as cv
import numpy as np
import os
import Functions


def Largest_contour(Img):

    Img_Contours,hec = cv.findContours(Img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    for c in range(0,len(Img_Contours)):
        cv.drawContours(Img,[Img_Contours[c]],0,(0,255,255),2,cv.LINE_8)
        box = cv.boundingRect(Img_Contours[c])
        (x,y,w,h) = box
        cv.rectangle(Img,(x,y),(x+w,y+h),(255,255,255),-1,cv.LINE_8)
        print(w,h)
    cv.imshow("Img",Img)
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


def cutting_path_detection(Img):
    print("Detecting IN")
    Cutting_Path_Parameters = [0,0,0,0,0,0]
    Img_Check = Img
    Img_Width_Check = len(Img_Check[0])
    Img_Hight_Check = len(Img_Check)
    Img_Center_Check = [int(Img_Width_Check/2),int(Img_Hight_Check/2)]


    total = 0
    hor_val = []
    Cutting_Path_Edges = []
    for h in range(0,Img_Hight_Check):
        for w in range(0,Img_Width_Check):
            
            total = total+ int(Img_Check[h,w])
        hor_val.append(total/Img_Width_Check)
        total = 0
    

    sorted_array = [x for x in hor_val if 0<x<200]
    outlier = np.mean(sorted_array)
    sorted_array = [x for x in sorted_array if x<outlier]
    lowest_degree = int(np.mean(sorted_array))
    print(lowest_degree)
    if lowest_degree <40:
        lowest_degree = 40
    for i in range(int(len(hor_val)/2),5,-1):
        if i > int(len(hor_val)/2)-5 and i <int(len(hor_val)/2)+5 :
            continue
        curren_value = int(hor_val[i])
        print(curren_value,lowest_degree)
        if curren_value>= lowest_degree*1.3: #and curren_value <lowest_degree+15:
            #print(i,Cutting_Path_Edges)
            Cutting_Path_Edges.append(i+2)
            break
    for i in range(int(len(hor_val)/2),len(hor_val)-5):
        if i > int(len(hor_val)/2)-5 and i <int(len(hor_val)/2)+5:
            continue
        curren_value = int(hor_val[i])
        print(curren_value,lowest_degree)
        if curren_value>= lowest_degree*1.3: #and curren_value <lowest_degree+15:
            #print(i,Cutting_Path_Edges)
            Cutting_Path_Edges.append(i-2)
            break
    try:
        Cutting_Path_Top , Cutting_Path_Bot = Cutting_Path_Edges
    except:
        Img = cv.cvtColor(Img,cv.COLOR_GRAY2BGR)
        return 1,"无法定位切割道",Img,Cutting_Path_Parameters

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
        if up_mean <15 or down_mean < 15:
            up_mean ,down_mean = 15 ,15
        Up_Crack = Img_Check[Cutting_Path_Top-30:Cutting_Path_Top+3, 0:Img_Width_Check]
        Down_Crack = Img_Check[Cutting_Path_Bot-3:Cutting_Path_Bot+30 ,0:Img_Width_Check]


        crack_mean = 0
        if up_mean > down_mean:
            crack_mean = up_mean
        else:
            crack_mean = down_mean
        if crack_mean * 0.15<20:
            crack_mean = crack_mean+20
        else:
            crack_mean = crack_mean*1.15
 

        print(crack_mean)
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
        cv.drawContours(Down_Crack,Down_Crack_Contours,Down_Crack_Index,(0,255,0),2,cv.LINE_8)
        cv.line(Up_Crack,(0,33),(Img_Width_Check,33),(0,0,0),3,cv.LINE_8)
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
        return 2,"检测切割道过窄",Img,Cutting_Path_Parameters
    Cutting_Path_Parameters = [Cutting_Path_Center_Shift,Cutting_Path_Width,Cutting_Path_Width_Total,Center_to_MaxDefect,Crack_Max,Crack_Area]
    print("Detecting OUT")

    return 0,"切痕检查完成",Img_Check,Cutting_Path_Parameters


for i in os.listdir("Data_cutting_path"):
    image = cv.imread("Data_cutting_path\\"+i)
    image_width             = image.shape[1]
    image_hight             = image.shape[0]
    image_center            = [int(image_width/2),int(image_hight/2)]
    #image_check = image[image_center[1]-100:image_center[1]+100,image_center[0]-500:image_center[0]+500]
    image_check = image
    image_check = Functions.Center_block(image_check,10)
    ret,ret_content,result_image,result = cutting_path_detection(image_check)
    cv.imshow("result",result_image)
    cv.waitKey(0)
    print(ret)
    print(ret_content)
    print(result)