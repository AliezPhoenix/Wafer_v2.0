import numpy as np
import time
from PIL import Image
from ctypes import *
from MvImport.MvCameraControl_class import *

class CameraController():

    def __init__(self,obj_cam,netIp,deviceIp,b_open_device=False,b_start_grabbing = False,h_thread_handle=None,\
                b_thread_closed=False,st_frame_info=None,b_exit=False,b_save_bmp=False,b_save_jpg=False,buf_save_image=None,\
                n_save_image_size=0,n_win_gui_id=0,frame_rate=0,exposure_time=0,gain=0):

        self.obj_cam:MvCamera= obj_cam
        self.b_open_device = b_open_device
        self.netIp = netIp
        self.deviceIp = deviceIp
        self.b_start_grabbing = b_start_grabbing 
        self.b_thread_closed = b_thread_closed
        self.st_frame_info = st_frame_info
        self.b_exit = b_exit
        self.b_save_bmp = b_save_bmp
        self.b_save_jpg = b_save_jpg
        self.buf_save_image = buf_save_image
        self.h_thread_handle = h_thread_handle
        self.n_win_gui_id = n_win_gui_id
        self.n_save_image_size = n_save_image_size
        self.b_thread_closed
        self.frame_rate = frame_rate
        self.exposure_time = exposure_time
        self.gain = gain

    def To_hex_str(self,num):
        chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
        hexStr = ""
        if num < 0:
            num = num + 2**32
        while num >= 16:
            digit = num % 16
            hexStr = chaDic.get(digit, str(digit)) + hexStr
            num //= 16
        hexStr = chaDic.get(num, str(num)) + hexStr   
        return hexStr

    def Open_device(self):
        if False == self.b_open_device:
            stDevInfo = MV_CC_DEVICE_INFO()
            stGigEDev = MV_GIGE_DEVICE_INFO()
            deviceIpList = self.deviceIp.split('.')
            stGigEDev.nCurrentIp = (int(deviceIpList[0]) << 24) | (int(deviceIpList[1]) << 16) | (int(deviceIpList[2]) << 8) | int(deviceIpList[3])
            netIpList = self.netIp.split('.')
            stGigEDev.nNetExport =  (int(netIpList[0]) << 24) | (int(netIpList[1]) << 16) | (int(netIpList[2]) << 8) | int(netIpList[3])
            stDevInfo.nTLayerType = MV_GIGE_DEVICE
            stDevInfo.SpecialInfo.stGigEInfo = stGigEDev
            self.cam = MvCamera()
            g_bExit = False
            ret = self.obj_cam.MV_CC_CreateHandle(stDevInfo)
            if ret != 0:
                self.obj_cam.MV_CC_DestroyHandle()
                print('show error','create handle fail! ret = '+ self.To_hex_str(ret))
                return ret

            ret = self.obj_cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
            if ret != 0:
                print('show error','open device fail! ret = '+ self.To_hex_str(ret))
                return ret
            print ("open device successfully!")
            self.b_open_device = True
            self.b_thread_closed = False

            # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
            if stDevInfo.nTLayerType == MV_GIGE_DEVICE:
                nPacketSize = self.obj_cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.obj_cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
                    if ret != 0:
                        print ("warning: set packet size fail! ret[0x%x]" % ret)
                else:
                    print ("warning: set packet size fail! ret[0x%x]" % nPacketSize)

            stBool = c_bool(False)
            ret =self.obj_cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
            if ret != 0:
                print ("get acquisition frame rate enable fail! ret[0x%x]" % ret)

            # ch:设置触发模式为off | en:Set trigger mode as off
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print ("set trigger mode fail! ret[0x%x]" % ret)
            return 0

    def Start_grabbing(self):
        if False == self.b_start_grabbing and True == self.b_open_device:
            self.b_exit = False
            ret = self.obj_cam.MV_CC_StartGrabbing()
            if ret != 0:
                print('show error','start grabbing fail! ret = '+ self.To_hex_str(ret))
                return
            self.b_start_grabbing = True
            print ("start grabbing successfully!")

    def Stop_grabbing(self):
        if True == self.b_start_grabbing and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_StopGrabbing()
            if ret != 0:
                print('show error','stop grabbing fail! ret = '+self.To_hex_str(ret))
                return
            print ("stop grabbing successfully!")
            self.b_start_grabbing = False
            self.b_exit  = True      

    def Close_device(self):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_CloseDevice()
            if ret != 0:
                print('show error','close deivce fail! ret = '+self.To_hex_str(ret))
                return
                
        # ch:销毁句柄 | Destroy handle
        self.obj_cam.MV_CC_DestroyHandle()
        self.b_open_device = False
        self.b_start_grabbing = False
        self.b_exit  = True
        print ("close device successfully!")

    def Set_trigger_mode(self,strMode):
        if True == self.b_open_device:
            if "continuous" == strMode: 
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode",0)
                if ret != 0:
                    print('show error','set triggermode fail! ret = '+self.To_hex_str(ret))
            if "triggermode" == strMode:
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode",1)
                if ret != 0:
                    print('show error','set triggermode fail! ret = '+self.To_hex_str(ret))
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource",7)
                if ret != 0:
                    print('show error','set triggersource fail! ret = '+self.To_hex_str(ret))

    def Trigger_once(self,nCommand):
        if True == self.b_open_device:
            if 1 == nCommand: 
                ret = self.obj_cam.MV_CC_SetCommandValue("TriggerSoftware")
                if ret != 0:
                    print('show error','set triggersoftware fail! ret = '+self.To_hex_str(ret))

    def Get_parameter(self,parameter_type = None):
        ret = 0
        st_float_param = MVCC_FLOATVALUE()
        memset(byref(st_float_param), 0, sizeof(MVCC_FLOATVALUE))
        if parameter_type is None: 
            return 1, "Please Enter a Parameter Type"
        if self.b_open_device == False:
            return 1, "Please Open Device First"
        
        if parameter_type == "ExposureTime":
            ret = self.obj_cam.MV_CC_GetFloatValue("ExposureTime", st_float_param)
            if ret != 0:
                return ret,'show error','get exposure time fail! ret = '+self.To_hex_str(ret), st_float_param.fCurValue
            else:
                return ret, 'get exposure time success', 'ExposureTime = '+ st_float_param.fCurValue
        elif parameter_type == "Gain":
            ret = self.obj_cam.MV_CC_GetFloatValue("Gain", st_float_param)
            if ret != 0:
                return ret,'show error','get gain fail! ret = '+self.To_hex_str(ret), st_float_param.fCurValue
            else:
                return ret, 'get gain success', 'Gain = '+ st_float_param.fCurValue
        elif parameter_type == "Gamma":
            ret = self.obj_cam.MV_CC_GetFloatValue("Gamma", st_float_param)
            if ret != 0:
                return ret,'show error','get gamma fail! ret = '+self.To_hex_str(ret), st_float_param.fCurValue
            else:
                return ret, 'get gamma success', 'Gamma = '+ st_float_param.fCurValue
        elif parameter_type == "AcquisitionFrameRate":
            ret = self.obj_cam.MV_CC_GetFloatValue("AcquisitionFrameRate", st_float_param)
            if ret != 0:
                return ret,'show error','get AcquisitionFrameRate fail! ret = '+self.To_hex_str(ret), st_float_param.fCurValue
            else:
                return ret, 'get AcquisitionFrameRate success', 'AcquisitionFrameRate = '+ st_float_param.fCurValue

        # if True == self.b_open_device:
        #     stFloatParam_FrameRate =  MVCC_FLOATVALUE()
        #     memset(byref(stFloatParam_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
        #     stFloatParam_exposureTime = MVCC_FLOATVALUE()
        #     memset(byref(stFloatParam_exposureTime), 0, sizeof(MVCC_FLOATVALUE))
        #     stFloatParam_gain = MVCC_FLOATVALUE()
        #     memset(byref(stFloatParam_gain), 0, sizeof(MVCC_FLOATVALUE))
        #     ret = self.obj_cam.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatParam_FrameRate)
        #     if ret != 0:
        #         print('show error','get acquistion frame rate fail! ret = '+self.To_hex_str(ret))
        #     self.frame_rate = stFloatParam_FrameRate.fCurValue
        #     ret = self.obj_cam.MV_CC_GetFloatValue("ExposureTime", stFloatParam_exposureTime)
        #     if ret != 0:
        #         print('show error','get exposure time fail! ret = '+self.To_hex_str(ret))
        #     self.exposure_time = stFloatParam_exposureTime.fCurValue
        #     ret = self.obj_cam.MV_CC_GetFloatValue("Gain", stFloatParam_gain)
        #     if ret != 0:
        #         print('show error','get gain fail! ret = '+self.To_hex_str(ret))
        #     self.gain = stFloatParam_gain.fCurValue
        #     print('show info','get parameter success!')

    def Set_parameter(self,value =0 ,parameter_type = None):
        ret = 0
        if parameter_type is None:
            return 1, "Please Enter a Parameter Type"
        if self.b_open_device == False:
            return 1, "Please Open Device First"
        else:
            if parameter_type == 'AcquisitionFrameRate':
                ret = self.obj_cam.MV_CC_SetFloatValue("AcquisitionFrameRate", value)
                if ret != 0:
                    print('show error','set parameter fail! ret = '+self.To_hex_str(ret))
            if parameter_type == 'ExposureTime':
                ret = self.obj_cam.MV_CC_SetFloatValue("ExposureTime",float(value))
                if ret != 0:
                    print('show error','set exposure time fail! ret = '+self.To_hex_str(ret))
            if parameter_type == 'Gain':
                ret = self.obj_cam.MV_CC_SetFloatValue("Gain",float(value))
                if ret != 0:
                    print('show error','set gain fail! ret = '+self.To_hex_str(ret))
            if parameter_type == "Gamma":
                ret = self.obj_cam.MV_CC_SetFloatValue("Gamma",float(value))
                if ret != 0:
                    print('show error','set gamma fail! ret = '+self.To_hex_str(ret))
        return ret,"Success"

    # def Work_thread(self):
    def Get_image(self):
        stOutFrame = MV_FRAME_OUT()  
        img_buff = None
        buf_cache = None
        numArray = None
        retry_counter = 0
        while True:
            ret = self.obj_cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
            if 0 == ret:
                if None == buf_cache:
                    buf_cache = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
                #获取到图像的时间开始节点获取到图像的时间开始节点
                self.st_frame_info = stOutFrame.stFrameInfo
                cdll.msvcrt.memcpy(byref(buf_cache), stOutFrame.pBufAddr, self.st_frame_info.nFrameLen)
                # print ("get one frame: Width[%d], Height[%d], nFrameNum[%d]"  % (self.st_frame_info.nWidth, self.st_frame_info.nHeight, self.st_frame_info.nFrameNum))
                self.n_save_image_size = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3 + 2048
                if img_buff is None:
                    img_buff = (c_ubyte * self.n_save_image_size)()
                
                if True == self.b_save_jpg:
                    self.Save_jpg(buf_cache) #ch:保存Jpg图片 | en:Save Jpg
                if True == self.b_save_bmp:
                    self.Save_Bmp(buf_cache) #ch:保存Bmp图片 | en:Save Bmp
            else:
                retry_counter += 1
                print("no data, nret = "+self.To_hex_str(ret), "\n retry_counter = "+str(retry_counter))
                if retry_counter > 10:
                    retry_counter = 0
                    return None
                continue

            #转换像素结构体赋值
            stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
            memset(byref(stConvertParam), 0, sizeof(stConvertParam))
            stConvertParam.nWidth = self.st_frame_info.nWidth
            stConvertParam.nHeight = self.st_frame_info.nHeight
            stConvertParam.pSrcData = cast(buf_cache, POINTER(c_ubyte))
            stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
            stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType 

            mode = None     # array转为Image图像的转换模式
            # RGB8直接显示
            if PixelType_Gvsp_RGB8_Packed == self.st_frame_info.enPixelType :
                numArray = CameraController.Color_numpy(self,buf_cache,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                mode = "RGB"

            # Mono8直接显示
            elif PixelType_Gvsp_Mono8 == self.st_frame_info.enPixelType :
                numArray = CameraController.Mono_numpy(self,buf_cache,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                mode = "L"

            # 如果是彩色且非RGB则转为RGB后显示
            elif self.Is_color_data(self.st_frame_info.enPixelType):
                nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
                stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize
                time_start=time.time()
                ret = self.obj_cam.MV_CC_ConvertPixelType(stConvertParam)
                time_end=time.time()
                # print('MV_CC_ConvertPixelType to RGB:',time_end - time_start) 
                if ret != 0:
                    print('show error','convert pixel fail! ret = '+self.To_hex_str(ret))
                    continue
                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                numArray = CameraController.Color_numpy(self,img_buff,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                mode = "RGB"
                
            # 如果是黑白且非Mono8则转为Mono8后显示
            elif self.Is_mono_data(self.st_frame_info.enPixelType):
                nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight
                stConvertParam.enDstPixelType = PixelType_Gvsp_Mono8
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize
                time_start=time.time()
                ret = self.obj_cam.MV_CC_ConvertPixelType(stConvertParam)
                time_end=time.time()
                # print('MV_CC_ConvertPixelType to Mono8:',time_end - time_start) 
                if ret != 0:
                    print('show error','convert pixel fail! ret = '+self.To_hex_str(ret))
                    continue
                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                numArray = CameraController.Mono_numpy(self,img_buff,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                mode = "L"

            #转换为OpenCV图像
            current_image = Image.frombuffer(mode, (self.st_frame_info.nWidth,self.st_frame_info.nHeight), numArray.astype('uint8')).resize((self.st_frame_info.nWidth,self.st_frame_info.nHeight), Image.LANCZOS)
            nRet = self.obj_cam.MV_CC_FreeImageBuffer(stOutFrame)
            if self.b_exit == True:
                if img_buff is not None:
                    del img_buff
                if buf_cache is not None:
                    del buf_cache
            break
            
        image_result = np.asarray(current_image)
        return image_result

    def Save_jpg(self,buf_cache):
        if(None == buf_cache):
            return
        self.buf_save_image = None
        file_path = str(self.st_frame_info.nFrameNum) + ".jpg"
        self.n_save_image_size = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3 + 2048
        if self.buf_save_image is None:
            self.buf_save_image = (c_ubyte * self.n_save_image_size)()

        stParam = MV_SAVE_IMAGE_PARAM_EX()
        stParam.enImageType = MV_Image_Jpeg;                                        # ch:需要保存的图像类型 | en:Image format to save
        stParam.enPixelType = self.st_frame_info.enPixelType                               # ch:相机对应的像素格式 | en:Camera pixel type
        stParam.nWidth      = self.st_frame_info.nWidth                                    # ch:相机对应的宽 | en:Width
        stParam.nHeight     = self.st_frame_info.nHeight                                   # ch:相机对应的高 | en:Height
        stParam.nDataLen    = self.st_frame_info.nFrameLen
        stParam.pData       = cast(buf_cache, POINTER(c_ubyte))
        stParam.pImageBuffer=  cast(byref(self.buf_save_image), POINTER(c_ubyte)) 
        stParam.nBufferSize = self.n_save_image_size                                 # ch:存储节点的大小 | en:Buffer node size
        stParam.nJpgQuality = 80;                                                    # ch:jpg编码，仅在保存Jpg图像时有效。保存BMP时SDK内忽略该参数
        return_code = self.obj_cam.MV_CC_SaveImageEx2(stParam)            

        if return_code != 0:
            print('show error','save jpg fail! ret = '+self.To_hex_str(return_code))
            self.b_save_jpg = False
            return
        file_open = open(file_path.encode('ascii'), 'wb+')
        img_buff = (c_ubyte * stParam.nImageLen)()
        try:
            cdll.msvcrt.memcpy(byref(img_buff), stParam.pImageBuffer, stParam.nImageLen)
            file_open.write(img_buff)
            self.b_save_jpg = False
            print('show info','save jpg success!')
        except Exception as e:
            self.b_save_jpg = False
            raise Exception("get one frame failed:%s" % e.message)
        if None != img_buff:
            del img_buff
        if None != self.buf_save_image:
            del self.buf_save_image

    def Save_Bmp(self,buf_cache):
        if(0 == buf_cache):
            return
        self.buf_save_image = None
        file_path = str(self.st_frame_info.nFrameNum) + ".bmp"    
        self.n_save_image_size = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3 + 2048
        if self.buf_save_image is None:
            self.buf_save_image = (c_ubyte * self.n_save_image_size)()

        stParam = MV_SAVE_IMAGE_PARAM_EX()
        stParam.enImageType = MV_Image_Bmp;                                        # ch:需要保存的图像类型 | en:Image format to save
        stParam.enPixelType = self.st_frame_info.enPixelType                               # ch:相机对应的像素格式 | en:Camera pixel type
        stParam.nWidth      = self.st_frame_info.nWidth                                    # ch:相机对应的宽 | en:Width
        stParam.nHeight     = self.st_frame_info.nHeight                                   # ch:相机对应的高 | en:Height
        stParam.nDataLen    = self.st_frame_info.nFrameLen
        stParam.pData       = cast(buf_cache, POINTER(c_ubyte))
        stParam.pImageBuffer=  cast(byref(self.buf_save_image), POINTER(c_ubyte)) 
        stParam.nBufferSize = self.n_save_image_size                                 # ch:存储节点的大小 | en:Buffer node size
        return_code = self.obj_cam.MV_CC_SaveImageEx2(stParam)            
        if return_code != 0:
            print('show error','save bmp fail! ret = '+self.To_hex_str(return_code))
            self.b_save_bmp = False
            return
        file_open = open(file_path.encode('ascii'), 'wb+')
        img_buff = (c_ubyte * stParam.nImageLen)()
        try:
            cdll.msvcrt.memcpy(byref(img_buff), stParam.pImageBuffer, stParam.nImageLen)
            file_open.write(img_buff)
            self.b_save_bmp = False
            print('show info','save bmp success!')
        except Exception as e:
            self.b_save_bmp = False
            raise Exception("get one frame failed:%s" % e.message)
        if None != img_buff:
            del img_buff
        if None != self.buf_save_image:
            del self.buf_save_image

    def Is_mono_data(self,enGvspPixelType):
        if PixelType_Gvsp_Mono8 == enGvspPixelType or PixelType_Gvsp_Mono10 == enGvspPixelType \
            or PixelType_Gvsp_Mono10_Packed == enGvspPixelType or PixelType_Gvsp_Mono12 == enGvspPixelType \
            or PixelType_Gvsp_Mono12_Packed == enGvspPixelType:
            return True
        else:
            return False

    def Is_color_data(self,enGvspPixelType):
        if PixelType_Gvsp_BayerGR8 == enGvspPixelType or PixelType_Gvsp_BayerRG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB8 == enGvspPixelType or PixelType_Gvsp_BayerBG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10 == enGvspPixelType or PixelType_Gvsp_BayerRG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10 == enGvspPixelType or PixelType_Gvsp_BayerBG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12 == enGvspPixelType or PixelType_Gvsp_BayerRG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB12 == enGvspPixelType or PixelType_Gvsp_BayerBG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG12_Packed== enGvspPixelType \
            or PixelType_Gvsp_BayerGB12_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG12_Packed == enGvspPixelType \
            or PixelType_Gvsp_YUV422_Packed == enGvspPixelType or PixelType_Gvsp_YUV422_YUYV_Packed == enGvspPixelType:
            return True
        else:
            return False

    def Mono_numpy(self,data,nWidth,nHeight):
        data_ = np.frombuffer(data, count=int(nWidth * nHeight), dtype=np.uint8, offset=0)
        data_mono_arr = data_.reshape(nHeight, nWidth)
        numArray = np.zeros([nHeight, nWidth, 1],"uint8")
        numArray[:, :, 0] = data_mono_arr
        return numArray

    def Color_numpy(self,data,nWidth,nHeight):
        data_ = np.frombuffer(data, count=int(nWidth*nHeight*3), dtype=np.uint8, offset=0)
        data_r = data_[0:nWidth*nHeight*3:3]
        data_g = data_[1:nWidth*nHeight*3:3]
        data_b = data_[2:nWidth*nHeight*3:3]

        data_r_arr = data_r.reshape(nHeight, nWidth)
        data_g_arr = data_g.reshape(nHeight, nWidth)
        data_b_arr = data_b.reshape(nHeight, nWidth)
        numArray = np.zeros([nHeight, nWidth, 3],"uint8")

        numArray[:, :, 0] = data_r_arr
        numArray[:, :, 1] = data_g_arr
        numArray[:, :, 2] = data_b_arr
        return numArray