#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示按模板排列组织的二维数组转换功能
"""

import numpy as np
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

def demo_template_array():
    """
    演示按模板排列的二维数组转换
    """
    print("=== 按模板排列的二维数组转换演示 ===")
    
    # 模拟一个3x3的模板排列，允许y方向有误差
    unique_points = [
        # 第一行
        (100, 100),   # 第0行第0列
        (200, 105),   # 第0行第1列 (y方向有5像素误差)
        (300, 98),    # 第0行第2列 (y方向有2像素误差)
        
        # 第二行
        (95, 200),    # 第1行第0列 (x方向有5像素误差)
        (200, 200),   # 第1行第1列
        (305, 195),   # 第1行第2列 (x,y方向都有误差)
        
        # 第三行
        (100, 300),   # 第2行第0列
        (200, 300),   # 第2行第1列
        (300, 300),   # 第2行第2列
    ]
    
    template_width = 50
    template_height = 50
    y_tolerance = template_height / 3  # 约16.67像素
    
    print(f"模板尺寸: {template_width} x {template_height}")
    print(f"Y方向容差: {y_tolerance:.1f} 像素")
    print(f"原始匹配点: {unique_points}")
    
    # 转换为二维数组
    points_2d_array = points_to_2d_array(unique_points, template_width, template_height)
    
    print(f"\n二维数组形状: {points_2d_array.shape}")
    print("二维数组内容:")
    
    # 打印二维数组内容
    for i in range(points_2d_array.shape[0]):
        row_content = []
        for j in range(points_2d_array.shape[1]):
            if points_2d_array[i][j] is not None:
                row_content.append(f"({points_2d_array[i][j][0]},{points_2d_array[i][j][1]})")
            else:
                row_content.append("None")
        print(f"  第{i}行: {row_content}")
    
    print("\n访问示例:")
    print(f"array[0][0] = {points_2d_array[0][0]}")  # 最靠近左上角的模板
    print(f"array[0][1] = {points_2d_array[0][1]}")  # 其右边的模板
    print(f"array[1][0] = {points_2d_array[1][0]}")  # 第二行第一个
    print(f"array[2][2] = {points_2d_array[2][2]}")  # 第三行第三个
    
    print("\n验证Y方向容差:")
    for i in range(points_2d_array.shape[0]):
        row_y_values = []
        for j in range(points_2d_array.shape[1]):
            if points_2d_array[i][j] is not None:
                row_y_values.append(points_2d_array[i][j][1])
        if len(row_y_values) > 1:
            y_range = max(row_y_values) - min(row_y_values)
            print(f"第{i}行Y坐标范围: {min(row_y_values)}-{max(row_y_values)} (范围: {y_range:.1f}像素)")

if __name__ == "__main__":
    demo_template_array()
