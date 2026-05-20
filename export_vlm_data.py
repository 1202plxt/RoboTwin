
import sys
sys.path.append("./")

import h5py
import numpy as np
import os
import json
from PIL import Image
import argparse
from pathlib import Path

def project_3d_to_2d(point_3d, camera_intrinsic, camera_extrinsic):
    """
    将 3D 点投影到 2D 图像平面
    point_3d: [x, y, z]
    camera_intrinsic: 3x3 内参矩阵
    camera_extrinsic: 4x4 外参矩阵
    返回: [u, v] 像素坐标
    """
    # 转换到相机坐标系
    point_hom = np.array([point_3d[0], point_3d[1], point_3d[2], 1.0])
    point_cam = np.linalg.inv(camera_extrinsic) @ point_hom
    point_cam = point_cam[:3] / point_cam[3] if point_cam[3] != 0 else point_cam[:3]
    
    # 投影到图像平面
    point_img_hom = camera_intrinsic @ point_cam
    point_img = point_img_hom[:2] / point_img_hom[2]
    
    return point_img

def get_bbox_from_segmentation(segmentation_mask, actor_id=None):
    """
    从分割图中计算物体的 bounding box
    """
    if actor_id is None:
        # 找到所有非零像素
        coords = np.argwhere(segmentation_mask > 0)
    else:
        coords = np.argwhere(segmentation_mask == actor_id)
    
    if len(coords) == 0:
        return None
    
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)
    
    return [int(x_min), int(y_min), int(x_max), int(y_max)]

def export_episode_for_vlm(hdf5_path, output_dir):
    """
    从一个 episode 的 HDF5 文件中导出 VLM 训练数据
    包含：RGB图像 + 分割图 + Bounding Boxes + 3D坐标
    """
    print(f"处理文件: {hdf5_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    with h5py.File(hdf5_path, 'r') as f:
        # 查看文件结构
        print("HDF5 文件结构:")
        def print_attrs(name, obj):
            print(f"  {name}")
        f.visititems(print_attrs)
        
        # 假设数据结构是按时间步保存的（你需要根据实际结构调整）
        # 这里只是一个框架，你需要根据实际数据结构来调整
        
        # 导出一个简单的示例JSON
        output_json = {
            "info": "这是一个 VLM 训练数据导出框架",
            "hdf5_path": hdf5_path,
            "tips": [
                "1. 根据实际 HDF5 数据结构修改此脚本",
                "2. 利用 data_type 中的 mesh_segmentation 和 actor_segmentation",
                "3. 结合 endpose 中的物体 3D 坐标",
                "4. 使用相机内参投影计算 2D BBox"
            ]
        }
        
        with open(os.path.join(output_dir, "vlm_export_example.json"), "w") as f_json:
            json.dump(output_json, f_json, indent=2, ensure_ascii=False)
        
        print(f"导出完成！查看: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="导出 RoboTwin 数据用于 VLM 训练")
    parser.add_argument("--data_dir", type=str, default="./data_vlm", 
                        help="数据目录")
    parser.add_argument("--output_dir", type=str, default="./vlm_dataset", 
                        help="输出目录")
    
    args = parser.parse_args()
    
    # 先查看一下数据目录结构
    print(f"查看数据目录: {args.data_dir}")
    if os.path.exists(args.data_dir):
        for root, dirs, files in os.walk(args.data_dir):
            for file in files:
                if file.endswith('.hdf5'):
                    full_path = os.path.join(root, file)
                    print(f"  找到: {full_path}")
                    
                    # 处理第一个文件作为示例
                    episode_name = Path(full_path).stem
                    export_episode_for_vlm(full_path, os.path.join(args.output_dir, episode_name))
                    return
    else:
        print("❌ 数据目录不存在！请先运行数据收集脚本：")
        print("bash collect_data.sh place_a2b_left vlm_training 0")

if __name__ == "__main__":
    main()
