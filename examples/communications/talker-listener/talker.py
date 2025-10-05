from eigen.core.client.comm_infrastructure.base_node import BaseNode, main
from eigen.types.generated import string_t
from eigen.core.tools.log import log
from typing import Dict, Any, Optional
import time

class ListenerNode(BaseNode):

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("Listener")
        self.sub = self.create_subscriber("chatter", string_t, self.listener_callback)

    def listener_callback(self, t, channel, msg: string_t):
        log.info(f"Received message data: {msg.data}")


if __name__ == "__main__":
    main(ListenerNode)