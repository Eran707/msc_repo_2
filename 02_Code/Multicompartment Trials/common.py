# -*- coding: utf-8 -*-
"""
"""
# constants
# R with different units
# 8.31451                   J K-1 mol-1
# 8.20578 x 10-2            L atm K-1 mol-1
# 8.31451 x 10-2                L bar K-1 mol-1
# 8.31451                           Pa m3 K-1 mol-1
# 62.364                             L Torr K-1 mol-1
# 1.98722                           cal K-1 mol-1
R = 8.31446
F: float = 96485.33  # Faraday's constant        C mol-1
k = 1.38e-23  # Boltzmann constant        J K-1
q = 1.602176620898e-19  # elementary charge         C
Na = 6.022e23  # Avogadro's constant       mol-1

T = 37 + 273.15
RTF = R * T / F
RT = R * T
# permeabilities
gna = 2e-3/F
gk = 7e-3/F
gcl = 2e-3/F
gx = 1e-8 # gna,gk,gcl: conductances in mS/cm^2 conv to S/dm^2 (10^-3/10^-2) - corrected for neuron
g_kcc2 = 2e-3/F
g_na_k_atpase=(10 ** -1) / F
# stochiometries
ck = 2
cna = 3  # cna,ck: pump (ATPase) stoichiometries
# pump rates
default_p = 0.1
# concentrations
nao = 145e-3
clo = 119e-3
ko = 3.5e-3
xo = 29.5e-3
#xo = -1.0 * (clo - nao - ko)  # nao,clo,ko,xo: extracellular concentrations (mM converted to M)
xo_z = xo * 0.02
oso = xo + nao + clo + ko

# DEFAULT cell dimensions
default_radius = 5 * 1e-5  # radius in um convert to dm
default_length = 100 * 1e-5  # length in um converted to dm

default_radius_short = 0.5 * 1e-5  # radius in um convert to dm
default_length_short = 100 * 1e-5  # length in um converted to dm

points_to_plot = 200  # points to plot

vw = 0.018 #partial molar volume of water, dm3/mol
pw = 0.0015 #osmotic permeability, biological membrane (muscle? unknown), dm s
km=5*10**(-14) #extensional rigidity of RBC at 23 deg, Mohandas and Evans (1994), N/dm

cm = 2e-4 #default membrane capacitance (F/dm^2)

val = {"na":1, "k":1, "cl":-1,"x":-0.85}

diff_constants = {"na" : 1.33e-7, "k": 1.96e-7, "cl":2.03e-7, "x":0} #diffusion coefficients for the various ions in dm2/s
#diff_constants = {"na" : 1.33e-8, "k": 1.96e-8, "cl":2.03e-8, "x":0}

def valence(ion: str):
    ion = ion.lower()
    if ion.endswith("i") or ion.endswith("o"):
        ion = ion[:-1]
    return {"cl": -1, "k": 1, "na": 1}[ion]
