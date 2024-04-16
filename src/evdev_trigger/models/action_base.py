import typer
from evdev import InputEvent
from evdev_trigger.models.devices import Device


class BaseAction:
    """Base class for all actions. All actions should inherit from this class."""

    action_name: str = "SOME_ACTION_HERE"
    action_description: str = "SOME_DESCRIPTION_HERE"

    def __init__(self):
        # validate the action
        if not self.action_name or self.action_name == "SOME_ACTION_HERE":
            typer.echo("Action name is required")
            raise typer.Exit(code=1)
        if (
            not self.action_description
            or self.action_description == "SOME_DESCRIPTION_HERE"
        ):
            typer.echo("Action description is required")
            raise typer.Exit(code=1)

    def execute(self, input_device: Device, event: InputEvent):
        """Execute the action"""
        typer.echo(f"Execute has not been implemented on action {self.action_name}")
        raise typer.Exit(code=1)
