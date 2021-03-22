def residual(SV, SVdot, self, counter, params):
    import numpy as np
    import cantera as ct
    
    resid = np.zeros((self.nVars,))

    # Save local copies of the solution vectors, pointers for this electrode:
    SVptr = self.SVptr
    SV_loc = SV[SVptr['residual']]
    SVdot_loc = SVdot[SVptr['residual']]

    # Read and set electrolyte electric potential:
    phi_ed = SV_loc[SVptr['phi_ed']]
    phi_elyte = phi_ed + SV_loc[SVptr['phi_dl']]

    # Set electric potentials for Cantera objects:
    self.bulk_obj.electric_potential = phi_ed
    self.conductor_obj.electric_potential = phi_ed
    self.elyte_obj.electric_potential = phi_elyte

    #TODO #18
    
    # Faradaic current density is positive when electrons are consumed 
    # (Li transferred to the anode)
    sdot_electron = self.surf_obj.get_net_production_rates(self.conductor_obj)
    i_Far = -ct.faraday*sdot_electron
    
    # Double layer current has the same sign as i_Far:
    i_dl = self.i_ext_flag*params['i_ext']/self.A_surf_ratio - i_Far
    
    if self.name=='anode':
        resid[SVptr['residual'][SVptr['phi_ed']]] = SV_loc[SVptr['phi_ed']]
    elif self.name=='cathode':
        # TEMPORARY: phi_elyte in cathode matches that in the anode.
        # TODO #21
        phi_elyte_an = SV[counter.SVptr['residual'][counter.SVptr['phi_dl']]]
        resid[SVptr['phi_ed']] = phi_elyte - phi_elyte_an 

    resid[SVptr['phi_dl']] = (SVdot_loc[SVptr['phi_dl']] - i_dl*self.C_dl_Inv)

    resid[SVptr['C_k_ed']] = SVdot_loc[SVptr['C_k_ed']]
    resid[SVptr['C_k_elyte']] = SVdot_loc[SVptr['C_k_elyte']]

    return resid