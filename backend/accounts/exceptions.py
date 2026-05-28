# accounts/exceptions.py

class AutopilotDisabledError(Exception):
    pass


class AutopilotRiskExceededError(Exception):
    pass


class AutopilotModeError(Exception):
    pass


class AutopilotConfigurationError(Exception):
    pass