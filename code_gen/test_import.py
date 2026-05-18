import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import importlib
try:
    envs_module = importlib.import_module("envs_gen.gpt_pick_dual_bottles_custom")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
