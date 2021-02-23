"""
Example 8
---------
This example reproduces the figures in Annex F :cite:`JARUS_AnnexF`.

The various figures can be separately generated by calling the functions with the appropriate boolean settings as shown
in this example. However, other variations of the figures can also be generated. The documentation for each figure is
provided in :class:`Figures`.
"""
from casex import Figures

figures = Figures()

figures.figure_angle_vs_speed()

figures.figure_iGRC_CA_vs_PopDensity(filename="_img1", show_reduced_CA_axis=False,
                                     show_old_quantization=False, show_x_wingspan=True,
                                     show_x_velocity=True, show_x_CA=True,
                                     show_x_CA_above=True, show_additional_grid=False)

figures.figure_iGRC_CA_vs_PopDensity(filename="_img2", show_reduced_CA_axis=True,
                                     show_old_quantization=True, show_x_wingspan=True,
                                     show_x_velocity=False, show_x_CA=False,
                                     show_x_CA_above=True, show_descriptors=True, save_fig = False)

figures.figure_obstacle_critical_area_reduction(save_fig=False)
