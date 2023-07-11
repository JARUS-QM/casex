========================
Example 1: Critical area
========================

This first example demonstrates how to use the CasEx package for computing a critical area for a specific aircraft.
This computation can be used for determining a more accurate iGRC value than what is possible for the iGRC table.

We start by setting two basic parameters required for computing the size of the critical area, namely
the height of a standad person and the "radius" of a standard person. The latter is the radius of a circle circumscribing
a person seen from above. It is possible to leave out these values when instantiating the critical area model, and it will revert
to the standard value, which are the same as we use here (and also the values used throughout Annex F).

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 9-10
    
We then instantiate first the class that can provide some friction coefficients, and then the class
that holds the various models for computing the size of the critical area.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 13-14

We then need to decide the impact speed and the impact angle. The former is the speed the aircraft will have along the direction
of travel at the time it impacts the ground. This is used for computing the glide distance after impact. The latter is the angle
of the straight line that the aircraft follows just prior to impact. This is measured from horizontal, so that 10 degrees is a very
shallow impact, while 90 is a vertical impact. For this example, we chose a speed of impact of
45 m/s and a 35 degree impact angle .

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 17-18

We also need to specify some properties of the aircraft. This is done using the :class:`AircraftSpecs` class. But first, we set some of the
parameters used in the instantiation of the class.

We have the wingspan (also known as width or characterstic dimension), the mass, and the coefficient of friction
between the aircraft and the terrain. The latter is in this case captured from the :class:`FrictionCoefficients`, but could also be set
manually. Note that in Annex F this value is always 0.65.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 21-25

Then we instantiate the aircraft class, and set the friction value.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 28-29

The deflagration model can be included by setting the type of fuel and the amount of fuel. Here, we set the amount to 0, which
effectively deactivates the deflagration model. It can be activated by setting a non-zero amount of fuel.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 32-33

The coefficient of restitution is set as a function of the impact angle.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 36

When the deflagration model is used there will be an overlap between the critical area from the glide and slide and the
critical area from the deflagration (since the deflagration happens to some extend in the same area). We therefore need to
set the fraction of overlap. The total critical area (sum of glide/slide and deflagration) is reduced by the smaller of the two
multiplied with the overlap factor.

Note that this value is not used when there is no fuel onboard, and therefore no deflagration.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 40

During the slide, the aircraft dissipates kinetic energy, which ends at 0 when the aircraft comes to a halt. It is possible to
reduce the size of the critical area by assuming that the aircraft is no longer lethal at a higher kinetic energy than 0. The
chosen value is set here. If the default value is to be used, the value is set to -1.
The documentation for :class:`critical_area_models` has more info on this.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 45

We are now ready to compute the size of the critical area. We do this by calling the `critical_area` method.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 48-49
    
The output from this method is a list with nine values.
These are 1) total critical area, 2) glide area, 3) slide area, 4) the inert critical area, 5) the critical
area from the deflagration, 6) the glide distance, 7) the slide distance until the kinetic energy has reached
the non-lethal limit, 8) the speed at which the sliding aircraft has the kinetinc energy from 7),
9) the time it takes to reach the kinetic energy from 7).
The first five are shown in the output below along with some of the aircraft parameters.

Finally, we can also compute the raw iGRC as described in Annex F. This is done using the :class:`AnnexFParms` class. Here we need to input
the population density, which is set to 3000 here.

.. literalinclude:: ../../../casex/examples/example1_critical_area.py
    :lines: 52

This iGRC value can now be used in the SORA process. The value should be rounded up to the nearest larger integer.

The output of the example is as follows. We see that the raw iGRC is 6.4, which must be rounded up to
7 for the actual iGRC value. This demonstrates
how an aircraft, which belongs in the third column (due to the high impact speed above 35 m/s)
can achieve a lower iGRC value than given in the
table (which would be 8) by doing the actual calculations for the critical area.

.. code-block:: console

    Wingspan:                   2.2 m
    Mass:                       5 kg
    Horizontal impact speed:    36.9 m/s
    Glide area:                 6.2 m^2
    Slide area:                 78.1 m^2
    Critical area inert:        84.2 m^2
    Critical area deflagration: 0.0 m^2
    Total critical area:        84 m^2
    Raw iGRC:                   6.4

It is important to note that this example uses rubber against concrete as the friction coefficient.
This obviously has to be adjusted depending on
the aircraft and the overflown terrain. Alternatively, it is always acceptable to use the Annex F standard value of 0.65.

