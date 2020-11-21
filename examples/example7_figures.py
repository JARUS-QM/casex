"""
Example 7
---------
MISSING DOC
"""
from casex import Figures

figures = Figures()

figures.figure_angle_vs_speed()

figures.figure_GRC_model_vs_iGRC()

# Figure 1.
figures.figure_iGRC_CA_vs_PopDensity(filename="_img1", show_with_obstacles=False, show_reduced_CA_axis=False,
                                     show_old_quantization=False, show_iGRC_prefix=True, show_additional_grid=False,
                                     show_colorbar=False, show_x_wingspan=False, show_x_velocity=False, show_x_CA=True,
                                     show_x_CA_above=False, show_title=False, save_image=True)

# Figure 2.
figures.figure_iGRC_CA_vs_PopDensity(filename="_img2", show_with_obstacles=False, show_reduced_CA_axis=False,
                                     show_old_quantization=False, show_iGRC_prefix=True, show_additional_grid=False,
                                     show_colorbar=False, show_x_wingspan=True, show_x_velocity=True, show_x_CA=True,
                                     show_x_CA_above=True, show_title=False, save_image=True)

# Figure 3.
figures.figure_iGRC_CA_vs_PopDensity(filename="_img3", show_with_obstacles=False, show_reduced_CA_axis=True,
                                     show_old_quantization=True, show_iGRC_prefix=True, show_additional_grid=False,
                                     show_colorbar=False, show_x_wingspan=True, show_x_velocity=False, show_x_CA=False,
                                     show_x_CA_above=False, show_title=False, save_image=True)
