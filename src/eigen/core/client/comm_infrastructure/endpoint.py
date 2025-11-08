from pathlib import Path
import lcm
from lcm import LCM
import uuid
from omegaconf import DictConfig

from eigen.core.config_utils.load_config import load_config, get_node_config

class EndPoint:
    def __init__(self, name: str, type: str, global_config: dict | Path | str | None) -> None:
        """!
        Initialize an Endpoint object for interacting with the registry and
        setting up LCM communication.

        @param global_config: Global configuration containing network settings.
        """
        self.name: str = name
        self.type: str = type
        self.node_id = str(uuid.uuid4())

        self.global_config: DictConfig = load_config(global_config)
        self.config, self.file = get_node_config(name, type, self.global_config)  #ignore type: tuple[DictConfig, str]
        
        self.network_config = self.global_config.get("network", {})

        self.registry_host = self.network_config.get(
            "registry_host", "127.0.0.1"
        )
        self.registry_port = self.network_config.get(
            "registry_port", 1234
        )
        self.lcm_network_bounces = self.network_config.get(
            "lcm_network_bounces", 1
        )
        
        udpm = f"udpm://239.255.76.67:7667?ttl={self.lcm_network_bounces}"
        self._lcm: LCM = lcm.LCM(udpm)


    
