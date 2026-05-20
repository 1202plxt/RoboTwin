#!/usr/bin/env python3
"""
🚀 简单修复脚本
直接在 save_pkl 之后插入记录逻辑
"""

def simple_fix():
    """简单直接的修复方法"""
    
    print("=" * 80)
    print("🚀 开始修复")
    print("=" * 80)
    print()
    
    # 读取文件
    with open('envs/_base_task.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到 save_pkl 那一行
    target_line_idx = None
    for i, line in enumerate(lines):
        if 'save_pkl(self.folder_path["cache"] + f"{self.FRAME_IDX}.pkl", pkl_dic)' in line:
            target_line_idx = i
            break
    
    if target_line_idx is None:
        print("❌ 未找到 save_pkl 目标行")
        print()
        print("尝试另一种搜索...")
        for i, line in enumerate(lines):
            if 'save_pkl' in line and 'FRAME_IDX' in line:
                target_line_idx = i
                print(f"找到第 {i+1} 行: {line.strip()}")
                break
    
    if target_line_idx is None:
        print("❌ 无法定位 save_pkl 行")
        print()
        print("请手动操作：")
        print("1. 打开 envs/_base_task.py")
        print("2. 找到约第524行，save_pkl(..., pkl_dic) 这一行")
        print("3. 在这一行之后、self.FRAME_IDX += 1 之前插入：")
        print()
        print("=" * 80)
        print("""        # ========== 记录物体坐标信息 ==========
        frame_data = self.pose_recorder.record_frame(self.scene, self.FRAME_IDX)
        # print_frame_info(frame_data)  # 取消注释以打印详细信息
        # ======================================""")
        print("=" * 80)
        return
    
    print(f"✅ 找到 save_pkl 调用在第 {target_line_idx + 1} 行")
    print()
    
    # 检查下一行是不是 FRAME_IDX
    next_line_idx = target_line_idx + 1
    if next_line_idx < len(lines):
        next_line = lines[next_line_idx]
        print(f"下一行 ({next_line_idx + 1}): {next_line.strip()}")
        
        if 'self.FRAME_IDX += 1' in next_line:
            print("✅ 确认下一行是 self.FRAME_IDX += 1")
        else:
            print("⚠️ 下一行不是 self.FRAME_IDX += 1，请检查")
    
    print()
    
    # 构建新的行列表
    new_lines = []
    
    # 添加 save_pkl 行及其后面的行（直到 FRAME_IDX）
    for i in range(len(lines)):
        new_lines.append(lines[i])
        
        # 在 save_pkl 行之后添加记录代码
        if i == target_line_idx:
            # 添加空行和记录代码
            new_lines.append('\n')
            new_lines.append('        # ========== 记录物体坐标信息 ==========\n')
            new_lines.append('        frame_data = self.pose_recorder.record_frame(self.scene, self.FRAME_IDX)\n')
            new_lines.append('        # print_frame_info(frame_data)  # 取消注释以打印详细信息\n')
            new_lines.append('        # ======================================\n')
    
    # 写入文件
    with open('envs/_base_task.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ 修复完成！")
    print()
    print("验证修复结果...")
    print()
    
    # 验证
    with open('envs/_base_task.py', 'r', encoding='utf-8') as f:
        verify_content = f.read()
    
    if 'self.pose_recorder.record_frame' in verify_content:
        print("✅ 验证成功：记录逻辑已添加")
        
        # 显示修改后的代码段
        print()
        print("修改后的代码段：")
        print("-" * 80)
        for i, line in enumerate(lines[max(0, target_line_idx-2):target_line_idx+5], 
                                    start=max(1, target_line_idx-1)):
            print(f"{i:4d}: {line}", end='')
        print("-" * 80)
    else:
        print("❌ 验证失败：记录逻辑未添加成功")
    
    print()
    print("=" * 80)
    print("🎉 完成！")
    print("=" * 80)
    print()
    print("现在可以运行数据采集：")
    print("  python script/collect_data.py place_a2b_left demo_randomized")
    print()


if __name__ == "__main__":
    simple_fix()
