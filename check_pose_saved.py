#!/usr/bin/env python3
"""
🔍 检查物体坐标数据是否保存到HDF5文件中
"""

import h5py
import numpy as np

def check_hdf5_pose_data(hdf5_path):
    """
    检查HDF5文件中是否包含物体坐标信息
    """
    print("=" * 80)
    print(f"🔍 检查HDF5文件: {hdf5_path}")
    print("=" * 80)
    print()

    try:
        with h5py.File(hdf5_path, 'r') as f:
            print("✅ 文件可以正常打开")
            print()

            # 递归打印文件结构
            def print_structure(name, obj):
                indent = "  " * name.count('/')
                if isinstance(obj, h5py.Dataset):
                    shape = obj.shape
                    dtype = obj.dtype
                    print(f"{indent}📊 {name}: shape={shape}, dtype={dtype}")
                else:
                    print(f"{indent}📁 {name}/")

            print("📂 文件结构:")
            f.visititems(print_structure)
            print()

            # 检查是否有 endpose 数据
            if 'endpose' in f:
                print("✅ 找到 'endpose' 数据组！")
                print()
                endpose = f['endpose']
                print("endpose 包含的keys:")
                for key in endpose.keys():
                    dataset = endpose[key]
                    if isinstance(dataset, h5py.Dataset):
                        print(f"  - {key}: shape={dataset.shape}, dtype={dataset.dtype}")
                        # 如果是第一帧，显示一些示例数据
                        if dataset.shape[0] > 0:
                            print(f"    示例数据（第0帧）: {dataset[0] if len(dataset.shape) == 1 else dataset[0][:3]}")
                print()

                # 检查是否有物体坐标
                pose_keys = [k for k in endpose.keys() if '_pos' in k or '_quat' in k]
                if pose_keys:
                    print(f"✅ 找到 {len(pose_keys)} 个物体坐标数据集！")
                    print("物体列表:")
                    for key in pose_keys[:10]:  # 只显示前10个
                        print(f"  - {key}")
                    if len(pose_keys) > 10:
                        print(f"  ... 还有 {len(pose_keys) - 10} 个")
                else:
                    print("⚠️ 未找到物体坐标数据（_pos, _quat）")
            else:
                print("⚠️ 未找到 'endpose' 数据组")
                print()
                print("这说明你的物体坐标代码可能没有正确执行。")
                print("请检查：")
                print("  1. _take_picture 方法中的代码是否被正确执行")
                print("  2. pkl_dic['endpose'] 是否被正确初始化")
                print("  3. 是否有错误被忽略")
            print()

    except FileNotFoundError:
        print(f"❌ 文件不存在: {hdf5_path}")
        print()
        print("请确保：")
        print("  1. 数据采集已经完成")
        print("  2. HDF5文件已经生成")
        print("  3. 路径正确")
        print()
        print("示例路径应该是:")
        print("  data/place_a2b_left/demo_randomized/data/episode0.hdf5")
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        import traceback
        traceback.print_exc()


def check_pkl_cache():
    """
    检查缓存的pkl文件是否包含物体坐标
    """
    print("\n" + "=" * 80)
    print("🔍 检查PKL缓存文件")
    print("=" * 80)
    print()

    import pickle
    import os

    cache_dir = "data/place_a2b_left/demo_randomized/.cache/episode0/"

    if not os.path.exists(cache_dir):
        print(f"⚠️ 缓存目录不存在: {cache_dir}")
        print("这可能意味着数据采集还没有执行，或者缓存已经被清理。")
        return

    pkl_files = [f for f in os.listdir(cache_dir) if f.endswith('.pkl')]
    if not pkl_files:
        print("⚠️ 缓存目录中没有pkl文件")
        return

    # 读取第一个pkl文件
    pkl_path = os.path.join(cache_dir, "0.pkl")
    if not os.path.exists(pkl_path):
        pkl_path = os.path.join(cache_dir, sorted(pkl_files)[0])

    print(f"读取文件: {pkl_path}")
    print()

    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)

        print(f"✅ PKL文件包含的顶层keys: {list(data.keys())}")
        print()

        if 'endpose' in data:
            print("✅ 找到 'endpose' 数据！")
            endpose = data['endpose']
            print(f"endpose 包含的keys: {list(endpose.keys())}")
            print()

            # 查找物体坐标相关的数据
            pose_keys = [k for k in endpose.keys() if '_pos' in k or '_quat' in k]
            if pose_keys:
                print(f"✅ 找到 {len(pose_keys)} 个物体坐标数据:")
                for key in pose_keys[:15]:  # 只显示前15个
                    value = endpose[key]
                    if isinstance(value, list):
                        print(f"  - {key}: {value[:3]}...")
                    else:
                        print(f"  - {key}: {value}")
                if len(pose_keys) > 15:
                    print(f"  ... 还有 {len(pose_keys) - 15} 个")
            else:
                print("⚠️ 未找到物体坐标数据（_pos, _quat）")
                print()
                print("这说明你的代码可能没有正确执行。")
                print("请检查 _take_picture 方法中的代码。")
        else:
            print("⚠️ 未找到 'endpose' 数据")
            print()
            print("这意味着你的物体坐标记录代码没有被执行。")
            print("请检查：")
            print("  1. _take_picture 方法中是否添加了记录代码")
            print("  2. pkl_dic['endpose'] 是否被正确初始化")
            print("  3. 代码缩进是否正确")

    except Exception as e:
        print(f"❌ 读取pkl文件时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 80)
    print("🎯 RoboTwin 物体坐标数据检查工具")
    print("=" * 80)
    print()
    print("请确保在 RoboTwin 项目根目录运行此脚本：")
    print("  cd ~/autodl-tmp/RoboTwin")
    print()

    # 检查HDF5文件
    hdf5_path = "data/place_a2b_left/demo_randomized/data/episode0.hdf5"
    if len(sys.argv) > 1:
        hdf5_path = sys.argv[1]

    check_hdf5_pose_data(hdf5_path)

    # 检查PKL缓存（可选）
    print("\n是否检查PKL缓存文件？(可能需要数据采集完成后、合并前才有)")
    print("按 Ctrl+C 跳过，或等待10秒...")
    import time
    try:
        time.sleep(10)
        check_pkl_cache()
    except KeyboardInterrupt:
        print("\n\n跳过PKL检查。")

    print()
    print("=" * 80)
    print("✅ 检查完成")
    print("=" * 80)
