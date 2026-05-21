
"""place_a2b_left dataset."""

from typing import Iterator, Tuple, Any
import os
import h5py
import glob
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
import sys
sys.path.append('.')
from place_a2b_left.conversion_utils import MultiThreadedDatasetBuilder


def _generate_examples(paths) -&gt; Iterator[Tuple[str, Any]]:
    """Yields episodes for list of data paths."""

    def _parse_example(episode_path):
        # Load raw data
        with h5py.File(episode_path, "r") as f:
            # Read data from ALOHA format
            action = f["action"][()]
            # Since we don't have state (joint positions) in this format,
            # we'll create dummy state or use relative actions as state
            # For now, let's use the action as the state for compatibility
            state = np.zeros((action.shape[0], 14), dtype=np.float32)  # 14D for compatibility (7D left + 7D right)
            
            # Images
            head_camera_image = f["head_camera_image"][()]
            left_wrist_image = f["left_wrist_image"][()]
            right_wrist_image = f["right_wrist_image"][()]
            low_cam_image = f["low_cam_image"][()]
            
            # Read language instructions
            seen_instructions = f["seen"][()]
            # Pick a random instruction from seen list
            if seen_instructions.size &gt; 0:
                # Choose the first instruction
                language_instruction = seen_instructions[0].decode('utf-8') if hasattr(seen_instructions[0], 'decode') else str(seen_instructions[0])
            else:
                # Default instruction
                language_instruction = "Place the object from the left of the target object"

        # Assemble episode
        episode = []
        for i in range(action.shape[0]):
            episode.append({
                'observation': {
                    'image': head_camera_image[i],
                    'left_wrist_image': left_wrist_image[i],
                    'right_wrist_image': right_wrist_image[i],
                    'low_cam_image': low_cam_image[i],
                    'state': np.asarray(state[i], np.float32),
                },
                'action': np.asarray(action[i], dtype=np.float32),
                'discount': 1.0,
                'reward': float(i == (action.shape[0] - 1)),
                'is_first': i == 0,
                'is_last': i == (action.shape[0] - 1),
                'is_terminal': i == (action.shape[0] - 1),
                'language_instruction': language_instruction,
            })

        # Create output data sample
        sample = {
            'steps': episode,
            'episode_metadata': {
                'file_path': episode_path
            }
        }

        return episode_path, sample

    # For smallish datasets, use single-thread parsing
    for sample in paths:
        ret = _parse_example(sample)
        yield ret


class PlaceA2BLeft(MultiThreadedDatasetBuilder):
    """DatasetBuilder for place_a2b_left dataset."""

    VERSION = tfds.core.Version('1.0.0')
    RELEASE_NOTES = {
        '1.0.0': 'Initial release.',
    }
    N_WORKERS = 4
    MAX_PATHS_IN_MEMORY = 20
    PARSE_FCN = _generate_examples

    def _info(self) -&gt; tfds.core.DatasetInfo:
        """Dataset metadata (homepage, citation,...)."""
        return self.dataset_info_from_configs(
            features=tfds.features.FeaturesDict({
                'steps': tfds.features.Dataset({
                    'observation': tfds.features.FeaturesDict({
                        'image': tfds.features.Image(
                            shape=(256, 256, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Head camera RGB observation.',
                        ),
                        'left_wrist_image': tfds.features.Image(
                            shape=(256, 256, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Left wrist camera RGB observation.',
                        ),
                        'right_wrist_image': tfds.features.Image(
                            shape=(256, 256, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Right wrist camera RGB observation.',
                        ),
                        'low_cam_image': tfds.features.Image(
                            shape=(256, 256, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Lower camera RGB observation.',
                        ),
                        'state': tfds.features.Tensor(
                            shape=(14,),
                            dtype=np.float32,
                            doc='Robot joint state (7D left + 7D right, dummy values for compatibility).',
                        ),
                    }),
                    'action': tfds.features.Tensor(
                        shape=(14,),
                        dtype=np.float32,
                        doc='Robot arm action.',
                    ),
                    'discount': tfds.features.Scalar(
                        dtype=np.float32,
                        doc='Discount if provided, default to 1.'
                    ),
                    'reward': tfds.features.Scalar(
                        dtype=np.float32,
                        doc='Reward if provided, 1 on final step for demos.'
                    ),
                    'is_first': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on first step of the episode.'
                    ),
                    'is_last': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on last step of the episode.'
                    ),
                    'is_terminal': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on last step of the episode if it is a terminal step, True for demos.'
                    ),
                    'language_instruction': tfds.features.Text(
                        doc='Language Instruction for place_a2b_left task.'
                    ),
                }),
                'episode_metadata': tfds.features.FeaturesDict({
                    'file_path': tfds.features.Text(
                        doc='Path to the original data file.'
                    ),
                }),
            }))

    def _split_paths(self):
        """Define filepaths for data splits."""
        return {
            "train": sorted(glob.glob("/root/autodl-tmp/RoboTwin/data/aloha_place_a2b_left/train/*.hdf5")),
            "val": sorted(glob.glob("/root/autodl-tmp/RoboTwin/data/aloha_place_a2b_left/val/*.hdf5")),
        }

