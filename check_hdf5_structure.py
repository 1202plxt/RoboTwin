#!/usr/bin/env python3
"""
查看HDF5文件结构
"""

import h5py
import numpy as np

def print_structure(name, obj):
    """递归打印HDF5结构"""
    indent = "  " * (name.count("/"))
    if isinstance(obj, h5py.Group):
        print(f"{indent}📁 {name}")
    elif isinstance(obj, h5py.Dataset):
        print(f"{indent}📊 {name:40} shape={obj.shape} dtype={obj.dtype}")

def check_hdf5_structure(hdf5_path):
    print("=" * 80)
    print("🔍 HDF5文件结构分析")
    print("=" * 80)
    
    with h5py.File(hdf5_path, 'r') as f:
        f.visititems(print_structure)
        
        print("\n" + "=" * 80)
        print("📸 查看相机配置数据（首帧）")
        print("=" * 80)
        
        if 'observation' in f:
            for cam_name in ['head_camera', 'left_camera', 'right_camera']:
                if cam_name in f['observation']:
                    print(f"\n🎥 {cam_name}:")
                    if 'intrinsic_cv' in f['observation'][cam_name]:
                        print(f"  intrinsic_cv: shape={f['observation'][cam_name]['intrinsic_cv'].shape}")
                        print(f"  {f['observation'][cam_name]['intrinsic_cv'][0]}")
                    if 'extrinsic_cv' in f['observation'][cam_name]:
                        print(f"  extrinsic_cv: shape={f['observation'][cam_name]['extrinsic_cv'].shape}")
                        print(f"  {f['observation'][cam_name]['extrinsic_cv'][0]}")
                    if 'cam2world_gl' in f['observation'][cam_name]:
                        print(f"  cam2world_gl: shape={f['observation'][cam_name]['cam2world_gl'].shape}")
                    if 'rgb' in f['observation'][cam_name]:
                        print(f"  rgb: shape={f['observation'][cam_name]['rgb'].shape}")
        
        print("\n" + "=" * 80)
        print("📦 查看物体坐标数据")
        print("=" * 80)
        
        if 'endpose' in f:
            objects = set()
            for key in f['endpose'].keys():
                if '_pos' in key:
                    obj_name = key.replace('_pos', '')
                    objects.add(obj_name)
            
            print(f"检测到 {len(objects)} 个物体:")
            for obj_name in sorted(objects):
                pos_key = f"{obj_name}_pos"
                quat_key = f"{obj_name}_quat"
                print(f"  • {obj_name}")
                if pos_key in f['endpose']:
                    print(f"    - 位置: {f['endpose'][pos_key].shape}")
                    print(f"    - 首帧: {f['endpose'][pos_key][0]}")
                if quat_key in f['endpose']:
                    print(f"    - 旋转: {f['endpose'][quat_key].shape}")

if __name__ == "__main__":
    import sys
    
    hdf5_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    if hdf5_path:
        check_hdf5_structure(hdf5_path)
    else:
        print("请提供HDF5文件路径")
        print("用法: python check_hdf5_structure.py data/xxx/demo_randomized/data/episode0.hdf5")
