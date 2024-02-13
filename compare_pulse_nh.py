from simple_pid import PID
import matplotlib.pyplot as plt
import colorednoise as cn
import numpy as np
from scipy.stats import pearsonr   
import pandas as pd
import random
import argparse
import sys
from myclim import clim_sh_nh_from_rf, aod2rf, rf2aod

df=pd.read_csv('temp.csv')
df['t_nh1_GLOBE_yr']=(df['t_nh1_NH_yr']+df['t_nh1_SH_yr'])/2.
df['t_nh2_GLOBE_yr']=(df['t_nh2_NH_yr']+df['t_nh2_SH_yr'])/2.
df['t_nh3_GLOBE_yr']=(df['t_nh3_NH_yr']+df['t_nh3_SH_yr'])/2.
df['t_sh1_GLOBE_yr']=(df['t_sh1_NH_yr']+df['t_sh1_SH_yr'])/2.
df['t_sh2_GLOBE_yr']=(df['t_sh2_NH_yr']+df['t_sh2_SH_yr'])/2.
df['t_sh3_GLOBE_yr']=(df['t_sh3_NH_yr']+df['t_sh3_SH_yr'])/2.
df['t_nh1_GLOBE_yr']=df['t_nh1_GLOBE_yr']-df['t_nh1_GLOBE_yr'].iloc[0]-0.25
df['t_nh2_GLOBE_yr']=df['t_nh2_GLOBE_yr']-df['t_nh2_GLOBE_yr'].iloc[0]-0.25
df['t_nh3_GLOBE_yr']=df['t_nh3_GLOBE_yr']-df['t_nh3_GLOBE_yr'].iloc[0]-0.25
df['t_sh1_GLOBE_yr']=df['t_sh1_GLOBE_yr']-df['t_sh1_GLOBE_yr'].iloc[0]-0.25
df['t_sh2_GLOBE_yr']=df['t_sh2_GLOBE_yr']-df['t_sh2_GLOBE_yr'].iloc[0]-0.25
df['t_sh3_GLOBE_yr']=df['t_sh3_GLOBE_yr']-df['t_sh3_GLOBE_yr'].iloc[0]-0.25

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
dy=5
t0=0 ; t5=2*dy
#--noise level
noise_T=0.15       #--in K
noise_monsoon=10.  #--in % change
#noise_monsoon=1.  #--in % change
#
#--interhemispheric timescales (in years)
tau_nh_sh_upper=7.
tau_nh_sh_lower=10.
#--feedback parameter (Wm-2K-1)
lam=0.8
# C = atmosphere/land/upper-ocean heat capacity
C=6.0
# C0 = deep-ocean heat capacity in W.yr.m-2.K-1
C0=150.0
#
#--format float
myformat="{0:3.1f}"
#
#--initialise more stuff
T_SRM=[] ; T_SRM_sh=[] ; T_SRM_nh=[] ; g_sh=[] ; g_nh=[]
TSRMsh=0 ; T0SRMsh=0 ; TSRMnh=0 ; T0SRMnh=0
#
#--hemispheric stratospheric AOD 
saod=0.4
#
gsh=np.zeros((t5))
gnh=np.zeros((t5))
gnh[0:dy]=aod2rf(saod,hem='NH')
gsh[0:dy]=0.0
gnh[dy:2*dy]=0.0
gsh[dy:2*dy]=aod2rf(saod,hem='SH')
#
#--loop on time
for t in range(t0,t5):
  #
  TSRM, TSRMsh,TSRMnh,T0SRMsh,T0SRMnh = clim_sh_nh_from_rf(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh[t],gnh[t],\
                                        f=0,lam=lam,C=C,C0=C0,Tsh_noise=0,Tnh_noise=0,\
                                        tau_nh_sh_upper=tau_nh_sh_upper,tau_nh_sh_lower=tau_nh_sh_lower)
  T_SRM.append(TSRM) ; T_SRM_sh.append(TSRMsh) ; T_SRM_nh.append(TSRMnh)  ; g_sh.append(gsh[t]) ; g_nh.append(gnh[t])
#
#--globe average 
T_SRM_globe=[(x+y)/2. for x,y in zip(T_SRM_nh,T_SRM_sh)]
#--interhemispheric difference in T
T_SRM_delta=[x-y for x,y in zip(T_SRM_nh,T_SRM_sh)]
#--interhemispheric difference in AOD
aod_delta=[rf2aod(x)-rf2aod(y) for x,y in zip(g_nh,g_sh)]
#--range of years
yrs=np.arange(1,11,1)

#--basic plot with results - GLOBE
fig, ax1 = plt.subplots(figsize=(10,13))
#title=''
#fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_nh1_GLOBE_yr'].values,color='black')
ax1.plot(yrs,df['t_nh2_GLOBE_yr'].values,color='black')
ax1.plot(yrs,df['t_nh3_GLOBE_yr'].values,color='black')
ax1.plot(yrs,T_SRM_globe,color='green')
ax2.plot(yrs,aod_delta,color='blue')
ax1.set_xlim(0.5,10.5)
ax2.set_xlim(0.5,10.5)
ax1.set_xticks(range(1,11))
ax1.set_ylim(-2,0)
ax2.set_ylim(-0.5,0.5)
ax1.set_xlabel('Years',fontsize=15)
ax1.set_ylabel('$\Delta$T (globe) in °C',fontsize=15,color='black')
ax2.set_ylabel('$\Delta$SAOD (NH-SH)',fontsize=15,color='blue')
ax2.spines['right'].set_color('blue')
ax1.tick_params(axis='both', which='major', labelsize=13)
ax2.tick_params(axis='both', which='major', labelsize=13, colors='blue')
plt.savefig('compare_T_GLOBE_nh.png',bbox_inches='tight')
plt.show()
#
#--basic plot with results - DIFF
fig, ax1 = plt.subplots(figsize=(10,13))
#title=''
#fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_nh1_DIFF_yr'].values,color='black')
ax1.plot(yrs,df['t_nh2_DIFF_yr'].values,color='black')
ax1.plot(yrs,df['t_nh3_DIFF_yr'].values,color='black')
ax1.plot(yrs,T_SRM_delta,color='green')
ax2.plot(yrs,aod_delta,color='blue')
ax1.set_xlim(0.5,10.5)
ax2.set_xlim(0.5,10.5)
ax1.set_xticks(range(1,11))
ax1.set_ylim(-2,2)
ax2.set_ylim(-0.5,0.5)
ax1.set_xlabel('Years',fontsize=15)
ax1.set_ylabel('$\Delta$T (NH-SH) in °C',fontsize=15,color='black')
ax2.set_ylabel('$\Delta$SAOD (NH-SH)',fontsize=15,color='blue')
ax2.spines['right'].set_color('blue')
ax1.tick_params(axis='both', which='major', labelsize=13)
ax2.tick_params(axis='both', which='major', labelsize=13, colors='blue')
plt.savefig('compare_T_DIFF_nh.png',bbox_inches='tight')
plt.show()
#
