class SASS_Parser_Parameters:
    def __init__(self, params:dict):
        for param in params.keys():
            setattr(self, param, params[param])
