def singleton(cls):
    """
    Decorator to make a class a singleton.

    Args:
        cls (type): The class to be decorated.

    Returns:
        function: The get_instance function that returns the singleton instance.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        # Return the existing instance if it exists, otherwise create a new one.
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance