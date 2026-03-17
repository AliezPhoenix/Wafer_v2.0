from ftplib import FTP
import socket
from Functions import *
def Analyze_Data(Data, Double_Int_File):
    High_Rank_1 = 0
    High_Rank_2 = 0
    Low_Rank_1 = 0
    Low_Rank_2 = 0
    result = 0 
    if Double_Int_File == "double":
        High_Rank_1 =  Data[6:8]
        High_Rank_2 =  Data[4:6]
        Low_Rank_1 = Data[2:4]
        Low_Rank_2 = Data[0:2]
        result = High_Rank_1+High_Rank_2+Low_Rank_1+Low_Rank_2
        return int(result,16)
    if Double_Int_File == "int":
        Low_Rank_1 = Data[2:4]
        Low_Rank_2 = Data[0:2]
        result = Low_Rank_1+Low_Rank_2
        return int(result,16)
    if Double_Int_File == "file":
        Data_Analized = "".join(hexStr_to_str(Data).split("\x00"))
        result = Data_Analized.rstrip(" ").lstrip(" ")[2::]
        return result
class Signals_Recieved_From_PLC():
        #   DT1000	心跳监视
        # 	DT1001	使用相机
        # 	DT1002	动作模式
        # 	DT1003	布局
        # 	DT1004	实时窗口大小
        # 	DT1005	标记显示控制
        # 	DT1006	目标窗口_宽
        # 	DT1007	目标窗口_高
        # 	DT1008	对齐基准线宽度
        # 	DT1009	刀痕基准线宽度
        #   DT1010	注册模板
        # 	DT1011	检查触发
        # 	DT1012	保存图片位置
        # 	DT1013	保存图片尺寸
        # 	DT1014	自动对焦启动
        # 	DT1015	手动存图
        # 	DT1016	清除存图窗口
        # 	DT1017  保存到布局
        # 	DT1018	U盘导入导出
        # 	DT1019	工件数据操作
        #   DT1020	低倍像素尺寸
        # 	DT1021	低倍像素尺寸
        # 	DT1022	高倍像素尺寸
        # 	DT1023	高倍像素尺寸
        # 	DT1024	螺旋检查Q阀值
        # 	DT1025	索引检查Y允许偏差
        # 	DT1026	模板匹配Q阀值 
        # 	DT1027	低倍螺旋检查范围X
        # 	DT1028	低倍螺旋检查范围Y
        # 	DT1029	对齐模式
        # 	DT1030	切痕_识别阀值
        # 	DT1031	切痕_偏离中心Max
        # 	DT1032	切痕_宽度(不含崩边)Max
        # 	DT1033	切痕_宽度(不含崩边)Min
        # 	DT1034	切痕_宽度(含崩边)Max
        # 	DT1035	切痕_宽度(中心-崩边)Max
        # 	DT1036	切痕_崩边宽度Max
        # 	DT1037	切痕_崩边面积Max
        # 	DT1038	切痕_识别窗口宽度
        # 	DT1039	切痕_识别灵敏度
        # 	DT1040	切痕_遮罩中心宽度
        # 	DT1041	切痕_遮罩外边宽度
        # 	DT1042	模板检查遮罩功能使用
        # 	DT1043	预留
        # 	DT1044	工件类型
        # 	DT1045	模板匹配参数选择
        # 	DT1046-DT1047	晶粒尺寸X
        # 	DT1048-DT1049	晶粒尺寸Y
        # 	DT1050-DT1066	文件操作源目录名
        # 	DT1067	文件操作源工件数据No
        # 	DT1068-DT1084	文件操作目标目录名
        # 	DT1085	文件操作目标工件数据No
        # 	DT1086-DT1102	当前使用中数据目录名
        # 	DT1103	当前使用中数据No
        # 	DT1104-DT1120	文件操作源工件数据ID
        # 	DT1121-DT1137	文件操作目标数据ID
        # 	DT1138-DT1154	当前使用中工件数据ID
        # 	DT1155-DT1163	预留
        # 	DT1164	XY交换
        #   DT1165	CH1角度
        # 	DT1166	CH2角度
        # 	DT1167	CH3角度
        # 	DT1168	CH4角度
        # 	DT1169	WorkpieceMap文件刷新计数
        # 	DT1170	当前框架形状
        # 	DT1171	当前框架尺寸CH1
        # 	DT1172	当前框架尺寸CH2
        # 	DT1173	当前框架工件数量
        # 	DT1174	当前工件形状
        # 	DT1175	当前工件尺寸CH1
        # 	DT1176	当前工件尺寸CH2
        # 	DT1177	切割中状态
        # 	DT1178	当前显示的工件No
        # 	DT1179	当前显示的CH
        # 	DT1180	X进给位置
        # 	DT1181	SP1切割的线No
        # 	DT1182	SP2切割的线No
        # 	DT1183	当前查看的线No
        # 	DT1184	当前显示的比例
        # 	DT1185	当前触摸的位置X
        # 	DT1186	当前触摸的位置Y
        # 	DT1187	LineMap文件写入标志
        # 	DT1188	LineMap文件刷新计数
        # 	DT1189	当前工件序列号
        # 	DT1190	当前显示轴(预留)
        # 	DT1191	当前显示CH(预留)
        # 	DT1192	机器状态
        # 	DT1193	CH切完状态
        # 	DT1194	自动对焦ROI_X
        # 	DT1195	自动对焦ROI_Y
        # 	DT1196	当前X坐标
        # 	DT1197	
        # 	DT1198	当前Y坐标
        # 	DT1199
    def __init__(self,start_index,end_index):
        self.signals = dict()
        self.index_s = int(start_index[2:6])
        self.index_e = int(end_index[2:6])
        for i in range(self.index_s, self.index_e):
            signal_key = f"DT{i:04d}"  # 生成格式化的键名，例如 "DT1000"
            self.signals[signal_key] = 0
    def refresh(self,Data_R):
        count = 0
        for i in range(self.index_s, self.index_e):
            signal_key = f"DT{i:04d}"  
            singel_len = 4*count
            self.signals[signal_key] = Data_R[6+singel_len:10+singel_len]
            count += 1
        ####### 赋值完毕 ：DT1000~DT1199 #######
	
    
    def decode(self,data_index_start,data_index_end,d_type):
        values = list(self.signals.values())
        index_s = int(data_index_start[2:6])-1000
        index_e = int(data_index_end[2:6])-1000
        if d_type == "int":
            return Analyze_Data(values[index_s],"int") 
        if d_type == "double":
            return Analyze_Data(" ".join(values[index_s:index_e]),"double")
        if d_type == "file":
            return Analyze_Data("".join(values[index_s:index_e]),"file")
    
    def get_singal_list(self):
        Values = self.signals.values()
        Values = list(Values)
        return Values
class Signals_Send_To_PLC():
    def __init__(self,start_index,end_index):
        self.signals = dict()
        self.index_s = int(start_index[2:6])
        self.index_e = int(end_index[2:6])
        for i in range(self.index_s, self.index_e):
            signal_key = f"DT{i:04d}"  # 生成格式化的键名，例如 "DT1200"
            self.signals[signal_key] = "0000"
        
        ###### 赋值完毕 ：DT1200~DT1400 #######
        # DT1200	心跳监视；范围为0-32767，每秒+1变化
        # DT1201	当前使用相机
        # DT1202	当前动作模式
        # DT1203	当前使用布局
        # DT1204	当前实时窗口大小
        # DT1205	当前标记显示状态
            
        # DT1206	目标窗口_宽_当前值
        # DT1207	目标窗口_高_当前值
        # DT1208	对齐基准线宽度_当前值
        # DT1209	刀痕基准线宽度_当前值
        # DT1210	执行状态_注册模板
        # DT1211	"执行状态_检查触发
                                        # 9000：    切痕检查参数错误_遮罩
                                        # 9001:     无注册目标"
        # DT1212	执行状态_保存图片
        # DT1213	执行状态_保存图片
        # DT1214	执行状态_自动对焦
        # DT1215	执行状态_手动保存图片
        # DT1216	执行状态_清除存图窗口
        # DT1217	执行状态_保存结果布局
        # DT1218	"执行状态_U盘导入导出。1：执行中；
                                        # -DT1018：执行完成；
                                        # 9000：    目录不存在或错误；
                                        # 9001：文件不存在或错误；
                                        # 9002：    文件访问冲突"
        # DT1219	执行状态_工件数据操作
        # DT1220	模板匹配结果_X；单位:0.1um
        # DT1221	模板匹配结果_X；单位:0.1um
        # DT1222	模板匹配结果_Y；单位:0.1um
        # DT1223	
        # DT1224	模板匹配结果_θ；单位:0.001度
        # DT1225	模板匹配结果_θ；单位:0.001度
        # DT1226	模板匹配结果_Q；范围：0%~100%，没有识别到填0%。
        # DT1227	模板匹配结果_X像素值；单位:像素
        # DT1228	模板匹配结果_Y像素值；单位:像素
        # DT1229	自动对焦图片质量结果；单位:像素
        # DT1230	切痕检查结果_识别Q值；范围：0%~100%，没有识别到填0%
        # DT1231	切痕检查结果_偏离中心；单位:像素
        # DT1232	切痕检查结果_宽度(不含崩边)；单位:像素
        # DT1233	切痕检查结果_宽度(含崩边)；单位:像素
        # DT1234	切痕检查结果_宽度(中心-崩边)；单位:像素
        # DT1235	切痕检查结果_崩边宽度；单位:像素
        # DT1236	切痕检查结果_崩边面积；单位:像素
        # DT1237	
        # DT1238	
        # DT1239	
        # DT1240	
        # DT1241	
        # DT1242-DT1249	预留                                 
        # DT1250-DT1266	返回完成的文件操作源目录名
        # DT1267	    返回完成的文件操作源工件数据No
        # DT1268-DT1284	返回完成的文件操作目标目录名
        # DT1285	    返回完成的文件操作目标工件数据No
        # DT1286-DT1302	返回当前使用中数据目录名
        # DT1303	    返回当前使用中工件数据No
        # DT1304-DT1320	
        # DT1321-DT1337	
        # DT1338-DT1354	
        # DT1355-DT1369	         
        # DT1370	
        # DT1371	
        # DT1372	
        # DT1373	
        # DT1374	
        # DT1375	
        # DT1376	
        # DT1377	
        # DT1378	
        # DT1379	
        # DT1380	
        # DT1381	
        # DT1382	
        # DT1383	PC返回当前实际的查看线No
        # DT1384	PC返回当前实际的显示比例
        # DT1385	
        # DT1386	当前触摸的线No：PC检测到DT1186>0时，将对应的线No写入。DT1186<=0时，写入0
        # DT1387	LineMap文件读取标志：0：无动作；1：读取中
        # DT1388	
        # DT1389	
        # DT1390	
        # DT1391	
        # DT1392	返回U盘存在状态：0：不存在；1：存在
        # DT1393	FTP连接状态：0：未连接；1：已连接
        # DT1394	
        # DT1395	
        # DT1396	
        # DT1397	
        # DT1398	
        # DT1399	

    def motify_encode(self,data_index,value,d_type):
        if d_type == "int":
            if value< 0:
                self.signals[data_index] = Data_to_hex_relabled("0000"+hex(0xffff+value+0x0001)[2:])
            else:
                self.signals[data_index] = Data_to_hex_relabled("0000"+hex(value)[2:])
        if d_type == "file" or d_type == "double":
            data_index_start = int(data_index[2:6])
            data_index_end = int(data_index[9::])
            for i in range(data_index_start, data_index_end):
                signal_key = f"DT{i:04d}"
                self.signals[signal_key] = value.signals[f"DT{i-200:04d}"]

    def get_singal_list(self):
        return "".join(list(self.signals.values()))
    def signal_refresh(self,signal_r:Signals_Recieved_From_PLC):
        self.signals["DT1200"] = signal_r.signals["DT1000"]
        self.signals["DT1201"] = signal_r.signals["DT1001"]
        self.signals["DT1202"] = signal_r.signals["DT1002"]
        self.signals["DT1203"] = signal_r.signals["DT1003"]
        self.signals["DT1204"] = signal_r.signals["DT1004"]
        self.signals["DT1205"] = signal_r.signals["DT1005"]
        self.signals["DT1206"] = signal_r.signals["DT1006"]
        self.signals["DT1207"] = signal_r.signals["DT1007"]
        self.signals["DT1208"] = signal_r.signals["DT1008"]
        self.signals["DT1209"] = signal_r.signals["DT1009"]
        for i in range(1250, 1303):
            signal_key = f"DT{i:04d}"
            self.signals[signal_key] = signal_r.signals[f"DT{i-200:04d}"]
    def signal_refresh_cam(self,signal_r:Signals_Recieved_From_PLC):
        for i in range(1400,1450):
            signal_key = f"DT{i:04d}"
            self.signals[signal_key] = signal_r.signals[f"DT{i-200:04d}"]
class Communicate():
    def __init__(self,**kwargs):
        self.Code = "<01#RD{}{}**\r".format("D01000","01199")
        self.Sender  = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ip = kwargs.get("ip")
        self.port = kwargs.get("port")
        self.Sender.settimeout(1)
    def get_signals(self,start_index,end_index):
        index_s = int(start_index[2:6])
        index_e = int(end_index[2:6]) -1
        Signals_Receive = Signals_Recieved_From_PLC("DT1000","DT1200")
        self.Code = "<01#RD{}{}**\r".format("D0"+str(index_s),"0"+str(index_e))
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.Sender.send(self.Code.encode())
                Data_Receive = self.Sender.recv(1024).decode()
                Signals_Receive.refresh(Data_Receive)
                return 0,Signals_Receive
            except Exception as e:
                retry_count += 1
                print(f"Socket通信失败 (尝试 {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    # 尝试重新连接
                    try:
                        self.Sender.close()
                    except:
                        pass
                    
                    self.Sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.Sender.settimeout(5)  # 增加超时时间
                    
                    if self.connect() == 0:
                        print("无法重新建立Socket连接")
                        return 1, None
                else:
                    return 1, None
        
        return 1, None 
    def send_signals(self,Data_Send:Signals_Send_To_PLC,start_index,end_index):
        index_s = int(start_index[2:6])
        index_e = int(end_index[2:6])-1
        data = Data_Send.get_singal_list()
        self.Code = "<01#WD{}{}{}**\r".format("D0"+str(index_s),"0"+str(index_e),data).upper()
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.Sender.send(self.Code.encode())
                Data_Receive = self.Sender.recv(1024).decode()###清除接收缓存
                return 0
            except Exception as e:
                retry_count += 1
                print(f"Socket发送失败 (尝试 {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    # 尝试重新连接
                    try:
                        self.Sender.close()
                    except:
                        pass
                    
                    self.Sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.Sender.settimeout(5)  # 增加超时时间
                    
                    if self.connect() == 0:
                        print("无法重新建立Socket连接")
                        return 1
                else:
                    return 1
        
        return 1

    def connect(self):
        try:
            self.Sender.connect((self.ip,self.port))
            return 0
        except:
            self.Sender.close()
            return 1
    def close(self):
        self.Sender.close()
        
