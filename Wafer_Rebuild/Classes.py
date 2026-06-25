import logging.handlers
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Functions import *
from Communicate import *
from Camera import CameraController
from MvImport.MvCameraControl_class import *
import os
import time
import shutil
import sys
import csv
import logging
sys.path.append("../DLL")

class WorkThread(QThread):
    _shut_down_signal = pyqtSignal(bool)
    def __init__(self, **kwargs):
        super().__init__()

        self.Camlow:CameraController    = kwargs.get("Camlow")  ## current_cam  = 0
        self.Camlow2:CameraController   = kwargs.get("Camlow2") ## current_cam  = 3
        self.Camhigh:CameraController   = kwargs.get("Camhigh") ## current_cam  = 1
        self.Camhigh2:CameraController  = kwargs.get("Camhigh2") ## current_cam = 2
    
        self.pixel_size         = 0   
        self.image_show_lable:QLabel= kwargs.get('image_show_lable')
        self.image_show         = cv.typing.MatLike
        self.image              = cv.typing.MatLike
        self.Signals            = Signals_Recieved_From_PLC("DT1000","DT1200")
        self.Signals_Last       = Signals_Recieved_From_PLC("DT1000","DT1200")
        self.Signals_Send       = Signals_Send_To_PLC("DT1200","DT1400")
        self.Signals_Camera_Recv = Signals_Recieved_From_PLC("DT1400","DT1500")
        self.Signals_Camera_Send= Signals_Send_To_PLC("DT1600","DT1700")
        self.display_mode       = "live"
        self.COM                = Communicate(ip = "192.168.1.5",port = 60011)
        self.map_data           = []
        
        path                    = os.path.join(os.curdir,"Dll/Template_Match_Dll.dll")
        self.dll                =  C.cdll.LoadLibrary(path)
        self.dll.Match.restype  = C.POINTER(C.c_double*80)
        self.dll.Match.argtypes = [C.c_int, C.c_int, C.POINTER(C.c_ubyte),C.c_int, C.c_int, C.POINTER(C.c_ubyte),C.c_int, C.c_double,C.c_int,C.c_int]

        self.logger:logging.Logger             = kwargs.get('logger')
    

        self.connection_ret     = 0
        self.read_map_ret       = 0
        try:
            ##重启时关闭相机初始化
            self.Camhigh.Stop_grabbing()
            self.Camhigh2.Stop_grabbing()
            self.Camlow.Stop_grabbing()
            self.Camlow2.Stop_grabbing()
            self.Camhigh.Close_device()
            self.Camhigh2.Close_device()
            self.Camlow.Close_device()
            self.Camlow2.Close_device()
        except:
            pass

        try:
            ret = self.Camlow.Open_device()
            ret = self.Camlow.Start_grabbing()
        except:
            print("低倍相机1 启动失败")
            self.Camlow = None
        try:
            ret = self.Camlow2.Open_device()
            ret = self.Camlow2.Start_grabbing()
        except :
            print("低倍相机2 启动失败")
            self.Camlow2 = None
        try:
            ret = self.Camhigh.Open_device()
            ret = self.Camhigh.Start_grabbing()
        except:
            print("高倍相机 启动失败")
            self.Camhigh = None
        try:
            ret = self.Camhigh2.Open_device()
            ret = self.Camhigh2.Start_grabbing()
        except:
            print("高倍相机2 启动失败")
            self.Camhigh2 = None
    
    def get_image(self):
        if self.Signals is None:
            return None,0
        pixel_size_low = self.Signals.decode("DT1020","DT1021","double")
        pixel_size_high = self.Signals.decode("DT1022","DT1023","double")
        current_cam = self.Signals.decode("DT1001","DT1001","int")
        if current_cam == 0:
            return self.Camlow.Get_image(),pixel_size_low
        if current_cam == 1:
            return self.Camhigh.Get_image(),pixel_size_high
        if current_cam == 2:
            return self.Camhigh2.Get_image(),pixel_size_high
        if current_cam == 3:
            return self.Camlow2.Get_image(),pixel_size_low
    
    def actions(self,action:str):
        if self.Signals is None:
            return
        signals_current         = self.Signals
        heart_beat              = signals_current.decode("DT1000","DT1000","int")
        current_cam             = signals_current.decode("DT1001","DT1001","int")    
        layout_use              = signals_current.decode("DT1003","DT1003","int")   
        target_window_width     = int(signals_current.decode("DT1006","DT1006","int")/2)
        target_window_hight     = int(signals_current.decode("DT1007","DT1007","int")/2)
        standard_line_hight     = signals_current.decode("DT1008","DT1008","int")
        template_establish      = signals_current.decode("DT1010","DT1010","int")
        template_id             = signals_current.decode("DT1011","DT1011","int")
        start_po                = signals_current.decode("DT1012","DT1012","int")
        display_size            = signals_current.decode("DT1013","DT1013","int")
        auto_focal_signal       = signals_current.decode("DT1014","DT1014","int")
        clear_display           = signals_current.decode("DT1016","DT1016","int")
        layout_save             = signals_current.decode("DT1017","DT1017","int")
        file_signal             = signals_current.decode("DT1019","DT1019","int")
        template_standard       = signals_current.decode("DT1026","DT1026","int")
        cut_path_shift_std      = signals_current.decode("DT1031","DT1031","int")
        cut_path_width_std      = signals_current.decode("DT1032","DT1032","int")
        cut_path_min_w_std      = signals_current.decode("DT1033","DT1033","int")
        cut_path_max_w_std      = signals_current.decode("DT1034","DT1034","int")
        cut_path_half_w_std     = signals_current.decode("DT1035","DT1035","int")
        cut_path_chip_max_std   = signals_current.decode("DT1036","DT1036","int")
        cut_path_c_area_std     = signals_current.decode("DT1037","DT1037","int")
        cutting_path_roi_width  = signals_current.decode("DT1038","DT1038","int") 
        cutting_path_block_hight= signals_current.decode("DT1040","DT1040","int") 
        cutting_path_roi_hight  = signals_current.decode("DT1041","DT1041","int") 
        chip_size               =(signals_current.decode("DT1046","DT1047","double"),
                                  signals_current.decode("DT1048","DT1049","double"))
        current_source          = signals_current.decode("DT1086","DT1102","file")
        current_file            = signals_current.decode("DT1103","DT1103","int")
        auto_focal_roi_x        = signals_current.decode("DT1194","DT1194","int")
        auto_focal_roi_y        = signals_current.decode("DT1195","DT1195","int")
        
        image                   = self.image.copy()
        image_width             = image.shape[1]
        image_hight             = image.shape[0]
        image_center            = [int(image_width/2),int(image_hight/2)]
        pixel_size              = self.pixel_size
        log = self.logger
        #读取切割信息
        if action == "Read_Map":
            log.info("读取切割信息")
            ftp_client:FTP
            self.map_data = []
            self.read_map_ret = 0
            ftp_ret,ftp_client = conn_ftp() 
            try:
                ret = download_file(ftp_client,"/FTP","Data_FTP",'CutLineMap.CSV')
            except:             
                ftp_client = conn_ftp()
                ret = download_file(ftp_client,"/FTP","Data_FTP",'CutLineMap.CSV')
            if ret == "NG" or ftp_ret == 0:
                log.error("CutLineMap.CSV 读取失败")
                self.read_map_ret = 1
            with open('./Data_FTP/CutLineMap.CSV',encoding = 'utf-8-sig') as f:
                for row in csv.reader(f,skipinitialspace = True):
                    try:
                        if int(row[0]) == int(row[1]) == 0:
                            continue
                        else:
                            for i in (0,len(row)-1):
                                row[i] = int(row[i])
                            self.map_data.append(row)
                    except Exception as e:
                        print("CutLineMap.CSV Error Code: ",e)
                        continue
            
        #文件操作
        if action[0:4] == "File" or action[0:6] == "Source":
            ori_source          = "Data_M\\" + signals_current.decode("DT1050","DT1066","file")
            target_source       = "Data_M\\" + signals_current.decode("DT1068","DT1084","file")
            file_ori_source     =  ori_source +"\\"+ str(signals_current.decode("DT1067","DT1067","int"))
            file_target_source  =  target_source + "\\"+ str(signals_current.decode("DT1085","DT1085","int"))
            print(file_ori_source)
            print(file_target_source)
            print(os.path.exists(file_ori_source))
            if action == "File_Copy":
                log.info("文件复制")
                if os.path.exists(file_ori_source):
                    if os.path.exists(file_target_source):
                        shutil.rmtree(file_target_source)
                    shutil.copytree(file_ori_source,file_target_source)
                else:
                    log.error("文件复制失败: 指定文件不存在")

            if action == "File_Move":
                log.info("文件移动")
                if os.path.exists(file_ori_source):
                    if os.path.exists(file_target_source):
                        shutil.rmtree(file_target_source)
                    shutil.move(file_ori_source,file_target_source)
                else:
                    log.error("文件移动失败: 指定文件不存在")

            if action == "File_Rename":
                log.info("文件重命名")
                if os.path.exists(file_ori_source):
                    os.rename(file_ori_source,file_target_source)
                else:
                    log.error("文件重命名失败: 指定文件不存在")
            
            if action == "File_Delete":
                log.info("文件删除")
                if os.path.exists(file_ori_source):
                    shutil.rmtree(file_ori_source)
                else:
                    log.error("文件删除失败: 指定文件不存在")
                
            
            if action == "Source_Create":
                log.info("创建目录")
                os.makedirs(ori_source)
            
            if action == "Source_Delete":
                log.info("删除目录")
                if os.path.exists(ori_source):
                    shutil.rmtree(ori_source)
                else:
                    log.error("目录删除失败: 指定目录不存在")
                    
            
            if action == "Source_Rename":
                log.info("目录重命名")
                if os.path.exists(ori_source):
                    os.rename(ori_source,target_source)
                else:
                    log.error("目录重命名失败: 指定目录不存在")
                

            self.Signals_Send.motify_encode("DT1219",-file_signal,"int")
        
        #使用布局
        if action == "Layout_Use":
            log.info("使用布局")
            self.image_show = cv.imread("Data_Layout/Layout_{}.bmp".format(layout_use))
            self.Signals_Send.motify_encode("DT1203",-layout_use,"int")
            
        #保存布局
        if action == "LayOut_Save":
            log.info("保存布局")
            cv.imwrite("Data_Layout/Layout_{}.bmp".format(layout_save),self.image_show)
            self.Signals_Send.motify_encode("DT1217",-layout_save,"int")
        
        #显示清除
        if action == "Clear_Display":
            log.info("显示清除")
            self.image_show = np.zeros(self.image_show.shape,np.uint8)
            self.Signals_Send.motify_encode("DT1216",-clear_display,"int")
        
        #自动对焦
        if action == "Auto_Focal":
            log.info("自动对焦")
            image_clarity = auto_focal(image)
            self.Signals_Send.motify_encode("DT1229",image_clarity,"int")
            self.Signals_Send.motify_encode("DT1214",-auto_focal_signal,"int")
        
        #保存模板图像
        if action == "Template_Establish":
            log.info("模板建立")
            template = self.image[int(image_center[1]-target_window_hight):int(image_center[1]+target_window_hight),int(image_center[0]-target_window_width):int(image_center[0]+target_window_width)]
            path = "Data_M/"+str(current_source)+"/"+str(current_file)+"/"+"Template_{}.bmp".format(template_establish)
            if os.path.exists("Data_M/"+str(current_source)+"/"+str(current_file)):
                pass
            else:
                log.error("模板注册失败,无目标位置: "+path)
                

            cv.imwrite(path,template)
            self.Signals_Send.motify_encode("DT1210",-template_establish,"int")

        #模板匹配定位
        if action == "Template_Match":
            log.info("开始模板匹配")
            pixel_size = self.pixel_size
            path = "Data_M\\"+current_source+"\\"+str(current_file)+"\\"+"Template_{}.bmp".format(template_id)
            print(path)
            template = cv.imread(path)
            ##### 未读取报警####
            if template is None:
                log.error("模板匹配失败: 无模板文件；目标位置："+ path)
                q_value = int(-9999)
                text_list = ["0","0","0","0"]
                #image = insert_text(image,text_list,start_po,0.7,(0,0,255),"template")
                self.image_show = Display_Devide(image,display_size,start_po,self.image_show,True,(0,0,255)) 
                self.image_show = insert_text(self.image_show,text_list,start_po,0.7,(0,0,255),"template")              
                self.Signals_Send.motify_encode("DT1226",q_value,"int")
                self.Signals_Send.motify_encode("DT1212",start_po,"int")
                self.Signals_Send.motify_encode("DT1213",display_size,"int")
                self.Signals_Send.motify_encode("DT1211",(9001),"int")
                return
            
            template_width = template.shape[1]
            template_hight = template.shape[0]
            template_max = max(template_width,template_hight)+max(template_width,template_hight)

            if signals_current.decode("DT1002","DT1002","int") == 3:
                log.info("执行螺旋检查")
                border_color_ng = (0,255,0)
                border_color_ok = (0,0,255)
            else:
                border_color_ng = (0,0,255)
                border_color_ok = (0,255,0)
            
            #### 芯片尺寸的1.5倍作为roi
            #roi_x = int(chip_size[0]/pixel_size/100*1.5)  ##chip_size(0.1um)  pixel_size(1nm)  scale = 1.5
            #roi_y = int(chip_size[1]/pixel_size/100*1.5)

            roi_x = template_max*2
            roi_y = template_max
            if roi_x >400 or roi_y>400:
                roi_x = 400
                roi_y = 400
            
            #### ret = 0 模板匹配成功
            #### ret = 1 模板匹配失败
            #### ret = 2 Q值未达到设定值
            if current_cam == 0 or current_cam == 3:
                ret,ret_content,result_template = template_dll_match(image,template,roi_x,roi_y,self.dll,template_standard)
            if current_cam == 1 or current_cam == 2:
                ret,ret_content,result_template = template_match(image,template,template_standard)
            
            print("ret_content: ",ret_content)
            print("result_template: ",result_template)
            print("roi_x: ",roi_x)
            print("roi_y: ",roi_y)
            if ret != 0 :
                log.error("模板匹配失败:" + ret_content)
                q_value = int(round(result_template[2],5)*100)
                text_list = [str(q_value),"0","0","0"]
            
                self.image_show = Display_Devide(image,display_size,start_po,self.image_show,True,border_color_ng) 
                self.image_show = insert_text(self.image_show,text_list,start_po,0.7,border_color_ng,"template")              
                cv.imwrite("Data_failed\\template_mathc_fail{}_{}.bmp".format(heart_beat,ret),image)

                self.Signals_Send.motify_encode("DT1226",q_value,"int")
                self.Signals_Send.motify_encode("DT1212",start_po,"int")
                self.Signals_Send.motify_encode("DT1213",display_size,"int")
                self.Signals_Send.motify_encode("DT1211",(-template_id),"int")
            else:
                template_value  = result_template[2]
                angel           = result_template[3]
                template_x      = result_template[0]
                template_y      = result_template[1]
                x_shift         = int(template_x-image_center[0])
                x_shift_pixel   = int(x_shift*pixel_size/100)
                y_shift         = -int(template_y-image_center[1])
                y_shift_pixel   = int(y_shift*pixel_size/100)
                q_value         = int(round(template_value,5)*100)
                angel_value     = int(round(angel,6)*1000)
                text_list       = [str(q_value),str(angel_value),str(x_shift),str(y_shift)]
                cv.rectangle(image,(image_center[0]-target_window_width,image_center[1]-target_window_hight)
                             ,(image_center[0]+target_window_width,image_center[1]+target_window_hight),(0,255,0),2)
                cv.rectangle(image,(int(template_x-int(template_width/2)),int(template_y-int(template_hight/2)))
                             ,(int(template_x+int(template_width/2)),int(template_y+int(template_hight/2))),(255,255,0),2)              
                self.image_show = Display_Devide(image,display_size,start_po,self.image_show,True,border_color_ok)
                self.image_show = insert_text(self.image_show,text_list,start_po,0.7,border_color_ok,"template") 
                self.Signals_Send.motify_encode("DT1212",start_po,"int")
                self.Signals_Send.motify_encode("DT1213",display_size,"int")
                self.Signals_Send.motify_encode("DT1220",x_shift_pixel,"int") 
                self.Signals_Send.motify_encode("DT1222",y_shift_pixel,"int")
                self.Signals_Send.motify_encode("DT1224",angel_value,"int") 
                self.Signals_Send.motify_encode("DT1226",q_value,"int")
                self.Signals_Send.motify_encode("DT1227",x_shift,"int")
                self.Signals_Send.motify_encode("DT1228",y_shift,"int")
                self.Signals_Send.motify_encode("DT1211",(-template_id),"int")
                log.info("模板匹配成功")
            log.info("模板匹配结束")
            return 
        
        #切痕检查
        if action == "Cutting_Path_Detection":
            log.info("开始切痕检查")

            cutting_path_roi_width =int((10-cutting_path_roi_width)*(image_width/20))
            cutting_path_roi_hight = int(cutting_path_roi_hight/2)
            
            if cutting_path_roi_hight <= 100 and cutting_path_roi_hight>0:
                log.warning("切痕检查: 切痕roi高度过小,当前设定值为{}mm，最小值为:{}mm ".format((cutting_path_roi_hight*2*pixel_size/1000000),(100*2*pixel_size/1000000)))
                cutting_path_roi_hight = 100
                ret = 1
            if cutting_path_roi_hight == 0:
                cutting_path_roi_hight = int(standard_line_hight/2)+10
                
            if cutting_path_roi_width >500:
                cutting_path_roi_width = 500 

            image_check = image[image_center[1]-cutting_path_roi_hight:image_center[1]+cutting_path_roi_hight,
                                image_center[0]-cutting_path_roi_width:image_center[0]+cutting_path_roi_width]
            if cutting_path_block_hight >0:
                image_check = Center_block(image_check,cutting_path_block_hight)
            else:
                image_check = Center_block(image_check,0)
            
            ret,ret_content,result_image,result = cutting_path_detection(image_check)
            if ret != 0:
                print("cutting_path_roi_width:",cutting_path_roi_width,"cutting_path_roi_hight: ",cutting_path_roi_hight)
                cv.imwrite("Data_failed\\failed_{}.bmp".format(time.time()),image_check)
                log.error("切痕检查失败: "+ret_content)
                text_color = (0,0,255)
                template_id = -template_id
                q_value = 0
            else:
                log.info("切痕检查成功")
                template_id = -template_id
                text_color = (0,255,0)
                q_value = 100
            text_list = [str(result[0]*self.pixel_size/1000)+"um",
                            str(result[1]*self.pixel_size/1000)+"um",
                            str(result[2]*self.pixel_size/1000)+"um",
                            str(result[3]*self.pixel_size/1000)+"um",
                            str(result[4]*self.pixel_size/1000)+"um",
                            str(result[5])]
            
            check_list = [cut_path_shift_std,
                          cut_path_width_std,
                          cut_path_max_w_std,
                          cut_path_min_w_std,
                          cut_path_chip_max_std,
                          cut_path_c_area_std]
            image[image_center[1]-cutting_path_roi_hight:image_center[1]+cutting_path_roi_hight,image_center[0]-cutting_path_roi_width:image_center[0]+cutting_path_roi_width] = result_image
            self.image_show = Display_Devide(image,display_size,start_po,self.image_show,False,(0,0,0))
            self.image_show = insert_text(self.image_show,text_list,start_po,1,text_color,"cutting_path")  
            
            self.Signals_Send.motify_encode("DT1211",template_id,"int")
            self.Signals_Send.motify_encode("DT1212",start_po,"int")
            self.Signals_Send.motify_encode("DT1213",display_size,"int")
            self.Signals_Send.motify_encode("DT1230",q_value,"int")
            self.Signals_Send.motify_encode("DT1231",result[0],"int")
            self.Signals_Send.motify_encode("DT1232",result[1],"int")
            self.Signals_Send.motify_encode("DT1233",result[2],"int")
            self.Signals_Send.motify_encode("DT1234",result[3],"int")
            self.Signals_Send.motify_encode("DT1235",result[4],"int")
            self.Signals_Send.motify_encode("DT1236",result[5],"int")
            
            pass
       
        #单张显示
        if action == "Take_One_photo":
            log.info("单张显示")
            image = self.image.copy()
            image = Mark_image(image,
                                    self.Signals.decode("DT1005","DT1005","int"),
                                    self.Signals.decode("DT1006","DT1006","int"),
                                    self.Signals.decode("DT1007","DT1007","int"),
                                    self.Signals.decode("DT1008","DT1008","int"),
                                    self.Signals.decode("DT1009","DT1009","int")
                                    )
            self.image_show  = Display_Devide(image,display_size,start_po,self.image_show,False,(255,255,255))
            self.Signals_Send.motify_encode("DT1211",-template_id,"int")
    
        #相机参数设置
        if action == "Set_Camera_Parameters":
            ret, self.Signals_Camera_Recv = self.COM.get_signals("DT1400","DT1500")
            explosure_time = 0
            gain = 0
            gamma = 0
            if current_cam == 0:## CAM_LOW
                explosure_time = self.Signals_Camera_Recv.decode("DT1400","DT1401","double")
                gain = self.Signals_Camera_Recv.decode("DT1402","DT1402","int")/10
                gamma = self.Signals_Camera_Recv.decode("DT1404","DT1404","int")/10
                ret,ret_content = self.Camlow.Set_parameter(explosure_time, "ExposureTime")
                ret,ret_content = self.Camlow.Set_parameter(gain, "Gain")
                ret,ret_content = self.Camlow.Set_parameter(gamma, "Gamma")
                if ret == 0:
                    self.Signals_Camera_Send.motify_encode("DT1600",explosure_time,"int")
                    self.Signals_Camera_Send.motify_encode("DT1602",gain*10,"int")
                    self.Signals_Camera_Send.motify_encode("DT1604",gamma*10,"int")

            if current_cam == 1:## CAM_hgih
                explosure_time = self.Signals_Camera_Recv.decode("DT1410","DT1411","double")
                gain = self.Signals_Camera_Recv.decode("DT1412","DT1412","int")/10
                gamma = self.Signals_Camera_Recv.decode("DT1414","DT1414","int")/10
                ret,ret_content = self.Camhigh.Set_parameter(explosure_time, "ExposureTime")
                ret,ret_content = self.Camhigh.Set_parameter(gain, "Gain")
                ret,ret_content = self.Camhigh.Set_parameter(gamma, "Gamma")
                if ret == 0:
                    self.Signals_Camera_Send.motify_encode("DT1610",explosure_time,"int")
                    self.Signals_Camera_Send.motify_encode("DT1612",gain*10,"int")
                    self.Signals_Camera_Send.motify_encode("DT1614",gamma*10,"int")
            
            if current_cam == 2:## CAM_high2
                explosure_time = self.Signals_Camera_Recv.decode("DT1420","DT1421","double")
                gain = self.Signals_Camera_Recv.decode("DT1422","DT1422","int")/10
                gamma = self.Signals_Camera_Recv.decode("DT1424","DT1424","int")/10
                ret,ret_content = self.Camhigh2.Set_parameter(explosure_time, "ExposureTime")
                ret,ret_content = self.Camhigh2.Set_parameter(gain, "Gain")
                ret,ret_content = self.Camhigh2.Set_parameter(gamma, "Gamma")
                if ret == 0:
                    self.Signals_Camera_Send.motify_encode("DT1620",explosure_time,"int")
                    self.Signals_Camera_Send.motify_encode("DT1622",gain*10,"int")
                    self.Signals_Camera_Send.motify_encode("DT1624",gamma*10,"int")
            
            if current_cam == 3:## CAM_low2
                explosure_time = self.Signals_Camera_Recv.decode("DT1430","DT1431","double")
                gain = self.Signals_Camera_Recv.decode("DT1432","DT1432","int")/10
                gamma = self.Signals_Camera_Recv.decode("DT1434","DT1434","int")/10
                ret,ret_content = self.Camlow.Set_parameter(explosure_time, "ExposureTime")
                ret,ret_content = self.Camlow.Set_parameter(gain, "Gain")
                ret,ret_content = self.Camlow.Set_parameter(gamma, "Gamma")
                if ret == 0:
                    self.Signals_Camera_Send.motify_encode("DT1630",explosure_time,"int")
                    self.Signals_Camera_Send.motify_encode("DT1632",gain*10,"int")
                    self.Signals_Camera_Send.motify_encode("DT1634",gamma*10,"int")
            
            self.Signals_Send.motify_encode("DT1359",-1,"int") 

        if action == "Get_Camera_Parameters":
            if current_cam == 0:## CAM_LOW
                ret,ret_content,explosure_time = self.Camlow.Get_parameter("ExposureTime")
                ret,ret_content,gain = self.Camlow.Get_parameter("Gain")
                ret,ret_content,gamma = self.Camlow.Get_parameter("Gamma")
                if ret == 0:
                    self.Signals_Camera_Send.motify_encode("DT1600",explosure_time,"int")
                    self.Signals_Camera_Send.motify_encode("DT1602",gain*10,"int")
                    self.Signals_Camera_Send.motify_encode("DT1604",gamma*10,"int")

            if current_cam == 1:## CAM_hgih
                ret,ret_content,explosure_time = self.Camhigh.Get_parameter("ExposureTime")
                ret,ret_content,gain = self.Camhigh.Get_parameter("Gain")
                ret,ret_content,gamma = self.Camhigh.Get_parameter("Gamma")
                if ret == 0:
                    self.Signals_Camera_Send.motify_encode("DT1610",explosure_time,"int")
                    self.Signals_Camera_Send.motify_encode("DT1612",gain*10,"int")
                    self.Signals_Camera_Send.motify_encode("DT1614",gamma*10,"int")
            
            if current_cam == 2:## CAM_high2
                ret,ret_content,explosure_time = self.Camhigh2.Get_parameter(explosure_time, "ExposureTime")
                ret,ret_content,gain= self.Camhigh2.Get_parameter(gain, "Gain")
                ret,ret_content,gamma = self.Camhigh2.Get_parameter(gamma, "Gamma")
                if ret == 0:
                    self.Signals_Camera_Send.motify_encode("DT1620",explosure_time,"int")
                    self.Signals_Camera_Send.motify_encode("DT1622",gain*10,"int")
                    self.Signals_Camera_Send.motify_encode("DT1624",gamma*10,"int")
            
            if current_cam == 3:## CAM_low2
                ret,ret_content,explosure_time = self.Camlow.Get_parameter("ExposureTime")
                ret,ret_content,gain = self.Camlow.Get_parameter("Gain")
                ret,ret_content,gamma = self.Camlow.Get_parameter("Gamma")
                if ret == 0:
                    self.Signals_Camera_Send.motify_encode("DT1630",explosure_time,"int")
                    self.Signals_Camera_Send.motify_encode("DT1632",gain*10,"int")
                    self.Signals_Camera_Send.motify_encode("DT1634",gamma*10,"int")

            self.Signals_Send.motify_encode("DT1359",-2,"int") 
    def display_image(self,temp,border_on_or_off,border_color):
        mode = self.display_mode
        log = self.logger
        size = 0
        start_po = 0
        live_size = self.Signals.decode("DT1004","DT1004","int")
        if mode == "live":
            self.image = Mark_image(self.image,
                                    self.Signals.decode("DT1005","DT1005","int"),
                                    self.Signals.decode("DT1006","DT1006","int"),
                                    self.Signals.decode("DT1007","DT1007","int"),
                                    self.Signals.decode("DT1008","DT1008","int"),
                                    self.Signals.decode("DT1009","DT1009","int")
                                    )
            if live_size == 0:
                size = 0
                start_po = 0
            if live_size == 1:
                size = 1
                start_po = 57
            if live_size == 16:
                size = 16
                start_po = 33
            if live_size == 64:
                temp = True 
                start_po = 0
            else:
                
                self.image_show = Display_Devide(self.image, 
                                                    size, 
                                                    start_po,
                                                    self.image_show, 
                                                    border_on_or_off, 
                                                    border_color)
            if temp:
                bytes_per_line = self.image.shape[2]*self.image.shape[1]
                image_pix_map = QImage(self.image.data, self.image.shape[1], self.image.shape[0],bytes_per_line,QImage.Format_BGR888)                       
            else:
                bytes_per_line = self.image_show.shape[2]*self.image_show.shape[1]
                image_pix_map = QImage(self.image_show.data, self.image_show.shape[1], self.image_show.shape[0],bytes_per_line,QImage.Format_BGR888)  
                
        if mode == "animation":
            if self.map_data == []:
                self.image_show = np.zeros(self.image_show.shape,np.uint8)
                cv.putText(self.image_show,"无法显示：读取切割信息失败",(300,580),cv.FONT_HERSHEY_TRIPLEX,5,(0,0,255),3)
                bytes_per_line = self.image_show.shape[2]*self.image_show.shape[1]
                image_pix_map = QImage(self.image_show.data, self.image_show.shape[1], self.image_show.shape[0],bytes_per_line,QImage.Format_BGR888)

            current_path_sp = [0,0]
            current_path_sp[0] = self.Signals.decode("DT1181","DT1181","int")-1
            current_path_sp[1] = self.Signals.decode("DT1182","DT1182","int")-1
            current_x = self.Signals.decode("DT1180","DT1180","int")
            current_selected = self.Signals.decode("DT1183","DT1183","int")
            zoom_size = self.Signals.decode("DT1184","DT1184","int")
            scale = 1000/self.Signals.decode("DT1171","DT1171","int")
            wafer_size_x = self.Signals.decode("DT1175","DT1175","int")
            wafer_size_y = self.Signals.decode("DT1176","DT1176","int")
            cutting_status = self.Signals.decode("DT1177","DT1177","int")

            if self.Signals.decode("DT1174","DT1174","int") == 1:
                shape = "Square"
                image_size = [int(wafer_size_y*scale),int(wafer_size_x*scale)]
            else:
                shape = "Circle" 
                diameter = abs(self.map_data[0][0])+abs(self.map_data[-1][0])    
                image_size = [diameter,diameter]
            
            if current_x > 1600:
                current_x = current_x - 65536
            current_x = int(500+(current_x*scale))
            if current_selected > len(self.map_data):
                current_selected = len(self.map_data)-1
            
            image_animation,self.map_data = Animation_Y_POS(image_size,self.map_data,
                                                            current_path_sp,current_x,current_selected,zoom_size,
                                                            cutting_status,shape,scale)
            
            bytes_per_line = image_animation.shape[2]*image_animation.shape[1]
            image_pix_map = QImage(image_animation.data, image_animation.shape[1], image_animation.shape[0],bytes_per_line,QImage.Format_BGR888)
        
            self.Signals_Send.motify_encode("DT1383",current_selected,"int")
            self.Signals_Send.motify_encode("DT1384",zoom_size,"int")
        self.image_show_lable.setPixmap(QPixmap.fromImage(image_pix_map))
        QApplication.processEvents()
    
    def run(self):          
        ret = self.COM.connect()
        log = self.logger
        self.connection_ret, self.Signals = self.COM.get_signals("DT1000","DT1200")
        self.connection_ret, self.Signals_Last = self.COM.get_signals("DT1000","DT1200")
        self.image,self.pixel_size= self.get_image()
        
        
        if self.image is not None:
            self.actions("Read_Map")
            self.image_show = self.image.copy()
            self.image_show = cv.cvtColor(self.image_show,cv.COLOR_GRAY2BGR)
        else:
            log.error("图像获取失败")
        log.info("切割机视觉软件启动")
        while(True):
            #start_time = time.time()
            self.connection_ret , self.Signals = self.COM.get_signals("DT1000","DT1200")
            self.image,self.pixel_size= self.get_image()
            if (self.connection_ret == 1) or (self.read_map_ret == 1) or (self.image is None) or (ret == 0):
                log.error("线程断开退出")
                self._shut_down_signal.emit(True)
                break 
            heart_beat = self.Signals.decode("DT1000","DT1000","int")
            current_cam = self.Signals.decode("DT1001","DT1001","int")
            current_layout = self.Signals.decode("DT1003","DT1003","int")
            layout_save = self.Signals.decode("DT1017","DT1017","int")
            line_map_flag = self.Signals.decode("DT1188","DT1188","int")
            image_clear = self.Signals.decode("DT1016","DT1016","int")
            template_establish = self.Signals.decode("DT1010","DT1010","int")
            detection = self.Signals.decode("DT1011","DT1011","int")
            auto_focal = self.Signals.decode("DT1014","DT1014","int")
            file_operate = self.Signals.decode("DT1019","DT1019","int")
            
            image_angle_low1 = self.Signals.decode("DT1155","DT1155","int")
            image_angle_low2 = self.Signals.decode("DT1158","DT1158","int")
            image_angle_high1 = self.Signals.decode("DT1156","DT1156","int")
            image_angle_high_2 = self.Signals.decode("DT1157","DT1157","int")
            camera_parameter_flag = self.Signals.decode("DT1159","DT1159","int")
            
            image_angle_list = [image_angle_low1,image_angle_high1,image_angle_high_2,image_angle_low2]

            self.image = image_preprocess(image = self.image, 
                                      image_angle_list = image_angle_list, 
                                      current_cam = current_cam)

            
            if heart_beat %5 == 0 and heart_beat!= self.Signals_Last.decode("DT1000","DT1000","int"):
                print("Running...")

            if camera_parameter_flag != self.Signals_Last.decode("DT1159","DT1159","int"):
                log.info("相机参数设置触发")
                if camera_parameter_flag == 1 :
                    self.actions("Set_Camera_Parameters")
                elif camera_parameter_flag == 2:
                    self.actions("Get_Camera_Parameters")
            if current_layout != self.Signals_Last.decode("DT1003","DT1003","int"):
                log.info("切换布局触发")
                if current_layout == 0:
                    self.display_mode = "live"
                elif current_layout == 5:
                    self.display_mode = "animation"
                elif current_layout >-1:
                    self.actions("Layout_Use")
                    self.display_mode = "live"
                print(current_layout,self.display_mode)
            
            if line_map_flag != self.Signals_Last.decode("DT1188","DT1188","int"):
                self.actions("Read_Map")
                log.info("读取map文件触发")
                time.sleep(0.2)

            if layout_save != self.Signals_Last.decode("DT1017","DT1017","int"):
                if layout_save>-1:
                    self.actions("LayOut_Save")

            if image_clear != self.Signals_Last.decode("DT1016","DT1016","int"):
                if image_clear == 1:
                    self.actions("Clear_Display")
                if image_clear == 0:
                    self.Signals_Send.motify_encode("DT1216",0,"int")

            if template_establish != self.Signals_Last.decode("DT1010","DT1010","int"):                
                if template_establish >0:
                    self.actions("Template_Establish")
                if template_establish == 0:
                    self.Signals_Send.motify_encode("DT1210",0,"int")

            if detection != self.Signals_Last.decode("DT1011","DT1011","int"):         
                if detection <= 0:
                    self.Signals_Send.motify_encode("DT1211",0,"int") 
                if detection >0:   
                    if detection <100:
                        self.actions("Template_Match")
                    if detection == 100:
                        self.actions("Cutting_Path_Detection")
                    if detection == 110:
                        self.actions("Take_One_photo")
                     
            if auto_focal != self.Signals_Last.decode("DT1014","DT1014","int"):
                if auto_focal == 1:
                    self.actions("Auto_Focal")
                if auto_focal == 0:
                    self.Signals_Send.motify_encode("DT1214",0,"int")

            if file_operate != self.Signals_Last.decode("DT1019","DT1019","int"):
                if file_operate == 1:
                    self.actions("File_Copy")
                if file_operate == 2:
                    self.actions("File_Move")
                if file_operate == 3:
                    self.actions("File_Rename")
                if file_operate == 4:
                    self.actions("File_Delete")
                if file_operate == 6:
                    self.actions("Source_Create")
                if file_operate == 7:
                    self.actions("Source_Delete")
                if file_operate == 8:
                    self.actions("Source_Rename")
                if file_operate == 0:
                    self.Signals_Send.motify_encode("DT1219",0,"int")
            self.Signals_Send.signal_refresh(self.Signals)   
            self.connection_ret = self.COM.send_signals(self.Signals_Send,"DT1200","DT1400")
            if self.connection_ret == 1 or self.read_map_ret == 1:
                log.error("线程断开退出")
                self._shut_down_signal.emit(True)    
                break 
            self.display_image(False,False,[0,0,0])
            self.Signals_Last = self.Signals
            


class Supervise(QThread):
    _restart_signal = pyqtSignal(bool)
    def __init__(self, **kwargs):
        super().__init__()
        self.target_thread:QThread = kwargs.get("target_thread")
        self.main_ui:QDialog = kwargs.get("main_ui")
    def restart_target_thread(self):
        self._restart_signal.emit(True)
        
    def run(self):
        while (True):
            print("Supervise_Running...")
            if self.target_thread.isRunning():
                time.sleep(5)
            else:
                print("Restart Work Thread")
                self.target_thread.quit()
                self.restart_target_thread()
