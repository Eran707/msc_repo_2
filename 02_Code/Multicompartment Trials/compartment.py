# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 17:45:32 2021

@author: eshor

Class which defines the compartments object and related methods.

Class: Compartment : New compartment Methods: __int__ : Initializes compartment object set_ion_properties: define
intracellular ionic properties of the compartment (extracellular properties are imported) step: actions to take at
every time point in the simulation update_volumes: change the volume of the compartment (as well as ion
concentrations based on new volume) update_arrays: update the arrays for each parameter of the compartment ed_update:
make changes to the compartment based on the results of electrodiffusion get_ed_dict: sends the current status of the
compartment back to the simulation to be evaluated by electrodiffusion equations get_fin_vals: sends the final values
of the compartment back to the simulation get_df_array: sends the dataframe arrays back to the simulation


"""

##################################################################################
# IMPORTS

import numpy as np

from common import \
    gk, gna, gcl, \
    pw, vw, RTF, cm, F



##################################################################################
# COMPARTMENT CLASS

class Compartment:

    def __init__(self, compartment_name, radius=1e-5, length=10e-5):

        self.name = compartment_name
        self.radius = radius  # in dm
        self.length = length  # in dm
        self.w = np.pi * (self.radius ** 2) * self.length
        self.dw, self.w2 = 0, 0
        self.sa = 2 * np.pi * self.radius * self.length
        self.ar = self.sa / self.w

        self.FinvCAr = F / (cm * self.ar)

        self.j_kcc2 = 0
        self.j_p = 0

        self.v, self.E_cl, self.E_k, self.E_na, self.drivingf_cl = 0, 0, 0, 0, 0
        self.na_i, self.k_i, self.cl_i, self.x_i, self.z_i, self.osm_i = 0, 0, 0, 0, 0, 0
        self.na_i_start, self.x_start, self.z_start = 0, 0, 0

        self.x_default = 154.962e-3
        self.z_default = -0.85

        self.xflux_setup, self.zflux_setup, self.external_xflux_setup = True, True, True
        self.xflux_switch, self.zflux_switch = False, False
        self.xflux, self.xoflux = 0, 0
        self.t_xflux = 0
        self.xflux_params = {"type": "dynamic", "start_t": 0, "end_t": 0, "x_conc": 1,
                             "flux_rate": 60, "z": 0}
        self.zflux_params = {"start_t": 0, "end_t": 0, "z": 0}
        self.dt_xflux, self.flux_points, self.alpha, self.beta = 0, 0, 0, 0
        self.d_xflux, self.d_zflux, self.total_x_flux, self.static_xflux, self.x_final = 0, 0, 0, 0, 0
        self.osmo_final = 0
        self.z_diff, self.z_final, self.z_diff, self.z_inc, self.zflux = 0, 0, 0, 0, 0
        self.synapse_on = False
        self.current_on = False
        # Zeroing Delta values
        self.d_na_i, self.d_na_atpase, self.d_na_leak = 0, 0, 0
        self.d_k_i, self.d_k_atpase, self.d_k_leak, self.d_k_kcc2 = 0, 0, 0, 0
        self.d_cl_i, self.d_cl_leak, self.d_cl_kcc2 = 0, 0, 0
        self.d_x_i = 0

        self.dt, self.syn_t_on, self.syn_t_off = 0, 0, 0  # Timing

    def set_ion_properties(self, na_i =0.013992400181361907, k_i= 0.12285356226659946,cl_i= 0.0051732641296024845,
                           x_i=0.15497985672007658, z_i = -0.85,
                           osmol_neutral_start=True):
        """
        - Adjustment of starting concentrations to ensure starting electroneutrality
       old defaults: na_i=14.001840415288e-3, k_i=122.870162657e-3, cl_i=5.1653366e-3,
                           x_i=154.972660318083e-3, z_i=-0.85
        """
        self.na_i, self.k_i, self.cl_i, self.x_i, self.z_i = na_i, k_i, cl_i, x_i, z_i  # Intracellular ion conc.
        self.na_i_start, self.x_start, self.z_start = na_i, x_i, z_i
        na_o = 145e-3
        k_o = 3.5e-3
        cl_o = 119e-3
        x_o = 29.5e-3
        z_o = -0.85

        if osmol_neutral_start:
            self.k_i = self.cl_i - self.z_i * self.x_i - self.na_i
            #self.cl_i = self.k_i +self.z_i*self.x_i +self.na_i
        self.v = self.FinvCAr * (self.na_i + self.k_i + (self.z_i * self.x_i) - self.cl_i)
        self.E_na = -1 * RTF * np.log(self.na_i / na_o)
        self.E_k = -1 * RTF * np.log(self.k_i / k_o)
        self.E_cl = RTF * np.log(self.cl_i / cl_o)
        self.drivingf_cl = self.v - self.E_cl

    def set_synapse(self, synapse_type='Inhibitory', start_t=0, duration=2e-3, max_neurotransmitter=1e-3, synapse_conductance = 1e-9):
        self.synapse_on = True
        self.synapse_type = synapse_type
        self.syn_start_t = start_t
        self.duration = duration
        self.nt_max = max_neurotransmitter
        self.g_synapse = synapse_conductance
        if synapse_type == 'Inhibitory':
            self.alpha = 0.5e-6  # ms-1.mM-1 --> s-1.M-1= Forward rate constant
            self.beta = 0.1e-3  # ms-1 --> s-1 == Backward rate constant
        elif synapse_type == 'Excitatory':
            self.alpha = 2e-6
            self.beta = 1e-3
        self.r_initial = 1  # ratio of NT bound initially
        self.r_t = 0  # current ratio of NT bound
        self.r_infinity = (self.alpha * self.nt_max) / (self.alpha * self.nt_max + self.beta)
        self.tau = 1 / (self.alpha * self.nt_max + self.beta)
        self.g_synapse = 5e-9   # 1nS -->S

    def synapse_step(self, run_t):

        self.r_t = self.r_infinity + (self.r_initial)* np.exp(-(run_t) / self.tau)

        I_syn = 0

        if self.synapse_type == 'Inhibitory':
            I_syn = self.g_synapse * self.r_t * (self.v - self.E_cl)
            I_syn = I_syn * 4 / 5  # CL- only contributes about 80% of the GABA current, HCO3- contributes the rest.
            I_syn = I_syn / F  # converting coloumb to mol
            I_syn = I_syn * self.dt  # getting the mol input for the timestep
            cl_entry = I_syn / self.w
            self.cl_i += cl_entry

        elif self.synapse_type == 'Excitatory':
            I_syn = self.g_synapse * self.r_t * (self.E_na - self.v)
            I_syn = I_syn / F  # converting coloumb to mol
            I_syn = I_syn * self.dt  # getting the mol input for the timestep
            na_entry = I_syn / self.w
            self.na_i += na_entry

    def set_current(self, current_dict=None):
        if current_dict is None:
            current_dict = {"Compartment": 0, "Current Type": 0, "Start Time": 0,
                            "Duration": 0, "End Time":0, "Current Amplitude": 0}
        self.current_dict = current_dict

        self.mol_per_s = current_dict["Current Amplitude"] / F

        self.current_on = True

    def current_step(self,run_t=0, dt=1e-6):

        if self.current_dict["Current Type"] == 0:  #Inihibitory current
            cl_current = self.mol_per_s /self.w
            cl_current = cl_current * dt
            self.cl_i +=  cl_current

        elif self.current_dict["Current Type"] == 1: #Excitatory current
            na_current = self.mol_per_s / self.w
            na_current = na_current * dt
            self.na_i +=  na_current

        self.current_on = False


    def step(self, dt=0.001,
             na_o=0, k_o=0, cl_o=0,
             constant_j_atp=False, p=(10 ** -1) / F,
             p_kcc2=2e-3 / F):
        """
        Perform a time step for the specific compartment.
        """
        # 1) Zeroing deltas
        self.d_na_i, self.d_k_i, self.d_cl_i, self.d_x_i = 0, 0, 0, 0

        # 2) Updating voltages
        self.v = self.FinvCAr * (self.na_i + self.k_i + (self.z_i * self.x_i) - self.cl_i)
        self.E_na = -1 * RTF * np.log(self.na_i / na_o)
        self.E_k = -1 * RTF * np.log(self.k_i / k_o)
        self.E_cl = RTF * np.log(self.cl_i / cl_o)
        self.drivingf_cl = self.v - self.E_cl

        # 3) Update ATPase and KCC2 pump rate
        if not constant_j_atp:
            self.j_p = p * (self.na_i / na_o) ** 3
        elif constant_j_atp:
            self.j_p = p * (self.na_i_start / na_o) ** 3

        self.j_kcc2 = p_kcc2 * (self.E_k - self.E_cl)

        # 4) Solve ion flux equations for t+dt from t
        self.d_na_leak = - dt * self.ar * gna * (self.v + RTF * np.log(self.na_i / na_o))
        self.d_na_atpase = - dt * self.ar * (+3 * self.j_p)
        self.d_na_i = self.d_na_leak + self.d_na_atpase

        self.d_k_leak = - dt * self.ar * gk * (self.v + RTF * np.log(self.k_i / k_o))
        self.d_k_atpase = - dt * self.ar * (- 2 * self.j_p)
        self.d_k_kcc2 = - dt * self.ar * (- self.j_kcc2)
        self.d_k_i = self.d_k_leak + self.d_k_atpase + self.d_k_kcc2

        self.d_cl_leak = + dt * self.ar * gcl * (self.v + RTF * np.log(cl_o / self.cl_i))
        self.d_cl_kcc2 = + dt * self.ar * self.j_kcc2
        self.d_cl_i = self.d_cl_leak + self.d_cl_kcc2

        if self.cl_i < 0:
            print("Cl_i = " + str(self.cl_i))
            print("d_Cl_i = " + str(self.d_cl_i))
            raise Exception("chloride log can't have a negative number")

        if self.k_i < 0:
            print("k_i = " + str(self.k_i))
            print("d_k_i = " + str(self.d_k_i))
            raise Exception("[K+] <0 --  log can't have a negative number")

        # 5) Update ion concentrations
        self.na_i = self.na_i + self.d_na_i
        self.k_i = self.k_i + self.d_k_i
        self.cl_i = self.cl_i + self.d_cl_i

    def update_volumes(self, dt, osm_o=1, constant_ar=False):
        """ Calculates the new compartment volume (dm3)
        Elongation should occur radially
        """
        self.osm_i = self.na_i + self.k_i + self.cl_i + self.x_i
        self.dw = dt * (vw * pw * self.sa * (self.osm_i - osm_o))
        self.w2 = self.w + self.dw

        self.na_i = self.na_i * self.w / self.w2
        self.k_i = self.k_i * self.w / self.w2
        self.cl_i = self.cl_i * self.w / self.w2
        self.x_i = self.x_i * self.w / self.w2

        self.radius = np.sqrt(self.w2 / (self.length * np.pi))
        self.sa = 2 * np.pi * self.radius * self.length

        if constant_ar:
            self.ar = self.ar
        else:
            self.ar = self.sa / self.w2

        self.w = self.w2
        self.FinvCAr = F / (cm * self.ar)

    def ed_update(self, ed_change: dict, sign="positive"):
        """
        Receives a dictionary and update
        """

        if sign == "positive":
            self.na_i += (ed_change["na"] / self.length) / self.w
            self.cl_i += (ed_change["cl"] / self.length) / self.w
            self.k_i += (ed_change["k"] / self.length) / self.w
            self.x_i += (ed_change["x"] / self.length) / self.w
        elif sign == "negative":
            self.na_i -= (ed_change["na"] / self.length) / self.w
            self.cl_i -= (ed_change["cl"] / self.length) / self.w
            self.k_i -= (ed_change["k"] / self.length) / self.w
            self.x_i -= (ed_change["x"] / self.length) / self.w

    def get_ed_dict(self):
        ed_dict = {"na": self.na_i, "k": self.k_i, "cl": self.cl_i, "x": self.x_i, "Vm": self.v}
        return ed_dict

    def get_df_dict(self, time=0):
        df_dict = {"time": time, "name": self.name, "radius": self.radius, "length": self.length, "volume": self.w,
                   "na": self.na_i, "k": self.k_i,
                   "cl": self.cl_i, "x": self.x_i, "z": self.z_i, "vm": self.v, "e_k": self.E_k, "e_cl": self.E_cl}
        return df_dict

    def get_array(self, time=0):
        array = [time, self.radius, self.length, self.w,
                 self.na_i, self.k_i, self.cl_i, self.x_i, self.z_i,
                 self.d_na_i, self.d_na_leak, self.d_na_atpase,
                 self.d_k_i, self.d_k_leak, self.d_k_atpase, self.d_k_kcc2,
                 self.d_cl_i, self.d_cl_leak, self.d_cl_kcc2,
                 self.v, self.E_k, self.E_cl]
        return array

    def x_flux(self):
        """
        FLUX IMPERMEANTS INTO THE COMPARTMENT

        """
        if self.xflux_setup:
            # starting values for flux
            self.x_start, self.z_start = self.x_i, self.z_i
            self.static_xflux = (self.xflux_params["flux_rate"]) * self.dt
            self.x_final = self.x_i + self.xflux_params["x_conc"]
            self.osmo_final = (self.x_start * self.z_start) + (self.xflux_params["x_conc"] * self.xflux_params["z"])
            self.z_final = self.osmo_final / self.x_final
            self.z_diff = self.z_final - self.z_start
            self.flux_points = (self.xflux_params["end_t"] - self.xflux_params["start_t"]) * (1 / self.dt)
            self.dt_xflux = 4 / self.flux_points
            self.alpha = 1
            self.beta = -1
            self.xflux_setup = False

        if (self.xflux_params["type"] == 'dynamic') and (self.x_i <= self.x_final):
            self.t_xflux += self.dt_xflux
            self.d_xflux = self.alpha - np.e ** (self.beta * self.t_xflux)
            self.xflux = self.d_xflux * self.xflux_params["x_conc"]
            self.zflux = self.d_xflux * self.z_diff  # z can adjust at the same rate as x
            self.total_x_flux += self.xflux
            self.x_i = self.x_start + self.xflux
            self.z_i = self.z_start + self.zflux


        elif self.xflux_params["type"] == 'static':
            self.total_x_flux += self.static_xflux
            z_temp = (self.x_start * self.z_start) + (self.total_x_flux * self.xflux_params["z"])
            self.z_i = z_temp / (self.x_start + self.total_x_flux)
            self.x_i = self.x_i + self.static_xflux
            self.t_xflux += self.dt_xflux

    def z_flux(self):
        """
        Changing the charge of intra-compartmental impermeants during the simulation
        """
        if self.zflux_setup:
            self.z_diff = self.zflux_params["z"] - self.z_i
            # self.x_mol_start =  self.w * self.x_i
            t_diff = (self.zflux_params["end_t"] - self.zflux_params["start_t"]) / self.dt
            self.z_inc = self.z_diff / t_diff
            self.zflux_setup = False
        else:
            self.z_i += self.z_inc
