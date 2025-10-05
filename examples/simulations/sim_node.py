# Import necessary modules
from eigen.core.client.comm_infrastructure.base_node import main
from eigen.core.system.simulation.simulator_node import SimulatorNode
from eigen.core.tools.log import log

# Path to your configuration file
CONFIG_PATH = "global_config.yaml"

# Create your custom simulator by inheriting from SimulatorNode
class MySimulatorNode(SimulatorNode):

    def initialize_scene(self):
        """
        This function is called after objects are loaded but before simulation starts.
        Use it to set up your scene, modify parameters, or add custom objects.
        """
        pass
    
    def step(self):
        """
        This function is called at each simulation step.
        Use it for debugging or implementing custom behaviors during simulation.
        
        Examples:
        - Print debug info: log.info("Current position: ", self.robot.get_position())
        - Apply forces: self.apply_force(...)
        - Check conditions: if self.check_collision(): ...
        """
        pass

# Entry point - this runs your node with the specified configuration
if __name__ == "__main__":
    main(MySimulatorNode, CONFIG_PATH)