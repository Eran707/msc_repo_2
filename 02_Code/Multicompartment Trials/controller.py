"""
Main script to run simulation
"""

import simulator3

file_name = "Experiment-H"


# 1) DEFINE SIMULATOR CLASS AND ADD COMPARTMENTS
sim = simulator3.simulator(file_name)

sim.add_default_multicompartment(number_of_comps=9,rad=5e-5, len=20e-5, soma=False)
sim.set_z("All", z=-0.45)
# 2) SET SIMULATION SETTINGS

sim.set_electrodiffusion_properties(ED_on=True, diff_constant_dict={"na" : 1.33e-8, "k": 1.96e-8, "cl":2.03e-8, "x":0})

sim.set_external_ion_properties()
sim.set_j_atp(constant_j_atp=True)
sim.set_area_scale(constant_ar=True)
total_t = 30
time_step = 1e-6
sim.set_timing(total_t=total_t, time_step=time_step, intervals=1000)

# sim.add_synapse("Comp2", "Inhibitory", 5, 2 * 1e-3, 1e-2)
#sim.add_current("Comp8","Excitatory",start_t=0.5,duration=1e-3, current_mA=1e-6,)

#sim.set_xflux(comps=["Comp8"], flux_type="static", start_t=120, end_t=180, x_conc=1e-3, z=-0.85, flux_rate=300*1e-3/60)
#sim.set_zflux(comps=["Comp8"], start_t=120, end_t=180, z_end=-1.25)

# sim.set_zflux()
# sim.set_xoflux()
# run_t_arr = np.arange[0:total_t:time_step]

# 4) RUN SIMULATION
sim.run_simulation()
print("fin")
