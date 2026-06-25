import cv2 as cv
import numpy as np
import math
import os
import ctypes as C
import Functions 
def template_match(image,template,template_standard):
    image = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    template = cv.cvtColor(template,cv.COLOR_BGR2GRAY)
    #ret,image = cv.threshold(image,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    #ret,template = cv.threshold(template,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
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

    print(max_loc[0]+int(template_width/2),max_loc[1]+int(template_hight/2))

    for i in zip(*loc[::-1]):
        points.append((i[0]+int(template_width/2),i[1]+int(template_hight/2)))
    if len(points) == 0:
        return 1,"无目标图像",closest_template
    if max_val<template_standard:
        closest_template[2] = max_val
        return 2, "无目标图像: Q值未达到设定值",closest_template
    for each_template in points:
        distence = np.sqrt(math.pow(abs(each_template[0]-img_center[0]),2)+ math.pow(abs(each_template[1]-img_center[1]),2))
        if distence <= temp:
            temp = distence
            closest_template[0] = each_template[0]
            closest_template[1] = each_template[1]
    closest_template[2] = max_val

    print(closest_template)
    return 0,"模板匹配成功",closest_template


if __name__ == "__main__":
    path               = os.path.join(os.curdir,"Dll\Template_Match_Dll.dll")
    dll                =  C.cdll.LoadLibrary(path)
    dll.Match.restype  = C.POINTER(C.c_double*80)
    dll.Match.argtypes = [C.c_int, C.c_int, C.POINTER(C.c_ubyte),C.c_int, C.c_int, C.POINTER(C.c_ubyte),C.c_int, C.c_double,C.c_int,C.c_int]
    for i in os.listdir("0826\-2mm"):
        print(i)
        image = cv.imread("0826\-2mm/"+i)
        image_width             = image.shape[1]
        image_hight             = image.shape[0]
        image_center            = [int(image_width/2),int(image_hight/2)]
        template = cv.imread("0826\-2mm\Template_1.bmp")
        template_width = template.shape[1]
        template_hight = template.shape[0]
        template_max = max(template_width,template_hight)+max(template_width,template_hight)

        #ret,ret_1,image_result = template_match(image,template,0.9)
        print(template_width,template_hight)
        ret,ret_1,image_result = Functions.template_dll_match(image,template,template_width*2,template_hight,dll,90)
        print(image_result)
        if ret == 0:
            template_x      = image_result[0]
            template_y      = image_result[1]
            cv.rectangle(image,(image_center[0]-20,image_center[1]-20)
                             ,(image_center[0]+20,image_center[1]+20),(0,255,0),2)
            cv.rectangle(image,(int(template_x-int(template_width/2)),int(template_y-int(template_hight/2)))
                             ,(int(template_x+int(template_width/2)),int(template_y+int(template_hight/2))),(255,255,0),2) 
            rotate_matrix = cv.getRotationMatrix2D((image_center[0],image_center[1]),-image_result[2],1)
            image_rotate = cv.warpAffine(image,rotate_matrix,(image.shape[1],image.shape[0]))
            cv.imshow("image",image)
            cv.imshow("image_rotate",image_rotate)
            cv.imshow("template",template)
            cv.waitKey(0)
            
