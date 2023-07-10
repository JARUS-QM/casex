===========================================
Example 5: Isoparametric critical area plot
===========================================

This example makes a colored plot of the lethal area for varying impact angle and
impact speed. The size of the aircraft
as well as the other parameters are fixed.
The idea is to visualize the relation between
angle and speed, since this is one of the challenges in understanding the
transition from the JARUS model to the iGRC table.

The target for this example is the first column in the iGRC table, where the lethal area
is 6.5 m^2. Therefore, the isoparametric curve for 6.5 m^2 is shown in yellow
along with other iso curves in white for comparison.

The JARUS model is used throughout this example.

We start by setting up the critical area class.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 18-23

We instantiate the :class:`AnnexFParms` class, since we want to use the parameters
for the smallest size aircraft in the iGRC table, and we can find them in that class.
It requires an impact
angle as input, but since we will not use any impact angle related values from the
class, we just choose 35 here at random.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 26

We then setup the aircraft based on the parmaters for the first column
in the iGRC table (thus the index `[0]` on `AFP.CA_Parms`). Note that this is not specific
for fixed-wing, since this information is not currently being used by
the critical area computation.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 29-31

We do not use any fuel.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 32-33

And we use the friction coefficient from Annex F.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 34

We want to plot over the full range of impact speed and impact angles. However,
since very shallow impact angles are not handled well by the model, we start at
5 degrees. For speed, we cap it at 40 m/s. Each axis will be 100 steps, which is
fine for a relatively smooth plot.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 36-38

We then compute the critical area for all combinations of speed and angle. Note that we
could have replaced one of the loops with an array input, but since we cannot replace both
(since the `critical_area` method does not support 2D array input), we have chosen to run both
dimensions as loops for code clarity.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 40-44

The plot is setup with room for a colorbar on the right.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 46-49

The matrix is added to the plot.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 51-52

Conturs are added to the plot.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 54-55

A yellow contour is added for the target critical area for the first column
in the iGRC table.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 57-58

And the colorbar is added along with axes labels and title.

.. literalinclude:: ../../../casex/examples/example4_iso_CA_plot.py
    :lines: 60-65

The contours in the output image show where there is a constant critical area for varying
combinations of speed and angle. 

.. image:: images/example_4.png

There is a significant "drop" visible for the
smaller critical areas. This is coming from the "no slide" concession described
in Annex F, i.e. the disregard of the slide part of the critical area, combined with
the lethal kinetic energy limit. As a consequence of those, when the aircraft impact
speed is below a certain value,
there simply is not enough energy in the aircraft for it to be lethal,
and only the glide part of the critical is left. Since the size of this depends
only on the angle and not the speed, it stays constant for speeds down to 0 at impact angle with gives
a critical area equal to the value on the iso-parametric curve.