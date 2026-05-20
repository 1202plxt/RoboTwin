#!/usr/bin/env python3
"""
🚀 一键修改脚本：自动添加物体坐标记录代码到 _base_task.py
不需要任何额外文件！
"""

def modify_base_task():
    """自动修改 _base_task.py"""
    
    print("=" * 80)
    print("🚀 开始自动修改 _base_task.py")
    print("=" * 80)
    print()
    
    # 读取文件
    with open('envs/_base_task.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到 save_pkl 那一行
    target_idx = None
    for i, line in enumerate(lines):
        if 'save_pkl(self.folder_path["cache"] + f"{self.FRAME_IDX}.pkl", pkl_dic)' in line:
            target_idx = i
            break
    
    if target_idx is None:
        print("❌ 未找到 save_pkl 目标行")
        print()
        print("请手动检查 envs/_base_task.py 文件")
        return False
    
    print(f"✅ 找到 save_pkl 调用在第 {target_idx + 1} 行")
    
    # 检查是否已经添加过
    code_to_add = '''    # ========== 记录所有物体的坐标和旋转 ==========
    for actor in self.scene.get_all_actors():
        name = actor.get_name()
        if not name or name in ["ground", "table", "wall"]:
            continue
        if "link" in name.lower() or "camera" in name.lower() or "gripper" in name.lower():
            continue
        
        pose = actor.get_pose()
        pkl_dic["endpose"][f"{name}_pos"] = pose.p.tolist()
        pkl_dic["endpose"][f"{name}_quat"] = pose.q.tolist()
    # ==================================================
    
'''
    
    # 检查是否已经添加过
    check_code = 'pkl_dic["endpose"][f"{name}_pos"] = pose.p.tolist()'
    for line in lines:
        if check_code in line:
            print()
            print("✅ 代码已经添加过了！")
            print("   无需重复添加")
            return True
    
    print()
    print("📝 正在添加物体坐标记录代码...")
    
    # 在 save_pkl 之后插入新代码
    lines.insert(target_idx + 1, code_to_add)
    
    # 写回文件
    with open('envs/_base_task.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ 修改完成！")
    print()
    
    # 验证
    with open('envs/_base_task.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'pkl_dic["endpose"][f"{name}_pos"] = pose.p.tolist()' in content:
        print("✅ 验证成功：代码已正确添加")
        print()
        print("🎉 可以开始运行数据采集了！")
        print()
        print("运行命令：")
        print("  python script/collect_data.py place_a2b_left demo_randomized")
        return True
    else:
        print("❌ 验证失败：代码未正确添加")
        return False


if __name__ == "__main__":
    modify_base_task()
