"""
MISSING DOC
"""


class Conversion:
    """Provide functionality for converting between imperial and metric system.

    Note that all methods are static, and can be called without instantiating :class:`Conversion`, i.e.

    .. code-block:: python
       length = casex.Conversion.ft_to_m(32)
    """
    @staticmethod
    def kg_to_lbs(mass):
        """Converts kg to pounds. Simply a division with 0.45359237 lbs/kg.

        Parameters
        ----------
        mass : float
            Mass in [lbs].

        Returns
        -------
        mass : float
            Mass in [kg].
        """
        return mass / 0.45359237

    @staticmethod
    def lbs_to_kg(mass):
        """Converts pounds to kg. Simply a multiplication with 0.45359237 lbs/kg.

        Parameters
        ----------
        mass : float
            Mass in [kg].

        Returns
        -------
        mass : float
            Mass in [lbs].
        """
        return mass * 0.45359237

    @staticmethod
    def ft_to_m(length):
        """Converts feet to meter. Simply a multiplication with 0.3048 ft/m.

        Parameters
        ----------
        length : float
            Length in [ft].

        Returns
        -------
        length : float
            Length in [m].
        """
        return length * 0.3048

    @staticmethod
    def m_to_ft(length):
        """Converts meter to feet. Simply a division with 0.3048 ft/m.

        Parameters
        ----------
        length : float
            Length in [m].

        Returns
        -------
        length : float
            Length in [ft].
        """
        return length / 0.3048

    @staticmethod
    def ftlb_to_J(energy):
        """Converts foot-pound to joule. Simply a multiplication with 1.355818 J/ft-lbs.

        Parameters
        ----------
        energy : float
            Energy in [ft-lbs].

        Returns
        -------
        energy : float
            Kinetic energy in [J].
        """
        return energy * 1.355818
