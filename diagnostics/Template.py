from LAMP.diagnostic import Diagnostic

class Template(Diagnostic):
    """Minimal template for a user diagnostic. This can be used as a starting point for creating
    new diagnostics. It inherits from the base Diagnostic class, which provides shared attributes
    and functions for all diagnostics.
    """

    def __init__(self, exp_obj, config_filepath):
        """Initiate parent base Diagnostic class to get all shared attributes and funcs"""
        self.data_type = config_filepath['data_type'] # This is needed for __init__ of Diagnostic
        super().__init__(exp_obj, config_filepath)
        return
