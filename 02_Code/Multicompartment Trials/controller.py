"""
Main script to run simulation
"""
import time

import compartment
import simulator3
import pandas as pd
import h5py

file_name = "Experiment-D15"

# 1) DEFINE SIMULATOR CLASS AND ADD COMPARTMENTS
sim = simulator3.simulator(file_name)

sim.add_default_multicompartment(number_of_comps=9, soma = False)

# 2) SET SIMULATION SETTINGS

sim.set_electrodiffusion_properties(ED_on=False)


sim.set_external_ion_properties()
sim.set_j_atp(constant_j_atp=True)
sim.set_area_scale(constant_ar=True)
total_t = 420
time_step = 1e-6
sim.set_timing(total_t=total_t, time_step=time_step, intervals=1000)
#sim.add_synapse("Comp2", "Inhibitory", 5, 2 * 1e-3, 1e-2)
#sim.set_xflux(comps=["Comp2"], flux_type="static", start_t=60, end_t=120, x_conc=1e-3, z=-0.85, flux_rate=10*1e-3/60)
sim.set_zflux(comps=["Comp8"], start_t=120, end_t=180, z_end=-1.25)




# sim.set_zflux()
##sim.set_xoflux()
# run_t_arr = np.arange[0:total_t:time_step]

sim.run_simulation()
print("fin")
# 4) RUN SIMULATION


# 5) ACCESS RESULTS
