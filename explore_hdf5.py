
import sys
sys.path.append("./")

import h5py
import numpy as np
import os
import glob

def explore_hdf5_structure(file_path, indent=0):
    """递归探索HDF5文件结构"""
    prefix = "  " * indent
    
    def print_attrs(name, obj):
        print(f"{prefix}{name}")
        if hasattr(obj, 'attrs') and len(obj.attrs) > 0:
            for key, val in obj.attrs.items():
                print(f"{prefix}  [ATTR] {key}: {val}")
        if isinstance(obj, h5py.Dataset):
            print(f"{prefix}  [DATA] shape: {obj.shape}, dtype: {obj.dtype}")
            if obj.size <= 20:  # 小数据就直接打印
                try:
                    print(f"{prefix}  [VALUE] {obj[()]}")
                except:
                    pass
    
    with h5py.File(file_path, 'r') as f:
        print(f"\n📂 HDF5 文件: {file_path}")
        print("="*80)
        f.visititems(print_attrs)

def main():
    # 尝试查找示例数据文件
    data_patterns = [
        "./data_vlm/*/*/data/*.hdf5",
        "./data/*/*/data/*.hdf5",
        "./data/*/*/*.hdf5"
    ]
    
    found_files = []
    for pattern in data_patterns:
        files = glob.glob(pattern)
        found_files.extend(files)
    
    if found_files:
        print(f"找到 {len(found_files)} 个 HDF5 文件！")
        for file in found_files[:3]:  # 只查看前3个
            explore_hdf5_structure(file)
    else:
        print("❌ 没有找到 HDF5 文件！")
        print("💡 请先运行数据收集命令：")
        print("bash collect_data.sh place_a2b_left vlm_training 0")

if __name__ == "__main__":
    main()
