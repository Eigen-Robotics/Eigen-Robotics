from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
import re

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class ComponentType(str, Enum):
    ROBOT = "robot"
    SENSOR = "sensor"
    OBJECT = "object"


class InvalidComponentNameError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ComponentSpec(BaseModel):
    component_type: ComponentType
    is_driver: bool = False
    id: str = Field(..., min_length=3, max_length=50)

    @field_validator("id", mode="after")
    @classmethod
    def validate_id(cls, v: str) -> str:
        # Semantic ID: lowercase, alphanumeric with hyphens/underscores
        if not re.match(r"^[a-z][a-z0-9_\-]*$", v):
            raise ValueError(
                "ID must start with letter, contain only lowercase letters, numbers, hyphens, underscores"
            )

        # Ensure 'base' is never used in the first part
        first_part = v.replace("_", "-").split("-")[0]
        if first_part == "base":
            raise InvalidComponentNameError(
                "'base' cannot be used as the first part of component ID"
            )

        return v

    @field_validator("id", mode="after")
    @classmethod
    def validate_semantic_naming(cls, value: str, info: ValidationInfo) -> str:
        # Ensure ID is somewhat semantic to component type
        if info.data and "component_type" in info.data:
            # component_type = info.data["component_type"]
            # e.g. "franka-base" or "franka_custom"

            # TODO(FV): Implement proper validation logic for "base" restriction
            # Currently commented out to allow flexible naming except for "base" restriction
            # Default components should use "base", non-default should not use "base"
            # if not any(
            #     part in value.replace("_", "-").split("-")[1:]
            #     for part in ["base", "custom"]
            # ):
            #     raise InvalidComponentNameError(
            #         "Component must contain a semantic designation of 'default' or 'custom' in the ID on any of the parts except the first. Parts separated by '-' or '_'."
            #     )
            pass

        return value


def _validate_component_inheritance(cls: type, spec: ComponentSpec) -> None:
    """! Validate that registered component inherits from correct base class."""

    # Import here to avoid circular imports
    from eigen.core.system.driver import (
        ComponentDriver,
        RobotDriver,
        SensorDriver,
    )

    if spec.is_driver:
        if spec.component_type == ComponentType.SENSOR:
            if not issubclass(cls, SensorDriver):
                raise TypeError(
                    f"Sensor driver {cls.__name__} must inherit from SensorDriver"
                )

        elif spec.component_type == ComponentType.ROBOT:
            if not issubclass(cls, RobotDriver):
                raise TypeError(
                    f"Robot driver {cls.__name__} must inherit from RobotDriver"
                )

        elif spec.component_type == ComponentType.OBJECT:
            # TODO(FV): comment out for now
            # Objects can have drivers but use base ComponentDriver?
            if not issubclass(cls, ComponentDriver):
                raise TypeError(
                    f"Object driver {cls.__name__} must inherit from ComponentDriver"
                )

    else:
        # Add validation for non-driver components if you have base classes for them
        # For example:
        # if spec.component_type == ComponentType.SENSOR:
        #   if not issubclass(cls, BaseSensor):
        #     raise TypeError(f"Sensor {cls.__name__} must inherit from BaseSensor")
        pass


@dataclass(frozen=True)
class _ComponentKey:
    component_type: ComponentType
    component_id: str
    is_default: bool
    is_driver: bool


_component_registry: dict[_ComponentKey, type] = {}


def _validate_default_component_naming(component_id: str) -> None:
    """Validate that default components have 'base' in non-first parts."""
    parts = component_id.replace("_", "-").split("-")
    if len(parts) < 2:
        raise InvalidComponentNameError(
            "Default component ID must contain 'base' in a non-first part (separated by '-' or '_')"
        )

    non_first_parts = parts[1:]
    if "base" not in non_first_parts:
        raise InvalidComponentNameError(
            "Default component ID must contain 'base' in a non-first part (separated by '-' or '_')"
        )


def _validate_non_default_component_naming(component_id: str) -> None:
    """Validate that non-default components do not contain 'base' anywhere."""
    parts = component_id.replace("_", "-").split("-")
    if "base" in parts:
        raise InvalidComponentNameError(
            "Non-default component ID must not contain 'base' (reserved for default components)"
        )


def _register_default_component(spec: ComponentSpec):
    def decorator(cls: type):
        _validate_component_inheritance(cls, spec)
        _validate_default_component_naming(spec.id)

        key = _ComponentKey(
            component_type=spec.component_type,
            component_id=spec.id,
            is_driver=spec.is_driver,
            is_default=True,
        )
        _component_registry[key] = cls
        return cls

    return decorator


def register_component(spec: ComponentSpec):
    def decorator(cls: type):
        _validate_component_inheritance(cls, spec)
        _validate_non_default_component_naming(spec.id)

        key = _ComponentKey(
            component_type=spec.component_type,
            component_id=spec.id,
            is_driver=spec.is_driver,
            is_default=False,
        )
        # TODO(FV): check if id is already registered and reject it
        _component_registry[key] = cls
        return cls

    return decorator


def list_components() -> dict[_ComponentKey, type]:
    return deepcopy(_component_registry)


def get_component(
    component_type: ComponentType, component_id: str, is_driver: bool = False
) -> type | None:
    """Gets a single component."""
    # Try non-default first, then default
    key_non_default = _ComponentKey(
        component_type=component_type,
        component_id=component_id,
        is_default=False,
        is_driver=is_driver,
    )
    component = _component_registry.get(key_non_default)
    if component is not None:
        return component

    # Try default
    key_default = _ComponentKey(
        component_type=component_type,
        component_id=component_id,
        is_default=True,
        is_driver=is_driver,
    )
    component = _component_registry.get(key_default)
    return component


def get_component_pair(
    component_type: ComponentType, component_id: str
) -> tuple[type | None, type | None]:
    """Gets a driver and component pair."""
    # Returns (component_class, driver_class)
    component = get_component(component_type, component_id, is_driver=False)
    driver = get_component(component_type, component_id, is_driver=True)
    return (component, driver)


# usage
# # This will work
# @register_component(ComponentSpec(
#   component_type=ComponentType.SENSOR,
#   id="lidar_velodyne",
#   is_driver=True
# ))
# class VelodyneLidarDriver(SensorDriver):
#   # Implementation...
#   pass

# # This will raise TypeError
# @register_component(ComponentSpec(
#   component_type=ComponentType.SENSOR,
#   id="bad_sensor",
#   is_driver=True
# ))
# class BadSensorDriver:  # Missing SensorDriver inheritance
#   pass
