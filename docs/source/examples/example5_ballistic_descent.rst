============================
Example 5: Ballistic descent
============================

This example shows how to compute a series of values describing a ballistic
descent. The same approach is used in Annex F for computing the ballistic
values found in Appendix A.

The class :class:`BallisticDescent2ndOrderDragApproximation`
is based on :cite:`lacourharbo2020a`, which thus
describes the detail on how the ballistic descent model works.

We first instantiate the class.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 14

We set the standard aircraft parameters.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 17-20

We instantiate the aircraft class.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 23
    
We need to set the drag coefficient and the frontal area, since where are
used in the computation of the ballistic descent. The frontal
area is the are covered by the aircraft in the direction of travel during
descent. Here we guess that it will be 60 cm by 60 cm, which is reasonable
for a 90 kg aircraft.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 24-25
    
The ballistic descent class must "be aware" of the aircraft as well.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 26

We also set the initial values for the descent, namely the altitude above the ground
and the velocity of the aircraft at the beginning of the descent.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 29-31

We can now compute the ballistic descent.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 35
    
Note that `p` is a list with various values about the descent. Note also that
the `BDM` has additional values available, relating to the intermediate
computations as decribed in :cite:`lacourharbo2020a`. All available values
are printed to the screen.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 37-41
    
which gives

.. code-block:: console

    Distance: 115.7 m    Impact speed: 45.7 m/s   Angle: 61.9 deg   Time : 4.66 s
    Distances: 0.000  74.174  41.477
    Times:     -0.000  2.851  4.662
    Speeds:    21.480  40.309   

It is possible to do ballistic descent computations with vector input.
We do this by setting the initial velocity to an array. 

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 45-47
    
However, we cannot have both horizontal and vertical velocities be arrays
at the same time, so we use them individually.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 49-53
    
The drag coefficient can also be an array.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 56-59
    
Now `p` contains the about from each of the three calculations, and this
can be plotted to show the variation of the output. Here are some of the
possible combination of input and output parameters.

.. image:: images/example_5.png

Finally, this example also shows how to get the ballistic computations found in Annex F Appendix A.
This is done by instantiating the :class:`AnnexFParms` class (with a random impact angle since it is
not used for ballistic computations)

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 86

and then simply accessing the associated attributes in the class.

.. literalinclude:: ../../../examples/example5_ballistic_descent.py
    :lines: 93-99

The printed values

.. code-block:: console

    Ballistic descent computations
    ------------------------------
    Class   Init horiz     From     Terminal   Impact   Impact   Distance   Descent      KE
              speed      altitude   velocity   speed    angle    traveled    time      impact
     1 m       25 m/s       75 m     30 m/s    29 m/s   72 deg      71 m      4.4 s        2 kJ
     3 m       35 m/s      100 m     48 m/s    41 m/s   62 deg     127 m      4.8 s       42 kJ
     8 m       75 m/s      200 m     61 m/s    58 m/s   58 deg     327 m      7.0 s      677 kJ
    20 m      150 m/s      500 m     96 m/s    95 m/s   55 deg     951 m     11.0 s    22390 kJ
    40 m      200 m/s     1000 m    107 m/s   110 m/s   62 deg    1559 m     16.4 s    60750 kJ
    
are the same as found in the ballistic table in Appendix A of Annex F :cite:`JARUS_AnnexF`.

.. bibliography:: ../bibtex.bib
   :style: plain
   :filter: docname in docnames
