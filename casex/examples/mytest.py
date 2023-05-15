from casex import enums, FrictionCoefficients, CriticalAreaModels, AircraftSpecs, AnnexFParms, AnnexFTables
from casex import Figures

#console_output = AnnexFTables.ballistic_descent_table()

console_output = AnnexFTables.scenario_computation_table(1)
for s in console_output:
    print(s)

console_output = AnnexFTables.scenario_computation_table(2)
for s in console_output:
    print(s)

console_output = AnnexFTables.scenario_computation_table(3)
for s in console_output:
    print(s)

figures = Figures()
figures.figure_angle_vs_speed()
