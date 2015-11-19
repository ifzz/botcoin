class BarValidationError(Exception):
    pass

class NoBarsException(BarValidationError):
    pass

class NotEnoughBarsException(BarValidationError):
    pass

class EmptyBarsException(BarValidationError):
    pass
