import os
import typer
from typing_extensions import Annotated
from evdev_trigger.core.storage import Storage
from evdev_trigger.core.input_devices import InputDevices
from evdev_trigger.core.spawners import spawn_listeners

app = typer.Typer(
    name="evdev-trigger",
    help="Trigger actions based on input events from evdev devices",
)


@app.command()
def run(
    file: Annotated[
        str, typer.Option(help="Storage file to use for storing reactions")
    ] = "storage.json",
    reset_storage: Annotated[
        bool,
        typer.Option(
            help="Remove all devices and actions from storage (will not remove actions folder)"
        ),
    ] = False,
    actions: Annotated[str, typer.Option(help="Folder to load actions from")] = None,
) -> None:
    """Main function"""
    # Make sure user is running as root
    if not os.geteuid() == 0:
        typer.echo("This script needs to run as root")
        raise typer.Exit(code=1)

    # Initialize storage
    storage = Storage(storage_file=file)
    if reset_storage:
        storage.reset()
    storage.load()

    # Initialize input devices
    input_devices = InputDevices(input_devices=storage.storage, actions_folder=actions)

    # Save before starting listeners if it started from a clean slate
    if not storage.storage:
        storage.save(input_devices.input_devices)

    # Start listeners
    spawn_listeners(input_devices.input_devices)


if __name__ == "__main__":
    app()
