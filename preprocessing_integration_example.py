"""
预处理方案集成示例
展示如何在 cutting_path_reflection 函数中集成预处理方法
"""
import cv2 as cv
import numpy as np
from preprocessing_methods import apply_preprocessing_to_roi, get_recommended_preprocessing


def cutting_path_reflection_with_preprocessing(Img: np.ndarray, 
                                               roi, 
                                               method: str = "std",
                                               preprocess_method: str = "none",
                                               **preprocess_kwargs):
    """
    带预处理的反射切割道检测函数
    
    参数:
    - Img: 输入图像
    - roi: ROI区域 [width, height, mid_ignore]
    - method: 检测方法 "std" 或 "reflection"
    - preprocess_method: 预处理方法
      "none": 不使用预处理（原始方法）
      "clahe": CLAHE自适应直方图均衡化
      "adaptive_thresh": 自适应阈值
      "morphology": 形态学边缘检测
      "bilateral": 双边滤波
      "contrast": 对比度增强
      "recommended": 根据图像条件自动推荐
      "combined": 组合方法
    - **preprocess_kwargs: 预处理方法的特定参数
    """
    from typing import List, Tuple
    
    Cutting_Path_Parameters = [0,0,0,0,0,0]
    image = Img.copy()
    
    # 灰度保护
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    image_width = image.shape[1]
    image_hight = image.shape[0]
    image_center = [int(image_width/2), int(image_hight/2)]
    
    check_roi = roi
    # 提取ROI区域
    image_check = image[image_center[1]-check_roi[1]:image_center[1]+check_roi[1], 
                       image_center[0]-check_roi[0]:image_center[0]+check_roi[0]]
    
    # ========== 预处理步骤 ==========
    if preprocess_method != "none":
        if preprocess_method == "recommended":
            # 自动判断图像条件并推荐预处理
            image_mean = np.mean(image_check)
            image_std = np.std(image_check)
            
            if image_mean < 80:
                condition = "dark"
            elif image_std < 20:
                condition = "low_contrast"
            elif image_std > 50:
                condition = "noisy"
            else:
                condition = "normal"
            
            image_check = get_recommended_preprocessing(image_check, condition)
            print(f"自动检测图像条件: {condition}")
        else:
            # 使用指定的预处理方法
            image_check = apply_preprocessing_to_roi(image_check, preprocess_method, **preprocess_kwargs)
    
    # ========== 原有的检测逻辑 ==========
    image_mean = np.mean(image_check)
    
    # 根据预处理结果调整阈值策略
    if preprocess_method == "adaptive_thresh" or preprocess_method == "otsu":
        # 如果已经二值化，直接使用
        image_mask = image_check.copy()
    else:
        # 原有的阈值方法
        if method == "std":
            image_mask = np.where(image_check >= image_mean, 255, 0).astype(np.uint8)
        elif method == "reflection":
            image_mask = np.where(image_check <= image_mean-10, 255, 0).astype(np.uint8)
    
    # 使用掩码提取感兴趣区域
    image_check_masked = cv.bitwise_and(image_check, image_mask)
    
    # 计算水平投影值
    hor_val = np.sum(image_mask, axis=1) / image_mask.shape[1]
    hor_val = hor_val.tolist()
    
    # ... 后续检测逻辑保持不变 ...
    # (这里省略了原有的边界检测和缺陷检测代码)
    
    return image_check, image_mask, hor_val


# ==================== 使用示例 ====================

def example_usage():
    """使用示例"""
    import os
    
    # 读取图像
    image = cv.imread("Wafer_Rebuild/Image/TGA/TGA129/Image_20260129102656012.bmp")
    
    if image is None:
        print("无法读取图像")
        return
    
    roi = [300, 60, 20]  # [width, height, mid_ignore]
    
    # 示例1: 使用CLAHE预处理
    print("示例1: CLAHE预处理")
    result1, mask1, hor_val1 = cutting_path_reflection_with_preprocessing(
        image, roi, method="std", 
        preprocess_method="clahe",
        clip_limit=2.0,
        tile_size=(8, 8)
    )
    
    # 示例2: 使用自适应阈值
    print("示例2: 自适应阈值预处理")
    result2, mask2, hor_val2 = cutting_path_reflection_with_preprocessing(
        image, roi, method="std",
        preprocess_method="adaptive_thresh",
        block_size=15,
        C=3
    )
    
    # 示例3: 使用推荐预处理（自动判断）
    print("示例3: 自动推荐预处理")
    result3, mask3, hor_val3 = cutting_path_reflection_with_preprocessing(
        image, roi, method="std",
        preprocess_method="recommended"
    )
    
    # 示例4: 组合预处理
    print("示例4: 组合预处理")
    result4, mask4, hor_val4 = cutting_path_reflection_with_preprocessing(
        image, roi, method="std",
        preprocess_method="combined",
        sequence=["clahe", "bilateral", "morphology"]
    )
    
    # 显示结果
    cv.imshow("Original ROI", result1)
    cv.imshow("CLAHE Result", mask1)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    example_usage()
    # INSERT_YOUR_CODE
    # 对比所有预处理方式图
    from preprocessing_comparison import compare_preprocessing_methods

    # 这里可以直接调用图像路径进行对比
    image_path = "Wafer_Rebuild/Image/TGA/TGA129/Image_20260129102656012.bmp"
    compare_preprocessing_methods(image_path,roi = [300,60,20])
