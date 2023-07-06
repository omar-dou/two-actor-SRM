from simple_pid import PID
import matplotlib.pyplot as plt
import colorednoise as cn
import numpy as np
import random
import argparse
import sys
from myclim import clim_sh_nh, initialise_aod_responses, emi2aod, emi2rf, Monsoon

#--call script as: python test.py --exp=4 --noise=mixed

parser = argparse.ArgumentParser()
parser.add_argument('--exp', type=str, default='4', help='experiment number')
parser.add_argument('--noise', type=str, default='mixed', choices=['white','red','mixed'],help='Noise type')
args = parser.parse_args()
exp=args.exp
noise_type=args.noise

#--initialise PID controller for each actors
#--PID(Kp, Ki, Kd, setpoint)
#--Kp: proportional gain (typically 0.8 (TgS/yr)/°C    for T target and 0.08 (TgS/yr)/% monsoon    for monsoon change target)
#--Ki: integral gain     (typically 0.6 (TgS/yr)/°C/yr for T target and 0.06 (TgS/yr)/% monsoon/yr for monsoon change target)
#--Kd: derivative gain (typically 0)
#--type: GMST (global mean surf temp), NHST (NH surf temp), SHST (SH surf temp), monsoon
#--setpoint: objective (temperature change in K, monsoon change in %)
#--emimin, emimax: bounds of emissions (in TgS/yr)
#--emipoints: emission points: 30N, 15N, Eq, 15S, 30S
#--t0= start of model integration (in years)
#--t1: start of ramping up SRM intervention
#--t2: end of ramping up SRM intervention
#--t3-t4: period of SRM interruption (use 0 and 0 not to stop)
#--t5= time of end of SRM intervention (in years)
#--fmax: max value for GHG forcing (Wm-2)
#--noise: noise level for T0 (in K)

#--directory for plots
dirout='plots/'
#--show plots while running
ltshow=True
#--period 
t0=0 ; t5=200
#--volcano
volcano=True
#--max GHG forcing
fmax=4.0
#--noise level
noise_T=0.15       #--in K
noise_monsoon=10.  #--in % change
#noise_monsoon=1.  #--in % change
#
#--List of experiments with list of actors, type of setpoint, setpoint, emissions min/max and emission points
#--single actor in NH emitting in his own hemisphere
if exp=="1a":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'NHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15N'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--single actor in NH emitting in opposite hemisphere
elif exp=="1b":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'NHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15S'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--single actor in SH emitting in opposite hemisphere
elif exp=="1c":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'SHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15N'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--single actor in SH emitting in opposite hemisphere
elif exp=="1d":
  A={'Kp':0.008,'Ki':0.006,'Kd':0.0,'type':'monsoon', 'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15S'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--two actors with each one injection point in same hemisphere
elif exp=="2a":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'NHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15N'],'t1':50,'t2':70,'t3':0,'t4':0}
  B={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'SHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15S'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--two actors with each one injection point in opposite hemisphere
elif exp=="2b":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'NHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15S'],'t1':50,'t2':70,'t3':0,'t4':0}
  B={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'SHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15N'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--two actors who each have two injection points and same limits
elif exp=="3a":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'NHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15S','15N'],'t1':50,'t2':70,'t3':0,'t4':0}
  B={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'SHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15S','15N'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--two actors who each have two injection points and different limits
elif exp=="3b":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'NHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15S','15N'],'t1':50,'t2':70,'t3':0,'t4':0}
  B={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'SHST',    'setpoint':0.0, 'emimin':0.0,'emimax':5.0,'emipoints':['15S','15N'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--two actors with targets on NHST and monsoon
elif exp=="4":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'NHST',   'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15N'],'t1':50,'t2':70,'t3':0,'t4':0}
  B={'Kp':0.08,'Ki':0.06,'Kd':0.0,'type':'monsoon','setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['30S'],'t1':50,'t2':70,'t3':0,'t4':0}
  #--test
  B={'Kp':0.08,'Ki':0.6,'Kd':0.0,'type':'monsoon','setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['30S'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--two actors with targets on GMST
elif exp=="5a":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'GMST','setpoint':0.0,'emimin':0.0,'emimax':10.0,'emipoints':['eq'],'t1':50,'t2':70,'t3':0,'t4':0}
  B={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'GMST','setpoint':0.0,'emimin':0.0,'emimax':10.0,'emipoints':['eq'],'t1':50,'t2':70,'t3':0,'t4':0}
#--two actors with targets on GMST
elif exp=="5b":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'GMST','setpoint':0.0,'emimin':0.0,'emimax':10.0,'emipoints':['eq'],'t1':50,'t2':70,'t3':100,'t4':120}
  B={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'GMST','setpoint':0.0,'emimin':0.0,'emimax':10.0,'emipoints':['eq'],'t1':50,'t2':70,'t3':0,'t4':0}
#
#--three actors
elif exp=="6":
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':'NHST',    'setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['15N'],'t1':50,'t2':70,'t3':0,'t4':0}
  B={'Kp':0.08,'Ki':0.06,'Kd':0.0,'type':'monsoon','setpoint':0.0, 'emimin':0.0,'emimax':10.0,'emipoints':['30S'],'t1':50,'t2':70,'t3':0,'t4':0}
  C={'Kp':0.09,'Ki':0.05,'Kd':0.0,'type':'monsoon','setpoint':10.0,'emimin':0.0,'emimax':10.0,'emipoints':['15S'],'t1':50,'t2':70,'t3':0,'t4':0}
else: 
  sys.exit('This scenario is not parametrized')
#
#--Initialise properties of Actors
P={'A':A}
if 'B' in vars(): P['B']=B
if 'C' in vars(): P['C']=C
if 'D' in vars(): P['D']=D
Actors=P.keys()
Kp='Kp' ; Ki='Ki' ; Kd='Kd' ; setpoint='setpoint'
#
#--print Actors and their properties on screen
title=''
for Actor in Actors:
  title=title+' - '+Actor+' '+P[Actor]['type']+' '+str(P[Actor]['setpoint'])
  print(Actor,'=',P[Actor])
print('Scenario title: ',title)
#
#--create a list of all emission points
emipoints=[]
for Actor in Actors:
    for emipoint in P[Actor]['emipoints']:
        if emipoint not in emipoints: emipoints.append(emipoint)
    #--if target type is monsoon, reverse sign of target for technical reason
    if P[Actor]['type']=='monsoon': P[Actor]['setpoint'] = -1.* P[Actor]['setpoint']
print('List of emission points:', emipoints)
markers={'60S':'v','30S':'v','15S':'v','eq':'o','15N':'^','30N':'^','60N':'^',}
sizes={'60S':30,'30S':30,'15S':15,'eq':10,'15N':15,'30N':30,'60N':30}
colors={'A':'green','B':'orange','C':'purple'}
#
#--format float
myformat="{0:3.1f}"
#
#--initialise impulse response functions
aod_strat_sh, aod_strat_nh, nbyr_irf = initialise_aod_responses()
#
#--initialise GHG forcing scenario, increases linearly for 100 yrs then constant then decrease slowly
f=np.zeros((t5))
f[0:100]=np.linspace(0.,fmax,100)
f[100:150]=fmax
f[150:]=np.linspace(fmax,3*fmax/4,50)
#--transient decrease in forcing if volcanic eruption
if volcano:
   f[125]+=-2.0
   f[126]+=-1.0
#
#--time profiles of climate noise
if noise_type=='white':
  white_noise_T=cn.powerlaw_psd_gaussian(0,t5)*noise_T
  Tnh_noise=white_noise_T
  Tsh_noise=white_noise_T
elif noise_type=='red':
  Tnh_noise=cn.powerlaw_psd_gaussian(2,t5)*noise_T
  Tsh_noise=cn.powerlaw_psd_gaussian(2,t5)*noise_T
elif noise_type=='mixed':
  white_noise_T=cn.powerlaw_psd_gaussian(0,t5)*noise_T/2.
  red_noise_T=cn.powerlaw_psd_gaussian(0,t5)*noise_T/2.
  Tnh_noise=white_noise_T+red_noise_T
  red_noise_T=cn.powerlaw_psd_gaussian(0,t5)*noise_T/2.
  Tsh_noise=white_noise_T+red_noise_T
#--monsoon noise
monsoon_noise=cn.powerlaw_psd_gaussian(0,t5)*noise_monsoon
#
#--time profiles of observation noise
TSRM_noise_obs=np.random.normal(0,0.01,t5)
TSRMnh_noise_obs=np.random.normal(0,0.01,t5)
TSRMsh_noise_obs=np.random.normal(0,0.01,t5)
monsoon_noise_obs=np.random.normal(0,1,t5)
#
#--define filename
filename='test'+exp+'.png'
#
#--define the PIDs and the emission min/max profiles
PIDs={} ; emissmin={} ; emissmax={} ; emi_SRM={}
#--loop on Actors
for Actor in Actors:
  PIDs[Actor]={}
  emi_SRM[Actor]={}
  #--loop on emission points of Actor
  for emipoint in P[Actor]['emipoints']:
    #--initialise the PID
    PIDs[Actor][emipoint] = PID(P[Actor][Kp],P[Actor][Ki],P[Actor][Kd],setpoint=P[Actor][setpoint])
    #--initialise the emission arrays
    emi_SRM[Actor][emipoint]=[0.0]
  #--initialise the profile of emission min/max (emissions are counted negative)
  emimin=-1*P[Actor]['emimax'] ; emimax=-1*P[Actor]['emimin']
  t1=P[Actor]['t1'] ; t2=P[Actor]['t2'] ; t3=P[Actor]['t3'] ; t4=P[Actor]['t4']
  emissmin[Actor]=np.zeros((t5))
  emissmax[Actor]=np.zeros((t5))
  emissmin[Actor][t1:t2]=np.linspace(0.0,emimin,t2-t1)
  emissmax[Actor][t1:t2]=np.linspace(0.0,emimax,t2-t1)
  emissmin[Actor][t2:]=emimin
  emissmax[Actor][t2:]=emimax
  emissmin[Actor][t3:t4]=0
  emissmax[Actor][t3:t4]=0
#
#--initialise more stuff
T_SRM=[] ; T_SRM_sh=[] ; T_SRM_nh=[] ; T_noSRM=[] ; T_noSRM_sh=[] ; T_noSRM_nh=[] ; g_SRM_sh=[] ; g_SRM_nh=[]
TnoSRMsh=0 ; T0noSRMsh=0 ; TnoSRMnh=0 ; T0noSRMnh=0
TSRMsh=0   ; T0SRMsh=0   ; TSRMnh=0   ; T0SRMnh=0
monsoon_SRM=[] ; monsoon_noSRM=[] 
#
#--loop on time
for t in range(t0,t5):
  #
  #--reference calculation with no SRM 
  #-----------------------------------
  TnoSRM, TnoSRMsh,TnoSRMnh,T0noSRMsh,T0noSRMnh,gsh,gnh = clim_sh_nh(TnoSRMsh,TnoSRMnh,T0noSRMsh,T0noSRMnh,{},aod_strat_sh,aod_strat_nh,nbyr_irf,\
                                                                     f=f[t],Tsh_noise=Tsh_noise[t],Tnh_noise=Tnh_noise[t])
  T_noSRM.append(TnoSRM) ; T_noSRM_sh.append(TnoSRMsh) ; T_noSRM_nh.append(TnoSRMnh) 
  monsoon=Monsoon(0.0,0.0,noise=monsoon_noise[t]) ; monsoon_noSRM.append(monsoon)
  #
  #--calculation with SRM
  #----------------------
  #--setting limits on emissions for each Actor's PID
  for Actor in Actors:
    for emipoint in P[Actor]['emipoints']:
      PIDs[Actor][emipoint].output_limits = (emissmin[Actor][t],emissmax[Actor][t])
  #
  #--prepare dictionary of combined emissions across all Actors
  emits={}
  #--loop on emission points of Actor
  for Actor in Actors:
     for emipoint in P[Actor]['emipoints']:
        if emipoint in emits:
           emits[emipoint] = [x + y for x,y in zip(emits[emipoint],emi_SRM[Actor][emipoint])]
        else:
           emits[emipoint] = emi_SRM[Actor][emipoint]
  #
  #--iterate climate model
  TSRM, TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh,gnh = clim_sh_nh(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,emits,aod_strat_sh,aod_strat_nh,nbyr_irf,\
                                                           f=f[t],Tsh_noise=Tsh_noise[t],Tnh_noise=Tnh_noise[t])
  #--compute monsoon change
  monsoon=Monsoon(*emi2aod(emits,aod_strat_sh,aod_strat_nh,nbyr_irf),noise=monsoon_noise[t])
  #
  #--report climate model output into lists for plots
  T_SRM.append(TSRM) ; T_SRM_sh.append(TSRMsh) ; T_SRM_nh.append(TSRMnh) ; g_SRM_sh.append(gsh) ; g_SRM_nh.append(gnh) ; monsoon_SRM.append(monsoon)
  #
  # compute new ouput from the PID according to the systems current value
  #--loop on emission points of Actor
  for Actor in Actors:
    for emipoint in P[Actor]['emipoints']:
       #--append the emission arrays
       if P[Actor]['type']=='GMST':
           emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](TSRM+TSRM_noise_obs[t],dt=1))
       if P[Actor]['type']=='NHST':
           emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](TSRMnh+TSRMnh_noise_obs[t],dt=1))
       if P[Actor]['type']=='SHST':
           emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](TSRMsh+TSRMsh_noise_obs[t],dt=1))
       if P[Actor]['type']=='monsoon':
           emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](-1*monsoon+monsoon_noise_obs[t],dt=1))
#
#--change sign of emissions before plotting
for Actor in Actors:
   for emipoint in P[Actor]['emipoints']:
       emi_SRM[Actor][emipoint] = [-1.*x for x in emi_SRM[Actor][emipoint]]
#
#--assess mean and variability
print('Mean and s.d. of TSRMnh w/o SRM:',myformat.format(np.mean(T_noSRM_nh[t2:])),'+/-',myformat.format(np.std(T_noSRM_nh[t2:])))
print('Mean and s.d. of TSRMnh w   SRM:',myformat.format(np.mean(T_SRM_nh[t2:])),'+/-',myformat.format(np.std(T_SRM_nh[t2:])))
#
print('Mean and s.d. of TSRMsh w/o SRM:',myformat.format(np.mean(T_noSRM_sh[t2:])),'+/-',myformat.format(np.std(T_noSRM_sh[t2:])))
print('Mean and s.d. of TSRMsh w   SRM:',myformat.format(np.mean(T_SRM_sh[t2:])),'+/-',myformat.format(np.std(T_SRM_sh[t2:])))
#
print('Mean and s.d. of monsoon w/o SRM:',myformat.format(np.mean(monsoon_noSRM[t2:])),'+/-',myformat.format(np.std(monsoon_noSRM[t2:])))
print('Mean and s.d. of monsoon w   SRM:',myformat.format(np.mean(monsoon_SRM[t2:])),'+/-',myformat.format(np.std(monsoon_SRM[t2:])))
#
#--basic plot with results
title='Controlling global SAI'+title
fig, axs = plt.subplots(3,2,figsize=(22,13))
fig.suptitle(title,fontsize=16)
plt.subplots_adjust(bottom=0.15)
#
axs[0,0].plot([t0,t5],[0,0],zorder=0,linewidth=0.4)
axs[0,0].plot(f,label='GHG RF',c='red')
axs[0,0].legend(loc='upper left',fontsize=12)
axs[0,0].set_ylabel('RF (Wm$^{-2}$)',fontsize=14)
axs[0,0].set_xlim(t0,t5)
axs[0,0].set_xticks(np.arange(t0,t5+1,25),[])
axs[0,0].tick_params(size=14)
axs[0,0].tick_params(size=14)
#
axs[0,1].plot([t0,t5],[0,0],zorder=0,linewidth=0.4)
axs[0,1].plot(Tnh_noise,label='NHST noise',c='black')
axs[0,1].plot(Tsh_noise,label='SHST noise',c='green')
axs[0,1].plot(monsoon_noise/100.,label='Monsoon noise',c='red')
axs[0,1].legend(loc='lower right',fontsize=12)
axs[0,1].set_ylabel('Noise level',fontsize=14)
axs[0,1].set_xlim(t0,t5)
axs[0,1].set_xticks(np.arange(t0,t5+1,25),[])
axs[0,1].tick_params(size=14)
axs[0,1].tick_params(size=14)
#
for Actor in Actors:
   for emipoint in P[Actor]['emipoints']:
       axs[1,0].plot(emi_SRM[Actor][emipoint],linestyle='solid',c=colors[Actor])
       axs[1,0].scatter(range(t0,t5+1,10),emi_SRM[Actor][emipoint][::10],label='Emissions '+Actor+' '+emipoint,c=colors[Actor],marker=markers[emipoint],s=sizes[emipoint])
       axs[1,0].plot(-1*emissmin[Actor],linestyle='dashed',linewidth=0.5,c=colors[Actor])
axs[1,0].legend(loc='upper left',fontsize=12)
axs[1,0].set_ylabel('Emi (TgS yr$^{-1}$)',fontsize=14)
axs[1,0].set_xlim(t0,t5)
axs[1,0].set_xticks(np.arange(t0,t5+1,25),[])
axs[1,0].tick_params(size=14)
axs[1,0].tick_params(size=14)
#
axs[1,1].plot(g_SRM_nh,label='NH SRM g',c='blue')
axs[1,1].plot(g_SRM_sh,label='SH SRM g',c='blue',linestyle='dashed')
axs[1,1].legend(loc='upper left',fontsize=12)
axs[1,1].set_ylabel('RF SRM (Wm$^{-2}$)',fontsize=14)
axs[1,1].set_xlim(t0,t5)
axs[1,1].set_xticks(np.arange(t0,t5+1,25),[])
axs[1,1].tick_params(size=14)
axs[1,1].tick_params(size=14)
#
axs[2,0].plot(T_noSRM_nh,label='NH dT w/o SRM',c='red',zorder=100)
axs[2,0].plot(T_noSRM_sh,label='SH dT w/o SRM',c='red',linestyle='dashed',zorder=100)
axs[2,0].plot(T_SRM_nh,label='NH dT w SRM',c='blue',zorder=0)
axs[2,0].plot(T_SRM_sh,label='SH dT w SRM',c='blue',linestyle='dashed',zorder=0)
axs[2,0].plot([t0,t5],[0,0],c='black',linewidth=0.5)
axs[2,0].legend(loc='upper left',fontsize=12)
axs[2,0].set_xlabel('Years',fontsize=14)
axs[2,0].set_ylabel('Temp. ($^\circ$C)',fontsize=14)
axs[2,0].set_xlim(t0,t5)
axs[2,0].set_xticks(np.arange(t0,t5+1,25))
axs[2,0].tick_params(size=14)
axs[2,0].tick_params(size=14)
#
axs[2,1].plot(monsoon_noSRM,label='monsoon w/o SRM',c='red',zorder=100)
axs[2,1].plot(monsoon_SRM,label='monsoon w SRM',c='blue',zorder=0)
axs[2,1].plot([t0,t5],[0,0],c='black',linewidth=0.5)
axs[2,1].legend(loc='lower left',fontsize=12)
axs[2,1].set_xlabel('Years',fontsize=14)
axs[2,1].set_ylabel('Monsoon (%)',fontsize=14)
axs[2,1].set_xlim(t0,t5)
axs[2,1].set_xticks(np.arange(t0,t5+1,25))
axs[2,1].tick_params(size=14)
axs[2,1].tick_params(size=14)
#
fig.tight_layout()
fig.savefig(dirout+filename)
#plt.show()
