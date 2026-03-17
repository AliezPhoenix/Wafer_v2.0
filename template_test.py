import cv2 as cv
import numpy as np
import math
from typing import List, Tuple, Optional
import os
import time
import logging
import Functions
# 常量定义
D2R = math.pi / 180.0
R2D = 180.0 / math.pi
VISION_TOLERANCE = 0.0000001
MATCH_CANDIDATE_NUM = 5

class template_match_tool():
    def __init__(self,image:np.ndarray,template:np.ndarray,template_standard:float,logger:logging.Logger=None ):
        self.src_image = image
        self.template = template
        self.template_standard = template_standard
        self.src_image_width = self.src_image.shape[1]
        self.src_image_hight = self.src_image.shape[0]
        self.src_image_center = [int(self.src_image_width/2),int(self.src_image_hight/2)]
        self.template_width = self.template.shape[1]
        self.template_hight = self.template.shape[0]
        self.template_center = [int(self.template_width/2),int(self.template_hight/2)]
        self.src_image_prys = []
        self.template_image_prys = []

        self.match_result = []
        self.logger = logger
    def check_image_channel(self) -> bool:
        src_channel = len(self.src_image.shape)
        template_channel = len(self.template.shape)
        if src_channel == 2 and template_channel == 2: # 灰度图
            return True
        elif src_channel == 3 or template_channel == 3: # 彩色图
            if src_channel == 3:
                self.src_image = cv.cvtColor(self.src_image,cv.COLOR_BGR2GRAY)
            if template_channel == 3:
                self.template = cv.cvtColor(self.template,cv.COLOR_BGR2GRAY)
            return True
        else:
            return False
        
    
    def count_layers(self,image:np.ndarray):
        min_size = 20
        layers = 0
        width = image.shape[1]
        hight = image.shape[0]
        while (width > min_size and hight > min_size): 
            layers += 1
            hight = hight/2
            width = width/2

        return layers

    def min_angle_shift(self,image:np.ndarray):
        image_hight = image.shape[0]
        image_width = image.shape[1]
        diagonal = np.sqrt(image_hight**2+image_width**2)
        min_angle = math.atan(2/diagonal)*R2D

        return min_angle
    
    def set_src_image(self,image:np.ndarray):
        self.src_image = image

    def set_template_image(self,image:np.ndarray):
        self.template = image


    def template_match(self,image,template,template_standard):
        template_standard = template_standard
        image_width = image.shape[1]
        image_hight = image.shape[0]
        template_width = template.shape[1]
        template_hight = template.shape[0]
        points = []
        closest_template = [0,0,0,0]
        # 计算图像中心点
        img_center = (int(image_width/2), int(image_hight/2))


        match_result = cv.matchTemplate(image,template,cv.TM_CCOEFF_NORMED)
        min_val,max_val,min_loc,max_loc = cv.minMaxLoc(match_result)
        loc = np.where(match_result >= max_val-0.01)


        image = cv.cvtColor(image,cv.COLOR_GRAY2BGR)
        for i in zip(*loc[::-1]):
            points.append((i[0]+int(template_width/2),i[1]+int(template_hight/2)))
            cv.circle(image,(i[0]+int(template_width/2),i[1]+int(template_hight/2)),5,(0,255,0),-1)
        
        if len(points) == 0:
            return 1,"无目标图像",closest_template
        if max_val<template_standard:
            closest_template[2] = max_val
            return 2, "无目标图像: Q值未达到设定值",closest_template
        # 查找最靠近中心的匹配点
        min_distance = float('inf')
        closest_point = None
        for point in points:
            distance = np.sqrt((point[0] - img_center[0])**2 + (point[1] - img_center[1])**2)
            if distance < min_distance:
                min_distance = distance
                closest_point = point
        
        closest_template[0] = closest_point[0]
        closest_template[1] = closest_point[1]
        closest_template[2] = max_val
        cv.circle(image,(closest_template[0],closest_template[1]),5,(0,0,255),-1)
        cv.imshow("match",image)
        return 0,"模板匹配成功",closest_template


    def template_match_prys(self,image:np.ndarray,template:np.ndarray,template_standard:float):
        self.set_src_image(image)
        self.set_template_image(template)
        ret = self.check_image_channel()
    
        src_pry = cv.pyrUp(self.src_image)
        template_pry = cv.pyrUp(self.template)
        pry_layers_num = self.count_layers(self.template)
        for i in range(pry_layers_num+2):
            self.src_image_prys.append(src_pry)
            self.template_image_prys.append(template_pry)
            src_pry = cv.pyrDown(src_pry)
            template_pry = cv.pyrDown(template_pry)



        for i in range(pry_layers_num+1,0,-1):
            template_image = self.template_image_prys[i]
            src_image = self.src_image_prys[i]
            min_step = self.min_angle_shift(template_image)
            step_num = int(12/min_step)
            for i in range(0,step_num+1):
                angle = -6+(i*min_step)
                print(angle,min_step,i)
                template_rotate_matrix = cv.getRotationMatrix2D((template_image.shape[1]/2,template_image.shape[0]/2),angle,1)
                template_rotate = cv.warpAffine(template_image,template_rotate_matrix,(template_image.shape[1],template_image.shape[0]))
                ret,ret_content,BM = self.template_match(src_image,template_rotate,0.6)
                print(BM)
                cv.imshow("result",template_rotate)
                cv.waitKey(0)
        return 0,0,0

if __name__ == "__main__":
    template = cv.imread("Data_tempalte_match/"+"Template_1.bmp")
    for i in os.listdir("Data_tempalte_match"):
 
        img = cv.imread("Data_tempalte_match/"+i)
        template_standard = 0.8
        T_M_T = template_match_tool(img,template,template_standard)
        ret = T_M_T.check_image_channel()
        if ret:
            ret,ret_1,image_result = T_M_T.template_match_prys(img,template,0.8)