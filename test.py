from simple_pid import PID
import matplotlib.pyplot as plt
import numpy as np
from myclim import clim, clim_sh_nh, clim_sh_nh_v2, initialise_aod_responses, emi2aod, emi2rf, Monsoon

#--initialise PID controller for each actors
#--PID(Kp, Ki, Kd, setpoint)
#--Kp: proportional gain (typically for 0.8 for T target and 0.6 for monsoon target)
#--Ki: integral gain (typically for 0.08 for T target and 0.06 for monsoon target)
#--Kd: derivative gain (typically 0)
#--type: NHT (NH temp), SHT (SH temp), monsoon
#--setpoint: objective (temperature change in K, monsoon change in % counted negative)
#--emimin, emimax: bounds of emissions (counted negative)
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
pltshow=True
#--period 
t0=0 ; t5=200
#--max GHG forcing
fmax=4.0
#--noise level
noise_T=0.05
noise_monsoon=10.
#--list of actors, type of setpoint, setpoint, emissions min/max and emission points
A={'Kp':0.8,'Ki':0.6,'Kd':0.0,'type':'NHT','setpoint':0.0,'emimin':-20.0,'emimax':0.0,'emipoints':['15N'],'t1':50,'t2':70,'t3':0,'t4':0}
B={'Kp':0.08,'Ki':0.06,'Kd':0.0,'type':'monsoon','setpoint':-10.0,'emimin':-20.0,'emimax':0.0,'emipoints':['15S'],'t1':50,'t2':70,'t3':0,'t4':0}
#--Properties of Actors
P={'A':A,'B':B} 
Actors=P.keys()
Kp='Kp' ; Ki='Ki' ; Kd='Kd' ; setpoint='setpoint'
#--print Actors and their properties on creen
for Actor in Actors:
  print(Actor,'=',P[Actor])
#--create a list of all emission points
emipoints=[]
for Actor in Actors: 
    for emipoint in P[Actor]['emipoints']:
        if emipoint not in emipoints: emipoints.append(emipoint)
print('List of emission points:', emipoints)
#
#--initialise impulse response functions
aod_strat_sh, aod_strat_nh, nbyr_irf = initialise_aod_responses()
#
#--initialise GHG forcing scenario, increases linearly for 100 yrs then constant then decrease slowly
f=np.zeros((t5))
f[0:100]=np.linspace(0.,fmax,100)
f[100:150]=fmax
f[150:]=np.linspace(fmax,3*fmax/4,50)
#
#--define filename
filename='test.png'
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
  #--initialise the profile of emission min/max
  emimin=P[Actor]['emimin'] ; emimax=P[Actor]['emimax']
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
T_SRM_sh=[] ; T_SRM_nh=[] ; T_noSRM_sh=[] ; T_noSRM_nh=[] ; g_SRM_sh=[] ; g_SRM_nh=[]
TnoSRMsh=0 ; T0noSRMsh=0 ; TnoSRMnh=0 ; T0noSRMnh=0
TSRMsh=0   ; T0SRMsh=0   ; TSRMnh=0   ; T0SRMnh=0
monsoon_SRM=[] ; monsoon_noSRM=[] 
#
#--loop on time
for t in range(t0,t5):
  #
  #--reference calculation with no SRM 
  #-----------------------------------
  TnoSRMsh,TnoSRMnh,T0noSRMsh,T0noSRMnh=clim_sh_nh(TnoSRMsh,TnoSRMnh,T0noSRMsh,T0noSRMnh,f=f[t],gnh=0,gsh=0,noise=noise_T)
  T_noSRM_sh.append(TnoSRMsh) ; T_noSRM_nh.append(TnoSRMnh) 
  monsoon=Monsoon(0.0,0.0,noise=noise_monsoon) ; monsoon_noSRM.append(monsoon)
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
  TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh,gnh=clim_sh_nh_v2(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,emits,aod_strat_sh,aod_strat_nh,nbyr_irf,f=f[t],noise=noise_T)
  monsoon=Monsoon(*emi2aod(emits,aod_strat_sh,aod_strat_nh,nbyr_irf),noise=noise_monsoon)
  #
  #--report climate model output into lists for plots
  T_SRM_sh.append(TSRMsh) ; T_SRM_nh.append(TSRMnh) ; g_SRM_sh.append(gsh) ; g_SRM_nh.append(gnh) ; monsoon_SRM.append(monsoon)
  #
  # compute new ouput from the PID according to the systems current value
  #--loop on emission points of Actor
  for Actor in Actors:
    for emipoint in P[Actor]['emipoints']:
       #--append the emission arrays
       if P[Actor]['type']=='NHT':
           emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](TSRMnh,dt=1))
       if P[Actor]['type']=='SHT':
           emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](TSRMsh,dt=1))
       if P[Actor]['type']=='monsoon':
           emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](-1*monsoon,dt=1))
#
#--change sign of emissions before plotting
for Actor in Actors:
   for emipoint in P[Actor]['emipoints']:
       emi_SRM[Actor][emipoint] = [-1.*x for x in emi_SRM[Actor][emipoint]]
#
#--basic plot with results
myformat="{0:3.1f}"
title='Controlling global SAI intervention'
fig=plt.figure(figsize=(12,14))
#
plt.subplot(511)
plt.title(title,fontsize=10)
plt.plot([t0,t5],[0,0],zorder=0,linewidth=0.4)
plt.plot(f,label='GHG RF',c='red')
plt.legend(loc='upper left',fontsize=8)
plt.ylabel('RF (Wm$^{-2}$)',fontsize=10)
plt.xlim(t0,t5)
plt.xticks(np.arange(t0,t5+1,25),[])
#
plt.subplot(512)
for Actor in Actors:
   if Actor == 'A': linestyle='solid'
   if Actor == 'B': linestyle='dashed'
   for emipoint in P[Actor]['emipoints']:
       plt.plot(emi_SRM[Actor][emipoint],label='Emissions '+Actor+' '+emipoint,c='blue',linestyle=linestyle)
plt.legend(loc='upper left',fontsize=8)
plt.ylabel('Emi (TgS yr$^{-1}$)',fontsize=10)
plt.xlim(t0,t5)
plt.xticks(np.arange(t0,t5+1,25),[])
#
plt.subplot(513)
plt.plot(g_SRM_nh,label='NH SRM g',c='blue')
plt.plot(g_SRM_sh,label='SH SRM g',c='blue',linestyle='dashed')
plt.legend(loc='upper left',fontsize=8)
plt.ylabel('RF SRM (Wm$^{-2}$)',fontsize=10)
plt.xlim(t0,t5)
plt.xticks(np.arange(t0,t5+1,25),[])
#
plt.subplot(514)
plt.plot(T_noSRM_nh,label='NH dT w/o SRM',c='red')
plt.plot(T_noSRM_sh,label='SH dT w/o SRM',c='red',linestyle='dashed')
plt.plot(T_SRM_nh,label='NH dT w SRM',c='blue')
plt.plot(T_SRM_sh,label='SH dT w SRM',c='blue',linestyle='dashed')
plt.plot([t0,t5],[0,0],c='black',linewidth=0.5)
plt.legend(loc='upper left',fontsize=8)
plt.ylabel('Temp. ($^\circ$C)',fontsize=10)
plt.xlim(t0,t5)
plt.xticks(np.arange(t0,t5+1,25),[])
#
plt.subplot(515)
plt.plot(monsoon_noSRM,label='monsoon w/o SRM',c='red')
plt.plot(monsoon_SRM,label='monsoon w SRM',c='blue')
plt.plot([t0,t5],[0,0],c='black',linewidth=0.5)
plt.legend(loc='upper left',fontsize=8)
plt.xlabel('Years',fontsize=10)
plt.ylabel('Monsoon (%)',fontsize=10)
plt.xlim(t0,t5)
plt.xticks(np.arange(t0,t5+1,25))
#
plt.show()
plt.savefig(dirout+filename)
