=========================================
Example 7: JARUS model vs the iGRC values
=========================================

In this example we compare the iGRC table in Annex F with the actual output of the JARUS model. This is done by plotting
the critical area for a variety of wingspan and population densities. This is similar to the iGRC figures that can be
computed with the :class:`Figures` class, which do the same thing, but for the simplified model.

We start with setting standard person parameters.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 14-15
    
and then we need to decide the impact angle. This is not used in the
simplified model, where the impact angle has been simplified away. However,
for the JARUS model we need to set this, since the critical area depends on it.
Here we choose 35 degrees, but any angle will do (but obviously produce a slightly
different plot).

We also need to set an impact speed for the JARUS mode, and here we choose to
use the values from the :class:`AnnexFParms` class, possibly reduced, since this
is what is assumed in Annex F for the 9 degree glide angle. Here we do not reduce
the speed, since we have 35 degrees impact angle.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 16-17
    
We instantiate the CA model class.    

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 20
    
We set the sampling density for the two axes.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 23-24
    
We set the arrays for the sampling on the two axes. Note that the wingspan
axis is linear, while the population density axis is logarithmic.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 27-28
    
We instantiate the Annex F parmeters class :class:`AnnexFParms`.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 31
    
Initialize the background matrix with zeros.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 34

We run a for loop over the range of the wingspan.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 37

Now, for every value of the wingspan, we want to use the aircraft values
associated with the wingspan, i.e. the appropriate column in the iGRC table.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 40-49
    
We get the maximum impact speed for the column and set the aircraft width to match
the current value from the for loop.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 51-55

We then compute the size of the critical area using the standard values
from Annex F (including the assumptions on the kinetic energy, which we
get by setting a -1 as the last input). Since there is not deflagration, the
overlap is set to zero.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 58-59
    
Finally, we populate the background matrix for the plot, that is the iGRC values
associated with the combination of population density and critical area.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 62-63
    
This is followed by numerous lines for creating the plot. This includes showing
the matrix along with contours, setting the tick locations and labels,
and white lines and text for overlaying the iGRC. The result is as follows.

.. image:: images/example_7.png

The percent of area in Denmark which corresponds to the different population density
bands is also shown. This information does not come from CasEx, and is just
hardcoded into this example.