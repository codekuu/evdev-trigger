from evdev_trigger.models import BaseAction

from .some_file import Customer


class Action(BaseAction):  # pylint: disable=too-few-public-methods
    """This is a an example action which prints the hostname of the OS"""

    action_name: str = "EXAMPLE_COMPLEXT_ACTION"
    action_description: str = "Example of a complex action which uses mutlipe files"

    def execute(self, input_device, event):  # pylint: disable=unused-argument
        """Execute the action"""
        customer = Customer("Codekuu", 1337)
        customer.say_hello()
