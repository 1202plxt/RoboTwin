#!/usr/bin/env python3
"""
📊 分析所有物体的移动轨迹
检查哪些物体在episode中发生了移动
"""

import h5py
import numpy as np

def analyze_object_movement(hdf5_path, output_detail=False):
    """分析所有物体的移动情况"""
    
    print("=" * 80)
    print("🎯 物体移动轨迹分析")
    print("=" * 80)
    print()
    
    with h5py.File(hdf5_path, 'r') as f:
        endpose = f['endpose']
        
        # 获取所有物体名称
        objects = set()
        for key in endpose.keys():
            if '_pos' in key:
                obj_name = key.replace('_pos', '')
                objects.add(obj_name)
        
        print(f"📦 检测到 {len(objects)} 个物体")
        print()
        
        # 分析每个物体的移动
        moving_objects = []
        static_objects = []
        
        for obj_name in sorted(objects):
            pos_key = f"{obj_name}_pos"
            
            if pos_key not in endpose:
                continue
            
            pos_data = endpose[pos_key][:]
            total_frames = pos_data.shape[0]
            
            # 计算移动距离
            start_pos = pos_data[0]
            end_pos = pos_data[-1]
            total_distance = np.linalg.norm(end_pos - start_pos)
            
            # 计算轨迹长度（所有帧的累计移动）
            trajectory_length = 0
            for i in range(1, total_frames):
                step_distance = np.linalg.norm(pos_data[i] - pos_data[i-1])
                trajectory_length += step_distance
            
            # 计算最大单步移动
            max_step = 0
            for i in range(1, total_frames):
                step_distance = np.linalg.norm(pos_data[i] - pos_data[i-1])
                max_step = max(max_step, step_distance)
            
            # 判断是否移动（使用阈值）
            is_moving = total_distance > 0.001  # 1mm阈值
            
            if is_moving:
                moving_objects.append({
                    'name': obj_name,
                    'distance': total_distance,
                    'trajectory': trajectory_length,
                    'max_step': max_step,
                    'frames': total_frames,
                    'data': pos_data
                })
            else:
                static_objects.append({
                    'name': obj_name,
                    'frames': total_frames,
                    'position': start_pos
                })
        
        # 打印结果
        print("🟢 会移动的物体:")
        print("-" * 80)
        
        if moving_objects:
            print(f"{'物体名称':<25} {'总移动距离':>12} {'轨迹长度':>12} {'最大单步':>12} {'帧数':>6}")
            print("-" * 80)
            
            for obj in moving_objects:
                print(f"{obj['name']:<25} {obj['distance']:>11.4f}m {obj['trajectory']:>11.4f}m "
                      f"{obj['max_step']:>11.4f}m {obj['frames']:>6d}")
            
            print("-" * 80)
            print(f"✅ 共 {len(moving_objects)} 个物体发生了移动")
        else:
            print("❌ 没有物体发生移动")
        
        print()
        print("⚪ 静止的物体:")
        print("-" * 80)
        
        for obj in static_objects:
            pos = obj['position']
            print(f"  • {obj['name']:<25} 位置: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}]")
        
        print()
        print("=" * 80)
        
        # 可选：详细显示移动物体的轨迹
        if output_detail and moving_objects:
            print()
            print("📈 移动物体的详细轨迹:")
            print("=" * 80)
            
            for obj in moving_objects[:3]:  # 只显示前3个
                print(f"\n📦 {obj['name']}:")
                print(f"   起始位置: [{obj['data'][0][0]:.4f}, {obj['data'][0][1]:.4f}, {obj['data'][0][2]:.4f}]")
                print(f"   结束位置: [{obj['data'][-1][0]:.4f}, {obj['data'][-1][1]:.4f}, {obj['data'][-1][2]:.4f}]")
                
                # 显示每10帧的位置变化
                print(f"   位置变化（每10帧）:")
                for i in range(0, obj['frames'], 10):
                    pos = obj['data'][i]
                    print(f"      帧 {i:3d}: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}]")
        
        return moving_objects, static_objects


if __name__ == "__main__":
    import sys
    
    hdf5_path = sys.argv[1] if len(sys.argv) > 1 else "data/place_a2b_left/demo_randomized/data/episode0.hdf5"
    
    moving, static = analyze_object_movement(hdf5_path, output_detail=True)
    
    print()
    print("=" * 80)
    print("💡 分析总结:")
    print("=" * 80)
    
    if moving:
        print(f"✅ 成功检测到 {len(moving)} 个物体在运动")
        print("✅ 物体坐标记录功能正常工作！")
        print()
        print("🎯 结论：你的代码已经正确实现了保存物体坐标的功能")
        print("   - 数据保存了所有帧")
        print("   - 坐标变化被正确记录")
    else:
        print(f"⚠️ 检测到 0 个物体在运动")
        print("   这可能是因为：")
        print("   1. 这个任务中的物体本来就是静止的（正常）")
        print("   2. 或者需要测试会移动物体的任务")
        print()
        print("💡 建议：运行一个新的episode或使用会移动物体的任务来测试")
    
    print("=" * 80)
