# 🧪 Developer Test — Step-by-Step (Markdown-friendly)
Prereq: Ark must already be installed on your machine.
1) Create a new test folder
mkdir developer_test
cd developer_test
2) Create the simulation node
Create sim_node.yaml, and paste the exact “PyBullet Simulation” sim-node snippet:
# global_config.yaml

Follow: https://arkrobotics.notion.site/Pybullet-Simulation-22be053d9c6f80a89cfdcda43fc4eee6


Check you have set it up correctly by running sim_node.py. Make sure you start a registry before using: ark registry start

1) Add the floor object
From your “Adding Objects” page, copy the given floor config exactly and place it right after the sim node in sim_node.yaml:

Follow: https://arkrobotics.notion.site/Adding-Objects-22be053d9c6f8043b84be0a1f9321e1e
Example: Floor (Box)

The floor/plane URDF block should be added unmodified.

Run sim_node again and you should see a pink square appear.

1) Add the Franka Panda robot as an object
Follow the same object pattern used for the drill in your objects tutorial, but point to the Franka URDF in your repo:
packages/ark_robots/src/ark/robots/franka_panda/panda_with_gripper.urdf
Add a new object entry that mirrors the drill’s structure/key names (i.e., use the same field names as the drill example), changing only the name, urdf_path and base_position:

urdf_path: packages/ark_robots/src/ark/robots/franka_panda/panda_with_gripper.urdf
base_position: [0, 0, 1.0]   # spawn 1 meter above the floor

1) Final checklist
 cond.yaml contains the unaltered sim-node snippet from PyBullet Simulation.
 The floor object block is pasted exactly from Adding Objects, with no edits.
 A Franka object block is added using the same schema/keys as the drill example, with:
urdf_path → packages/ark_robots/src/ark/robots/franka_panda/panda_with_gripper.urdf
base_position → [0, 0, 1.0]

Run sim_node again and you should see a pink square appear will a franka panda (falling or flying...).  
