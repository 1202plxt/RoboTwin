# 🎯 物体坐标保存功能 - 快速使用指南

## 📦 文件清单

已为你创建以下文件：

1. **`object_pose_recorder.py`** - 物体坐标记录模块（核心功能）
2. **`INTEGRATION_GUIDE.md`** - 详细集成文档
3. **`integrate_pose_recorder.py`** - 自动集成脚本（推荐使用）

---

## 🚀 快速开始（3步完成）

### 步骤1：复制文件到你的服务器

在你的 **RoboTwin 项目根目录** 下执行：

```bash
cd ~/autodl-tmp/RoboTwin

# 复制文件（你需要手动执行这些命令）
# object_pose_recorder.py
# INTEGRATION_GUIDE.md  
# integrate_pose_recorder.py
```

### 步骤2：运行自动集成脚本

```bash
python3 integrate_pose_recorder.py
```

你应该会看到类似输出：

```
================================================================================
🚀 RoboTwin 物体坐标保存功能 - 自动集成
================================================================================

📋 步骤1: 检查必要文件...
✅ 必要文件检查通过

📝 步骤2: 读取代码...
🔧 步骤3: 添加导入语句...
✅ 添加导入语句成功
🔧 步骤4: 添加记录器初始化...
✅ 添加初始化代码成功
🔧 步骤5: 在_take_picture中添加记录逻辑...
✅ 添加记录逻辑成功
🔧 步骤6: 在close_env中添加JSON保存逻辑...
✅ 添加JSON保存逻辑成功
💾 步骤7: 保存修改...
✅ 保存成功
🔍 步骤8: 验证修改...
✅ 导入语句: OK
✅ 初始化: OK
✅ 记录逻辑: OK
✅ 保存逻辑: OK

================================================================================
🎉 集成完成！
================================================================================
```

### 步骤3：运行数据采集

```bash
python script/collect_data.py place_a2b_left demo_randomized
```

---

## 📊 查看生成的数据

数据会保存到：`data/{task_name}/{setting}/object_poses/episode{编号}.json`

### 示例：

```bash
# 查看目录
ls -lh data/place_a2b_left/demo_randomized/object_poses/

# 查看文件内容（前100行）
cat data/place_a2b_left/demo_randomized/object_poses/episode0.json | head -100

# 格式化查看
python3 -m json.tool data/place_a2b_left/demo_randomized/object_poses/episode0.json | head -50
```

---

## 🔍 JSON文件内容示例

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
    "articulations": {}
  },
  "1": {
    "frame_index": 1,
    ...
  }
}
```

---

## 🛠️ 高级功能

### 查看每帧详细信息

如果你想在采集时看到每帧的物体信息，可以**取消注释**一行代码：

编辑 `envs/_base_task.py`，找到这一行：

```python
# print_frame_info(frame_data)  # 取消注释以打印每帧详细信息
```

改为：

```python
print_frame_info(frame_data)  # 取消注释以打印每帧详细信息
```

然后重新运行数据采集。

### 只记录特定物体

如果你只想记录某些特定物体（如只记录 bottle 和 plate），可以修改 `object_pose_recorder.py` 中的 `record_frame` 方法：

```python
# 在 record_frame 方法中添加过滤
TARGET_OBJECTS = ['bottle', 'plate', 'bowl']  # 只记录这些物体

for actor in scene.get_all_actors():
    name = actor.get_name()
    if any(target in name.lower() for target in TARGET_OBJECTS):
        # 记录这个物体
        ...
```

---

## ❓ 常见问题

### Q1: JSON文件很大怎么办？

**A:** 这是正常的，因为每帧都保存了完整信息。解决方案：

```bash
# 压缩JSON文件
gzip data/place_a2b_left/demo_randomized/object_poses/episode0.json

# 或者使用更大的采样间隔（在代码中修改）
# 只记录每10帧的数据
if self.FRAME_IDX % 10 == 0:
    frame_data = self.pose_recorder.record_frame(...)
```

### Q2: 如何分析坐标数据？

```python
import json
import numpy as np

# 加载数据
with open('data/place_a2b_left/demo_randomized/object_poses/episode0.json', 'r') as f:
    data = json.load(f)

# 分析某个物体的移动轨迹
object_name = 'bottle_0'
positions = []

for frame_idx in sorted(data.keys(), key=int):
    if object_name in data[frame_idx]['rigid_bodies']:
        pos = data[frame_idx]['rigid_bodies'][object_name]['position']
        positions.append(pos)

positions = np.array(positions)
print(f"物体 {object_name} 的移动统计:")
print(f"  - 总帧数: {len(positions)}")
print(f"  - 起点: {positions[0]}")
print(f"  - 终点: {positions[-1]}")
print(f"  - 总移动距离: {np.linalg.norm(positions[-1] - positions[0]):.4f} 米")
```

### Q3: 如何验证数据是否正确？

```bash
# 运行测试脚本
python3 << 'EOF'
import json

# 检查文件
with open('data/place_a2b_left/demo_randomized/object_poses/episode0.json', 'r') as f:
    data = json.load(f)

print(f"✅ JSON文件有效")
print(f"📊 总帧数: {len(data)}")
print(f"📦 物体数量（第0帧）: {len(data['0']['rigid_bodies'])} 个刚体, "
      f"{len(data['0']['articulations'])} 个关节体")

# 检查数据结构
sample = data['0']['rigid_bodies']
if sample:
    obj_name = list(sample.keys())[0]
    obj_data = sample[obj_name]
    print(f"\n📝 示例物体 '{obj_name}':")
    print(f"   位置: {obj_data['position']}")
    print(f"   四元数: {obj_data['quaternion']}")
EOF
```

---

## 📝 数据字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `frame_index` | int | 帧索引 |
| `rigid_bodies` | dict | 刚体字典，键为物体名称 |
| `articulations` | dict | 关节体字典 |
| `position` | list[3] | 3D坐标 [x, y, z]，单位：米 |
| `quaternion` | list[4] | 四元数 [w, x, y, z] |
| `qpos` | list | 关节位置（仅关节体有） |
| `type` | str | 对象类型："rigid_body" 或 "articulation" |

---

## 🎓 技术细节

### 四元数说明

四元数是一种表示3D旋转的方式：
- `[w, x, y, z]` 格式
- `w` 是标量部分
- `[x, y, z]` 是向量部分
- 可以用 `transforms3d` 库转换为欧拉角

```python
import transforms3d

quat = [0.7071, 0.0, 0.7071, 0.0]  # 示例四元数
euler = transforms3d.quaternions.quat2euler(quat)  # 转为欧拉角
print(f"欧拉角（弧度）: {euler}")
print(f"欧拉角（度）: {np.degrees(euler)}")
```

---

## ✅ 验证清单

集成完成后，检查以下内容：

- [ ] `integrate_pose_recorder.py` 脚本运行成功
- [ ] `envs/_base_task.py` 文件被修改
- [ ] 运行数据采集没有报错
- [ ] `object_poses` 目录被创建
- [ ] JSON文件包含正确的数据结构
- [ ] 物体位置和旋转信息完整

---

## 🆘 如果遇到问题

### 问题1：集成脚本报错 "找不到文件"

**解决方案：**
```bash
# 确认在正确目录
pwd  # 应该显示 ~/autodl-tmp/RoboTwin

# 检查文件是否存在
ls -la object_pose_recorder.py
ls -la envs/_base_task.py
```

### 问题2：数据采集时报错

**解决方案：**
```bash
# 检查代码语法
python3 -m py_compile envs/_base_task.py

# 如果有语法错误，恢复原文件
git checkout envs/_base_task.py
# 然后重新运行集成脚本
```

### 问题3：JSON文件为空或不完整

**解决方案：**
- 确保 `save_data=True` 在配置中
- 检查终端输出是否有错误信息
- 查看日志文件

---

## 🎉 恭喜！

如果一切顺利，你现在应该能够：

1. ✅ 在数据采集时自动保存物体坐标信息
2. ✅ 每个episode生成一个独立的JSON文件
3. ✅ 每帧都包含完整的物体位置和旋转信息
4. ✅ 数据格式易于阅读和后续处理

---

## 📚 更多资源

- **详细集成文档**: `INTEGRATION_GUIDE.md`
- **核心模块源码**: `object_pose_recorder.py`
- **自动集成脚本**: `integrate_pose_recorder.py`

祝你使用愉快！ 🚀
