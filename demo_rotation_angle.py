#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示根据同一列模板坐标计算图像整体偏移角度的功能
"""

import numpy as np
import math
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 常量定义
D2R = math.pi / 180.0
R2D = 180.0 / math.pi

def points_to_2d_array(unique_points, template_width, template_height):
    """
    将去重后的匹配点转换为二维数组，按照模板的实际排列组织
    """
    if not unique_points:
        return np.array([])
    
    # 允许y方向有1/3个模板大小的误差
    y_tolerance = template_height / 3
    
    # 按y坐标分组，相近的y坐标认为是同一行
    rows = []
    current_row = []
    current_y = None
    
    for point in sorted(unique_points, key=lambda p: p[1]):
        if current_y is None or abs(point[1] - current_y) <= y_tolerance:
            # 同一行
            current_row.append(point)
            current_y = point[1] if current_y is None else (current_y + point[1]) / 2
        else:
            # 新的一行
            if current_row:
                rows.append(sorted(current_row, key=lambda p: p[0]))  # 按x坐标排序
            current_row = [point]
            current_y = point[1]
    
    # 添加最后一行
    if current_row:
        rows.append(sorted(current_row, key=lambda p: p[0]))
    
    # 计算列数（取最大行的列数）
    max_cols = max(len(row) for row in rows) if rows else 0
    
    # 创建二维数组
    result_array = np.full((len(rows), max_cols), None, dtype=object)
    
    # 填充二维数组
    for row_idx, row_points in enumerate(rows):
        for col_idx, point in enumerate(row_points):
            result_array[row_idx][col_idx] = point
    
    return result_array

def calculate_image_rotation_angle(points_2d_array):
    """
    根据同一列的模板坐标计算图像整体偏移角度
    """
    if points_2d_array.size == 0:
        return 0.0
    
    angles = []
    
    # 遍历每一列，计算该列的倾斜角度
    for col in range(points_2d_array.shape[1]):
        column_points = []
        
        # 收集该列的所有有效点
        for row in range(points_2d_array.shape[0]):
            if points_2d_array[row][col] is not None:
                column_points.append(points_2d_array[row][col])
        
        # 如果该列有至少2个点，计算角度
        if len(column_points) >= 2:
            # 按y坐标排序
            column_points.sort(key=lambda p: p[1])
            
            # 计算该列的角度
            for i in range(len(column_points) - 1):
                point1 = column_points[i]
                point2 = column_points[i + 1]
                
                # 计算两点间的角度
                dx = point2[0] - point1[0]  # x方向差值
                dy = point2[1] - point1[1]  # y方向差值
                
                if dx != 0:  # 避免除零错误
                    angle = math.atan(dx / dy) * R2D  # 转换为度
                    angles.append(angle)
    
    # 计算平均角度
    if angles:
        avg_angle = sum(angles) / len(angles)
        print(f"检测到的角度: {[f'{a:.2f}' for a in angles]}")
        print(f"平均偏移角度: {avg_angle:.2f} 度")
        return avg_angle
    else:
        print("无法计算偏移角度：没有足够的列数据")
        return 0.0

def demo_rotation_angle():
    """
    演示角度计算功能
    """
    print("=== 图像偏移角度计算演示 ===")
    
    # 测试案例1：无旋转的模板排列
    print("\n测试案例1：无旋转的模板排列")
    points_no_rotation = [
        (100, 100), (200, 100), (300, 100),  # 第一行
        (100, 200), (200, 200), (300, 200),  # 第二行
        (100, 300), (200, 300), (300, 300),  # 第三行
    ]
    
    array1 = points_to_2d_array(points_no_rotation, 50, 50)
    angle1 = calculate_image_rotation_angle(array1)
    
    # 测试案例2：有旋转的模板排列（顺时针旋转约5度）
    print("\n测试案例2：有旋转的模板排列（顺时针旋转约5度）")
    # 模拟旋转后的坐标
    rotation_angle = 5.0  # 度
    cos_a = math.cos(rotation_angle * D2R)
    sin_a = math.sin(rotation_angle * D2R)
    
    points_rotated = []
    for x, y in points_no_rotation:
        # 绕原点旋转
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        points_rotated.append((new_x, new_y))
    
    array2 = points_to_2d_array(points_rotated, 50, 50)
    angle2 = calculate_image_rotation_angle(array2)
    
    # 测试案例3：不规则的模板排列
    print("\n测试案例3：不规则的模板排列")
    points_irregular = [
        (100, 100), (200, 105), (300, 98),   # 第一行（略有倾斜）
        (95, 200), (200, 200), (305, 195),   # 第二行（略有倾斜）
        (100, 300), (200, 300), (300, 300),  # 第三行
    ]
    
    array3 = points_to_2d_array(points_irregular, 50, 50)
    angle3 = calculate_image_rotation_angle(array3)
    
    print(f"\n总结:")
    print(f"无旋转情况: {angle1:.2f} 度")
    print(f"旋转5度情况: {angle2:.2f} 度")
    print(f"不规则排列: {angle3:.2f} 度")

if __name__ == "__main__":
    demo_rotation_angle()
