=====================================
Example 3: iGRC table
=====================================

This example reproduces the nominal iGRC table in Annex F :cite:`j-JARUS_AnnexF`.
It also allows for seeing the table with different impact angles, for ballistic descent, 
as well as with and without both obstacles and the conservative assumption of -0.3 (see details in Annex F).

First, we call the AnnexFTables class (the called method is static).

.. literalinclude:: ../../../casex/examples/example11_iGRC_tables.py
    :lines: 10-14

The returned value is a list of strings to print to the console, which we then do.

.. literalinclude:: ../../../casex/examples/example11_iGRC_tables.py
    :lines: 16-17

.. code-block:: console

    iGRC table (35 deg)
                              1 m       3 m       8 m      20 m      40 m
    --------------------+-------------------------------------------------
    Controlled (< 0.1)  |     1.1       2.3       3.3       4.3       5.1   
          8 [ppl/km^2]  |     2.6       3.8       4.8       5.8       6.6   
         25 [ppl/km^2]  |     3.1       4.3       5.3       6.3       7.1   
         75 [ppl/km^2]  |     3.6       4.8       5.8       6.8       7.6   
        250 [ppl/km^2]  |     4.1       5.3       6.3       7.3       8.1   
        750 [ppl/km^2]  |     4.6       5.8       6.8       7.8       8.6   
       2500 [ppl/km^2]  |     5.1       6.3       7.3       8.3       9.1   
       7500 [ppl/km^2]  |     5.6       6.8       7.8       8.8       9.6   
      25000 [ppl/km^2]  |     6.1       7.3       8.3       9.3      10.1   
     250000 [ppl/km^2]  |     7.1       8.3       9.3      10.3      11.1   
     750000 [ppl/km^2]  |     7.6       8.8       9.8      10.8      11.6   
     750000 [ppl/km^2]  |     7.6       8.8       9.8      10.8      11.6   
    2500000 [ppl/km^2]  |     8.1       9.3      10.3      11.3      12.1   
    --------------------+-------------------------------------------------
         CA size [m^2]  |       5        85       878      8190     47875  
    Slide distance [m]  |       0        26       106       403      1178  
    --------------------+-------------------------------------------------

.. bibliography::
   :keyprefix: j-
