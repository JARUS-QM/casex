====================
Example 6: Obstacles
====================

The use of obstacles for reducing the critical area is demonstrated in this example.
The nominal critical area is 200 m:math:`^2`, and we want to see how much the critical
area is reduced for an obstacle density of 800 houses per km:math:`^2`.

The critical area of 200 m:math:`^2` is associated with the second column in the
iGRC, which is for the 3 m wing span. Therefore, we set the width of the CA to 3.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 13

Consequently, the length of the CA must be 200 divided by the width.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 16

We set the density to 800 houses per km:math:`^2`, and convert to
a density measure in obstacles per square meter.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 19-20

The size of the houses follows a 2D normal distribution for width and length.
We set the mean values and standard deviations for width

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 23-24

and for length

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 27-28

We instantiate the :class:`Obstacles` class. The third input argument
is only used for simulation, which we don't do here. So it is just
set to zero.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 31

We want to compute the probability for varying length of the critical area,
so we generate an array from 0 to the length of the nominal CA.
Since the resulting curve is quite smooth, it is not necessary to use
all that many points. We have chosen 10 here, which is usually sufficient.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 35-36

The computations of the cumulatative density function there are 3 integrals that
have to be evaluated. We must specify at what resolution this happens.
A value of 25 is typically sufficient. Increasing it will not produce notiable
different results.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 40

For the plot, we want to emphasize a critical area of 120, which coincides with the
reduced critical area relative to the 200, as described in Annex F Section 2. So
we stored this value for use in a bit.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 43

We now compute the CDF curve.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 46-47

We also compute the value corresponding specifically to our target CA value.

.. literalinclude:: ../../../examples/example6_obstacles.py
    :lines: 50-51

The resulting curve is plotted along with the target CA and the probability associated
with the target CA.

.. image:: images/example_6.png

The blue curve shows the probability of the CA being reduced to a given value or less.
So, as marked by the orange lines, the probability of the CA being less than 120
m:math:`^2` is approximately 0.6, or 60%. The actual value is printed to the screen.

.. code-block:: console

    Probability of reduction to at most 120 m^2 is 62%
