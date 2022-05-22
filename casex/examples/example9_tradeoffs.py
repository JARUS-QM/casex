"""
Example 9
---------
This example demonstrates the validity of the trade offs between population density, speed and max dimensions.

The example prints one of the 6 different trade-offs described in Annex F for alternative iGRC tables.
It is also possible to print the difference between the original iGRC and any of the 6 alternatives.

Note that this example accounts for both the 0.3 reduction in iGRC and reduction due to obstacles, as described in the Annex.
"""
from casex import AnnexFTables

# Set the tradeoff table to T2
tradeoff_type = 1

# Do not show the results a ceil'ed integers.
show_integer_iGRC = False

# Show values relative to nominal iGRC table.
show_relative = True

console_output = AnnexFTables.iGRC_tradeoff_tables(tradeoff_type, show_integer_iGRC, show_relative)

for s in console_output:
    print(s)
