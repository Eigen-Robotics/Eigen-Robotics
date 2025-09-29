from dataclasses import dataclass
import enum
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time

import typer
import yaml

app = typer.Typer()


class TargetType(enum.Enum):
    """
    An enumeration to specify the type of target that will be executed:

    1. SCRIPT: A Python file (e.g., my_script.py).
    2. MODULE: A Python module (e.g., my_package.my_module).
    """

    SCRIPT = 0
    MODULE = 1


@dataclass
class NodeProcessInfo:
    """
    A data class that holds information about a running node process:

    Attributes:
        node_name (str): The unique name of the node.
        process (subprocess.Popen): The Popen object representing the node's process.
        log_path (Optional[Path]): The optional path to the log file (None if using terminal).
        log_file (Optional[object]): The optional file handle for the log file.
    """

    node_name: str
    process: subprocess.Popen
    log_path: Path | None
    log_file: object | None


class NodeExecutor:
    """
    A class responsible for configuring and launching a node as described by a YAML configuration.

    Usage:
        node_exec = NodeExecutor("my_node", config_dictionary)
        node_info = node_exec.run()

    This will spawn the specified target (script or module) in a subprocess,
    optionally logging its output to a file or displaying it in the terminal.
    """

    def __init__(self, node_name: str, config: dict):
        """
        Initialize the NodeExecutor with a node name and its corresponding configuration.

        Args:
            node_name (str): The unique name of this node.
            config (dict): The YAML-derived configuration dictionary for this node.
        """
        self.name = node_name
        self.config = config

    def get_target(self) -> str:
        """
        Retrieve the 'target' value from the configuration.

        Returns:
            str: The 'target' string (file path or module name).

        Raises:
            ValueError: If the 'target' key is missing from the configuration.
        """
        try:
            return self.config["target"]
        except KeyError as ke:
            raise ValueError(
                f"You must provide a target for the node '{self.name}'"
            ) from ke

    def get_target_type(self) -> TargetType:
        """
        Determine whether the target is a Python script or a Python module.

        Returns:
            TargetType: An enum indicating SCRIPT or MODULE.

        Raises:
            ValueError: If the target is neither a recognized file nor an importable module.
        """
        target = self.get_target()

        # Check if it's a file
        if os.path.isfile(target):  # noqa: PTH113
            return TargetType.SCRIPT

        # Otherwise, check if it is an importable module
        spec = importlib.util.find_spec(target)
        if spec is not None:
            return TargetType.MODULE

        raise ValueError(
            f"Target '{target}' is neither a valid script file nor an importable module."
        )

    def get_command(self) -> list:
        """
        Build the full command (list of strings) for the subprocess.
        This includes the Python executable and the target (script or module).

        Returns:
            list: The full command list for starting the subprocess.
        """
        python_cmd = [
            sys.executable,
            "-u",  # unbuffered output
        ]

        target_type = self.get_target_type()

        if target_type == TargetType.SCRIPT:
            # e.g. python -u my_script.py
            cmd = python_cmd + [self.get_target()]
        else:
            # e.g. python -u -m my_module
            cmd = python_cmd + ["-m", self.get_target()]

        return cmd

    def setup_display(self):
        """
        Set up how the node's output (stdout, stderr) will be handled:

        'terminal' -> output goes to the parent's stdout/stderr.
        'logfile'  -> output is directed to a dedicated log file under .noahrlogs/<node_name>.
        Any other string -> considered a file path, output is directed to that file.

        Returns:
            tuple: (stdout, stderr, log_path, log_file)
        """
        display = self.config.get("display", "logfile")  # default is 'logfile'
        log_file, log_path = None, None

        if display == "terminal":
            # Inherit stdout/stderr from parent
            stdout, stderr = None, None
        elif display == "logfile":
            # Store logs in the current working directory under .noahrlogs/<node_name>
            logs_dir = Path.cwd() / ".arklogs"
            logs_dir.mkdir(parents=True, exist_ok=True)

            node_logs_dir = logs_dir / self.name
            node_logs_dir.mkdir(parents=True, exist_ok=True)

            stamp = time.time_ns()
            log_path = node_logs_dir / f"{stamp}.log"
            # TODO(FV): review, remova noqa
            log_file = open(log_path, "w", buffering=1)  # noqa: PTH123
            stdout, stderr = log_file, subprocess.STDOUT
        else:
            # Treat 'display' as a path to a file
            log_path = Path(display)
            log_file = open(log_path, "w", buffering=1)  # noqa: PTH123
            stdout, stderr = log_file, subprocess.STDOUT

        return stdout, stderr, log_path, log_file

    def run(self) -> NodeProcessInfo:
        """
        Launch the node process according to the configuration.

        Returns:
            NodeProcessInfo: An object containing process details (PID, log paths, etc.)
        """
        cmd = self.get_command()
        stdout, stderr, log_path, log_file = self.setup_display()

        process = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)

        return NodeProcessInfo(
            node_name=self.name,
            process=process,
            log_path=log_path,
            log_file=log_file,
        )


def load_launch_file(launch_path: Path, included_files: set[Path]) -> dict:
    """
    Recursively load a YAML launch file and return a dictionary of node configurations.
    Supports the 'include' key, allowing composition of multiple YAML files.

    Args:
        launch_path (Path): The filesystem path to the launch file.
        included_files (Set[Path]): A set of files that have already been included (to prevent loops).

    Returns:
        Dict: A dictionary mapping node names to their configuration dictionaries.

    Raises:
        ValueError: If there's a circular include or duplicate node name.
    """
    launch_path = launch_path.resolve()

    if launch_path in included_files:
        raise ValueError(f"Circular include detected for file: {launch_path}")
    included_files.add(launch_path)

    # TODO(FV): review, remove noqa
    with open(launch_path, "r") as f:  # noqa: PTH123, UP015
        launch_content = yaml.load(f, Loader=yaml.SafeLoader)

    nodes = {}

    # The YAML should be a dict of node_name -> node_config
    for key, config in launch_content.items():
        if "include" in config:
            include_path = Path(config["include"])
            if not include_path.is_absolute():
                include_path = launch_path.parent / include_path

            included_nodes = load_launch_file(include_path, included_files)

            for included_node_name in included_nodes:
                if included_node_name in nodes:
                    raise ValueError(
                        f"Duplicate node name '{included_node_name}' found "
                        f"when including '{include_path}'"
                    )
                nodes[included_node_name] = included_nodes[included_node_name]
        else:
            if key in nodes:
                raise ValueError(
                    f"Duplicate node name '{key}' found in '{launch_path}'"
                )
            nodes[key] = config

    return nodes
