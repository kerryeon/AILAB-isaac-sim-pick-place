# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

# add necessary directories to sys.path
import sys, os
from pathlib import Path
current_dir = os.path.dirname(os.path.realpath(__file__))
directory = Path(current_dir).parent
sys.path.append(str(directory))

from utils.tasks.basic_task import SetUpUR5e
from omni.isaac.core import World
from omni.kit.viewport.utility import get_active_viewport
import numpy as np
from utils.controllers.gripper import GripperController

# if you don't declare objects_position, the objects will be placed randomly
objects_position = np.array([0.4, 0.4, 0.1])
target_position = np.array([0.4, -0.33, 0.05])  # 0.55 for considering the length of the gripper tip
target_orientation = np.array([0, 0, 0, 1])
offset = np.array([0, 0, 0.1])  # releasing offset at the target position

my_world = World(stage_units_in_meters=1.0)
my_task = SetUpUR5e()
my_world.add_task(my_task)
my_world.reset()

task_params = my_task.get_params()
my_ur5e = my_world.scene.get_object(task_params["robot_name"]["value"])
my_controller = GripperController(
    name="gripper_controller", gripper=my_ur5e.gripper, robot_articulation=my_ur5e
    )
'''
check that you modified the rmp_flow_config in the PickPlaceController -> RMPFlowController
from "UR10", "RMPflowSuction" to "UR5e", "RMPflow"

self.rmp_flow_config = mg.interface_config_loader.load_supported_motion_policy_config(
    # "UR10", "RMPflowSuction"
    "UR5e", "RMPflow"
)
'''

articulation_controller = my_ur5e.get_articulation_controller()
my_controller.reset()

viewport = get_active_viewport()
viewport.set_active_camera('/World/ur5e/realsense/Depth')
viewport.set_active_camera('/OmniverseKit_Persp')

while True:
    code = input('Enter the code:')
    if code in ["o", "open", "c", "close"]:
        break
    else:    
        print("wrong code")
print('code : ', code)

while simulation_app.is_running():
    my_world.step(render=True)
    if my_world.is_playing():
        observations = my_world.get_observations()
        if code == "o" or code == "open":
            actions = my_controller.open(
                current_joint_positions=observations[task_params["robot_name"]["value"]]["joint_positions"],
            )
        elif code == "c" or code == "close":
            actions = my_controller.close(
                current_joint_positions=observations[task_params["robot_name"]["value"]]["joint_positions"],
            )

        articulation_controller.apply_action(actions)
        if my_controller.is_done():
            if code == "o" or code == "open":
                print("done opening the gripper\n")
            elif code == "c" or code == "close":
                print("done closing the gripper\n")

            while True:
                code = input('Enter the code:')
                if code in ["o", "open", "c", "close", "q", "quit"]:
                    break
                else:    
                    print("wrong code")
            print('code : ', code)
            print()
            if code == 'q' or code == 'quit':
                break
            my_controller.reset()
simulation_app.close()
