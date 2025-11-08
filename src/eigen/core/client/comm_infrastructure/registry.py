import json
import socket
import struct
import sys
import threading
from collections.abc import Callable
from typing import Any

from eigen import DEFAULT_SERVICE_DECORATOR
from eigen.core.client.comm_handler.services import (
    Service,
    send_service_request,
)
from eigen.core.client.comm_infrastructure.endpoint import EndPoint
from eigen.core.tools import log
from eigen.types import flag_t, network_info_t, node_info_t

RequestPayload = dict[str, Any]
ResponsePayload = dict[str, Any]
ServiceLocation = tuple[str, int]


class Registry(EndPoint):
    """LCM registry responsible for service registration, discovery, and metadata."""

    SOCKET_TIMEOUT = 1.0

    def __init__(
        self,
        registry_host: str = "127.0.0.1",
        registry_port: int = 1234,
        lcm_network_bounces: int = 1,
    ):
        network_config = {
            "registry_host": registry_host,
            "registry_port": registry_port,
            "lcm_network_bounces": lcm_network_bounces,
        }
        global_config = {
            "network": network_config,
            "registry": {
                "registry": {
                    "config": {},
                    "file": "",
                }
            },
        }

        super().__init__(name="registry", type="registry", global_config=global_config)

        self.registry_host = registry_host
        self.registry_port = registry_port
        self.lcm_network_bounces = lcm_network_bounces

        self._services: dict[str, ServiceLocation] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self.error_flag = False
        self._server_thread: threading.Thread | None = None
        self._server_socket: socket.socket | None = None
        self._info_service: Service | None = None

        self._request_handlers: dict[
            str, Callable[[RequestPayload], ResponsePayload]
        ] = {
            "REGISTER": self._handle_register,
            "DISCOVER": self._handle_discover,
            "DEREGISTER": self._handle_deregister,
        }

    def _callback_get_network_info(self, channel, msg):  # noqa: D401 - LCM callback
        """Aggregate basic information about all nodes registered in the system."""
        del channel, msg  # Unused callback arguments

        nodes_info: list[node_info_t] = []
        req = flag_t()

        with self._lock:
            service_names = [
                name
                for name in self._services
                if name.startswith(f"{DEFAULT_SERVICE_DECORATOR}/GetInfo")
            ]

        for service_name in service_names:
            node_info = send_service_request(
                self.registry_host,
                self.registry_port,
                service_name,
                req,
                node_info_t,
            )
            if node_info is not None:
                nodes_info.append(node_info)

        res = network_info_t()
        res.n_nodes = len(nodes_info)
        for node in nodes_info:
            res.nodes.append(node)
        return res

    def _serve(self) -> None:
        """Main loop handling incoming registry requests."""
        try:
            server = self._create_server_socket()
        except OSError as exc:
            log.error(f"Error starting Registry server: {exc}")
            self.error_flag = True
            self._stop_event.set()
            return

        self._server_socket = server
        try:
            while not self._stop_event.is_set():
                try:
                    conn, addr = server.accept()
                except socket.timeout:
                    continue
                except OSError as exc:
                    if self._stop_event.is_set():
                        break
                    log.error(f"Registry: Error accepting connection: {exc}")
                    continue
                self._handle_connection(conn, addr)
        finally:
            server.close()
            self._server_socket = None

    def _create_server_socket(self) -> socket.socket:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.registry_host, self.registry_port))
        server.listen()
        server.settimeout(self.SOCKET_TIMEOUT)
        log.info(
            f"Registry Server started on {self.registry_host} : {self.registry_port}"
        )
        return server

    def _handle_connection(self, conn: socket.socket, addr: tuple[str, int]) -> None:
        with conn:
            log.info(f"Registry: Connected via client (ip, port): {addr}")
            try:
                request = self._receive_json(conn)
            except ValueError as exc:
                log.error(f"Registry: {exc}")
                return

            response = self._dispatch_request(request)
            self._send_json(conn, response)

    def _dispatch_request(self, request: RequestPayload) -> ResponsePayload:
        req_type = request.get("type")
        handler = self._request_handlers.get(req_type or "")
        if handler is None:
            return {"status": "ERROR", "message": "Unknown request type"}
        return handler(request)

    def _handle_register(self, request: RequestPayload) -> ResponsePayload:
        service_name = request.get("service_name")
        host = request.get("host")
        port = request.get("port")

        if not all([service_name, host, port]):
            return {"status": "ERROR", "message": "Missing fields in REGISTER"}

        with self._lock:
            self._services[service_name] = (host, port)

        log.info(
            f"Registry: Registered service '{service_name}' at {host}:{port}"
        )
        return {"status": "OK", "message": "Service registered successfully"}

    def _handle_discover(self, request: RequestPayload) -> ResponsePayload:
        service_name = request.get("service_name")
        if not service_name:
            return {
                "status": "ERROR",
                "message": "Missing service_name in DISCOVER",
            }

        with self._lock:
            service = self._services.get(service_name)

        if not service:
            log.warning(f"Registry: Service '{service_name}' not found")
            return {"status": "ERROR", "message": "Service not found"}

        host, port = service
        log.info(f"Registry: Service '{service_name}' found at {host}:{port}")
        return {"status": "OK", "host": host, "port": port}

    def _handle_deregister(self, request: RequestPayload) -> ResponsePayload:
        service_name = request.get("service_name") or request.get("name")
        if not service_name:
            return {
                "status": "ERROR",
                "message": "Missing service_name in DEREGISTER",
            }

        with self._lock:
            removed = self._services.pop(service_name, None)

        if removed:
            log.info(f"Registry: Deregistered service '{service_name}'")
            return {"status": "OK", "message": "Service deregistered successfully"}

        log.warning(f"Registry: Service '{service_name}' not found")
        return {"status": "ERROR", "message": "Service not found"}

    def _receive_json(self, conn: socket.socket) -> RequestPayload:
        raw_len = self._recvall(conn, 4)
        if not raw_len:
            raise ValueError("No message length received.")

        msg_len = struct.unpack("!I", raw_len)[0]
        payload = self._recvall(conn, msg_len)
        if not payload:
            raise ValueError("No data received.")

        try:
            return json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid request payload: {exc}") from exc

    def _send_json(self, conn: socket.socket, payload: ResponsePayload) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        conn.sendall(struct.pack("!I", len(encoded)))
        conn.sendall(encoded)

    def _recvall(self, conn: socket.socket, n: int) -> bytes | None:
        data = bytearray()
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def _stop(self) -> None:
        log.info("Shutting down server...")
        self._stop_event.set()

        if self._info_service:
            self._info_service.suspend()
            self._info_service = None

        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None

        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join()
        self._server_thread = None

        log.info("Registry Server stopped.")

    def _start_network_info_service(self) -> None:
        try:
            self._info_service = Service(
                f"{DEFAULT_SERVICE_DECORATOR}/GetNetworkInfo",
                flag_t,
                network_info_t,
                self._callback_get_network_info,
                self.registry_host,
                self.registry_port,
                host=self.registry_host,
                port=None,
                is_default=True,
            )
        except Exception as exc:  # pragma: no cover - defensive
            log.error(f"Failed to start default network info service: {exc}")
            self.error_flag = True
            self._stop_event.set()
            return

        if not self._info_service.registered:
            log.error("Default network info service failed to register.")
            self.error_flag = True
            self._stop_event.set()

    def start(self) -> None:
        """Start the registry server and block until it stops."""
        keyboard_interrupt = False
        self.error_flag = False
        self._stop_event.clear()

        try:
            self._server_thread = threading.Thread(target=self._serve, daemon=True)
            self._server_thread.start()

            self._start_network_info_service()

            while not self._stop_event.is_set():
                self._server_thread.join(timeout=1)
                if not self._server_thread.is_alive():
                    log.error("Server thread terminated unexpectedly.")
                    self.error_flag = True
                    break
        except KeyboardInterrupt:
            log.error("Program interrupted by user.")
            keyboard_interrupt = True
            self._stop_event.set()
        finally:
            self._stop()

        if self.error_flag:
            sys.exit(1)
        if keyboard_interrupt:
            sys.exit(0)
