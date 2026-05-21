
# place_a2b_left Dataset

## Dataset Description

This is the place_a2b_left dataset collected using the RoboTwin platform. The dataset contains demonstrations of a bimanual robot performing the task of placing an object to the left of a target object.

### Dataset Information

- **Task**: Place object A to the left of object B
- **Robot**: Bimanual robot (ALOHA agilex)
- **Total episodes**: Train (48 episodes), Val (2 episodes)
- **Cameras**: 
  - Head camera
  - Left wrist camera
  - Right wrist camera
  - Lower camera (front camera)
- **Image resolution**: 256x256 RGB
- **Action space**: 14D (7D left arm + 7D right arm)

### Data Structure

Each episode contains:
- `head_camera_image`: RGB images from the head camera
- `left_wrist_image`: RGB images from the left wrist camera
- `right_wrist_image`: RGB images from the right wrist camera
- `low_cam_image`: RGB images from the lower camera
- `action`: Robot joint actions (14D)
- `state`: Robot joint states (14D, dummy values for compatibility)
- `language_instruction`: Natural language instructions for the task

## Citation

If you use this dataset, please cite RoboTwin:

```bibtex
@inproceedings{
    robotwin2024,
    title={RoboTwin: A General-Purpose Bimanual Robotic Manipulation Platform},
    author={RoboTwin Team},
    booktitle={arXiv preprint},
    year={2024},
}
```
