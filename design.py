from simple_pid import PID
import matplotlib.pyplot as plt
import colorednoise as cn
import numpy as np
from scipy.stats import pearsonr   
import random
import argparse
import sys
from myclim import clim_sh_nh, initialise_aod_responses, emi2aod, emi2rf, rf2aod, Monsoon

#--initialise PID controller for each actors
#--PID(Kp, Ki, Kd, setpoint)
#--Kp: proportional gain (typically 0.8 (TgS/yr)/°C    for T target and 0.08 (TgS/yr)/% monsoon    for monsoon change target)
#--Ki: integral gain     (typically 0.6 (TgS/yr)/°C/yr for T target and 0.06 (TgS/yr)/% monsoon/yr for monsoon change target)
#--Kd: derivative gain   (typically 0)
#--type: GMST (global mean surf temp), NHST (NH surf temp), SHST (SH surf temp), monsoon
#--setpoint: objective (temperature change in K, monsoon change in %)
#--emimin, emimax: bounds of emissions (in TgS/yr)
#--emipoints: emission points: 30N, 15N, Eq, 15S, 30S
#--t0= start of model integration (in years)
#--t5= end of model integration (in years)
#--stops: periods of SRM interruption, list of tuples (t3,t4) and targets exceeded
#--fmax: max value for GHG forcing (Wm-2)
#--noise: noise level for T0 (in K)

#--directory for plots
dirout='plots/'
#--show plots while running
pltshow=True
#--period 
t0=0 ; t5=200
#--noise level
noise_T=0.15       #--in K
noise_monsoon=10.  #--in % change
#noise_monsoon=1.  #--in % change
#--interhemispheric timescales (in years)
tau_nh_sh_upper=20.
tau_nh_sh_lower=20.
#
#--create a list of all emission points
emipoints=['15S','15N']
emits={} ; emits_ts={}
for emipoint in emipoints:
   emits[emipoint]=[]
   emits_ts[emipoint]=[]
#
emits_ts['15S']=np.zeros((t5))
emits_ts['15N']=np.zeros((t5))
#
#emits_ts['15S'][1:2]=-5.0
#emits_ts['15S'][5:10]=-5.0
#emits_ts['15S'][15:20]=-10.0
#emits_ts['15S'][30:40]=-5.0
#emits_ts['15S'][50:60]=-10.0
#emits_ts['15S'][80:100]=-5.0
#emits_ts['15S'][150:200]=-5.0
#
#emits_ts['15N'][2:4]=-5.0
#emits_ts['15N'][10:14]=-10.0
#emits_ts['15N'][20:28]=-5.0
#emits_ts['15N'][40:50]=-5.0
#emits_ts['15N'][60:70]=-10.0
#emits_ts['15N'][100:140]=-5.0
#for t in range(t0,t5,3):
#    emits_ts['15S'][t]=-10.
#for t in range(t5//2+1,t5,5):
#    emits_ts['15S'][t]=-10.*5./3.
#for t in range(t0,t5//2,5):
#    emits_ts['15N'][t]=-10.*5./3.
#for t in range(t5//2+1,t5,3):
#    emits_ts['15N'][t]=-10.
for t in range(t0,t5,3):
    emits_ts['15S'][t]=-10.*(1+t/t5)
for t in range(t0,t5,7):
    emits_ts['15N'][t]=-10.*7./3.*(1+t/t5)
#
#--format float
myformat="{0:3.1f}"
#
#--initialise impulse response functions
aod_strat_sh, aod_strat_nh, nbyr_irf = initialise_aod_responses()
#
#--initialise more stuff
T_SRM=[] ; T_SRM_sh=[] ; T_SRM_nh=[] ; g_sh=[] ; g_nh=[]
TSRMsh=0 ; T0SRMsh=0 ; TSRMnh=0 ; T0SRMnh=0
#
#--loop on time
for t in range(t0,t5):
  #
  #--random walk
  #emits['15S'].append(-1*np.random.choice(3)*5.)
  #emits['15N'].append(-1*np.random.choice(3)*5.)
  #--alternate
  #emits['15S'].append(-5*(t%3))
  #emits['15N'].append(-5*((t+2)%3))
  #--sample 
  emits['15S']=emits_ts['15S'][0:t+1]
  emits['15N']=emits_ts['15N'][0:t+1]
  #
  TSRM, TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh,gnh = clim_sh_nh(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,emits,aod_strat_sh,aod_strat_nh,nbyr_irf,\
                                                                     f=0,Tsh_noise=0,Tnh_noise=0, tau_nh_sh_upper=tau_nh_sh_upper,tau_nh_sh_lower=tau_nh_sh_lower)
  T_SRM.append(TSRM) ; T_SRM_sh.append(TSRMsh) ; T_SRM_nh.append(TSRMnh)  ; g_sh.append(gsh) ; g_nh.append(gnh)

#--interhemispheric difference in T
T_SRM_delta=[x-y for x,y in zip(T_SRM_nh,T_SRM_sh)]
aod_sh=[rf2aod(x) for x in g_sh]
aod_nh=[rf2aod(x) for x in g_nh]
aod_delta=[rf2aod(x)-rf2aod(y) for x,y in zip(g_nh,g_sh)]
g_delta=[x-y for x,y in zip(g_nh,g_sh)]

#--correlations
print('correlation delta AOD / delta T=',pearsonr(aod_delta,T_SRM_delta))

#--basic plot with results
title='Designing ESM exp'
fig, axs = plt.subplots(2,2,figsize=(10,13))
fig.suptitle(title,fontsize=16)
plt.subplots_adjust(bottom=0.15)
#
axs[0,0].plot([t0,t5],[0,0],zorder=0,linewidth=0.4)
axs[0,0].plot([-1*x for x in emits['15S']],label='15S',c='red')
axs[0,0].plot([-1*x for x in emits['15N']],label='15N',c='green')
axs[0,0].legend(loc='upper left',fontsize=12)
axs[0,0].set_ylabel('Emissions',fontsize=14)
axs[0,0].set_xlim(t0,t5)
axs[0,0].set_xticks(np.arange(t0,t5+1,25))
axs[0,0].tick_params(size=14)
axs[0,0].tick_params(size=14)
#
axs[0,1].plot([t0,t5],[0,0],zorder=0,linewidth=0.4)
axs[0,1].plot(aod_sh,label='SH AOD',c='red')
axs[0,1].plot(aod_nh,label='NH AOD',c='green')
axs[0,1].plot(aod_delta,label='NH-SH AOD',c='black')
axs[0,1].legend(loc='upper left',fontsize=12)
axs[0,1].set_ylabel('AOD',fontsize=14)
axs[0,1].set_xlim(t0,t5)
axs[0,1].set_xticks(np.arange(t0,t5+1,25))
axs[0,1].tick_params(size=14)
axs[0,1].tick_params(size=14)
#
axs[1,0].plot([t0,t5],[0,0],zorder=0,linewidth=0.4)
axs[1,0].plot(T_SRM_sh,label='SHST',c='red')
axs[1,0].plot(T_SRM_nh,label='NHST',c='green')
axs[1,0].plot(T_SRM_delta,label='NHST-SHST',c='black')
axs[1,0].legend(loc='lower right',fontsize=12)
axs[1,0].set_ylabel('Temp',fontsize=14)
axs[1,0].set_xlim(t0,t5)
axs[1,0].set_xticks(np.arange(t0,t5+1,25))
axs[1,0].tick_params(size=14)
axs[1,0].tick_params(size=14)
#
axs[1,1].scatter(aod_delta,T_SRM_delta,marker='x',s=12)
axs[1,1].set_xlabel('delta AOD',fontsize=14)
axs[1,1].set_ylabel('delta Temp',fontsize=14)
axs[1,1].tick_params(size=14)
axs[1,1].tick_params(size=14)
#
fig.tight_layout()
fig.savefig('design.png')
plt.show()
