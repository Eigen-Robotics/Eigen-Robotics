from eigen.core.client.comm_infrastructure.base_node import BaseNode, main
from eigen.types.generated import string_t
from eigen.core.tools.log import log
from typing import Dict, Any, Optional
import time

class TalkerNode(BaseNode):

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("Talker")
        self.pub = self.create_publisher("chatter", string_t)
        self.create_stepper(10, self.step) # 10 Hz

    def step(self):
        msg = string_t()
        msg.data = f"Hello World {time.time()}"
        self.pub.publish(msg)
        log.info(f"Published message data: {msg.data}")


if __name__ == "__main__":
    main(TalkerNode)