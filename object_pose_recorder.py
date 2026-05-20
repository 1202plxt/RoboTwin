"""
物体坐标信息保存模块
用于在数据采集时保存每一帧的物体坐标和姿态信息到JSON文件
"""

import os
import json
from typing import Dict, List, Any


class ObjectPoseRecorder:
    """用于记录每一帧的物体坐标和姿态信息"""

    def __init__(self):
        self.episode_data = {}  # 存储整个episode的数据
        self.current_frame_idx = 0

    def reset(self):
        """重置记录器，为新的episode做准备"""
        self.episode_data = {}
        self.current_frame_idx = 0

    def record_frame(self, scene, frame_idx: int) -> Dict[str, Any]:
        """
        记录当前帧的所有物体坐标和姿态信息

        Args:
            scene: SAPIEN场景对象
            frame_idx: 当前帧索引

        Returns:
            包含当前帧所有物体信息的字典
        """
        frame_data = {
            "frame_index": frame_idx,
            "rigid_bodies": {},  # 刚体信息
            "articulations": {},  # 关节体信息
        }

        name_counts = {}

        # 1. 抓取所有【刚体】
        for actor in scene.get_all_actors():
            name = actor.get_name()
            # 跳过基础对象
            if not name or name in ["ground", "table", "wall"]:
                continue
            # 跳过链接、相机和夹爪
            if "link" in name.lower() or "camera" in name.lower() or "gripper" in name.lower():
                continue

            # 防重名处理
            if name in name_counts:
                name_counts[name] += 1
                unique_name = f"{name}_{name_counts[name]}"
            else:
                name_counts[name] = 0
                unique_name = name

            pose = actor.get_pose()
            pos = pose.p.tolist()  # 3D 坐标 [x, y, z]
            quat = pose.q.tolist()  # 旋转四元数 [w, x, y, z]

            frame_data["rigid_bodies"][unique_name] = {
                "position": pos,
                "quaternion": quat,
                "type": "rigid_body"
            }

        # 重置计数器用于关节体
        name_counts = {}

        # 2. 抓取所有【关节体】
        for art in scene.get_all_articulations():
            name = art.get_name()
            # 跳过机器人
            if not name or "aloha" in name.lower() or "franka" in name.lower() or "ur5" in name.lower() or "robot" in name.lower():
                continue

            # 防重名处理
            if name in name_counts:
                name_counts[name] += 1
                unique_name = f"{name}_{name_counts[name]}"
            else:
                name_counts[name] = 0
                unique_name = name

            pose = art.get_pose()
            pos = pose.p.tolist()  # 3D 坐标
            quat = pose.q.tolist()  # 旋转四元数
            qpos = art.get_qpos().tolist()  # 关节角度

            frame_data["articulations"][unique_name] = {
                "position": pos,
                "quaternion": quat,
                "qpos": qpos,  # 关节位置
                "type": "articulation"
            }

        # 存储到episode数据中
        self.episode_data[frame_idx] = frame_data
        self.current_frame_idx = frame_idx

        return frame_data

    def save_to_json(self, save_path: str):
        """
        将所有记录的数据保存到JSON文件

        Args:
            save_path: 保存路径（例如：./data/place_a2b_left/demo_randomized/episode_poses/episode0.json）
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 保存为JSON文件
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.episode_data, f, indent=2, ensure_ascii=False)

        print(f"✅ 物体坐标信息已保存到: {save_path}")
        print(f"   包含 {len(self.episode_data)} 帧数据")

    def get_summary(self) -> Dict[str, int]:
        """获取数据摘要"""
        rigid_body_count = 0
        articulation_count = 0

        for frame_data in self.episode_data.values():
            rigid_body_count = max(rigid_body_count, len(frame_data.get("rigid_bodies", {})))
            articulation_count = max(articulation_count, len(frame_data.get("articulations", {})))

        return {
            "total_frames": len(self.episode_data),
            "max_rigid_bodies_per_frame": rigid_body_count,
            "max_articulations_per_frame": articulation_count
        }


def print_frame_info(frame_data: Dict[str, Any]):
    """打印帧信息的友好格式"""
    print("\n" + "=" * 80)
    print(f"📊 Frame {frame_data['frame_index']} 物体信息")
    print("=" * 80)

    # 打印刚体信息
    if frame_data.get("rigid_bodies"):
        print("\n🔧 刚体 (Rigid Bodies):")
        print("-" * 80)
        for name, info in frame_data["rigid_bodies"].items():
            pos = info["position"]
            quat = info["quaternion"]
            print(f"  📦 {name: <20} | 坐标: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}] "
                  f"| 旋转: [{quat[0]:.4f}, {quat[1]:.4f}, {quat[2]:.4f}, {quat[3]:.4f}]")

    # 打印关节体信息
    if frame_data.get("articulations"):
        print("\n⚙️  关节体 (Articulations):")
        print("-" * 80)
        for name, info in frame_data["articulations"].items():
            pos = info["position"]
            quat = info["quaternion"]
            qpos_str = ", ".join([f"{q:.4f}" for q in info.get("qpos", [])])
            print(f"  💻 {name: <20} | 坐标: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}] "
                  f"| 旋转: [{quat[0]:.4f}, {quat[1]:.4f}, {quat[2]:.4f}, {quat[3]:.4f}]")
            if qpos_str:
                print(f"     └─ 关节角度: [{qpos_str}]")

    print("=" * 80 + "\n")


# 使用示例和使用说明
EXAMPLE_USAGE = '''
# ========================================
# 使用示例
# ========================================

# 1. 在你的任务类中初始化记录器
class YourTask(Base_Task):
    def __init__(self):
        super().__init__()
        self.pose_recorder = ObjectPoseRecorder()  # 添加这一行

# 2. 在setup时重置记录器（在setup_demo方法中）
def setup_demo(self, ...):
    self.pose_recorder.reset()  # 添加这一行
    # ... 其他初始化代码 ...

# 3. 在每次保存帧时记录物体信息（在_take_picture方法中）
def _take_picture(self):
    # ... 现有代码 ...
    pkl_dic = self.get_obs()
    save_pkl(...)

    # 添加：记录物体坐标信息
    frame_data = self.pose_recorder.record_frame(self.scene, self.FRAME_IDX)
    # 可选：打印帧信息
    print_frame_info(frame_data)

    self.FRAME_IDX += 1

# 4. 在episode结束时保存JSON（在close_env方法中或play_once返回后）
def close_env(self, ...):
    # ... 现有清理代码 ...

    # 添加：保存物体坐标到JSON文件
    json_save_path = os.path.join(self.save_dir, "object_poses", f"episode{self.ep_num}.json")
    self.pose_recorder.save_to_json(json_save_path)

    # ... 其他清理代码 ...
'''

if __name__ == "__main__":
    print("=" * 80)
    print("🎯 物体坐标信息保存模块")
    print("=" * 80)
    print("\n📝 功能说明:")
    print("  - 记录每个episode中所有帧的物体坐标和姿态")
    print("  - 支持刚体和关节体")
    print("  - 自动处理重名问题")
    print("  - 保存为易读的JSON格式")
    print("\n📁 输出格式:")
    print("  - 文件位置: {save_dir}/object_poses/episode{ep_num}.json")
    print("  - 包含每帧的position和quaternion信息")
    print("\n" + "=" * 80)
    print("\n💡 使用方法:")
    print(EXAMPLE_USAGE)
