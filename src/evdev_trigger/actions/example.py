from evdev_trigger.models import BaseAction


class Action(BaseAction):  # pylint: disable=too-few-public-methods
    """This is a an example action which prints the hostname of the OS"""

    action_name: str = "EXAMPLE_DEBUG_ACTIONS"
    action_description: str = "Prints the device name, event code and value"

    def execute(self, input_device, event):  # pylint: disable=unused-argument
        """Execute the action"""
        print(f"[EVENT] {input_device.input_device.name}: {event.code} - {event.value}")
