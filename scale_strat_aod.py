import numpy as np
import xarray as xr

sw=xr.open_dataset('/data/oboucher/CMIP6/VOLC/LR_v4/tauswstrat.2D.1991.nc')
lw=xr.open_dataset('/data/oboucher/CMIP6/VOLC/LR_v4/taulwstrat.2D.1991.nc')

sw_g_scaling=sw.GGG_SUN.sel(TIME=8,LAT=0.0,LEV=52).values
sw_aod_scaling=sw.TAU_SUN.sel(TIME=8,LAT=0.0,LEV=52).values
lw_aod_scaling=lw.TAU_EAR.sel(TIME=8,LAT=0.0,LEV=52).values

#--AOD at 550 nm
aod_550=0.7

#--sw AOD scaling
sw_aod=aod_550/sw_aod_scaling[2]*sw_aod_scaling
sw_aod=np.repeat(sw_aod[np.newaxis,:],12,axis=0)
sw_aod=np.repeat(sw_aod[:,:,np.newaxis],72,axis=2) #--only one hemisphere

#--sw g factor (no scaling as intensive variable)
sw_g=np.repeat(sw_g_scaling[np.newaxis,:],12,axis=0)
sw_g=np.repeat(sw_g[:,:,np.newaxis],72,axis=2) #--only one hemisphere

#--lw AOD scaling
lw_aod=aod_550/sw_aod_scaling[2]*lw_aod_scaling
lw_aod=np.repeat(lw_aod[np.newaxis,:],12,axis=0)
lw_aod=np.repeat(lw_aod[:,:,np.newaxis],72,axis=2) #--only one hemisphere

#--lw tau NH
lw.TAU_EAR.values=np.zeros((lw.TAU_EAR.shape))
lw.TAU_EAR.values[:,:,52,0:72]=lw_aod

#--sw tau NH
sw.TAU_SUN.values=np.zeros((sw.TAU_SUN.shape))
sw.TAU_SUN.values[:,:,52,0:72]=sw_aod

#--sw g and omega NH
sw.GGG_SUN.values=np.zeros((sw.TAU_SUN.shape))
sw.GGG_SUN.values[:,:,52,0:72]=sw_g
sw.OME_SUN.values=np.ones((sw.TAU_SUN.shape))

#--save to file NH
sw.to_netcdf('tauswstrat.2D.NH.nc')
lw.to_netcdf('taulwstrat.2D.NH.nc')

#--lw tau SH
lw.TAU_EAR.values=np.zeros((lw.TAU_EAR.shape))
lw.TAU_EAR.values[:,:,52,71:]=lw_aod

#--sw tau SH
sw.TAU_SUN.values=np.zeros((sw.TAU_SUN.shape))
sw.TAU_SUN.values[:,:,52,71:]=sw_aod

#--sw g and omega SH
sw.GGG_SUN.values=np.zeros((sw.TAU_SUN.shape))
sw.GGG_SUN.values[:,:,52,71:]=sw_g
sw.OME_SUN.values=np.ones((sw.TAU_SUN.shape))

#--save to file SH
sw.to_netcdf('tauswstrat.2D.SH.nc')
lw.to_netcdf('taulwstrat.2D.SH.nc')
