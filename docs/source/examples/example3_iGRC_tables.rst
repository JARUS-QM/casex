=====================================
Example 3: iGRC table
=====================================

NOT YET UPDATED TO SORA 2.5

This example reproduces the nominal iGRC table in Annex F :cite:`j-JARUS_AnnexF`. It also allows for seeing the table with different impact angles,
and with and without both obstacles and integer concession.

First, we call the AnnexFTables class (the called method is static).

.. literalinclude:: ../../../casex/examples/example11_iGRC_tables.py
    :lines: 10-14

The returned value is a list of strings to print to the console, which we then do.

.. literalinclude:: ../../../casex/examples/example11_iGRC_tables.py
    :lines: 16-17

.. code-block:: console

    Final iGRC (9 deg)
                              1 m       3 m       8 m      20 m      40 m
    --------------------+-------------------------------------------------
    Controlled (< 0.1)  |     1.3       2.4       3.3       4.3       4.8   
         10 [ppl/km^2]  |     3.3       4.4       5.3       6.3       6.8   
         30 [ppl/km^2]  |     3.8       4.8       5.8       6.8       7.3   
        100 [ppl/km^2]  |     4.3       5.4       6.3       7.3       7.8   
        300 [ppl/km^2]  |     4.8       5.8       6.8       7.8       8.3   
       1500 [ppl/km^2]  |     5.5       6.3       7.0       8.0       9.0   
       2000 [ppl/km^2]  |     5.6       6.4       7.2       8.1       9.1   
       2500 [ppl/km^2]  |     5.7       6.5       7.3       8.2       9.2   
       3000 [ppl/km^2]  |     5.8       6.6       7.3       8.3       9.3   
      10000 [ppl/km^2]  |     6.3       7.1       7.9       8.8       9.8   
      15000 [ppl/km^2]  |     6.5       7.3       8.0       9.0      10.0   
      20000 [ppl/km^2]  |     6.6       7.4       8.2       9.1      10.1   
      50000 [ppl/km^2]  |     7.0       7.8       8.6       9.5      10.5   
     100000 [ppl/km^2]  |     7.3       8.4       9.3      10.3      10.8   
    --------------------+-------------------------------------------------
         CA size [m^2]  |      20       231      2120     19176     67082  
    Slide distance [m]  |       0        60       246       930      1633  
    --------------------+-------------------------------------------------

.. bibliography::
   :keyprefix: j-
