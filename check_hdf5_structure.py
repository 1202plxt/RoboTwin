
import h5py
import numpy as np
import os

# 查看数据结构
data_path = "/root/autodl-tmp/RoboTwin/data/aloha_place_a2b_left/train/episode_0.hdf5"

print(f"Checking file: {data_path}")
print("-" * 80)

with h5py.File(data_path, 'r') as f:
    def print_attrs(name, obj):
        print(name)
        if hasattr(obj, 'attrs'):
            for key, val in obj.attrs.items():
                print(f"  {key}: {val}")

    f.visititems(print_attrs)
    
    print("\n" + "=" * 80)
    print("数据集详情：")
    
    for key in f.keys():
        print(f"\n{key}:")
        data = f[key]
        if isinstance(data, h5py.Dataset):
            print(f"  shape: {data.shape}")
            print(f"  dtype: {data.dtype}")
            if data.shape[0] > 0:
                if len(data.shape) > 1:
                    print(f"  sample[0] shape: {data[0].shape}")
                else:
                    print(f"  sample[0]: {data[0]}")

