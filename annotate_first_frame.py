#!/usr/bin/env python3
"""
在首帧图像上标注物体坐标
"""

import h5py
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def get_colors(n):
    """生成n种不同的颜色"""
    # 使用一些鲜明的颜色
    base_colors = [
        (255, 0, 0),      # 红色
        (0, 255, 0),      # 绿色
        (0, 0, 255),      # 蓝色
        (255, 255, 0),    # 黄色
        (255, 0, 255),    # 洋红
        (0, 255, 255),    # 青色
        (255, 128, 0),    # 橙色
        (128, 0, 255),    # 紫色
        (0, 255, 128),    # 青绿色
        (255, 128, 128),  # 浅红
        (128, 255, 128),  # 浅绿
        (128, 128, 255),  # 浅蓝
    ]
    # 扩展颜色列表
    colors = []
    for i in range(n):
        colors.append(base_colors[i % len(base_colors)])
    return colors

def project_point_to_image(point_3d, intrinsic, extrinsic):
    """
    将3D点投影到2D图像
    
    参数:
        point_3d: 3D坐标 (x, y, z)
        intrinsic: 相机内参矩阵 (3x3)
        extrinsic: 相机外参矩阵 (4x4, world_to_cam)
    
    返回:
        2D图像坐标 (u, v)
    """
    # 将3D点转换为齐次坐标
    point_homogeneous = np.array([point_3d[0], point_3d[1], point_3d[2], 1.0])
    
    # 从世界坐标系转换到相机坐标系
    point_cam = extrinsic @ point_homogeneous
    
    # 投影到图像平面
    point_image = intrinsic @ point_cam[:3]
    
    # 归一化
    u = point_image[0] / point_image[2]
    v = point_image[1] / point_image[2]
    
    return int(u), int(v)

def draw_annotation(image, u, v, label, color):
    """
    在图像上绘制标注
    
    参数:
        image: 输入图像
        u, v: 图像坐标
        label: 标签文本
        color: 颜色
    """
    # 绘制圆点
    cv2.circle(image, (u, v), 8, color, -1)
    cv2.circle(image, (u, v), 10, (0, 0, 0), 2)
    
    # 绘制标签
    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
    cv2.rectangle(
        image, 
        (u - 5, v + 10), 
        (u + label_size[0] + 5, v + 30), 
        color, 
        -1
    )
    cv2.putText(
        image, 
        label, 
        (u, v + 25), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        0.5, 
        (0, 0, 0), 
        2
    )
    
    return image

def decode_jpeg(jpeg_bytes):
    """解码JPEG数据"""
    nparr = np.frombuffer(jpeg_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def annotate_first_frame(hdf5_path, output_dir=None, camera_name='head_camera'):
    """
    在首帧图像上标注物体坐标
    
    参数:
        hdf5_path: HDF5文件路径
        output_dir: 输出目录（可选）
        camera_name: 相机名称（默认为head_camera）
    """
    print("=" * 80)
    print("📸 首帧物体坐标标注")
    print("=" * 80)
    
    # 创建输出目录
    if output_dir is None:
        output_dir = os.path.dirname(hdf5_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出文件路径
    base_name = os.path.basename(hdf5_path).replace('.hdf5', '')
    output_path = os.path.join(output_dir, f"{base_name}_annotated.png")
    
    with h5py.File(hdf5_path, 'r') as f:
        # 检查相机是否存在
        if 'observation' not in f or camera_name not in f['observation']:
            print(f"❌ 找不到相机 {camera_name} 的数据")
            available_cameras = [k for k in f['observation'].keys()] if 'observation' in f else []
            print(f"可用的相机: {available_cameras}")
            return None
        
        print(f"\n🎥 使用相机: {camera_name}")
        
        # 获取相机参数（首帧）
        try:
            intrinsic_data = f['observation'][camera_name]['intrinsic_cv']
            cam2world_data = f['observation'][camera_name]['extrinsic_cv']
            
            print(f"  intrinsic shape: {intrinsic_data.shape}")
            print(f"  cam2world shape: {cam2world_data.shape}")
            
            # 获取首帧数据
            if len(intrinsic_data.shape) == 3:
                intrinsic = intrinsic_data[0]
            else:
                intrinsic = intrinsic_data[:]
                
            if len(cam2world_data.shape) == 3:
                cam2world = cam2world_data[0]
            else:
                cam2world = cam2world_data[:]
            
            # 确保矩阵是正确的形状
            intrinsic = intrinsic.reshape(3, 3)
            cam2world = cam2world.reshape(4, 4)
            
            # 将 cam2world 转换为 world2cam（取逆）
            extrinsic = np.linalg.inv(cam2world)
            print(f"✅ 读取相机内参和外参")
            print(f"   内参:\n{intrinsic}")
            print(f"   cam2world:\n{cam2world}")
            print(f"   world2cam:\n{extrinsic}")
        except Exception as e:
            print(f"❌ 读取相机参数失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # 获取首帧图像
        try:
            rgb_data = f['observation'][camera_name]['rgb'][0]
            # 检查是JPEG编码还是原始数据
            if isinstance(rgb_data, bytes):
                image = decode_jpeg(rgb_data)
            else:
                image = rgb_data.copy()
            
            # 转换BGR到RGB（因为cv2读取的是BGR）
            if len(image.shape) == 3 and image.shape[2] == 3:
                # 检查是否需要转换颜色空间
                # 如果数据已经是BGR（来自cv2.imdecode），保持原样
                pass
            
            print(f"✅ 读取首帧图像: shape={image.shape}")
        except Exception as e:
            print(f"❌ 读取图像失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # 获取物体列表
        if 'endpose' not in f:
            print("❌ 找不到 endpose 数据")
            return None
        
        objects = set()
        for key in f['endpose'].keys():
            if '_pos' in key:
                obj_name = key.replace('_pos', '')
                objects.add(obj_name)
        
        print(f"\n📦 检测到 {len(objects)} 个物体")
        
        # 生成颜色
        colors = get_colors(len(objects))
        
        # 复制图像用于标注
        annotated_image = image.copy()
        
        # 在图像上标注每个物体
        object_info = []
        
        for i, obj_name in enumerate(sorted(objects)):
            pos_key = f"{obj_name}_pos"
            
            if pos_key not in f['endpose']:
                continue
            
            # 获取首帧的3D位置
            point_3d = f['endpose'][pos_key][0]
            
            # 投影到2D图像
            try:
                u, v = project_point_to_image(point_3d, intrinsic, extrinsic)
                
                # 检查坐标是否在图像范围内
                h, w = image.shape[:2]
                if 0 <= u < w and 0 <= v < h:
                    # 绘制标注
                    color = colors[i]
                    label = obj_name
                    annotated_image = draw_annotation(annotated_image, u, v, label, color)
                    
                    info = {
                        'name': obj_name,
                        'position_3d': point_3d.tolist(),
                        'position_2d': (u, v),
                        'color': color
                    }
                    object_info.append(info)
                    
                    print(f"✅ {obj_name}:")
                    print(f"   3D位置: {point_3d}")
                    print(f"   2D位置: ({u}, {v})")
                else:
                    print(f"⚠️ {obj_name}: 投影坐标超出图像范围 ({u}, {v})")
            except Exception as e:
                print(f"❌ 投影 {obj_name} 失败: {e}")
        
        # 保存标注后的图像
        cv2.imwrite(output_path, annotated_image)
        print(f"\n💾 标注图像已保存: {output_path}")
        
        # 同时保存一个带matplotlib的版本，方便查看
        fig, ax = plt.subplots(1, figsize=(12, 9))
        ax.imshow(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
        ax.axis('off')
        plt.title(f"Object Coordinates - First Frame", fontsize=14)
        
        # 添加图例
        legend_elements = []
        for info in object_info:
            # 将BGR (0-255) 转换为RGB归一化 (0-1)
            color_rgb = (info['color'][2]/255, info['color'][1]/255, info['color'][0]/255)
            legend_elements.append(patches.Patch(
                facecolor=color_rgb, 
                label=f"{info['name']}\n({info['position_3d'][0]:.3f}, {info['position_3d'][1]:.3f}, {info['position_3d'][2]:.3f})"
            ))
        
        if legend_elements:
            ax.legend(
                handles=legend_elements,
                loc='upper right',
                bbox_to_anchor=(1.28, 1),
                fontsize=10
            )
        
        plt.tight_layout()
        matplotlib_output = output_path.replace('.png', '_matplotlib.png')
        plt.savefig(matplotlib_output, dpi=150, bbox_inches='tight')
        print(f"💾 Matplotlib版本已保存: {matplotlib_output}")
        
        plt.close()
        
        return output_path, object_info

def batch_annotate(data_dir, camera_name='head_camera'):
    """
    批量标注一个目录下的所有episode
    
    参数:
        data_dir: 数据目录（如 data/place_a2b_left/demo_randomized/data）
        camera_name: 相机名称
    """
    if not os.path.exists(data_dir):
        print(f"❌ 目录不存在: {data_dir}")
        return
    
    # 查找所有HDF5文件
    hdf5_files = []
    for file in os.listdir(data_dir):
        if file.startswith('episode') and file.endswith('.hdf5'):
            hdf5_files.append(os.path.join(data_dir, file))
    
    hdf5_files.sort()
    print(f"📁 找到 {len(hdf5_files)} 个episode文件")
    
    results = []
    for hdf5_path in hdf5_files:
        print(f"\n{'='*80}")
        print(f"处理: {os.path.basename(hdf5_path)}")
        print('='*80)
        
        result = annotate_first_frame(hdf5_path, camera_name=camera_name)
        if result:
            results.append(result)
    
    print(f"\n✅ 完成，共处理 {len(results)} 个episode")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  单个文件: python annotate_first_frame.py <hdf5_path> [camera_name]")
        print("  批量处理: python annotate_first_frame.py --batch <data_dir> [camera_name]")
        print("\n示例:")
        print("  python annotate_first_frame.py data/place_a2b_left/demo_randomized/data/episode0.hdf5")
        print("  python annotate_first_frame.py --batch data/place_a2b_left/demo_randomized/data")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        data_dir = sys.argv[2]
        camera_name = sys.argv[3] if len(sys.argv) > 3 else 'head_camera'
        batch_annotate(data_dir, camera_name)
    else:
        hdf5_path = sys.argv[1]
        camera_name = sys.argv[2] if len(sys.argv) > 2 else 'head_camera'
        result = annotate_first_frame(hdf5_path, camera_name=camera_name)
