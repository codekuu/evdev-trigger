import os
import sys
import typer
import importlib
import importlib.util
from typing import List, Dict, Any
from evdev import InputDevice, list_devices
from pick import pick

from evdev_trigger.config import logger
from evdev_trigger.models import ReactOn, Device, DeviceAction, DeviceLoad, BaseAction


class InputDevices:
    """Class for handling input devices"""

    _actions: Dict[str, BaseAction] = {}
    _input_devices: Dict[str, InputDevice] = {}
    input_devices: List[Device] = []

    def __init__(self, input_devices: List[dict], actions_folder: str = None):
        """Initialize the input devices"""
        self._import_input_devices()
        self._import_actions(actions_folder)

        if input_devices:
            self._load(input_devices)
        else:
            self.create()

    def _import_input_devices(self):
        """Import all input devices"""
        self._input_devices = {}
        devices = [InputDevice(path) for path in list_devices()]
        if not devices:
            typer.echo("No input devices found, probably not running as root")
            raise typer.Exit(code=1)

        for input_device in devices:
            self._input_devices[input_device.name] = input_device

    def _actions_folder_exists(self, actions_folder: str) -> bool:
        """Check if the actions folder exists"""
        if not os.path.exists(actions_folder):
            return False
        return True

    def _create_default_actions_folder(self) -> str:
        """Create the default actions folder"""
        # dir from where command is running
        default_actions_folder = os.getcwd()
        if not os.path.exists(default_actions_folder):
            os.makedirs(default_actions_folder)

        # Copy the default actions to the actions folder
        program_folder = os.path.dirname(os.path.realpath(__file__))
        # Go back one folder
        evdev_trigger = os.path.dirname(program_folder)
        os.system(
            f"cp -r {evdev_trigger}/actions {default_actions_folder}/default_actions"
        )
        typer.echo(f"Default actions copied to {default_actions_folder}")

        return default_actions_folder + "/default_actions"

    def _import_actions(self, actions_folder: str = None):
        """Import all available actions"""
        self._actions = {}
        # Check if the actions folder exists
        full_path = os.path.dirname(os.path.realpath(__file__)) + "/default_actions"
        if actions_folder:
            if not self._actions_folder_exists(actions_folder):
                typer.echo(f"Invalid actions folder: {actions_folder}")
                raise typer.Exit(code=1)

            # Use the provided actions folder
            full_path = actions_folder

        if not self._actions_folder_exists(full_path):
            typer.echo(f"Missing actions folder: {full_path}, creating it")
            full_path = self._create_default_actions_folder()

        # Get specific files only
        files = [file for file in os.listdir(full_path) if not file.startswith("_")]
        for file in files:
            if file.endswith(".py"):
                file = file.replace(".py", "")

            sys.path.append(full_path)
            # Try catch if the file is not a python file
            try:
                module = importlib.import_module(file)
            except ModuleNotFoundError:
                file_path = full_path + "/" + file
                typer.echo(f"Could not import action file {file_path}, skipping")
                continue

            action_class: BaseAction = getattr(module, "Action", None)
            if not action_class:
                typer.echo(
                    f"Action class not found in {file}, will not import it", err=True
                )
                continue

            self._actions[action_class.action_name] = action_class()

        if not self._actions:
            typer.echo("No actions found, exiting")
            raise typer.Exit(code=1)

    def _get_react_on_x(self, react_on: str) -> List[Any]:
        react_on_data = []
        while not react_on_data:
            try:
                temp = input(f"React on {react_on}: ")
                if not temp:
                    react_on_data = ["ALL"]
                    continue

                temp = temp.replace(" ", "").split(",")
                temp_values = []
                for value in temp:
                    temp_values.append(int(value))

                react_on_data = temp_values

            except ValueError:
                logger.info("Invalid input")
                continue

        return react_on_data

    def _get_react_on(self, input_device: InputDevice, selected: List[str]) -> ReactOn:
        """Get the react on code and value"""
        react_on_codes = []
        react_on_values = []
        print(
            f"""
Input Device: {input_device.name}
Action: {selected[0]}

What CODE and VALUE should it react on (comma separated, e.g. 1,0)
If you want to react on all codes or values, just press enter"""
        )
        react_on_codes = self._get_react_on_x("codes")
        react_on_values = self._get_react_on_x("values")

        return ReactOn(codes=react_on_codes, values=react_on_values)

    def create(self):
        """
        Setup the input devices
        """
        input_options = [input_device for input_device in self._input_devices]
        selected = pick(
            input_options,
            "Select input devices to listen on",
            indicator="=>",
            multiselect=True,
            min_selection_count=1,
        )
        selected = [select[0] for select in selected]
        choosen_input_devices = [
            self._input_devices[input_device] for input_device in selected
        ]

        for input_device in choosen_input_devices:
            actions = {}
            action_options = list(self._actions)

            # Get the actions for each device
            while True:
                selected = pick(
                    action_options,
                    f"""======= {input_device.name} ======\n
Selected Actions: {", ".join(actions.keys()) or 'No actions selected'}\n\n
Add Action:""",
                    indicator="=>",
                    multiselect=False,
                    min_selection_count=1,
                )
                # Check if the user is done
                if selected[0] == "Done":
                    break

                # Get the react on codes and values
                react_on = self._get_react_on(input_device, selected)
                actions[selected[0]] = DeviceAction(
                    action=self._actions[selected[0]], react_on=react_on
                )

                # Remove selected action from the list
                action_options.remove(selected[0])

                # Add done to the list if there are no more actions
                if "Done" not in action_options:
                    action_options.append("Done")

                if len(action_options) == 1:
                    logger.info("No more actions to add")
                    break

                # Ask if the user wants to add another action
                if input("Do you want to add another action? [y/N]: ").lower() != "y":
                    break

            self.input_devices.append(
                Device(input_device=input_device, actions=actions)
            )

    def _convert(self, input_devices: List[DeviceLoad]) -> List[Device]:
        """Convert the input devices back to the original format

        Args:
            input_devices (list of DeviceLoad): The input devices

        Returns:
            list of Device: The converted input devices
        """
        input_devices_fixed = []
        for input_device in input_devices:
            try:
                actions = {}
                for action_name, action in input_device["actions"].items():
                    actions[action_name] = DeviceAction(
                        action=self._actions[action_name],
                        react_on=ReactOn(
                            codes=action["react_on"]["codes"],
                            values=action["react_on"]["values"],
                        ),
                    )
            except KeyError as e:
                typer.echo("Actions could not be found")
                raise typer.Exit(code=1) from e
            try:
                in_device = self._input_devices[input_device["input_device"]]
            except KeyError as e:
                typer.echo(
                    f"Input device {input_device['input_device']} not found, probably disconnected"
                )
                raise typer.Exit(code=1) from e

            input_devices_fixed.append(
                Device(
                    input_device=in_device,
                    actions=actions,
                )
            )

        return input_devices_fixed

    def _load(self, input_devices: List[DeviceLoad]):
        """Load the devices"""
        if self.input_devices:
            logger.info("Input devices already loaded, skipping")
            return
        converted_input_devices = self._convert(input_devices)
        self.input_devices = converted_input_devices
