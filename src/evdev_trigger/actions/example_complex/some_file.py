class Customer:
    """A simple class to represent a customer"""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def say_hello(self):
        """Prints a greeting"""
        print(f"Hello {self.name}, you are {self.age} years old")
