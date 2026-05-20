#!/usr/bin/env python3
"""
🚀 快速集成脚本
自动将物体坐标保存功能集成到你的数据采集代码中
"""

import os
import sys

def integrate():
    """执行集成"""
    
    print("=" * 80)
    print("🚀 RoboTwin 物体坐标保存功能 - 自动集成")
    print("=" * 80)
    print()
    
    # 1. 检查必要文件
    print("📋 步骤1: 检查必要文件...")
    
    base_task_path = 'envs/_base_task.py'
    if not os.path.exists(base_task_path):
        print(f"❌ 错误: 找不到 {base_task_path}")
        print("   请确保在 RoboTwin 项目根目录运行此脚本")
        return False
    
    pose_recorder_path = 'object_pose_recorder.py'
    if not os.path.exists(pose_recorder_path):
        print(f"❌ 错误: 找不到 {pose_recorder_path}")
        print("   请确保 object_pose_recorder.py 文件在项目根目录")
        return False
    
    print("✅ 必要文件检查通过")
    print()
    
    # 2. 读取_base_task.py
    print("📝 步骤2: 读取代码...")
    with open(base_task_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. 添加导入语句
    print("🔧 步骤3: 添加导入语句...")
    if 'from object_pose_recorder import ObjectPoseRecorder' not in content:
        # 在 import json 之后添加
        content = content.replace(
            'import json',
            'import json\nfrom object_pose_recorder import ObjectPoseRecorder, print_frame_info'
        )
        print("✅ 添加导入语句成功")
    else:
        print("⚠️  导入语句已存在，跳过")
    
    # 4. 添加初始化
    print("🔧 步骤4: 添加记录器初始化...")
    if 'self.pose_recorder = ObjectPoseRecorder()' not in content:
        # 在 self.FRAME_IDX = 0 之后添加
        content = content.replace(
            'self.FRAME_IDX = 0',
            'self.FRAME_IDX = 0\n        self.pose_recorder = ObjectPoseRecorder()'
        )
        print("✅ 添加初始化代码成功")
    else:
        print("⚠️  初始化代码已存在，跳过")
    
    # 5. 在_take_picture中添加记录逻辑
    print("🔧 步骤5: 在_take_picture中添加记录逻辑...")
    if 'self.pose_recorder.record_frame' not in content:
        # 找到save_pkl那一行并在其后添加记录代码
        old_code = 'save_pkl(self.folder_path["cache"] + f"{self.FRAME_IDX}.pkl", pkl_dic)  # use cache\n\n        self.FRAME_IDX += 1'
        new_code = '''save_pkl(self.folder_path["cache"] + f"{self.FRAME_IDX}.pkl", pkl_dic)  # use cache

        # ========== 记录物体坐标信息 ==========
        frame_data = self.pose_recorder.record_frame(self.scene, self.FRAME_IDX)
        # print_frame_info(frame_data)  # 取消注释以打印每帧详细信息
        # ======================================

        self.FRAME_IDX += 1'''
        
        content = content.replace(old_code, new_code)
        print("✅ 添加记录逻辑成功")
    else:
        print("⚠️  记录逻辑已存在，跳过")
    
    # 6. 在close_env中添加保存逻辑
    print("🔧 步骤6: 在close_env中添加JSON保存逻辑...")
    if 'self.pose_recorder.save_to_json' not in content:
        # 在close_env方法开始处添加保存逻辑
        # 找到 def close_env(self
        import re
        close_env_match = re.search(r'(def close_env\(self[^:]*\):)', content)
        if close_env_match:
            insert_pos = close_env_match.end()
            save_code = '''
    # ========== 保存物体坐标到JSON文件 ==========
    if getattr(self, 'pose_recorder', None) and getattr(self, 'save_data', False):
        json_save_path = os.path.join(self.save_dir, "object_poses", f"episode{self.ep_num}.json")
        self.pose_recorder.save_to_json(json_save_path)
        summary = self.pose_recorder.get_summary()
        print(f"\\n📊 物体坐标数据摘要: {summary['total_frames']} 帧, "
              f"最多 {summary['max_rigid_bodies_per_frame']} 个刚体, "
              f"{summary['max_articulations_per_frame']} 个关节体")
    # ===========================================
'''
            content = content[:insert_pos] + save_code + content[insert_pos:]
            print("✅ 添加JSON保存逻辑成功")
        else:
            print("⚠️  未找到close_env方法，跳过")
    else:
        print("⚠️  JSON保存逻辑已存在，跳过")
    
    # 7. 保存修改后的文件
    print("💾 步骤7: 保存修改...")
    with open(base_task_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 保存成功")
    print()
    
    # 8. 验证
    print("🔍 步骤8: 验证修改...")
    with open(base_task_path, 'r', encoding='utf-8') as f:
        verify_content = f.read()
    
    checks = [
        ('from object_pose_recorder import', '导入语句'),
        ('self.pose_recorder = ObjectPoseRecorder()', '初始化'),
        ('self.pose_recorder.record_frame', '记录逻辑'),
        ('self.pose_recorder.save_to_json', '保存逻辑'),
    ]
    
    all_ok = True
    for check_str, desc in checks:
        if check_str in verify_content:
            print(f"✅ {desc}: OK")
        else:
            print(f"❌ {desc}: 失败")
            all_ok = False
    
    print()
    
    if all_ok:
        print("=" * 80)
        print("🎉 集成完成！")
        print("=" * 80)
        print()
        print("📝 下一步操作:")
        print("   1. 运行数据采集: python script/collect_data.py place_a2b_left demo_randomized")
        print("   2. 查看生成的JSON文件: ls data/place_a2b_left/demo_randomized/object_poses/")
        print("   3. 查看数据内容: cat data/place_a2b_left/demo_randomized/object_poses/episode0.json")
        print()
        print("💡 提示: 如果想打印每帧详细信息，取消注释 print_frame_info(frame_data) 这一行")
        print("=" * 80)
    else:
        print("❌ 集成过程中出现问题，请检查代码或手动集成")
        print()
        print("📚 参考文档: INTEGRATION_GUIDE.md")
    
    return all_ok


if __name__ == "__main__":
    success = integrate()
    sys.exit(0 if success else 1)
