from eigen.core.client.comm_handler.service import send_service_request
from eigen.core.global_constants import DEFAULT_SERVICE_DECORATOR
from eigen.core.tools.eigen_graph.eigen_graph import network_info_lcm_to_dict
from eigen.types import flag_t, network_info_t


def fetch_network_info(host: str, port: int) -> dict:
    req = flag_t()
    lcm_msg = send_service_request(
        host,
        port,
        f"{DEFAULT_SERVICE_DECORATOR}/GetNetworkInfo",
        req,
        network_info_t,
    )
    return network_info_lcm_to_dict(lcm_msg)
