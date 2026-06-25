import cv2
import numpy as np
import matplotlib.pyplot as plt # 用于显示图像，可选
import os

print(f"OpenCV version: {cv2.__version__}")

# 尝试创建SIFT对象，以检查可用性
try:
    sift = cv2.SIFT_create()
    print("SIFT detector created successfully.")
except cv2.error as e:
    print(f"Error creating SIFT object: {e}")
    print("SIFT might not be available in your OpenCV build.")
    print("Try installing 'opencv-contrib-python': pip install opencv-contrib-python")
    exit()

# --- 1. 在单张图像上检测SIFT特征 ---
def detect_sift_features_single_image(image_path):
    """
    在单张图像上检测SIFT特征点和描述子，并可视化。
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"错误：无法加载图像 {image_path}")
        return

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. 创建 SIFT 对象 (已在全局创建，也可以在函数内创建)
    # sift = cv2.SIFT_create() # 可调整参数，如 nfeatures, nOctaveLayers, contrastThreshold 等

    # 4. 检测关键点
    keypoints = sift.detect(gray_img, None)
    # 或者，一步到位检测关键点并计算描述子:
    # keypoints, descriptors = sift.detectAndCompute(gray_img, None)

    # 5. 计算描述子
    # 如果只用了 detect()，需要单独计算描述子
    keypoints, descriptors = sift.compute(gray_img, keypoints)

    print(f"\n--- 单张图像分析: {image_path} ---")
    print(f"检测到的关键点数量: {len(keypoints)}")
    if descriptors is not None:
        print(f"描述子的形状: {descriptors.shape}") # (数量, 128) SIFT描述子是128维的

    # 6. 绘制关键点
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS 会绘制关键点的大小和方向
    img_with_keypoints = cv2.drawKeypoints(gray_img, keypoints, img.copy(), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # 使用 matplotlib 显示 (OpenCV的 imshow 在某些环境下可能行为不一致)
    plt.figure(figsize=(10, 8))
    plt.imshow(cv2.cvtColor(img_with_keypoints, cv2.COLOR_BGR2RGB))
    plt.title(f'SIFT Keypoints on {image_path.split("/")[-1]}')
    plt.axis('off')
    plt.show()

    # 或者使用 OpenCV 的 imshow (按任意键关闭窗口)
    # cv2.imshow(f'SIFT Keypoints on {image_path.split("/")[-1]}', img_with_keypoints)
    # cv2.waitKey(0)
    # cv2.destroyWindow(f'SIFT Keypoints on {image_path.split("/")[-1]}')

    return keypoints, descriptors, img

# --- 2. 在两张图像之间匹配SIFT特征 ---
def match_sift_features(img1_path, img2_path, good_match_ratio=0.7):
    """
    在两张图像之间检测并匹配SIFT特征。
    """
    kp1, des1, img1_bgr = detect_sift_features_single_image(img1_path)
    kp2, des2, img2_bgr = detect_sift_features_single_image(img2_path)

    if des1 is None or des2 is None:
        print("错误：其中一个图像未能成功提取描述子，无法进行匹配。")
        return

    print("\n--- 特征匹配 ---")
    # 创建 BFMatcher (Brute-Force Matcher) 对象
    # NORM_L2 适用于 SIFT/SURF 等浮点描述子
    # NORM_HAMMING 适用于 ORB/BRIEF/BRISK 等二进制字符串描述子
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False) # crossCheck=True 会返回更可靠的匹配，但会减少匹配数量

    # 使用 k-NN (k-Nearest Neighbors) 匹配
    # 对于每个 des1 中的描述子，在 des2 中找到 k 个最佳匹配
    matches = bf.knnMatch(des1, des2, k=2)
    print(f"初始 k-NN 匹配数量 (k=2): {len(matches)}")

    # 应用 Lowe's Ratio Test 来筛选好的匹配
    good_matches = []
    for m_pair in matches:
        if len(m_pair) == 2: # 确保knn返回了两个邻居
            m, n = m_pair
            if m.distance < good_match_ratio * n.distance:
                good_matches.append(m)
        elif len(m_pair) == 1: # 有时可能只返回一个 (如果crossCheck=True 或 k=1)
             # 如果 k=1, 那么直接添加，但通常 ratio test 用于 k=2
             pass # good_matches.append(m_pair[0]) # 如果 k=1

    print(f"经过 Lowe's Ratio Test 筛选后的 '好' 匹配数量: {len(good_matches)}")

    # 绘制好的匹配
    # img_matches = cv2.drawMatches(img1_bgr, kp1, img2_bgr, kp2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # 如果要绘制所有 knn 匹配中的最佳匹配（不经过ratio test），可以使用 matches1to2 = [m[0] for m in matches if len(m)>0]
    img_matches = cv2.drawMatchesKnn(img1_bgr, kp1, img2_bgr, kp2, [m_pair for m_pair in matches if len(m_pair)==2 and m_pair[0] in good_matches], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)


    plt.figure(figsize=(16, 8))
    plt.imshow(cv2.cvtColor(img_matches, cv2.COLOR_BGR2RGB))
    plt.title(f'SIFT Feature Matching (Good Matches: {len(good_matches)})')
    plt.axis('off')
    plt.show()

    # cv2.imshow('SIFT Matches', img_matches)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # 如果需要进行更高级的操作，例如查找单应性矩阵 (Homography)
    if len(good_matches) > 10: # MIN_MATCH_COUNT
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # 计算单应性矩阵
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is not None:
            matchesMask = mask.ravel().tolist()
            h, w = cv2.cvtColor(img1_bgr, cv2.COLOR_BGR2GRAY).shape
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            if pts is not None and M is not None:
                 dst_corners = cv2.perspectiveTransform(pts, M)
                 # 在第二张图上绘制边界框
                 img2_bgr_homography = cv2.polylines(img2_bgr.copy(), [np.int32(dst_corners)], True, (0,255,0), 3, cv2.LINE_AA)

                 plt.figure(figsize=(10, 8))
                 plt.imshow(cv2.cvtColor(img2_bgr_homography, cv2.COLOR_BGR2RGB))
                 plt.title('Detected Object in Second Image (Homography)')
                 plt.axis('off')
                 plt.show()
        else:
            print("无法计算单应性矩阵。")
            matchesMask = None
            print(f"Homography matrix (M): {M}")


        # 绘制内点 (inliers)
        # draw_params = dict(matchColor=(0, 255, 0), # draw matches in green color
        #                singlePointColor=None,
        #                matchesMask=matchesMask, # draw only inliers
        #                flags=2)
        # img_inliers = cv2.drawMatches(img1_bgr, kp1, img2_bgr, kp2, good_matches, None, **draw_params)

        # plt.figure(figsize=(16, 8))
        # plt.imshow(cv2.cvtColor(img_inliers, cv2.COLOR_BGR2RGB))
        # plt.title(f'SIFT Feature Matching (Inliers after RANSAC: {sum(matchesMask) if matchesMask else 0})')
        # plt.axis('off')
        # plt.show()

    else:
        print(f"没有足够的匹配点 ({len(good_matches)}) 来计算单应性矩阵。")


# --- 主程序调用 ---
if __name__ == '__main__':
    # 请将以下路径替换为你的图像路径
    # 为了演示，你需要两张包含一些共同特征的图像
    # 例如，一张是场景，另一张是场景中的一个物体或者场景的另一个视角
    image1_path = 'path/to/your/image1.jpg' # 例如：包含物体的图像
    image2_path = 'path/to/your/image2.jpg' # 例如：包含相同物体的场景图像

    # 提示用户输入路径，或使用占位符
    print("请输入第一张图像的路径 (例如: ./box.png):")
    image1_path_input = input().strip()
    if not image1_path_input:
        image1_path_input = 'box.png' # 默认或示例路径
        print(f"使用默认路径: {image1_path_input}")

    print("请输入第二张图像的路径 (例如: ./box_in_scene.png):")
    image2_path_input = input().strip()
    if not image2_path_input:
        image2_path_input = 'box_in_scene.png' # 默认或示例路径
        print(f"使用默认路径: {image2_path_input}")

    # 检查文件是否存在

    if not os.path.exists(image1_path_input):
        print(f"错误: 图像文件 {image1_path_input} 不存在。请确保路径正确或下载示例图像。")
        print("你可以从 OpenCV 教程中获取示例图像，例如 'box.png' 和 'box_in_scene.png'")
        exit()
    if not os.path.exists(image2_path_input):
        print(f"错误: 图像文件 {image2_path_input} 不存在。请确保路径正确或下载示例图像。")
        exit()


    # 1. 单张图像的SIFT特征检测
    print("\n--- 分析第一张图像 ---")
    detect_sift_features_single_image(image1_path_input)

    # 2. 两张图像之间的SIFT特征匹配
    print("\n--- 匹配两张图像的特征 ---")
    match_sift_features(image1_path_input, image2_path_input, good_match_ratio=0.75)

    print("\n处理完成。")