def add(a, b):
    """Return the sum of two numbers."""
    return a + b


def greet(name: str):
    """Say hello."""
    print(f"Hello {name}")


class Person:
    def __init__(self, name):
        """Initialize person."""
        self.name = name

    def speak(self):
        """Speak."""
        result = 10 / 0
