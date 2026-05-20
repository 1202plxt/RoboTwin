#!/usr/bin/env python3
"""
🔧 修复集成问题
手动检查并修复 _take_picture 方法中的记录逻辑
"""

import os
import re

def check_and_fix():
    """检查并修复 _take_picture 方法"""
    
    print("=" * 80)
    print("🔧 修复物体坐标记录逻辑")
    print("=" * 80)
    print()
    
    # 读取文件
    with open('envs/_base_task.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有记录逻辑
    if 'self.pose_recorder.record_frame' in content:
        print("✅ 记录逻辑已经存在！")
        print()
        print("你的代码可能已经被正确修改了。")
        print()
        print("尝试运行数据采集：")
        print("  python script/collect_data.py place_a2b_left demo_randomized")
        print()
        print("如果还是不行，请检查 envs/_base_task.py 第524行附近的代码。")
        return
    
    print("❌ 未找到记录逻辑，开始修复...")
    print()
    
    # 查找 _take_picture 方法
    take_picture_pattern = r'(def _take_picture\(self\):.*?save_pkl\(.*?\).*?self\.FRAME_IDX \+= 1)'
    match = re.search(take_picture_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ 无法找到 _take_picture 方法的 save_pkl 部分")
        print()
        print("请手动检查代码：")
        print("  1. 打开 envs/_base_task.py")
        print("  2. 找到 _take_picture 方法（约第508行）")
        print("  3. 在 save_pkl 之后、self.FRAME_IDX += 1 之前添加以下代码：")
        print()
        print("=" * 80)
        print("""        # ========== 记录物体坐标信息 ==========
        frame_data = self.pose_recorder.record_frame(self.scene, self.FRAME_IDX)
        # print_frame_info(frame_data)  # 取消注释以打印详细信息
        # ======================================""")
        print("=" * 80)
        return
    
    print(f"✅ 找到 _take_picture 方法中的 save_pkl 调用")
    print()
    
    # 提取原始代码片段
    original_code = match.group(1)
    print("原始代码片段：")
    print("-" * 80)
    print(original_code)
    print("-" * 80)
    print()
    
    # 准备新的代码
    new_code = original_code.replace(
        'self.FRAME_IDX += 1',
        '''# ========== 记录物体坐标信息 ==========
        frame_data = self.pose_recorder.record_frame(self.scene, self.FRAME_IDX)
        # print_frame_info(frame_data)  # 取消注释以打印详细信息
        # ======================================

        self.FRAME_IDX += 1'''
    )
    
    print("修改后的代码片段：")
    print("-" * 80)
    print(new_code)
    print("-" * 80)
    print()
    
    # 替换
    new_content = content.replace(original_code, new_code)
    
    # 保存
    with open('envs/_base_task.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 修复完成！")
    print()
    print("现在运行数据采集测试：")
    print("  python script/collect_data.py place_a2b_left demo_randomized")
    print()


if __name__ == "__main__":
    check_and_fix()
