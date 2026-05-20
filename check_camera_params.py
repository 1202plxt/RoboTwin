#!/usr/bin/env python3
"""
检查HDF5文件中相机参数的形状
"""

import h5py
import numpy as np
import sys

if len(sys.argv) < 2:
    print("请提供HDF5文件路径")
    sys.exit(1)

hdf5_path = sys.argv[1]

with h5py.File(hdf5_path, 'r') as f:
    print("=" * 80)
    print("📸 检查相机参数")
    print("=" * 80)
    
    for cam_name in ['head_camera', 'left_camera', 'right_camera']:
        if cam_name in f['observation']:
            print(f"\n🎥 {cam_name}:")
            
            for key in ['intrinsic_cv', 'extrinsic_cv', 'cam2world_gl']:
                if key in f['observation'][cam_name]:
                    data = f['observation'][cam_name][key]
                    print(f"  {key}: shape={data.shape} dtype={data.dtype}")
                    if len(data.shape) > 1:
                        print(f"  首帧:\n{data[0]}")
