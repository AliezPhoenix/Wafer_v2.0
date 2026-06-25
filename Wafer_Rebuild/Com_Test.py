from Communicate import *
import Camera
import time
# Com = Communicate(ip = "192.168.1.5",port = 60011)
# Com.connect()
# S_F_PLC = Signals_Recieved_From_PLC("DT1000","DT1200")
# S_S_PLC = Signals_Send_To_PLC("DT1200","DT1400")
# for i in range(0,5000):
#     ret, S_F_PLC = Com.get_signals("DT1000","DT1200")
#     #print(ret)
#     #print(S_F_PLC.get_singal_list(),len(S_F_PLC.get_singal_list()))
#     S_S_PLC.signal_refresh(S_F_PLC)
#     #print(S_S_PLC.get_singal_list(),len(S_S_PLC.get_singal_list()))
#     ret = Com.send_signals(S_S_PLC,"DT1200","DT1400")
#     time.sleep(0.5)

#print(S_F_PLC.decode("DT1406","DT1406","int"))

Cam_test = Camera.MvCamera()
Cam_test = Camera.CameraController(Cam_test,"192.168.1.244","192.168.1.157")
Cam_test.Open_device()
Cam_test.Start_grabbing()
while(True):  
    time.sleep(5)
    Cam_test.Stop_grabbing()
    Cam_test.Close_device()
    Cam_test.Open_device()
    Cam_test.Start_grabbing()




#     image = Cam_test.Get_image()
#     rotate_matrix = cv.getRotationMatrix2D((image.shape[1]/2,image.shape[0]/2),0.5895,1)
#     image = cv.warpAffine(image,rotate_matrix,(image.shape[1],image.shape[0]))
#     image = cv.cvtColor(image,cv.COLOR_GRAY2BGR)
#     cv.line(image,(100,512),(1000,512),(0,255,0),3)
#     cv.namedWindow("rotate",cv.WINDOW_NORMAL)
#     cv.imshow("rotate",image)
#     cv.waitKey(20)
