from typing import List
from threading import Thread
from evdev.events import InputEvent

from evdev_trigger.config import logger
from .input_devices import (  # pylint: disable=relative-beyond-top-level
    ReactOn,
    Device,
)


def should_react_on(react_on: ReactOn, event: InputEvent) -> bool:
    """Check if the event should be reacted on"""
    if "ALL" in react_on.codes or event.code in react_on.codes:
        if "ALL" in react_on.values or event.value in react_on.values:
            return True

    return False


def spawn_listener(input_device: Device) -> None:
    """Spawn a listener for the device"""
    for event in input_device.input_device.read_loop():
        for _, action in input_device.actions.items():
            if should_react_on(action.react_on, event):
                action.action.execute(input_device, event)


def spawn_listeners(input_devices: List[Device]) -> None:
    """Spawn listeners for the devices

    Args:
        devices (list): The devices {device: InputDevice, action: str, switch: Switch, react_on: str}

    Returns:
        None
    """
    logger.info("Starting listeners")
    for input_device in input_devices:
        listener = Thread(target=spawn_listener, args=(input_device,))
        listener.start()
        logger.info("Listening for input on %s", input_device.input_device.name)
