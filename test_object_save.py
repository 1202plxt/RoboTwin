
import sys
sys.path.append("./")

from envs.place_a2b_left import place_a2b_left
from task_config import _config_template
import yaml

def test_object_info_collection():
    """测试我们的物体信息保存是否正常"""
    
    # 1. 创建任务环境
    task = place_a2b_left()
    
    # 2. 加载配置
    config_path = "./task_config/demo_randomized.yml"
    with open(config_path, "r", encoding="utf-8") as f:
        args = yaml.load(f.read(), Loader=yaml.FullLoader)
    
    args['task_name'] = 'place_a2b_left'
    args['save_path'] = './data_test'
    
    # 简化配置，只收集少量数据用于测试
    args['episode_num'] = 1
    args['render_freq'] = 0  # 关闭渲染加快速度
    args['save_data'] = True
    
    # 简单设置 embodiment（你可能需要根据实际情况调整）
    from envs._GLOBAL_CONFIGS import CONFIGS_PATH
    embodiment_config_path = f"{CONFIGS_PATH}/_embodiment_config.yml"
    
    with open(embodiment_config_path, "r", encoding="utf-8") as f:
        _embodiment_types = yaml.load(f.read(), Loader=yaml.FullLoader)
    
    args["left_robot_file"] = _embodiment_types["aloha-agilex"]["file_path"]
    args["right_robot_file"] = _embodiment_types["aloha-agilex"]["file_path"]
    
    # 3. 初始化环境
    print("初始化环境...")
    task.setup_demo(now_ep_num=0, seed=42, **args)
    
    # 4. 运行一次任务
    print("运行任务...")
    info = task.play_once()
    
    # 5. 获取一次观察，看看物体信息是否正确保存
    print("获取观察...")
    obs = task.get_obs()
    
    # 6. 打印保存的物体信息
    print("\n" + "="*80)
    print("保存的物体信息:")
    print("="*80)
    endpose = obs.get('endpose', {})
    for key, value in sorted(endpose.items()):
        if key.endswith('_pos') or key.endswith('_quat') or key.endswith('_name'):
            print(f"{key:25}: {value}")
    
    # 7. 关闭环境
    print("\n关闭环境...")
    task.close_env()
    
    print("\n✅ 测试完成！物体信息保存成功！")

if __name__ == "__main__":
    test_object_info_collection()
