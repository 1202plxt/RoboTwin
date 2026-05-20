#!/usr/bin/env python3
"""
🧹 清理不必要的文件
"""

import os
import shutil

# 要删除的文件列表
files_to_delete = [
    'object_pose_recorder.py',
    'INTEGRATION_GUIDE.md',
    'QUICK_START.md',
    'integrate_pose_recorder.py',
    'simple_fix.py',
    'fix_integration.py',
    'check_pose_saved.py',
    'analyze_trajectory.py',
]

print("=" * 80)
print("🧹 清理不必要的文件")
print("=" * 80)
print()

deleted_count = 0
not_found_count = 0

for filename in files_to_delete:
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"✅ 删除: {filename}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ 删除失败: {filename} - {e}")
    else:
        print(f"⚠️  文件不存在（跳过）: {filename}")
        not_found_count += 1

print()
print("=" * 80)
print(f"✅ 清理完成！")
print(f"   删除: {deleted_count} 个文件")
print(f"   跳过: {not_found_count} 个文件（不存在）")
print("=" * 80)
print()
print("💡 你只需要保留 envs/_base_task.py 的修改即可")
print("   其他文件都是多余的！")
print()
