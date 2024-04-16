import os
import json
from typing import List, Dict
from dataclasses import asdict

from evdev_trigger.config import logger
from evdev_trigger.models import (  # pylint: disable=relative-beyond-top-level
    Device,
    DeviceAction,
    DeviceLoad,
    DeviceLoadAction,
)


class Storage:
    """Class for handling storage"""

    storage: DeviceLoad = {}

    def __init__(self, storage_file: str = "storage.json"):
        self.storage_file = storage_file

    def _convert_actions(self, actions: Dict[str, DeviceAction]) -> Dict[str, dict]:
        """Convert the actions to a loadable format"""
        converted = {}
        for action_name, action in actions.items():
            converted[action_name] = asdict(
                DeviceLoadAction(
                    name=action_name,
                    react_on=action.react_on,
                )
            )
        return converted

    def _convert(self, input_devices: List[Device]) -> List[dict]:
        """Convert the input devices to a loadable format"""
        converted = []
        for input_device in input_devices:
            actions = self._convert_actions(input_device.actions)
            converted.append(
                asdict(
                    DeviceLoad(
                        input_device=input_device.input_device.name, actions=actions
                    )
                )
            )
        return converted

    def save(self, input_devices: List[Device]):
        """Save the storage to json file"""
        self.storage = self._convert(input_devices)
        logger.info("Saving storage")
        with open(self.storage_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.storage))

    def load(self) -> dict:
        """Load the storage from json file"""
        logger.info("Loading storage")
        if not os.path.exists(self.storage_file):
            logger.info("No storage file found, creating a new one")
            self.save([])

        with open(self.storage_file, "r", encoding="utf-8") as f:
            self.storage = json.loads(f.read())

    def reset(self):
        """Reset the storage"""
        logger.info("Resetting storage")
        self.storage = {}
        self.save([])
