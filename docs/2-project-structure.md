# Comprehensive EIGEN Packaging Approaches Comparison

[back to README](../README.md)

## Directory Structures

### Approach 1 Granular Packages

```output
eigen_repositories/                       # Multiple repositories
├── eigen_framework/                      # Core package
│   ├── src/eigen_framework/
│   │   ├── core/
│   │   ├── communication/
│   │   └── __init__.py
│   └── pyproject.toml
├── eigen_robots_franka/                  # Franka robot package
│   ├── src/eigen_robots_franka/
│   │   ├── robot.py
│   │   └── __init__.py
│   └── pyproject.toml
├── eigen_robots_unitree/                 # Unitree robot package
│   ├── src/eigen_robots_unitree/
│   │   ├── robot.py
│   │   └── __init__.py
│   └── pyproject.toml
├── eigen_sensors_realsense/              # RealSense package
│   ├── src/eigen_sensors_realsense/
│   │   ├── camera.py
│   │   └── __init__.py
│   └── pyproject.toml
└── eigen_ml_rl/                          # RL package
    ├── src/eigen_ml_rl/
    │   ├── algorithms/
    │   └── __init__.py
    └── pyproject.toml
```

### Approach 2 Single Monolithic Package

```output
eigen_robotics/                           # Single package
├── src/eigen/
│   ├── core/                          # Core framework
│   │   ├── communication/
│   │   ├── graph/
│   │   └── __init__.py
│   ├── robots/
│   │   ├── franka/                    # Franka implementation
│   │   │   ├── robot.py
│   │   │   └── __init__.py
│   │   ├── unitree/                   # Unitree implementation
│   │   │   ├── robot.py
│   │   │   └── __init__.py
│   │   └── __init__.py                # Robot registry
│   ├── sensors/
│   │   ├── realsense/                 # RealSense implementation
│   │   │   ├── camera.py
│   │   │   └── __init__.py
│   │   └── __init__.py                # Sensor registry
│   └── ml/
│       ├── rl/                        # RL implementations
│       ├── il/                        # IL implementations
│       └── __init__.py
└── pyproject.toml                     # Single configuration
```

### Approach 3 Semantic Packages (Workspace)

```output
eigen_robotics/                           # Workspace root
├── Makefile                           # Cross-platform setup automation
├── scripts/
│   └── build_pybullet_macos.py       # macOS PyBullet builder
├── packages/
│   ├── eigen_framework/                 # Core abstractions + types
│   │   ├── src/eigen/
│   │   │   ├── core/
│   │   │   │   └── __init__.py
│   │   │   └── types/
│   │   │       ├── __init__.py
│   │   │       ├── eigen_type_defs/     # LCM definitions
│   │   │       └── utils/
│   │   └── pyproject.toml
│   ├── eigen_robots/                    # Robot embodiments
│   │   ├── src/eigen/
│   │   │   └── robots/
│   │   │       ├── __init__.py
│   │   │       └── main.py
│   │   └── pyproject.toml
│   ├── eigen_sensors/                   # Perception capabilities
│   │   ├── src/eigen/
│   │   │   └── sensors/
│   │   │       ├── __init__.py
│   │   │       └── main.py
│   │   └── pyproject.toml
│   └── eigen_ml/                        # Learning capabilities
│       ├── src/eigen/
│       │   └── ml/
│       │       ├── __init__.py
│       │       └── main.py
│       └── pyproject.toml
├── tests/                             # Integration tests
├── pyproject.toml                     # Workspace config
└── uv.lock                           # Unified lockfile
```

**⚠️ Critical for Namespace Packages**: NO `__init__.py` files in any `src/eigen/` directories! These break namespace package discovery.**

## Individual Approach Descriptions

### Approach Granular Packages

**Philosophy**: Each robot, sensor, or ML implementation gets its own package and repository.

**Installation**:

Work-In-Progress, this is the goal:

`pip install eigen-robots[franka] eigen-sensors[realsense]`

Currently:

**Selective installation**:

```bash
uv sync --extra robots --extra sensors --extra ml  # All capabilities
uv sync --extra robots                              # Just robots
uv sync --extra dev                                 # Development tools
```

**Characteristics**:

- Maximum separation of concerns
- Independent versioning per implementation
- Minimal dependency trees per package
- Requires understanding of implementation taxonomy
- High administrative overhead (15+ repositories)

**Best For**:

- Large teams with clear ownership boundaries
- When implementations have fundamentally incompatible dependencies
- Platform-as-a-service scenarios where users pick specific implementations

### Approach 2 Single Monolithic Package

**Philosophy**: Everything robotics-related lives in one package with optional dependencies.

**Installation**: `pip install eigen-robotics[franka,realsense,rl]`

**Characteristics**:

- Single installation entry point
- Unified namespace and version
- All implementations share dependency resolution
- Simplified development and testing
- Potential for dependency conflicts across unrelated implementations

**Best For**:

- Small to medium teams with shared ownership
- When user mental model is "I want robotics capabilities"
- Rapid prototyping and research environments

### Approach 3 Semantic Packages (Workspace)

**Philosophy**: Group related implementations by capability domain, manage as unified workspace.

**Installation**: `pip install eigen-framework eigen-robots[franka] eigen-sensors[realsense]`

**Characteristics**:

- Capability-based package boundaries
- Shared namespace across packages
- Domain-specific dependency resolution
- Natural team ownership boundaries
- Balanced modularity vs complexity

**Best For**:

- Medium to large teams organized by expertise areas
- When capabilities evolve at different rates
- Production systems requiring selective deployment

## Detailed Comparison

### Maintenance Burden

**Granular Packages**:

- **High**: 15+ repositories to maintain
- Separate CI/CD pipelines per package
- Version coordination matrix complexity
- Cross-package compatibility testing challenges
- Fragmented documentation and issue tracking

**Single Monolithic Package**:

- **Low**: Single repository and CI/CD pipeline
- Unified version management
- Comprehensive integration testing in one place
- Single point of documentation
- Potential for large, complex codebase

**Semantic Packages**:

- **Medium**: 4-5 packages to coordinate
- Domain-specific CI/CD with workspace-level integration
- Logical grouping reduces coordination complexity
- Clear ownership boundaries reduce conflicts

### Release Cycles

**Granular Packages**:

- **Maximum Flexibility**: Each implementation can release independently
- **Coordination Overhead**: Breaking changes require careful orchestration
- **User Confusion**: Complex compatibility matrix between packages
- Different implementations can have very different stability levels

**Single Monolithic Package**:

- **Unified Releases**: Everything releases together
- **Coordination Required**: All features must be ready simultaneously
- **Clear Versioning**: Single version number for entire framework
- Slower releases due to "weakest link" problem

**Semantic Packages**:

- **Domain-Specific Cycles**: Robots, sensors, ML can evolve independently
- **Logical Coordination**: Related implementations release together
- **Selective Updates**: Users can update capabilities independently
- Natural boundaries for stability levels (core stable, ML experimental)

### Dependency Resolution

**Granular Packages**:

- **Isolated**: Minimal dependencies per package
- **Complex Installation**: Users must understand dependency relationships
- **Conflicts Rare**: Limited scope per package
- Heavy dependency on package managers for resolution

**Single Monolithic Package**:

- **Unified**: All implementations share dependency space
- **Potential Conflicts**: Competing requirements between unrelated features
- **Simple Installation**: Single resolution process
- Optional dependencies provide some isolation

**Semantic Packages**:

- **Domain-Scoped**: Related implementations share resolution
- **Logical Isolation**: Unrelated capabilities (robots vs ML) separate
- **Manageable Complexity**: Users understand capability relationships
- Best balance of isolation and simplicity

### End User Use Cases

#### Running Single Robot in Real World

**Granular Packages**:

```bash
pip install eigen-framework eigen-robots-franka eigen-sensors-realsense
# User must know specific package names
# Minimal dependencies (good for edge deployment)
```

**Single Monolithic Package**:

```bash
pip install eigen-robotics[franka,realsense]
# Simple, discoverable syntax
# Pulls in some unused code (but not deps)
```

**Semantic Packages**:

```bash
pip install eigen-framework eigen-robots[franka] eigen-sensors[realsense]
# Intuitive capability-based selection
# Clean separation between robot and sensor capabilities
```

#### Simulating Graph of Multiple Robots

**Granular Packages**:

```bash
pip install eigen-framework eigen-robots-franka eigen-robots-unitree eigen-simulation
# Complex multi-package installation
# Must understand which packages provide simulation
```

**Single Monolithic Package**:

```bash
pip install eigen-robotics[franka,unitree,simulation]
# Simple syntax, all simulation features available
# Easy to discover all robot types
```

**Semantic Packages**:

```bash
pip install eigen-framework eigen-robots[franka,unitree,simulation]
# Clean capability grouping
# Simulation is logically part of robot capabilities
```

#### ML Research with Simulation

**Granular Packages**:

```bash
pip install eigen-framework eigen-robots-simulation eigen-ml-rl eigen-ml-il
# Complex installation for ML research
# ML algorithms in separate packages
```

**Single Monolithic Package**:

```bash
pip install eigen-robotics[simulation,rl,il]
# Simple research setup
# All ML features easily discoverable
```

**Semantic Packages**:

```bash
pip install eigen-framework eigen-robots[simulation] eigen-ml[rl,il]
# Natural separation: embodiment vs intelligence
# ML team can evolve algorithms independently
```

### Testing Strategy

**Granular Packages**:

- **Unit Testing**: Excellent isolation per package
- **Integration Testing**: Complex cross-package test setup
- **CI/CD**: Multiple pipelines, coordination challenges
- **Coverage**: Difficult to ensure comprehensive system coverage

**Single Monolithic Package**:

- **Unit Testing**: Requires careful module isolation
- **Integration Testing**: Comprehensive testing in single codebase
- **CI/CD**: Single pipeline with complete coverage
- **Coverage**: Easy to ensure full system testing

**Semantic Packages**:

- **Unit Testing**: Good isolation within capability domains
- **Integration Testing**: Cross-capability integration at workspace level
- **CI/CD**: Domain-specific + workspace-level testing
- **Coverage**: Balanced approach with clear test boundaries

## Comprehensive Comparison Matrix

| Aspect | Granular Packages | Single Monolithic | Semantic Packages |
|--------|------------------|-------------------|-------------------|
| **Installation Complexity** | High (15+ packages) | Low (1 command) | Medium (3-4 packages) |
| **User Mental Model** | Implementation-focused | Framework-focused | **Capability-focused** ✅ |
| **Dependency Conflicts** | Low (isolated) | High (shared space) | **Medium (domain-scoped)** ✅ |
| **Maintenance Burden** | High (many repos) | Low (one repo) | **Medium (few logical repos)** ✅ |
| **Release Coordination** | Complex (many packages) | Simple (one version) | **Balanced (domain cycles)** ✅ |
| **Team Ownership** | Over-fragmented | Too centralized | **Natural boundaries** ✅ |
| **Real Robot Deployment** | Minimal deps ✅ | Some unused code | **Clean capability selection** ✅ |
| **Multi-Robot Simulation** | Complex setup | Simple setup ✅ | **Logical grouping** ✅ |
| **ML Research** | Complex setup | Simple setup ✅ | **Domain separation** ✅ |
| **Discovery** | Poor (taxonomy knowledge) | Good (one place) | **Excellent (intuitive)** ✅ |
| **Namespace Clarity** | Fragmented | Unified ✅ | **Unified + Logical** ✅ |
| **Testing Integration** | Difficult | Easy ✅ | **Balanced** ✅ |
| **Documentation** | Fragmented | Unified ✅ | **Logically organized** ✅ |

## Recommendation

**Semantic Packages (Approach 3)** provides the optimal balance for EIGEN because it:

1. **Matches user mental models** (capabilities, not implementations)
2. **Provides natural team boundaries** (domain expertise)
3. **Balances modularity vs complexity** (4 packages vs 15+ or 1)
4. **Enables appropriate release cycles** (domains evolve at natural rates)
5. **Supports all use cases elegantly** (deployment, research, simulation)
6. **Reduces maintenance overhead** while preserving modularity benefits

This approach addresses your original concerns about multi-repo fragmentation while avoiding the potential issues of monolithic packaging, creating an architecture that scales with both team size and system complexity.

[back to README](../README.md)
