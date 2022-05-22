from casex import Figures

figures = Figures()

for k1 in [True, False]:
    for k2 in [True, False]:
        for k3 in [True, False]:
            for k4 in [True, False]:
                for k6 in [True, False]:
                    for k7 in [True, False]:
                        for k8 in [True, False]:
                            figures.figure_iGRC_CA_vs_PopDensity(filename="_img1",
                                     show_x_CA_above=k1,          #1
                                     show_reduced_CA_axis=k2,     #2
                                     show_old_quantization=k3,    #3
                                     show_additional_grid=k4,     #4
                                     show_x_wingspan=k6,          #6
                                     show_x_velocity=k7,          #7
                                     show_x_CA=k8,                #8
                                     show_with_obstacles=False,  
                                     show_iGRC_prefix=True,
                                     show_descriptors=False,
                                     show_colorbar=False,
                                     show_title=True,
                                     save_fig=False,
                                     return_fig=False)
