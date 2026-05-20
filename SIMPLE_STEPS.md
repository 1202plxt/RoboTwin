# 🎯 简化为：只需要修改 _base_task.py

## 📝 具体修改步骤

### 第1步：找到 _take_picture 方法（约第508行）

```bash
vim envs/_base_task.py
```

### 第2步：跳转到 _take_picture 方法

```bash
:508
```

### 第3步：修改代码

找到这段代码（约508-525行）：

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
    self.FRAME_IDX += 1
```

**改为：**

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
    
    # ========== 添加：记录所有物体的坐标和旋转 ==========
    for actor in self.scene.get_all_actors():
        name = actor.get_name()
        # 跳过不需要记录的物体
        if not name or name in ["ground", "table", "wall"]:
            continue
        if "link" in name.lower() or "camera" in name.lower() or "gripper" in name.lower():
            continue
        
        pose = actor.get_pose()
        pkl_dic["endpose"][f"{name}_pos"] = pose.p.tolist()
        pkl_dic["endpose"][f"{name}_quat"] = pose.q.tolist()
    # ==================================================
    
    save_pkl(self.folder_path["cache"] + f"{self.FRAME_IDX}.pkl", pkl_dic)  # use cache
    self.FRAME_IDX += 1
```

### 第4步：保存退出

```bash
:wq
```

---

## 📊 改动说明

**添加的内容**（共8行）：

```python
for actor in self.scene.get_all_actors():
    name = actor.get_name()
    if not name or name in ["ground", "table", "wall"]:
        continue
    if "link" in name.lower() or "camera" in name.lower() or "gripper" in name.lower():
        continue
    
    pose = actor.get_pose()
    pkl_dic["endpose"][f"{name}_pos"] = pose.p.tolist()
    pkl_dic["endpose"][f"{name}_quat"] = pose.q.tolist()
```

**这段代码的作用**：
1. 遍历场景中所有刚体
2. 跳过 ground, table, wall, gripper 等不需要的物体
3. 获取每个物体的坐标和旋转
4. 保存到 `pkl_dic["endpose"]` 中

---

## ✅ 验证修改

修改后运行：

```bash
python3 << 'EOF'
with open('envs/_base_task.py', 'r') as f:
    content = f.read()
    
    if 'for actor in self.scene.get_all_actors():' in content:
        print("✅ 代码添加成功！")
        print()
        print("现在可以运行数据采集：")
        print("  python script/collect_data.py place_a2b_left demo_randomized")
    else:
        print("❌ 代码添加失败")
EOF
```

---

## 🧹 清理多余文件

如果之前添加了 `object_pose_recorder.py`，可以删除：

```bash
rm -f object_pose_recorder.py INTEG*.md QUICK*.md integrate_*.py cleanup_files.py
```

---

## 🎉 完成！

**只需要修改 `_base_task.py` 一个文件，添加8行代码即可！**
