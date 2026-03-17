"""
预处理方法对比测试工具
可视化不同预处理方法的效果，帮助选择最佳方案
"""
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from preprocessing_methods import (
    preprocess_method_1_histogram_equalization,
    preprocess_method_2_clahe,
    preprocess_method_3_adaptive_threshold,
    preprocess_method_4_morphology_edge,
    preprocess_method_5_gaussian_canny,
    preprocess_method_6_contrast_enhancement,
    preprocess_method_7_bilateral_filter,
    preprocess_method_8_otsu_threshold,
    preprocess_method_10_combined,
    get_recommended_preprocessing
)


def compare_preprocessing_methods(image_path: str, roi: list = None):
    """
    对比所有预处理方法的效果
    
    参数:
    - image_path: 图像路径
    - roi: ROI区域 [x_center, y_center, width, height]，如果为None则使用整图
    """
    # 读取图像
    image = cv.imread(image_path)
    if image is None:
        print(f"无法读取图像: {image_path}")
        return
    
    # 转换为灰度
    if len(image.shape) == 3:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 提取ROI
    image_width = image.shape[1]
    image_hight = image.shape[0]
    image_center = [int(image_width/2),int(image_hight/2)]
    image_check = image[image_center[1]-roi[1]:image_center[1]+roi[1],image_center[0]-roi[0]:image_center[0]+roi[0]]
    
    # 存储所有预处理结果
    results = {}
    results["原始图像"] = image_check
    
    # 应用各种预处理方法
    print("正在应用预处理方法...")
    
    try:
        results["1. histogram"] = preprocess_method_1_histogram_equalization(image_check)
    except Exception as e:
        print(f"方法1失败: {e}")
    
    try:
        results["2. CLAHE"] = preprocess_method_2_clahe(image_check, clip_limit=2.0)
    except Exception as e:
        print(f"方法2失败: {e}")
    
    try:
        results["3. adaptive_threshold"] = preprocess_method_3_adaptive_threshold(image_check, block_size=11, C=2)
    except Exception as e:
        print(f"方法3失败: {e}")
    
    try:
        results["4. morphology_edge"] = preprocess_method_4_morphology_edge(image_check, morph_type="gradient")
    except Exception as e:
        print(f"方法4失败: {e}")
    
    try:
        results["5. morphology_blackhat"] = preprocess_method_4_morphology_edge(image_check, morph_type="blackhat")
    except Exception as e:
        print(f"方法5失败: {e}")
    
    try:
        results["6. gaussian_canny"] = preprocess_method_5_gaussian_canny(image_check)
    except Exception as e:
        print(f"方法6失败: {e}")
    
    try:
        results["7. contrast_enhancement"] = preprocess_method_6_contrast_enhancement(image_check, alpha=1.5, beta=30)
    except Exception as e:
        print(f"方法7失败: {e}")
    
    try:
        results["8. bilateral_filter"] = preprocess_method_7_bilateral_filter(image_check)
    except Exception as e:
        print(f"方法8失败: {e}")
    
    try:
        binary, threshold = preprocess_method_8_otsu_threshold(image_check)
        results["9. otsu_threshold"] = binary
        print(f"Otsu阈值: {threshold}")
    except Exception as e:
        print(f"方法9失败: {e}")
    
    try:
        results["10. combined"] = preprocess_method_10_combined(
            image_check, 
            method_sequence=["clahe", "bilateral", "morphology"]
        )
    except Exception as e:
        print(f"方法10失败: {e}")
    
    # 可视化结果
    num_methods = len(results)
    cols = 3
    rows = (num_methods + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
    axes = axes.flatten() if num_methods > 1 else [axes]
    
    for idx, (name, processed_img) in enumerate(results.items()):
        ax = axes[idx]
        
        # 显示图像
        if len(processed_img.shape) == 2:
            ax.imshow(processed_img, cmap='gray')
        else:
            ax.imshow(cv.cvtColor(processed_img, cv.COLOR_BGR2RGB))
        
        ax.set_title(name, fontsize=10)
        ax.axis('off')
        
        # 添加统计信息
        mean_val = np.mean(processed_img)
        std_val = np.std(processed_img)
        ax.text(0.02, 0.98, f'Mean: {mean_val:.1f}\nStd: {std_val:.1f}',
                transform=ax.transAxes, fontsize=8,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    # 隐藏多余的子图
    for idx in range(num_methods, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig('preprocessing_comparison.png', dpi=150, bbox_inches='tight')
    print("对比结果已保存为: preprocessing_comparison.png")
    plt.show()


def analyze_image_statistics(image_path: str, roi: list = None):
    """
    分析图像统计信息，帮助选择预处理方法
    
    参数:
    - image_path: 图像路径
    - roi: ROI区域
    """
    image = cv.imread(image_path)
    if image is None:
        print(f"无法读取图像: {image_path}")
        return
    
    if len(image.shape) == 3:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    if roi is not None:
        x, y, w, h = roi
        image_check = gray[y:y+h, x:x+w]
    else:
        h, w = gray.shape[:2]
        center_x, center_y = w // 2, h // 2
        roi_size = min(w, h) // 3
        image_check = gray[center_y-roi_size:center_y+roi_size, 
                          center_x-roi_size:center_x+roi_size]
    
    # 计算统计信息
    mean_val = np.mean(image_check)
    std_val = np.std(image_check)
    median_val = np.median(image_check)
    min_val = np.min(image_check)
    max_val = np.max(image_check)
    
    # 计算直方图
    hist = cv.calcHist([image_check], [0], None, [256], [0, 256])
    
    # 判断图像条件
    conditions = []
    recommendations = []
    
    if mean_val < 80:
        conditions.append("整体偏暗")
        recommendations.append("推荐: 对比度增强 + CLAHE")
    elif mean_val > 180:
        conditions.append("整体偏亮")
        recommendations.append("推荐: 降低亮度或使用自适应阈值")
    
    if std_val < 20:
        conditions.append("对比度低")
        recommendations.append("推荐: CLAHE 或 直方图均衡化")
    elif std_val > 50:
        conditions.append("噪声较多")
        recommendations.append("推荐: 双边滤波 或 高斯滤波")
    
    # 打印统计信息
    print("=" * 50)
    print("图像统计信息:")
    print(f"  均值 (Mean): {mean_val:.2f}")
    print(f"  标准差 (Std): {std_val:.2f}")
    print(f"  中位数 (Median): {median_val:.2f}")
    print(f"  最小值: {min_val}")
    print(f"  最大值: {max_val}")
    print(f"  动态范围: {max_val - min_val}")
    print("\n图像条件判断:")
    for cond in conditions:
        print(f"  - {cond}")
    print("\n预处理建议:")
    for rec in recommendations:
        print(f"  - {rec}")
    print("=" * 50)
    
    # 可视化直方图
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.imshow(image_check, cmap='gray')
    plt.title('ROI区域')
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.plot(hist)
    plt.title('灰度直方图')
    plt.xlabel('灰度值')
    plt.ylabel('像素数量')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('image_statistics.png', dpi=150, bbox_inches='tight')
    print("统计信息已保存为: image_statistics.png")
    plt.show()


def test_single_method(image_path: str, method_name: str, **kwargs):
    """
    测试单个预处理方法
    
    参数:
    - image_path: 图像路径
    - method_name: 方法名称
    - **kwargs: 方法参数
    """
    image = cv.imread(image_path)
    if image is None:
        print(f"无法读取图像: {image_path}")
        return
    
    if len(image.shape) == 3:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    h, w = gray.shape[:2]
    center_x, center_y = w // 2, h // 2
    roi_size = min(w, h) // 3
    image_check = gray[center_y-roi_size:center_y+roi_size, 
                      center_x-roi_size:center_x+roi_size]
    
    # 应用预处理
    method_map = {
        "hist_eq": preprocess_method_1_histogram_equalization,
        "clahe": preprocess_method_2_clahe,
        "adaptive_thresh": preprocess_method_3_adaptive_threshold,
        "morphology": preprocess_method_4_morphology_edge,
        "gaussian_canny": preprocess_method_5_gaussian_canny,
        "contrast": preprocess_method_6_contrast_enhancement,
        "bilateral": preprocess_method_7_bilateral_filter,
        "otsu": preprocess_method_8_otsu_threshold,
        "combined": preprocess_method_10_combined
    }
    
    if method_name not in method_map:
        print(f"未知方法: {method_name}")
        print(f"可用方法: {list(method_map.keys())}")
        return
    
    try:
        processed = method_map[method_name](image_check, **kwargs)
        
        # 显示对比
        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 1)
        plt.imshow(image_check, cmap='gray')
        plt.title('原始图像')
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        plt.imshow(processed, cmap='gray')
        plt.title(f'预处理后: {method_name}')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"处理失败: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python preprocessing_comparison.py <图像路径> [compare|analyze|test]")
        print("\n示例:")
        print("  python preprocessing_comparison.py image.tga compare  # 对比所有方法")
        print("  python preprocessing_comparison.py image.tga analyze  # 分析图像统计")
        print("  python preprocessing_comparison.py image.tga test clahe  # 测试单个方法")
        sys.exit(1)
    
    image_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "compare"
    
    if mode == "compare":
        compare_preprocessing_methods(image_path)
    elif mode == "analyze":
        analyze_image_statistics(image_path)
    elif mode == "test":
        method = sys.argv[3] if len(sys.argv) > 3 else "clahe"
        test_single_method(image_path, method)
    else:
        print(f"未知模式: {mode}")
