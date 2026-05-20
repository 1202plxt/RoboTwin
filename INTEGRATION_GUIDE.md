# 物体坐标信息保存 - 集成指南

## 📋 概述

本文档说明如何将 `object_pose_recorder.py` 模块集成到你的数据采集代码中，以保存每一帧的物体坐标和姿态信息。

---

## 🎯 目标

将以下信息保存到JSON文件：
- ✅ 每帧所有刚体的3D坐标和四元数旋转
- ✅ 每帧所有关节体的3D坐标、四元数旋转和关节角度
- ✅ 自动处理重名问题
- ✅ 每个episode保存为一个JSON文件

---

## 📁 输出示例

```json
{
  "0": {
    "frame_index": 0,
    "rigid_bodies": {
      "bottle_0": {
        "position": [0.1234, -0.0567, 0.7400],
        "quaternion": [0.7071, 0.0, 0.7071, 0.0],
        "type": "rigid_body"
      },
      "plate_0": {
        "position": [-0.2000, 0.1000, 0.7400],
        "quaternion": [1.0, 0.0, 0.0, 0.0],
        "type": "rigid_body"
      }
    },
    "articulations": {
      "drawer_0": {
        "position": [0.5, 0.0, 0.7400],
        "quaternion": [0.7071, 0.0, 0.7071, 0.0],
        "qpos": [0.0, 0.0, 0.0],
        "type": "articulation"
      }
    }
  },
  "1": {
    "frame_index": 1,
    ...
  }
}
```

---

## 🔧 集成步骤

### 步骤1：复制模块文件

将 `object_pose_recorder.py` 复制到你的项目根目录：

```bash
cp object_pose_recorder.py ~/autodl-tmp/RoboTwin/
```

### 步骤2：修改 `_base_task.py`

#### 2.1 在文件开头添加导入

在 `_base_task.py` 的导入部分添加：

```python
from object_pose_recorder import ObjectPoseRecorder, print_frame_info
```

#### 2.2 在 `_init_task_env_` 方法中初始化记录器

找到 `__init__` 相关的初始化代码，在适当位置添加：

```python
# 在类初始化或环境初始化中
self.pose_recorder = ObjectPoseRecorder()
```

#### 2.3 在 `setup_demo` 方法开始时重置记录器

在 `setup_demo` 方法的开头添加：

```python
def setup_demo(self, ...):
    self.pose_recorder.reset()  # 重置记录器
    # ... 其他初始化代码 ...
```

#### 2.4 在 `_take_picture` 方法中记录每帧数据

找到 `_take_picture` 方法（约第508行），在保存pkl之后添加：

```python
def _take_picture(self):  # save data
    if not self.save_data:
        return

    print("saving: episode = ", self.ep_num, " index = ", self.FRAME_IDX, end="\r")

    if self.FRAME_IDX == 0:
        self.folder_path = {"cache": f"{self.save_dir}/.cache/episode{self.ep_num}/"}

        for directory in self.folder_path.values():  # remove previous data
            if os.path.exists(directory):
                file_list = os.listdir(directory)
                for file in file_list:
                    os.remove(directory + file)

    pkl_dic = self.get_obs()
    save_pkl(self.folder_path["cache"] + f"{self.FRAME_IDX}.pkl", pkl_dic)  # use cache

    # ========== 添加：记录物体坐标信息 ==========
    frame_data = self.pose_recorder.record_frame(self.scene, self.FRAME_IDX)
    # 可选：打印每帧信息（如果不需要可以注释掉）
    # print_frame_info(frame_data)
    # ==========================================

    self.FRAME_IDX += 1
```

#### 2.5 在 `close_env` 方法中保存JSON文件

找到 `close_env` 方法，在清理代码之前添加：

```python
def close_env(self, clear_cache=False):
    # ========== 添加：保存物体坐标到JSON ==========
    if self.save_data:
        json_save_path = os.path.join(self.save_dir, "object_poses", f"episode{self.ep_num}.json")
        self.pose_recorder.save_to_json(json_save_path)
        summary = self.pose_recorder.get_summary()
        print(f"📊 数据摘要: {summary['total_frames']} 帧, "
              f"最多 {summary['max_rigid_bodies_per_frame']} 个刚体, "
              f"{summary['max_articulations_per_frame']} 个关节体")
    # ===========================================

    # ... 现有的清理代码 ...
    # 例如：
    # self.scene = None
    # self.engine = None
    # ...
```

---

## 🚀 快速集成脚本

如果你不想手动修改，可以使用以下脚本自动完成集成：

```bash
cd ~/autodl-tmp/RoboTwin && python3 << 'EOF'
import re

# 读取_base_task.py
with open('envs/_base_task.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加导入语句（在 import json 之后）
if 'from object_pose_recorder import ObjectPoseRecorder' not in content:
    content = content.replace(
        'import json',
        'import json\nfrom object_pose_recorder import ObjectPoseRecorder, print_frame_info'
    )

# 2. 在 _init_task_env_ 方法中添加初始化
if 'self.pose_recorder = ObjectPoseRecorder()' not in content:
    # 在 self.FRAME_IDX = 0 之后添加
    content = content.replace(
        'self.FRAME_IDX = 0',
        'self.FRAME_IDX = 0\n        self.pose_recorder = ObjectPoseRecorder()'
    )

# 3. 在 _take_picture 方法中添加记录代码
if 'self.pose_recorder.record_frame' not in content:
    # 在 save_pkl 之后，FRAME_IDX += 1 之前添加
    content = content.replace(
        'save_pkl(self.folder_path["cache"] + f"{self.FRAME_IDX}.pkl", pkl_dic)  # use cache\n\n        self.FRAME_IDX += 1',
        '''save_pkl(self.folder_path["cache"] + f"{self.FRAME_IDX}.pkl", pkl_dic)  # use cache

        # ========== 记录物体坐标信息 ==========
        frame_data = self.pose_recorder.record_frame(self.scene, self.FRAME_IDX)
        # print_frame_info(frame_data)  # 取消注释以打印每帧信息
        # ======================================

        self.FRAME_IDX += 1'''
    )

# 保存修改后的文件
with open('envs/_base_task.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 自动集成完成！")
print("✅ 请确保 object_pose_recorder.py 文件在项目根目录")
EOF
```

---

## 📍 修改后的文件结构

```
RoboTwin/
├── object_pose_recorder.py          # 新增：物体坐标记录模块
├── envs/
│   ├── _base_task.py               # 修改：添加坐标记录功能
│   └── ...
└── data/
    └── place_a2b_left/
        └── demo_randomized/
            ├── _traj_data/           # 现有的轨迹数据
            │   ├── episode0.pkl
            │   └── ...
            ├── object_poses/         # 新增：物体坐标数据
            │   ├── episode0.json     # 每帧的物体坐标信息
            │   ├── episode1.json
            │   └── ...
            └── ...
```

---

## 🧪 测试验证

运行数据采集后，检查生成的文件：

```bash
# 1. 检查JSON文件是否生成
ls -lh data/place_a2b_left/demo_randomized/object_poses/

# 2. 查看文件内容
cat data/place_a2b_left/demo_randomized/object_poses/episode0.json | head -50

# 3. 格式化查看（更易读）
python3 -m json.tool data/place_a2b_left/demo_randomized/object_poses/episode0.json | head -100

# 4. 统计帧数
python3 << 'EOF'
import json
with open('data/place_a2b_left/demo_randomized/object_poses/episode0.json', 'r') as f:
    data = json.load(f)
print(f"总帧数: {len(data)}")
print(f"物体类型: {list(data['0']['rigid_bodies'].keys())}")
EOF
```

---

## ⚙️ 自定义配置

### 只记录特定物体

如果只想记录特定物体，可以修改 `record_frame` 方法中的过滤逻辑：

```python
# 在 record_frame 方法中，添加过滤条件
TARGET_OBJECTS = ['bottle', 'plate', 'bowl']  # 你想记录的物体名称

for actor in scene.get_all_actors():
    name = actor.get_name()
    # 检查是否在目标列表中
    if any(target in name.lower() for target in TARGET_OBJECTS):
        # 记录这个物体
        ...
```

### 记录其他属性

可以添加更多属性记录，例如：

```python
# 添加速度信息
velocity = actor.get_velocity()  # 线速度
angular_velocity = actor.get_angular_velocity()  # 角速度

frame_data["rigid_bodies"][unique_name]["velocity"] = velocity.tolist()
frame_data["rigid_bodies"][unique_name]["angular_velocity"] = angular_velocity.tolist()
```

---

## ❓ 常见问题

### Q1: JSON文件太大怎么办？

A: JSON文件确实会比较大，因为每帧都保存了完整信息。解决方案：
- 使用压缩：`.json.gz` 格式
- 间隔采样：每N帧保存一次
- 只保存关键帧：开始、结束、中间状态

### Q2: 如何查看特定帧的信息？

```python
import json

with open('data/place_a2b_left/demo_randomized/object_poses/episode0.json', 'r') as f:
    data = json.load(f)

# 查看第50帧
frame_50 = data['50']
print(f"第50帧: {frame_50}")
```

### Q3: 如何可视化坐标数据？

```python
import json
import numpy as np

# 加载数据
with open('data/place_a2b_left/demo_randomized/object_poses/episode0.json', 'r') as f:
    data = json.load(f)

# 追踪某个物体在整个episode中的轨迹
object_name = 'bottle_0'
positions = []
for frame_idx in sorted(data.keys(), key=int):
    if object_name in data[frame_idx]['rigid_bodies']:
        pos = data[frame_idx]['rigid_bodies'][object_name]['position']
        positions.append(pos)

positions = np.array(positions)
print(f"物体移动距离: {np.linalg.norm(positions[-1] - positions[0]):.4f} 米")
```

---

## 🎉 完成！

按照以上步骤操作后，每次数据采集都会自动保存物体坐标信息到 `object_poses` 目录下的JSON文件中。
