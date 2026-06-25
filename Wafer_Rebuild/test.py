import cv2 as cv
from Communicate import *
import logging as log
import os 
import time 
import sys
import ctypes as C
import Functions
import csv
sys.path.append("../DLL")
def cutting_path_detection_1(Img):
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
            total += int(Img_Check[h,w] )      
        hor_val.append(total/Img_Width_Check)
        total = 0

    print(hor_val)
    lowest_degree = int(np.min(hor_val))
    if lowest_degree <40:
        lowest_degree = 40
    for i in range(int(len(hor_val)/2+10),20,-1):
        if i > int(len(hor_val)/2)-5 and i <int(len(hor_val)/2)+5 :
            continue
        curren_value = int(hor_val[i])
        if curren_value> lowest_degree+10: #and curren_value <lowest_degree+15:
            Cutting_Path_Edges.append(i)
            break
    for i in range(int(len(hor_val)/2-10),len(hor_val)-20):
        if i > int(len(hor_val)/2)-5 and i <int(len(hor_val)/2)+5 :
            continue
        curren_value = int(hor_val[i])
        if curren_value> lowest_degree+10: #and curren_value <lowest_degree+15:
            print(i,Cutting_Path_Edges)
            Cutting_Path_Edges.append(i)
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
        if up_mean == down_mean == 0:
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
        return 2,"检测切割道过窄",Img,Cutting_Path_Parameters
    Cutting_Path_Parameters = [Cutting_Path_Center_Shift,Cutting_Path_Width,Cutting_Path_Width_Total,Center_to_MaxDefect,Crack_Max,Crack_Area]
    print("Detecting OUT")

    return 0,"切痕检查完成",Img_Check,Cutting_Path_Parameters

# image = cv.imread("D:\\DATA\\Wafer_Rebuild\\Wafer_Rebuild\\Data_failed\\20250530032209.bmp")
# image_width             = image.shape[1]
# image_hight             = image.shape[0]
# image_center            = [int(image_width/2),int(image_hight/2)]
# image_check = image[image_center[1]-100:image_center[1]+100,image_center[0]-200:image_center[0]+200]
# image_check = Functions.Center_block(image_check,10)
# ret,ret_content,result_image,result = cutting_path_detection_1(image_check)

# print(ret,ret_content)
# cv.namedWindow("result",cv.WINDOW_AUTOSIZE)
# cv.imshow("result",result_image)
# cv.waitKey()

# print(image)
# com.connect()
# while(1):signals_currentsignals_currentsignals_currentsignals_currentsignals_current
#     signal_r = com.get_signals() 
#     heart_beat = signal_r.decode("DT1000","DT1000","int")
#     signal_s.motify_encode("DT1200",heart_beat,"int")
#     current_source = signal_r.decode("DT1086","DT1102","file")
#     current_file = signal_r.decode("DT1103","DT1103","int")
#     path = "Data_M/"+str(current_source)+"/"+str(current_file)+"/"+"Template_{}.bmp".format(0)
#     cv.imwrite(path,image)

#     print(signal_s.signals["DT1200"])
#     print("心跳： ",heart_beat)
#     print("低倍像素尺寸： ",signal_r.decode("DT1020","DT1021","double"))
#     print("高倍像素尺寸： ",signal_r.decode("DT1022","DT1023","double"))
#     print("当前使用中数据目录名: ",signal_r.decode("DT1086","DT1102","file"))
#     com.send_signals(signal_s)

#dll = C.cdll.LoadLibrary("DLL/Template_Match_Dll.dll")
#dll.Match.restype = C.POINTER(C.c_double*80)
#@dll.Match.argtypes = [C.c_int, C.c_int, C.POINTER(C.c_ubyte),C.c_int, C.c_int, C.POINTER(C.c_ubyte),C.c_int, C.c_double,C.c_int,C.c_int]

# for name in os.listdir("Data_X_Ray"):
#     break
#     Template = cv.imread("Data_X_Ray/Template.bmp")
#     Template = cv.cvtColor(Template,cv.COLOR_BGR2GRAY)
#     Template_h ,Template_w = Template.shape[0],Template.shape[1]
#     Template_Transfer = Template.ctypes.data_as(C.POINTER(C.c_ubyte))
#     total_angle = 0
#     res = 0
#     Img = cv.imread("Data_X_Ray/"+name)
#     Img_ori = Img.copy()
#     Img = cv.cvtColor(Img,cv.COLOR_BGR2GRAY)
#     start = time.time()
#     #ret = CamLowParameter[0].MV_CC_GetOneFrameTimeout(CamLowParameter[2], CamLowParameter[3], CamLowParameter[4], 1000)
#     #Img = np.array(CamLowParameter[1],dtype = np.uint8)
#     #Img= Img.reshape((960,1280),order = 'C')
    
  
#     #cv.imwrite("test.bmp",Img)
#     #Img = cv.cvtColor(Img,cv.COLOR_BGR2GRAY) 
#     (Img_h, Img_w) = (Img.shape[0], Img.shape[1])
#     Img = Img.ctypes.data_as(C.POINTER(C.c_ubyte))
#     print(Img,Template_Transfer)
#     Score = 0.9
#     roi_x = 600
#     roi_y = 500
#     res = dll.Match(Img_h, Img_w, Img,Template_h, Template_w, Template_Transfer,0,0.4,roi_x,roi_y)
#     result = []
#     closest_template = 0
#     temp = 1000

#     for i in range(0,20):
#         try:
#             print("Center: ",res.contents[0+i*4]," ",res.contents[1+i*4])
#             print("Q:" ,res.contents[2+i*4])
#             print("Angle: ",res.contents[3+i*4])
#             print(i)
#             result.append([res.contents[0+i*4],res.contents[1+i*4],res.contents[2+i*4],res.contents[3+i*4]])
#         except:
#             break
        
    
#     Template_w = int(Template_w/2)
#     Template_h = int(Template_h/2)
#     for c in result:
#         distence = np.sqrt(math.pow(abs(c[0]-roi_x),2)+ math.pow(abs(c[1]-roi_y),2))
#         if c[0] == 0 or c[2]<0.2:
#             continue
#         c[0] = int(c[0] - roi_x) + 640
#         c[1] = int(c[1] - roi_y) + 480
#         cv.rectangle(Img_ori,(c[0]-Template_w,c[1]-Template_h),(c[0]+Template_w,c[1]+Template_h),(0,255,0),2,cv.LINE_8)
#         print(closest_template,distence)
#         if distence <= temp:
#             temp = distence
#             closest_template = c
#     cv.rectangle(Img_ori,(closest_template[0]-Template_w,closest_template[1]-Template_h),(closest_template[0]+Template_w,closest_template[1]+Template_h),(0,255,0),2,cv.LINE_8)   
#     angle = result[0][3]
#     print(closest_template,"++++++++++++++")
#     closest_template[0] = int(closest_template[0] - roi_x) + 640
#     closest_template[1] = int(closest_template[1] - roi_y) + 480
#     #cv.rectangle(Img_ori,(closest_template[0]-Template_w,closest_template[1]-Template_h),(closest_template[0]+Template_w,closest_template[1]+Template_h),(0,255,255),2,cv.LINE_8)
#     #cv.line(Img_ori,(640,0),(640,1024),(255,0,255),2,cv.LINE_8)
#     #cv.line(Img_ori,(0,480),(1280,480),(255,0,255),2,cv.LINE_8)
#     cv.namedWindow("ori",cv.WINDOW_NORMAL)
#     cv.imshow("ori",Img_ori)
#     cv.waitKey(0)
#     print("\r",closest_template,angle,name,time.time() - start)
#     print("         SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS               ")
#     Img = 0
#     cv.waitKey(0)

ret,ftp_client = Functions.conn_ftp()
ret = download_file(ftp_client,"/LinearCompTable","Wafer_Rebuild\Data_FTP","Y1_HLA.CSV")
adjusted_loc = [[0,0]]
with open("Wafer_Rebuild\Data_FTP\Y1_HLA.CSV") as f:
    for row in csv.reader(f,skipinitialspace=False):
        adjusted_loc.append([int(row[0]),int(row[1])])
adjusted_loc.append([99999999,0])
def linear_correction(current_loc,adjusted_loc:list):
    result_loc = 0
    current_value =0
    next_value =0
    adjusted_loc_len = len(adjusted_loc)-1
    for index in range(0,adjusted_loc_len):
        current_value = adjusted_loc[index][1]
        next_value = (adjusted_loc[index+1])[1]
        if current_loc > adjusted_loc[index][0] and current_loc <=adjusted_loc[index+1][0]:
            x0 = adjusted_loc[index][0]
            x1 = adjusted_loc[index+1][0]
            y0 = adjusted_loc[index][1]
            y1 = adjusted_loc[index+1][1]
            correction = ((y1-y0)/(x1-x0)*(current_loc-x0))
            result_loc = current_loc - correction - 617767
            print(x0,y1,x1,y1,current_loc,correction)
            break
    return result_loc

print(linear_correction(1400000,adjusted_loc))
