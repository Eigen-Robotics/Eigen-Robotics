from pathlib import Path
import time

import typer

from ark.core.tools.launcher import NodeExecutor, load_launch_file
from ark.core.tools.log import log

app = typer.Typer()


def ark_launch(launch_file: str):
    """
    Main entry point for the launch script.

    Usage:
        python launch_script.py <launch_file.yaml>

    Steps:
        1. Parse the provided launch file path from sys.argv.
        2. Recursively load and merge all node configurations (including nested includes).
        3. Create and start each node process using NodeExecutor.
        4. Monitor the running processes, logging any failures or normal terminations.
        5. Shut down gracefully on user interrupt (Ctrl+C).
    """
    launch_path = Path(launch_file)

    included_files = set()
    nodes_config = load_launch_file(launch_path, included_files)

    processes = []
    for node_name, config in nodes_config.items():
        executor = NodeExecutor(node_name, config)
        node_info = executor.run()
        processes.append(node_info)

        log.ok(f"Started node '{node_name}' with PID {node_info.process.pid}")
        if node_info.log_path:
            log.ok(
                f"Logs for '{node_name}' are being written to {node_info.log_path}"
            )

    try:
        while processes:
            for node_info in processes[:]:
                retcode = node_info.process.poll()
                if retcode is not None:
                    if retcode == 0:
                        log.ok(
                            f"Node '{node_info.node_name}' has exited successfully."
                        )
                    else:
                        log.error(
                            f"Node '{node_info.node_name}' exited with return code {retcode}."
                        )
                        if node_info.log_path:
                            log.error(f"Check logs at {node_info.log_path}")

                    if node_info.log_file:
                        node_info.log_file.close()

                    processes.remove(node_info)

            time.sleep(1)
    except KeyboardInterrupt:
        log.warn("KeyboardInterrupt received. Terminating all nodes.")
        for node_info in processes:
            node_info.process.terminate()
        for node_info in processes:
            node_info.process.wait()
    finally:
        for node_info in processes:
            if node_info.log_file:
                node_info.log_file.close()
        log.ok("All nodes have been terminated.")


@app.command()
def start(launch_file: str):
    """
    Start the launcher with the specified launch file.

    Args:
        launch_file (str): The path to the launch file.
    """
    ark_launch(launch_file)


def main():
    app()


if __name__ == "__main__":
    main()

# TRIVIA: Side Oiled Slideway Launching or Chrstening are ways of launching an ARK(ship)

# ====================================================================================================
# Example Usage of the Launcher YAML Configuration
# ====================================================================================================

# talker:
#   target: /nfs/rlteam/sarthakdas/arkframework/examples/basics/talker_listener/talker.py
#   display: terminal
# listener:
#   target: /nfs/rlteam/sarthakdas/arkframework/examples/basics/talker_listener/listener.py
#   display: logfile
