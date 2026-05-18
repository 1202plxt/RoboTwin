from ._base_task import Base_Task
from .utils import *
import math
import sapien
import numpy as np


class place_apple_plate(Base_Task):

    def setup_demo(self, is_test=False, **kwags):
        super()._init_task_env_(**kwags)

    def load_actors(self):
        # Load the plate
        plate_pose = rand_pose(
            xlim=[0.1, 0.25], # Place the plate on the right side
            ylim=[-0.15, 0.05],
            ylim_prop=True,
            rotate_rand=True,
            rotate_lim=[0, 3.14, 0],
            qpos=[1, 0, 0, 0],
        )
        self.plate_id = np.random.choice([i for i in range(10)])
        self.plate = create_actor(
            scene=self,
            pose=plate_pose,
            modelname="003_plate",
            convex=True,
            model_id=0, # only model_data0.json is present
            is_static=True, # Make it static so it doesn't move when pushed
        )

        # Load the apple
        apple_pose = rand_pose(
            xlim=[-0.25, -0.05], # Place the apple on the left side
            ylim=[-0.15, 0.05],
            ylim_prop=True,
            rotate_rand=True,
            rotate_lim=[0, 3.14, 0],
            qpos=[1, 0, 0, 0],
        )
        self.apple_id = np.random.choice([0, 1]) # model_data0.json and model_data1.json are present
        self.apple = create_actor(
            scene=self,
            pose=apple_pose,
            modelname="035_apple",
            convex=True,
            model_id=self.apple_id,
        )

        self.add_prohibit_area(self.apple, padding=0.1)
        self.add_prohibit_area(self.plate, padding=0.1)

    def play_once(self):
        # The LLM will generate this part. For now, leave it empty.
        pass

    def check_success(self):
        # Check if the apple's center is close to the plate's center in x and y coordinates,
        # and slightly above the plate in the z coordinate
        apple_pose_p = np.array(self.apple.get_pose().p)
        plate_pose_p = np.array(self.plate.get_pose().p)

        # The apple should be directly above the plate's center
        target_pose_p = plate_pose_p.copy()
        target_pose_p[2] += 0.03 # Adjust this based on the thickness of the plate and radius of apple

        eps = np.array([0.05, 0.05, 0.05])

        return (np.all(abs(apple_pose_p - target_pose_p) < eps) and
                self.is_left_gripper_open() and
                self.is_right_gripper_open())
