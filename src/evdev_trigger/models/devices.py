from typing import List, Callable, Any, Dict
from dataclasses import dataclass
from evdev import InputDevice


@dataclass
class ReactOn:
    """Class for handling react on codes and values"""

    codes: List[Any]
    values: List[Any]


@dataclass
class DeviceAction:
    """Class for handling device actions"""

    action: Callable
    react_on: ReactOn


@dataclass
class Device:
    """Class for handling action devices"""

    input_device: InputDevice
    actions: Dict[str, DeviceAction]  # BaseAction


@dataclass
class DeviceLoadAction:
    """Class for handling action devices when loading"""

    name: str
    react_on: ReactOn


@dataclass
class DeviceLoad:
    """Class for handling action devices when loading"""

    input_device: str
    actions: Dict[str, DeviceLoadAction]
