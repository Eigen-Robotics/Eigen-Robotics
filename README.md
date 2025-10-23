<br><br>

<p align="center">
  <img src="assets/eigen_logo_vertical.png" alt="Eigen Robotics Logo" width="300"/>
</p>


<p align="center">
  <em>Python-First Robotics — Build, Simulate, and Deploy Robots 10× Faster</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/eigen-robotics/"><img src="https://img.shields.io/pypi/v/eigen-robotics.svg?color=FF66B2" alt="PyPI"></a>
  <a href="https://pypi.org/project/eigen-robotics/"><img src="https://img.shields.io/pypi/dm/eigen-robotics.svg?color=44cc11" alt="PyPI Downloads"></a>
  <a href="https://github.com/Eigen-Robotics/Eigen-Robotics/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Eigen-Robotics/Eigen-Robotics?color=lightgrey" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/github/stars/Eigen-Robotics/Eigen-Robotics?style=social" alt="Stars"></a>
</p>

---

## 🧭 Overview

**Eigen Robotics** is a **Python-first robotics framework** built to make **developing, training, and deploying robots** dramatically simpler and faster. It **unifies simulation and real-world operation** under a single, consistent codebase, removing the need to rebuild tasks across different simulators or hardware setups. With a **lightweight, modular architecture** and seamless **Python integration**, Eigen allows researchers and engineers to move from **idea to working robot** in a fraction of the time, enabling a workflow that feels as intuitive and flexible as **modern machine-learning frameworks like PyTorch**.

---

## ✨ Features

- 🚀 **Unified Codebase** — Run the same task in PyBullet, MuJoCo, or on the real robot.
- 🔌 **Extensible Drivers** — Integrate any robot or sensor through a simple interface.
- 🧠 **ML-Native Design** — Plug directly into PyTorch, imitation learning, and RL pipelines.
- 🧩 **Plug-and-Play Architecture** — Add robots, sensors, and simulators via YAML configs.
- ⚙️ **Cross-Platform** — Works seamlessly on macOS and Ubuntu.
- 🧰 **CLI + GUI Tools** — Launch graphs, monitor data, and visualize systems in real time.


---

## 🚀 Quick Start

### Install from PyPI
```bash
pip install eigen-robotics
```

### Develop from Source
```bash
git clone https://github.com/Eigen-Robotics/Eigen-Robotics.git
cd Eigen-Robotics
uv sync --extra default
```
Supports Python 3.11+ on macOS and Ubuntu.

---

## 🧪 Quick Example

### Python API
```python
import eigen

env = eigen.make("franka_pickplace", backend="pybullet")
env.reset()
env.step([0.1, -0.2, 0.3])
```

### CLI Workflow
```bash
eigen graph launch examples/franka_pickplace.yaml
```

<p align="center">
  <img src="assets/demo.gif" alt="Eigen Demo" width="70%"/>
</p>

---

## 🧱 Project Layout
```text
eigen-robotics/
├── packages/
│   ├── eigen_framework/
│   ├── eigen_types/
│   ├── eigen_franka/
│   └── eigen_sensors/
├── examples/
├── docs/
└── README.md
```

---

## 🧩 Configuration Example
```yaml
robot:
  type: franka
  backend: pybullet

sensors:
  - type: realsense
    topic: /camera/rgb
```

---

## 🤝 Contributing

We welcome contributions of all sizes. Before opening a PR:

```bash
pytest -v
ruff check .
```

See `CONTRIBUTING.md` for full guidelines.

---

## 📚 Documentation & Links

- 📘 Documentation: coming soon
- 🌍 Website: coming soon
- 💬 Discord: coming soon

---

## 📄 License

Released under the [Eigen Robotics Academic License (ERAL) v1.0](LICENSE), which permits academic and personal educational use only. Commercial usage and any use by companies or other for-profit entities is prohibited.

<p align="center">
  <em>“Turn concepts into robots — Python-first, modular, and fast.”</em>
</p>
