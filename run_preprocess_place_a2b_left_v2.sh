#!/bin/bash

# --- 配置参数（根据你的实际情况修改）---
# 1. 原始数据路径（你的数据在这里）
DATASET_PATH="/autodl-tmp/RoboTwin/data/place_a2b_left/demo_randomized/data"

# 2. 输出目录
OUT_BASE_DIR="/autodl-tmp/RoboTwin/data/aloha_place_a2b_left"

# 3. 指令文件目录（每个episode的instruction会自动生成）
INSTRUCTION_DIR="/autodl-tmp/RoboTwin/data/place_a2b_left/demo_randomized/instructions"

# 项目根目录
PROJECT_ROOT="/autodl-tmp/RoboTwin"

# --- 步骤1：生成episode指令---
echo "📝 第1步：生成episode指令..."
cd "$PROJECT_ROOT"
python description/utils/generate_episode_instructions.py place_a2b_left demo_randomized 100

# --- 步骤2：数据格式转换---
echo "🔄 第2步：转换数据格式..."
cd "$PROJECT_ROOT/policy/openvla-oft"
python preprocess_aloha.py \
    --dataset_path "$DATASET_PATH" \
    --out_base_dir "$OUT_BASE_DIR" \
    --percent_val 0.05 \
    --instruction_dir "$INSTRUCTION_DIR" \
    --img_resize_size 256

echo "✅ 预处理完成！"
echo "输出目录：$OUT_BASE_DIR"
