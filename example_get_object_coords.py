#!/usr/bin/env python3
"""
示例脚本：演示如何在 RoboTwin 环境中获取物体的坐标信息
"""

import sys
import os

# 确保可以导入 envs 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from envs.place_a2b_left import place_a2b_left
import numpy as np


def demo_object_coords():
    """演示如何获取物体坐标"""
    print("=" * 60)
    print("RoboTwin 物体坐标获取示例")
    print("=" * 60)
    
    # 初始化环境
    print("\n1. 初始化环境...")
    env = place_a2b_left()
    env.setup_demo(
        task_name="place_a2b_left",
        domain_randomization={
            "random_background": False,
            "cluttered_table": False,
            "random_light": False
        },
        render_freq=0,
        save_data=False
    )
    
    print("\n2. 获取环境中的物体...")
    # 访问环境中的物体对象
    if hasattr(env, 'object'):
        print(f"   - 找到物体 A: {env.object.get_name()}")
    if hasattr(env, 'target_object'):
        print(f"   - 找到物体 B: {env.target_object.get_name()}")
    
    print("\n3. 获取物体坐标信息...")
    
    # 获取物体 A 的位姿和坐标
    pose_a = env.object.get_pose()
    position_a = pose_a.p
    quaternion_a = pose_a.q
    
    print(f"\n   物体 A 的信息:")
    print(f"   - 位置 (x, y, z): {position_a[0]:.4f}, {position_a[1]:.4f}, {position_a[2]:.4f}")
    print(f"   - 四元数 (w, x, y, z): {quaternion_a[0]:.4f}, {quaternion_a[1]:.4f}, {quaternion_a[2]:.4f}, {quaternion_a[3]:.4f}")
    
    # 获取物体 B 的位姿和坐标
    pose_b = env.target_object.get_pose()
    position_b = pose_b.p
    quaternion_b = pose_b.q
    
    print(f"\n   物体 B 的信息:")
    print(f"   - 位置 (x, y, z): {position_b[0]:.4f}, {position_b[1]:.4f}, {position_b[2]:.4f}")
    print(f"   - 四元数 (w, x, y, z): {quaternion_b[0]:.4f}, {quaternion_b[1]:.4f}, {quaternion_b[2]:.4f}, {quaternion_b[3]:.4f}")
    
    # 计算两个物体之间的距离
    distance = np.linalg.norm(position_a - position_b)
    print(f"\n   物体 A 和 B 之间的距离: {distance:.4f} 米")
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)
    
    # 清理环境
    env.close_env()


if __name__ == "__main__":
    demo_object_coords()
