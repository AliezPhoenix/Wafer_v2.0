"""
OpenCV 切痕检测预处理方案集合
提供多种预处理方法以适应不同的图像条件
"""
import cv2 as cv
import numpy as np
from typing import Tuple, Optional


def preprocess_method_1_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    方案1: 直方图均衡化
    适用场景: 图像整体对比度低，但切痕与背景有灰度差异
    
    优点: 
    - 增强整体对比度
    - 简单快速
    - 适合光照不均的情况
    
    缺点:
    - 可能过度增强噪声
    - 不适合对比度已经很好的图像
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # 全局直方图均衡化
    equalized = cv.equalizeHist(image)
    
    return equalized


def preprocess_method_2_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    方案2: 自适应直方图均衡化 (CLAHE)
    适用场景: 局部光照不均，需要保持局部细节
    
    优点:
    - 限制局部对比度增强，避免过度增强
    - 保持图像自然外观
    - 适合有阴影或光照变化的图像
    
    参数:
    - clip_limit: 对比度限制阈值 (默认2.0)
    - tile_size: 局部区域大小 (默认8x8)
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # 创建CLAHE对象
    clahe = cv.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    equalized = clahe.apply(image)
    
    return equalized


def preprocess_method_3_adaptive_threshold(image: np.ndarray, 
                                           block_size: int = 11, 
                                           C: int = 2,
                                           method: int = cv.ADAPTIVE_THRESH_GAUSSIAN_C) -> np.ndarray:
    """
    方案3: 自适应阈值处理
    适用场景: 光照不均，全局阈值效果差
    
    优点:
    - 自动适应局部光照变化
    - 对光照不均的图像效果好
    - 直接输出二值图像
    
    参数:
    - block_size: 局部区域大小 (必须为奇数，如11, 15, 21)
    - C: 从均值中减去的常数 (通常2-5)
    - method: ADAPTIVE_THRESH_MEAN_C 或 ADAPTIVE_THRESH_GAUSSIAN_C
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # 确保block_size为奇数
    if block_size % 2 == 0:
        block_size += 1
    
    # 自适应阈值
    binary = cv.adaptiveThreshold(image, 255, method, cv.THRESH_BINARY, block_size, C)
    
    return binary


def preprocess_method_4_morphology_edge(image: np.ndarray, 
                                       kernel_size: int = 3,
                                       morph_type: str = "gradient") -> np.ndarray:
    """
    方案4: 形态学边缘检测
    适用场景: 需要突出切痕边缘，去除噪声
    
    优点:
    - 突出边缘特征
    - 对噪声有抑制作用
    - 适合边缘清晰的切痕
    
    参数:
    - kernel_size: 形态学核大小 (3, 5, 7)
    - morph_type: "gradient"(边缘), "tophat"(顶帽), "blackhat"(黑帽)
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (kernel_size, kernel_size))
    
    if morph_type == "gradient":
        # 形态学梯度：突出边缘
        result = cv.morphologyEx(image, cv.MORPH_GRADIENT, kernel)
    elif morph_type == "tophat":
        # 顶帽：突出比周围亮的区域
        result = cv.morphologyEx(image, cv.MORPH_TOPHAT, kernel)
    elif morph_type == "blackhat":
        # 黑帽：突出比周围暗的区域（适合暗色切痕）
        result = cv.morphologyEx(image, cv.MORPH_BLACKHAT, kernel)
    else:
        result = image
    
    return result


def preprocess_method_5_gaussian_canny(image: np.ndarray, 
                                      gaussian_kernel: int = 5,
                                      canny_low: int = 50,
                                      canny_high: int = 150) -> np.ndarray:
    """
    方案5: 高斯滤波 + Canny边缘检测
    适用场景: 需要精确的边缘定位，噪声较多
    
    优点:
    - 边缘定位精确
    - 噪声抑制效果好
    - 适合需要精确边缘的场景
    
    参数:
    - gaussian_kernel: 高斯核大小 (必须为奇数)
    - canny_low: Canny低阈值
    - canny_high: Canny高阈值
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # 确保核大小为奇数
    if gaussian_kernel % 2 == 0:
        gaussian_kernel += 1
    
    # 高斯模糊去噪
    blurred = cv.GaussianBlur(image, (gaussian_kernel, gaussian_kernel), 0)
    
    # Canny边缘检测
    edges = cv.Canny(blurred, canny_low, canny_high)
    
    return edges


def preprocess_method_6_contrast_enhancement(image: np.ndarray, 
                                            alpha: float = 1.5,
                                            beta: int = 30) -> np.ndarray:
    """
    方案6: 对比度和亮度调整
    适用场景: 图像整体偏暗或对比度不足
    
    优点:
    - 可控的对比度和亮度调整
    - 简单直接
    - 适合微调图像质量
    
    参数:
    - alpha: 对比度控制 (1.0-3.0, 1.0为原始)
    - beta: 亮度控制 (-100到100, 0为原始)
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # 线性变换: new_image = alpha * image + beta
    enhanced = cv.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    return enhanced


def preprocess_method_7_bilateral_filter(image: np.ndarray,
                                         d: int = 9,
                                         sigma_color: float = 75,
                                         sigma_space: float = 75) -> np.ndarray:
    """
    方案7: 双边滤波
    适用场景: 需要去噪但保持边缘清晰
    
    优点:
    - 去噪同时保持边缘
    - 适合有噪声但边缘重要的图像
    
    参数:
    - d: 邻域直径
    - sigma_color: 颜色空间标准差
    - sigma_space: 坐标空间标准差
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    filtered = cv.bilateralFilter(image, d, sigma_color, sigma_space)
    
    return filtered


def preprocess_method_8_otsu_threshold(image: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    方案8: Otsu自动阈值
    适用场景: 双峰直方图，需要自动确定最佳阈值
    
    优点:
    - 自动确定最佳阈值
    - 适合双峰分布的图像
    - 无需手动调整阈值
    
    返回:
    - 二值图像和阈值
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # Otsu阈值
    threshold_value, binary = cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    return binary, threshold_value


def preprocess_method_9_multi_scale(image: np.ndarray, 
                                    scales: list = [1.0, 0.5, 2.0]) -> list:
    """
    方案9: 多尺度处理
    适用场景: 切痕宽度变化大，需要多尺度检测
    
    优点:
    - 适应不同宽度的切痕
    - 提高检测鲁棒性
    
    参数:
    - scales: 缩放比例列表
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    results = []
    h, w = image.shape[:2]
    
    for scale in scales:
        if scale != 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            scaled = cv.resize(image, (new_w, new_h), interpolation=cv.INTER_LINEAR)
        else:
            scaled = image.copy()
        results.append(scaled)
    
    return results


def preprocess_method_10_combined(image: np.ndarray, 
                                  method_sequence: list = ["clahe", "bilateral", "morphology"]) -> np.ndarray:
    """
    方案10: 组合预处理
    适用场景: 复杂图像条件，单一方法效果不佳
    
    优点:
    - 结合多种方法优势
    - 适应复杂场景
    
    参数:
    - method_sequence: 预处理方法序列
      可选: "clahe", "bilateral", "morphology", "gaussian", "equalization"
    """
    if len(image.shape) == 3:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    result = image.copy()
    
    for method in method_sequence:
        if method == "clahe":
            result = preprocess_method_2_clahe(result)
        elif method == "bilateral":
            result = preprocess_method_7_bilateral_filter(result)
        elif method == "morphology":
            result = preprocess_method_4_morphology_edge(result, morph_type="gradient")
        elif method == "gaussian":
            result = cv.GaussianBlur(result, (5, 5), 0)
        elif method == "equalization":
            result = preprocess_method_1_histogram_equalization(result)
    
    return result


# ==================== 使用示例函数 ====================

def apply_preprocessing_to_roi(image_check: np.ndarray, 
                               method: str = "clahe",
                               **kwargs) -> np.ndarray:
    """
    将预处理方法应用到ROI区域
    
    参数:
    - image_check: ROI图像区域
    - method: 预处理方法名称
      可选: "hist_eq", "clahe", "adaptive_thresh", "morphology", 
            "gaussian_canny", "contrast", "bilateral", "otsu", 
            "combined"
    - **kwargs: 各方法的特定参数
    
    返回:
    - 预处理后的图像
    """
    if method == "hist_eq":
        return preprocess_method_1_histogram_equalization(image_check)
    
    elif method == "clahe":
        clip_limit = kwargs.get("clip_limit", 2.0)
        tile_size = kwargs.get("tile_size", (8, 8))
        return preprocess_method_2_clahe(image_check, clip_limit, tile_size)
    
    elif method == "adaptive_thresh":
        block_size = kwargs.get("block_size", 11)
        C = kwargs.get("C", 2)
        return preprocess_method_3_adaptive_threshold(image_check, block_size, C)
    
    elif method == "morphology":
        kernel_size = kwargs.get("kernel_size", 3)
        morph_type = kwargs.get("morph_type", "gradient")
        return preprocess_method_4_morphology_edge(image_check, kernel_size, morph_type)
    
    elif method == "gaussian_canny":
        gaussian_kernel = kwargs.get("gaussian_kernel", 5)
        canny_low = kwargs.get("canny_low", 50)
        canny_high = kwargs.get("canny_high", 150)
        return preprocess_method_5_gaussian_canny(image_check, gaussian_kernel, canny_low, canny_high)
    
    elif method == "contrast":
        alpha = kwargs.get("alpha", 1.5)
        beta = kwargs.get("beta", 30)
        return preprocess_method_6_contrast_enhancement(image_check, alpha, beta)
    
    elif method == "bilateral":
        d = kwargs.get("d", 9)
        sigma_color = kwargs.get("sigma_color", 75)
        sigma_space = kwargs.get("sigma_space", 75)
        return preprocess_method_7_bilateral_filter(image_check, d, sigma_color, sigma_space)
    
    elif method == "otsu":
        binary, threshold = preprocess_method_8_otsu_threshold(image_check)
        return binary
    
    elif method == "combined":
        sequence = kwargs.get("sequence", ["clahe", "bilateral"])
        return preprocess_method_10_combined(image_check, sequence)
    
    else:
        # 默认返回原图
        return image_check


# ==================== 推荐方案组合 ====================

def get_recommended_preprocessing(image_check: np.ndarray, 
                                 image_condition: str = "normal") -> np.ndarray:
    """
    根据图像条件推荐预处理方案
    
    参数:
    - image_check: ROI图像
    - image_condition: 图像条件
      "normal": 正常图像
      "low_contrast": 低对比度
      "noisy": 噪声较多
      "uneven_lighting": 光照不均
      "dark": 整体偏暗
      "reflection": 有反射干扰
    """
    if image_condition == "normal":
        # 正常图像：轻微CLAHE增强
        return preprocess_method_2_clahe(image_check, clip_limit=1.5, tile_size=(8, 8))
    
    elif image_condition == "low_contrast":
        # 低对比度：CLAHE + 对比度增强
        result = preprocess_method_2_clahe(image_check, clip_limit=2.5)
        result = preprocess_method_6_contrast_enhancement(result, alpha=1.3, beta=20)
        return result
    
    elif image_condition == "noisy":
        # 噪声多：双边滤波 + 形态学
        result = preprocess_method_7_bilateral_filter(image_check)
        result = preprocess_method_4_morphology_edge(result, morph_type="gradient")
        return result
    
    elif image_condition == "uneven_lighting":
        # 光照不均：自适应阈值
        return preprocess_method_3_adaptive_threshold(image_check, block_size=15, C=3)
    
    elif image_condition == "dark":
        # 整体偏暗：对比度增强 + CLAHE
        result = preprocess_method_6_contrast_enhancement(image_check, alpha=1.8, beta=40)
        result = preprocess_method_2_clahe(result, clip_limit=2.0)
        return result
    
    elif image_condition == "reflection":
        # 反射干扰：黑帽形态学 + 双边滤波
        result = preprocess_method_4_morphology_edge(image_check, morph_type="blackhat")
        result = preprocess_method_7_bilateral_filter(result)
        return result
    
    else:
        return image_check
