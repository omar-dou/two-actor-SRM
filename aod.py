import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
#
dirin="/thredds/tgcc/store/oboucher/S3A/"
exps=['eq','15S','15N','30S','30N']
emi0=10.0    #--GtS injected
nbmthinyr=12 #--number of months in yr
aod2rf=-100  #--Wm-2 per unit AOD
#
#--reference experiment
exp='ref'
file=dirin+'LMDZOR-S3A-'+exp+'_19950101_20041231_1M_od550_STRAT.nc'
xrfile=xr.open_dataset(file)
lons=xrfile.lon
lats=xrfile.lat
#--select SH and NH latitudes
lats_nh=lats[np.where(lats>=0.0)]
lats_sh=lats[np.where(lats<=0.0)]
#--length of pulse experiment (in yr)
nbyr=len(xrfile.time_counter)//nbmthinyr
#--select and hemispherically-average AOD for ref experiment
aod_ref_strat_sh=np.average(xrfile.sel(lat=lats_sh)['od550_STRAT'].values,axis=(1,2))
aod_ref_strat_nh=np.average(xrfile.sel(lat=lats_nh)['od550_STRAT'].values,axis=(1,2))
#
#--prepare AOD time series for 10 GtS injection experiments for 1 yr
aod_strat_sh={}
aod_strat_nh={}
for exp in exps: 
    file=dirin+'LMDZOR-S3A-'+exp+'_19950101_20041231_1M_od550_STRAT.nc'
    xrfile=xr.open_dataset(file)
    aod_strat_sh[exp]=np.maximum(0,np.average(xrfile.sel(lat=lats_sh)['od550_STRAT'].values,axis=(1,2))-aod_ref_strat_sh)
    aod_strat_nh[exp]=np.maximum(0,np.average(xrfile.sel(lat=lats_nh)['od550_STRAT'].values,axis=(1,2))-aod_ref_strat_nh)
#
#--plot IRF for SH AOD - monthly means
for exp in exps: 
    plt.plot(aod_strat_sh[exp],label=exp)
plt.title('SH AOD @550 nm')
plt.xlabel('Months after start of injection')
plt.legend()
plt.show()
#
#--plot IRF for NH AOD - monthly means
for exp in exps: 
    plt.plot(aod_strat_nh[exp],label=exp)
plt.title('NH AOD @550 nm')
plt.xlabel('Months after start of injection')
plt.legend()
plt.show()
#
#--compute annual means
for exp in exps: 
    aod_strat_sh[exp]=np.average(aod_strat_sh[exp].reshape((nbyr,nbmthinyr)),axis=1)
    aod_strat_nh[exp]=np.average(aod_strat_nh[exp].reshape((nbyr,nbmthinyr)),axis=1)
#
#--plot IRF for SH AOD - annual means
for exp in exps: 
    plt.plot(aod_strat_sh[exp],label=exp)
plt.title('SH AOD @550 nm')
plt.xlabel('Years after start of injection')
plt.legend()
plt.show()
#
#--plot IRF for NH AOD - annual means
for exp in exps: 
    plt.plot(aod_strat_nh[exp],label=exp)
plt.title('NH AOD @550 nm')
plt.xlabel('Years after start of injection')
plt.legend()
plt.show()
#
#--convolve emissions with IRF
#--time series of emissions (example)
emits={}
emits['eq']=[1,0,1]
emits['15S']=[0,1,0]
emits['15N']=[0,1,1]
emits['30S']=[0,0,1]
emits['30N']=[0,1,1]
#
#--routine to convolve emissions with IRF to produce SH and NH AOD
def emi2aod(emits):
    AOD_SH=0.0 ; AOD_NH=0.0
    yrend=min(nbyr,len(emits['eq'])) #--length (in yrs) of past injection time series
    #--loop on experiments
    for exp in exps:
        #--loop on time series, only consider last nbyr years
        for yr,emi in enumerate(emits[exp][-nbyr:]):     
            #--AODs by summing on injection points and years by convolving with IRF
            AOD_SH += aod_strat_sh[exp][yrend-1-yr]*emi/emi0
            AOD_NH += aod_strat_nh[exp][yrend-1-yr]*emi/emi0
    return AOD_SH, AOD_NH
#
#--routine to compute forcings from emissions
def emi2rf(emits):
    AOD_SH, AOD_NH = emi2aod(emits)
    return AOD_SH*aod2rf, AOD_NH*aod2rf
#
#--test
AOD_SH, AOD_NH = emi2aod(emits)
print('AOD=',AOD_SH, AOD_NH)
RF_SH, RF_NH = emi2rf(emits)
print('AOD=',RF_SH, RF_NH)
