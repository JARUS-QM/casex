class NegativeHorizontalVelocityError(Exception):
    """The horizontal velocity is negative."""
    pass


class HorizontalSmallerThanVerticalVelocityError(Exception):
    """The horizontal velocity is smaller than the vertical velocity."""
    pass


class InvalidAircraftError(Exception):
    """The aircraft is not of type AircraftSpecs."""
    pass

class OnlyOneVetorInputError(Exception):
    """There are more than one vector input, which is not supported."""
    pass
