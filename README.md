# ArkMonster

Called a monster because that is how it looks at first sight, but...

<!-- markdownlint-disable-next-line MD001 MD033 -->
<img alt="it all makes sense" src="./docs/iams.png" width="360" height="240" />

## Instructions

Short introduction meant to be carried forward, everything including and after [How to Use this](#how-to-use-this) is "temporary" to introduce the project structure.

### General info

The project is based around `uv` workspaces and PEP 420 namespaces. `uv` uses plain Pyhton `venv` environment to install the dependencies using its custom dependency resolution algorithms, the resolution is then saved into `uv.lock`, which is a proprietary format that attempts to resolve the dependency constraints on all project-supported platforms (presently linux+x86_64/macos+x86_64+arm64) ahead of time. This won't prevent runtime issues, or problems with packages that do not conform to general Python package versioning/naming schemas. The lock file is updated whenever a package is added or removed from either the mata `src/ark_monster/` package or any of the `/packages`.

#### ark_monster

`ark_monster` is purely a meta-package, you can think of it as a convenient way to getting some predefined configuration of dependencies. To just get strated, the _default_ group of optionals is suitable. `ark_monster` is not nescessary to get started with Ark overall, an advanced user might opt to install individual packages with theor specific optinal gorups from `/packages` instead.

#### PEP 420 namespaces

All the packages have a source folder with a folder `/packages/**/src/ark/` that forms an implicit namespace. That is not a Python module - important to differentiate. This along with their `pyproject.toml` configuration then causes all of the code within Ark to be available under the `ark.**` namespace, e.g. `ark.core`, `ark.robots` or `ark.ml`.

### Getting started with development

#### Requirements

To get started you need to make sure Python 3.11, `make`, and `uv` are available in your path. Make is used to facilitate a convenient way to execute and orchestrate the initial installation.

1. Python 3.11
    - verify with `python3 --version`
    - ensure the reported version is `3.11.x`; the workspace is pinned to that series
2. make
    - check by executing `make --version`
    - if not availabe, check [make website](https://www.gnu.org/software/make/#download), or install using your package manager of choice if not included with the OS by default
3. uv
    - check by executing `uv --version`
    - if not available see [how to install uv](https://docs.astral.sh/uv/getting-started/installation/)

#### Installing dev environment

To understand what we are running a bit better it is useful to see output of `make help`:

```output
Available commands:
  make install                  - First-time setup (builds PyBullet on macOS, generates ark comm primitives, installs a venv, and more one-off procedures)
  make sync                     - Update dependencies
  make clean                    - Clean cache files
  make clean-all                - Clean cache files including built wheels

After 'make install', you can use 'uv sync' directly
```

1. run `make install` in the project root
    - if you are running on macos it will download the pybullet reporitory and built a wheel from scratch
    - it will proceed to implicitly create a Python venv and install the _default_ and _dev_ dependency extras of `ark_monster`
2. activate the venv by executing `source .venv/bin/activate`
3. run `ark --help` to verify the installation
4. run `pytest` to run the tests included

#### Running a script
When the `.venv` is created, you can just create a python script and conveniently run it using `uv run myscript.py` or when the environment is sourced just use `python myscript.py`

## How to use this

- use it for discussioin and protyping of the rearchitecture
- start moving over pieces, from the center core to the leafs (framework -> coms -> robots -> sensors -> ml etc.)
  - focus on moving small pieces and building up the tests as you go
- finally a renaming of the root package

Currently the `ark_monster` package is a metadata package through which the rest of the packages and their PEP 735 extras are installable. `ark_monster` defines these through its own extras.

## Migrating Code over

- look for `# TODO(FV):` or `# TODO(PREV):` and resolve!

## Further recommendations

### Ark CLI

- The Ark CLI should have a defined sets of dependencies corresponding to node installations
- The Ark CLI should have the capability to discover the available nodes through a dynamic registration (dependency injection pattern), say via a decorator. Custom implementations in the user space should import that decorator and register a new node under an edge type (say "MyFranka") with a compatible API of `ark_robots`.
- The Ark CLI should then be able to check and list all the registered nodes that are runable using the union of the currently installed dependencies and the registered node's required set of dependencies.
- Consider lightening up the node installations by not including the static assets in the package's wheel and managing some sort of an asset cache managed by the CLI. Throwing appropriate errors when assets are not present, giving an easy way to download/update/delete those assets, e.g. physical spatial definitions for visualisation/simulation.

### Definng and constraining version compatibility

- Consider what and how often it needs to change and in which manner. The core should contain mostly major-release stable implementations. E.g., it would be inconvenient to often have to introduce a backwards-incompatible change and have to release the whole of ark packages + major version bump them. for example it might be tempting to include some utils in the core, but anything implementation specific should live at the edge, such that when it changes, only the edge package has to be re-released with just a patch/minor version bump.
- Constraining the compatible versions would decrease the test-matrix (incorrectly assuming everything needs to be able to be installable and runable at once, that would be $O(n^2)$). Constraining all ark_robots/ark_sensors to be compatible within a minor version would force version-catchup re-releases of the robot/sensor packages even if only one changes, but makes the robot/sensor subtree $O(n)$.

## Installation and dependency resolution

Work-In-Progress: You can cheat now and just get going with this by running `make install; uv sync --extra default`

Please see [dependencies](./docs/1-dependencies.md)

## Project structure

Please see [project-structure](./docs/2-project-structure.md)

## Code Style

Please see [code-style](./docs/3-code-style.md)

## Testing

Please see [testing](./docs/4-testing.md)
