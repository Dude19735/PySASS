class SASS_Parser_Constants:
    """
    This one is a container class for the CONSTANTS in the instructions.txt. Using a class
    and setattr will allow for easy access with autocompletion.
    """
    def __init__(self, consts:dict):
        for param in consts.keys():
            setattr(self, param, consts[param])
