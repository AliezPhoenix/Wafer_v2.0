import cv2 as cv
import numpy as np
import os
import Functions
import matplotlib.pyplot as plt
import ctypes as C
import sys
from typing import List, Tuple


def Largest_contour(Img,edge):
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
    return Img_Contours,max_index#Finde the largest contour and return its index


def Cross_Detection(Img_Up,Img_Down):
    Img = np.vstack((Img_Up,Img_Down))
    Img_Width = len(Img[0])
    Img_Hight = len(Img) 
    Img_Center = [int(Img_Width/2),int(Img_Hight/2)]
   
    #cv.imshow("Img",Img)
    #cv.waitKey(0)
    ver_val = []
    count = 0
    left_edge =0
    right_edge = 0
    for w in range(0,Img_Width):
        count =np.count_nonzero(Img[:,w])
        ver_val.append(count)
        count = 0

    for i in range(0,len(ver_val)-1):
        if ver_val[i] > Img_Hight-5:
            left_edge = i
            break
    for i in range(len(ver_val)-1,0,-1):
        if ver_val[i] > Img_Hight-5:
            right_edge = i
            break
    
    if left_edge == right_edge == 0:
        return None,None,Img
    else: 
        return left_edge,right_edge,Img
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
    # 优化为向量化计算
    hor_val = np.sum(image_mask, axis=1) / image_mask.shape[1]
    hor_val = hor_val.tolist()
    
    # 绘制投影图
    # INSERT_YOUR_CODE
    # 绘制hor_val的投影图
    import matplotlib.pyplot as plt


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
    
    plt.figure(figsize=(18, 8))
    # 显示水平投影曲线
    plt.subplot(2, 2, 1)
    plt.plot(hor_val, color='b', label="Horizontal Projection Value (hor_val)")
    plt.xlabel('Row Index')
    plt.ylabel('Projection Value')
    plt.title('Horizontal Projection (hor_val)')
    plt.legend()
    plt.grid(True)


    # 显示image_mask图像
    plt.subplot(2, 2, 2)
    plt.imshow(image_mask, cmap='gray')
    plt.title('image_mask')
    plt.axis('off')

    # 显示Img_Result彩色图像
    plt.subplot(2, 2, 3)
    plt.imshow(cv.cvtColor(Img_Result, cv.COLOR_BGR2RGB))
    plt.title('Img_Result (Color Output)')
    plt.axis('off')

    plt.tight_layout()
    plt.show()
    return 0, "反射切痕检查完成", Img_Result, Cutting_Path_Parameters



def cutting_path_detection_v2(image: np.ndarray,roi: List[int], method: str = "std"):
    result = [0,0,0,0,0,0]
    image_width = image.shape[1]
    image_hight = image.shape[0]
    image_center = [int(image_width/2),int(image_hight/2)]
    image_check = image[image_center[1]-roi[1]:image_center[1]+roi[1],image_center[0]-roi[0]:image_center[0]+roi[0]]
    image_check = cv.cvtColor(image_check, cv.COLOR_BGR2GRAY)
    image_mean = np.mean(image_check)
    if method == "std":
    # x，y方向分别做灰度投影，并绘制plt图像
        hor_val = np.sum(image_check, axis=1)  # 水平投影（y方向，逐行累加）
        ver_val = np.sum(image_check, axis=0)  # 垂直投影（x方向，逐列累加）

        # 计算平均亮度、中位亮度、标准差
        mean_brightness = np.mean(image_check)
        median_brightness = np.median(image_check)
        std_brightness = np.std(image_check)

        print(f"平均亮度 (Mean): {mean_brightness:.2f}")
        print(f"中位亮度 (Median): {median_brightness:.2f}")
        print(f"标准差 (Std): {std_brightness:.2f}")
        
        plt.figure(figsize=(18, 5))

        # 显示原图及统计信息
        plt.subplot(1, 3, 1)
        plt.imshow(cv.cvtColor(image_check, cv.COLOR_GRAY2RGB))
        plt.title(f'Original Image\nMean:{mean_brightness:.2f} | Median:{median_brightness:.2f}\nStd:{std_brightness:.2f}')
        plt.axis('off')

        # 显示水平投影曲线
        plt.subplot(1, 3, 2)
        plt.plot(hor_val, color='b', label="Horizontal Projection (Y axis)")
        plt.xlabel('Row Index')
        plt.ylabel('Projection Value')
        plt.title('Horizontal Projection')
        plt.legend()
        plt.grid(True)

        # 显示垂直投影曲线
        plt.subplot(1, 3, 3)
        plt.plot(ver_val, color='r', label="Vertical Projection (X axis)")
        plt.xlabel('Column Index')
        plt.ylabel('Projection Value')
        plt.title('Vertical Projection')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.show()
    elif method == "reflection":
        image_mask = np.where(image_check <= image_mean-10, 255, 0).astype(np.uint8)

    return 0, "equalized_image", image_check, result
mode = input("请输入模式(1:切割道检测,2:模板匹配):")
if mode == "1":
    for i in os.listdir("Wafer_Rebuild\Image\TGA\TGA129"):
        image = cv.imread("Wafer_Rebuild\Image\TGA\TGA129\\"+i)
        image_width             = image.shape[1]
        image_hight             = image.shape[0]
        image_center            = [int(image_width/2),int(image_hight/2)]
        #image_check = image[image_center[1]-100:image_center[1]+100,image_center[0]-500:image_center[0]+500]
        image_check = image
        #image_check = Functions.Center_block(image_check,20)1
        #ret,ret_content,result_image,result = Functions.cutting_path_detection(image_check)
        ret, ret_content, result_image, result = cutting_path_detection_v2(image_check,(300,60,20),"std")
        text_list = [str(result[0]*533/1000)+"um",
                                str(result[1]*533/1000)+"um",
                                str(result[2]*533/1000)+"um",
                                str(result[3]*533/1000)+"um",
                                str(result[4]*533/1000)+"um",
                                str(result[5])]
        color_list = [(0,255,0),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(0,255,0)]
        result_image = Functions.insert_text(result_image,text_list,1,1,(0,255,0),"cutting_path",color_list)  
        #cv.imshow("result",result_image)
        #cv.waitKey(0)
        print(ret, ret_content, result)
if mode == "2":
    path                    = "Dll\Template_Match_Dll.dll"
    dll                =  C.cdll.LoadLibrary(path)
    dll.Match.restype  = C.POINTER(C.c_double*80)
    dll.Match.argtypes = [C.c_int, C.c_int, C.POINTER(C.c_ubyte),C.c_int, C.c_int, C.POINTER(C.c_ubyte),C.c_int, C.c_double,C.c_int,C.c_int]
    for i in os.listdir("Data_template_match2"):
        image = cv.imread("Data_template_match2\\"+i)
        template = cv.imread("Data_template_match2\\Template_1.bmp")
        roi_x = template.shape[1]*2
        roi_y = template.shape[0]*2
        template_standard = 90
        ret,ret_content,result_template = Functions.template_dll_match(image,template,roi_x,roi_y,dll,template_standard)
        template_value  = result_template[2]
        angel           = result_template[3]
        template_x      = result_template[0]
        template_y      = result_template[1]
        cv.rectangle(image,(int(template_x-int(template.shape[1]/2)),int(template_y-int(template.shape[0]/2)))
                            ,(int(template_x+int(template.shape[1]/2)),int(template_y+int(template.shape[0]/2))),(255,255,0),2)    
        cv.circle(image,(int(template_x),int(template_y)),5,(0,255,0),2)
        #绘制图像中心
        cv.line(image,(int(image.shape[1]/2),0),(int(image.shape[1]/2),int(image.shape[0])),(255,0,255),2)
        cv.line(image,(0,int(image.shape[0]/2)),(int(image.shape[1]),int(image.shape[0]/2)),(255,0,255),2)
        cv.imshow("result",image)
        
        cv.waitKey(0)
        print(ret,ret_content,result_template)