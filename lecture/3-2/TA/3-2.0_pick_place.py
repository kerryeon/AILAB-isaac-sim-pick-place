# ---- ---- ---- ----
# GIST-AILAB, 2023 summer school
# Day3. 
# 3-2.0 pick and place with cube object
# ---- ---- ---- ----


from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})


import sys, os
from pathlib import Path
current_dir = os.path.dirname(os.path.realpath(__file__))
directory = Path(current_dir).parent
sys.path.append(str(directory))


from utils.tasks.pick_place_basic_task import UR5ePickPlace
from utils.controllers.pick_place_controller_robotiq import PickPlaceController
from omni.isaac.core import World

from omni.kit.viewport.utility import get_active_viewport
import numpy as np


objects_position = np.array([0.4, 0.4, 0.1])
target_position = np.array([0.4, -0.33, 0.05])
target_orientation = np.array([0, 0, 0, 1])
offset = np.array([0, 0, 0.1])

my_world = World(stage_units_in_meters=1.0)
my_task = UR5ePickPlace(
                        objects_position=objects_position,
                        target_position=target_position,
                        offset=offset,
                        )
my_world.add_task(my_task)
my_world.reset()

task_params = my_task.get_params()
my_ur5e = my_world.scene.get_object(task_params["robot_name"]["value"])
my_controller = PickPlaceController(
    name="pick_place_controller", gripper=my_ur5e.gripper, robot_articulation=my_ur5e
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

while simulation_app.is_running():
    my_world.step(render=True)
    if my_world.is_playing():
        observations = my_world.get_observations()
        actions = my_controller.forward(
            picking_position=observations[task_params["task_object_name_0"]["value"]]["position"],
            placing_position=observations[task_params["task_object_name_0"]["value"]]["target_position"],
            current_joint_positions=observations[task_params["robot_name"]["value"]]["joint_positions"],
        )
        if my_controller.is_done():
            print("done picking and placing")
            break
        articulation_controller.apply_action(actions)
simulation_app.close()
