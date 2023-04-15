import random
import sys
#
#--expdecay
def expdecay(x,a,b):
  return a*(1.-np.exp(-x/b))
#
def saod(emi30s,emi15s,emi15n,emi30n):
    rfsh=0.0 ; rfnh=0.0 
    for i,emi in enumerate(emi30s):
        rfnh += anh30s*emi30s*exp(-i*bnh30s)+anh15s*emi15s*exp(-i*bnh15s)+anh15n*emi15n*exp(-i*bnh15n)+anh30n*emi30n*exp(-i*bnh30n)
        rfsh += ash30s*emi30s*exp(-i*bsh30s)+ash15s*emi15s*exp(-i*bsh15s)+ash15n*emi15n*exp(-i*bsh15n)+ash30n*emi30n*exp(-i*bsh30n)
    return rfsh, rfnh
#
def clim(T,T0,f=1.,g=0.,geff=1.,C=7.,C0=100.,lam=1.,gamma=0.7, ndt=10, noise=0.0):
# simple climate model from Eq 1 and 2 in Geoffroy et al 
# https://journals.ametsoc.org/doi/pdf/10.1175/JCLI-D-12-00195.1
# T = surface air temperature anomaly in K 
# T0 = ocean temperature anomaly in K
# f = GHG forcing in Wm-2 
# g = applied SRM forcing in Wm-2
# geff = efficacy of SRM forcing 
# lam = lambda = feedback parameter Wm-2K-1
# gamma = heat exchange coefficient in Wm-2K-1
# C = atmosphere/land/upper-ocean heat capacity 
# C0 = deep-ocean heat capacity in W.yr.m-2.K-1
# ndt = number of timesteps in 1 yr
# dt = timestep in yr
# noise = noise in T - needs to put a more realistic climate noise
# also noise is only on Tf, should we put noise on T0f as well ?
#
#--test sign geff 
  if geff<0:
    sys.exit('SRM efficacy geff has to be a positive number')
#--discretize yearly timestep
  dt = 1./float(ndt)
#--initial T and TO
  Ti = T ; T0i = T0
# time loop
  for i in range(ndt):
     Tf  = Ti + dt/C*(f+geff*g-lam*Ti-gamma*(Ti-T0i))
     T0f = T0i + dt/C0*gamma*(Ti-T0i)
     Ti = Tf 
     T0i = T0f
# add noise on final Tf
  Tf = Tf + random.gauss(0.,1.)*noise
  return Tf, T0f
#
#
def clim_nh_sh(Tnh,Tsh,T0nh,T0sh,f=1.,gnh=0.,gsh=0.,geff=1.,tau_nh_sh=20.,C=7.,C0=100.,lam=1.,gamma=0.7, ndt=10, noise=0.0):
# simple climate model from Eq 1 and 2 in Geoffroy et al 
# https://journals.ametsoc.org/doi/pdf/10.1175/JCLI-D-12-00195.1
# Tnh,Tsh = surface air temperature anomaly in K 
# T0nh,T0sh = ocean temperature anomaly in K
# f = global GHG forcing in Wm-2 
# gnh,gsh = applied hemispheric SRM forcing in Wm-2
# geff = efficacy of SRM forcing 
# lam = lambda = feedback parameter Wm-2K-1
# gamma = heat exchange coefficient in Wm-2K-1
# tau_nh_sh = timescale (yrs) of interhemispheric heat transfer
# C = atmosphere/land/upper-ocean heat capacity 
# C0 = deep-ocean heat capacity in W.yr.m-2.K-1
# ndt = number of timesteps in 1 yr
# dt = timestep in yr
# noise = noise in T - needs to put a more realistic climate noise
# also noise is only on Tf, should we put noise on T0f as well ?
#
#--test sign geff 
  if geff<0:
    sys.exit('SRM efficacy geff has to be a positive number')
#--discretize yearly timestep
  dt = 1./float(ndt)
#--initial T and TO
  Ti_nh = Tnh ; T0i_nh = T0nh
  Ti_sh = Tsh ; T0i_sh = T0sh
# time loop
  for i in range(ndt):
     #--nh
     Tf_nh  = Ti_nh + dt/C*(f+geff*gnh-lam*Ti_nh-gamma*(Ti_nh-T0i_nh))
     T0f_nh = T0i_nh + dt/C0*gamma*(Ti_nh-T0i_nh)
     #--sh
     Tf_sh  = Ti_sh + dt/C*(f+geff*gsh-lam*Ti_sh-gamma*(Ti_sh-T0i_sh))
     T0f_sh = T0i_sh + dt/C0*gamma*(Ti_sh-T0i_sh)
     #--reducing inter-hemispheric T gradient
     dT  = Tf_nh - Tf_sh
     dT0 = T0f_nh - T0f_sh
     Tf_nh = Tf_nh - dt/tau_nh_sh * dT
     Tf_sh = Tf_sh + dt/tau_nh_sh * dT
     T0f_nh = T0f_nh - dt/tau_nh_sh * dT0
     T0f_sh = T0f_sh + dt/tau_nh_sh * dT0
     #--preparing for next time substep
     Ti_nh  = Tf_nh 
     T0i_nh = T0f_nh
     Ti_sh  = Tf_sh 
     T0i_sh = T0f_sh
# add noise on final Tf
  #Tnoise = random.gauss(0.,noise)
  #Tf_nh = Tf_nh + Tnoise
  #Tf_sh = Tf_sh + Tnoise
  Tf_nh = Tf_nh + random.gauss(0.,noise)
  Tf_sh = Tf_sh + random.gauss(0.,noise)
  return Tf_nh, Tf_sh, T0f_nh, T0f_sh
