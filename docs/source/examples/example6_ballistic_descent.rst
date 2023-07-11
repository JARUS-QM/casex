============================
Example 6: Ballistic descent
============================

This example shows how to compute a series of values for a ballistic
descent. The same approach is used in Annex F for computing the ballistic
values found in Appendix A.

The class :class:`BallisticDescent2ndOrderDragApproximation`
is based on :cite:`i-lacourharbo2020a`, which also
describes the detail on how the ballistic descent model works.

We first instantiate the class.

.. literalinclude:: ../../../examples/example6_ballistic_descent.py
    :lines: 14

We set the standard aircraft parameters

.. literalinclude:: ../../../examples/example6_ballistic_descent.py
    :lines: 17-20

and instantiate the aircraft class.

.. literalinclude:: ../../../examples/example6_ballistic_descent.py
    :lines: 23
    
We need to set the drag coefficient and the frontal area, since they are
used in the computation of the ballistic descent.
The drag coefficient is
typically in the range from 0.7 to around 1 for an aircraft which is
not descending "nicely", i.e., in its usually direction of travel. Here we
assume a normal helicopter-like rotorcraft, which may be tumbling during descent.
We guestimate the coeffient to be 0.8. A lower coefficient would give a higher
impact speed, and thus be more conservative. But 0.8 is not unreasonable for a tumbling
rotorcraft. See for instance the wiki page on drag coefficient for more detail on
drag for various shapes.

The frontal
area is the area covered by the aircraft in the direction of travel during
descent. Here we guess that it will be 60 cm by 60 cm, which is reasonable
for a 90 kg aircraft.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 24-25
    
The ballistic descent class must "be aware" of the aircraft.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 26

We also set the initial values for the descent, namely the altitude above the ground
and the velocity of the aircraft at the beginning of the descent.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 29-31

We can now compute the ballistic descent.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 35
    
Note that `p` is a list with various values about the descent. Note also that
 `BDM` has additional values (attributes) available, relating to the intermediate
computations as decribed in :cite:`i-lacourharbo2020a`. All available values
are printed to the screen here.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 37-43
    
which gives

.. code-block:: console

    Distance:     115.7 m    
    Impact speed: 45.7 m/s
    Angle:        61.9 degs
    Time :        4.66 s
    Distances:    0.000  74.245  41.461
    Times:        -0.000  2.854  4.664
    Speeds:       21.478  40.288

It is possible to do ballistic descent computations with vector input.
We do this by setting the initial velocity to an array. 

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 47-49
    
However, we cannot have both horizontal and vertical velocities be arrays
at the same time, so we use them individually.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 54-55
    
The drag coefficient can also be an array.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 58-61
    
Now `p` contains the output from each of the three calculations, and this
can be plotted to show the variation of the output. Here are some of the
possible combination of input and output parameters.

.. image:: images/example_6.png

Finally, this example also shows how to get the ballistic computations found in Annex F Appendix A.
This is done by instantiating the :class:`AnnexFParms` class, since all the ballistic values
are computed internally in the class during instantiation.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 88

Then we can easily access the associated attributes in the class to get the various ballistic values
for each category.

.. literalinclude:: ../../../casex/examples/example6_ballistic_descent.py
    :lines: 95-101

The printed values

.. code-block:: console

    Ballistic descent computations
    ------------------------------
    Class   Init horiz     From     Terminal   Impact   Impact   Distance   Descent      KE
              speed      altitude   velocity   speed    angle    traveled    time      impact
     1 m       25 m/s       75 m     25 m/s    24 m/s   76 deg      63 m      4.7 s        1 kJ
     3 m       35 m/s      100 m     45 m/s    39 m/s   64 deg     123 m      4.9 s       39 kJ
     8 m       75 m/s      200 m     63 m/s    60 m/s   57 deg     335 m      6.9 s      718 kJ
    20 m      150 m/s      500 m    112 m/s   106 m/s   51 deg    1044 m     10.8 s    27952 kJ
    40 m      200 m/s     1000 m    120 m/s   121 m/s   59 deg    1690 m     16.0 s    73038 kJ
    
are the same as found in the ballistic table in Appendix A of Annex F :cite:`i-JARUS_AnnexF`.

.. bibliography::
   :keyprefix: i-
