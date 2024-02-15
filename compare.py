from simple_pid import PID
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from numpy.linalg import norm
import colorednoise as cn
import numpy as np
from scipy.stats import pearsonr   
import pandas as pd
import random
import argparse
import sys
from myclim import clim_sh_nh_from_rf, clim_sh_nh_from_rf_v2, aod2rf, rf2aod
#
df=pd.read_csv('temp.csv')
#
df['t_nh1_GLOBE_yr']=(df['t_nh1_NH_yr']+df['t_nh1_SH_yr'])/2.
df['t_nh2_GLOBE_yr']=(df['t_nh2_NH_yr']+df['t_nh2_SH_yr'])/2.
df['t_nh3_GLOBE_yr']=(df['t_nh3_NH_yr']+df['t_nh3_SH_yr'])/2.
df['t_sh1_GLOBE_yr']=(df['t_sh1_NH_yr']+df['t_sh1_SH_yr'])/2.
df['t_sh2_GLOBE_yr']=(df['t_sh2_NH_yr']+df['t_sh2_SH_yr'])/2.
df['t_sh3_GLOBE_yr']=(df['t_sh3_NH_yr']+df['t_sh3_SH_yr'])/2.
#
df['t_nh1_GLOBE_yr']=df['t_nh1_GLOBE_yr']-df['t_nh1_GLOBE_yr'].iloc[0]-0.25
df['t_nh2_GLOBE_yr']=df['t_nh2_GLOBE_yr']-df['t_nh2_GLOBE_yr'].iloc[0]-0.25
df['t_nh3_GLOBE_yr']=df['t_nh3_GLOBE_yr']-df['t_nh3_GLOBE_yr'].iloc[0]-0.25
df['t_sh1_GLOBE_yr']=df['t_sh1_GLOBE_yr']-df['t_sh1_GLOBE_yr'].iloc[0]-0.25
df['t_sh2_GLOBE_yr']=df['t_sh2_GLOBE_yr']-df['t_sh2_GLOBE_yr'].iloc[0]-0.25
df['t_sh3_GLOBE_yr']=df['t_sh3_GLOBE_yr']-df['t_sh3_GLOBE_yr'].iloc[0]-0.25
#
df['t_nh1_NH_yr']=df['t_nh1_NH_yr']-df['t_nh1_NH_yr'].iloc[0]-0.5
df['t_nh2_NH_yr']=df['t_nh2_NH_yr']-df['t_nh2_NH_yr'].iloc[0]-0.5
df['t_nh3_NH_yr']=df['t_nh3_NH_yr']-df['t_nh3_NH_yr'].iloc[0]-0.5
df['t_sh1_NH_yr']=df['t_sh1_NH_yr']-df['t_sh1_NH_yr'].iloc[0]
df['t_sh2_NH_yr']=df['t_sh2_NH_yr']-df['t_sh2_NH_yr'].iloc[0]
df['t_sh3_NH_yr']=df['t_sh3_NH_yr']-df['t_sh3_NH_yr'].iloc[0]
#
df['t_nh1_SH_yr']=df['t_nh1_SH_yr']-df['t_nh1_SH_yr'].iloc[0]
df['t_nh2_SH_yr']=df['t_nh2_SH_yr']-df['t_nh2_SH_yr'].iloc[0]
df['t_nh3_SH_yr']=df['t_nh3_SH_yr']-df['t_nh3_SH_yr'].iloc[0]
df['t_sh1_SH_yr']=df['t_sh1_SH_yr']-df['t_sh1_SH_yr'].iloc[0]-0.5
df['t_sh2_SH_yr']=df['t_sh2_SH_yr']-df['t_sh2_SH_yr'].iloc[0]-0.5
df['t_sh3_SH_yr']=df['t_sh3_SH_yr']-df['t_sh3_SH_yr'].iloc[0]-0.5
#
#--ensemble means as target for model adjustment
#
target_t_nh_NH=(df['t_nh1_NH_yr']+df['t_nh2_NH_yr']+df['t_nh3_NH_yr'])/3.
target_t_sh_NH=(df['t_sh1_NH_yr']+df['t_sh2_NH_yr']+df['t_sh3_NH_yr'])/3.
#
target_t_nh_SH=(df['t_nh1_SH_yr']+df['t_nh2_SH_yr']+df['t_nh3_SH_yr'])/3.
target_t_sh_SH=(df['t_sh1_SH_yr']+df['t_sh2_SH_yr']+df['t_sh3_SH_yr'])/3.
#
target_t_nh_GLOBE=(df['t_nh1_GLOBE_yr']+df['t_nh2_GLOBE_yr']+df['t_nh3_GLOBE_yr'])/3.
target_t_sh_GLOBE=(df['t_sh1_GLOBE_yr']+df['t_sh2_GLOBE_yr']+df['t_sh3_GLOBE_yr'])/3.
#
target_t_nh_DIFF =(df['t_nh1_DIFF_yr']+df['t_nh2_DIFF_yr']+df['t_nh3_DIFF_yr'])/3.
target_t_sh_DIFF =(df['t_sh1_DIFF_yr']+df['t_sh2_DIFF_yr']+df['t_sh3_DIFF_yr'])/3.
#
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
#
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
#--minimization method 
method='SLSQP'
method='L-BFGS-B'
#--range of years
yrs=np.arange(1,11,1)
#
#--hemispheric stratospheric AOD 
saod=0.4
#
#--format float
myformat="{0:3.1f}"
#
#--default and initial values for tunable parameters
#--interhemispheric timescales (in years)
tau_nh_sh_upper_00=7.
tau_nh_sh_lower_00=10.
#
#--feedback parameter (Wm-2K-1)
lambdash_00=0.8
lambdanh_00=0.8
#
# gamma = heat exchange coefficient in W.m-2.K-1
gamma_00=0.7
#
# C = atmosphere/land/upper-ocean heat capacity in W.yr.m-2.K-1
Csh_00=6.0
Cnh_00=6.0
#
# C0 = deep-ocean heat capacity in W.yr.m-2.K-1
C0_00=150.0
#
def cost(x):
   T_SRM_nh_GLOBE,T_SRM_nh_NH,T_SRM_nh_SH,T_SRM_nh_DELTA,aod_DELTA_nh,T_SRM_sh_GLOBE,T_SRM_sh_NH,T_SRM_sh_SH,T_SRM_sh_DELTA,aod_DELTA_sh=calibration(*x)
   total_cost =((T_SRM_nh_GLOBE-target_t_nh_GLOBE)**2.).sum()
   total_cost+=((T_SRM_sh_GLOBE-target_t_sh_GLOBE)**2.).sum()
   total_cost+=((T_SRM_nh_DELTA-target_t_nh_DIFF)**2.).sum()
   total_cost+=((T_SRM_sh_DELTA-target_t_sh_DIFF)**2.).sum()

   #total_cost =(T_SRM_nh_GLOBE[4]-target_t_nh_GLOBE.iloc[4])**2.
   #total_cost+=(T_SRM_nh_GLOBE[9]-target_t_nh_GLOBE.iloc[9])**2.
   #total_cost+=(T_SRM_sh_GLOBE[4]-target_t_sh_GLOBE.iloc[4])**2.
   #total_cost+=(T_SRM_sh_GLOBE[9]-target_t_sh_GLOBE.iloc[9])**2.
   #total_cost+=(T_SRM_nh_DELTA[4]-target_t_nh_DIFF.iloc[4])**2.
   #total_cost+=(T_SRM_nh_DELTA[9]-target_t_nh_DIFF.iloc[9])**2.
   #total_cost+=(T_SRM_sh_DELTA[4]-target_t_sh_DIFF.iloc[4])**2.
   #total_cost+=(T_SRM_sh_DELTA[9]-target_t_sh_DIFF.iloc[9])**2.

   return total_cost
# 
#---forward run to calibrate the model
#--all tunable parameters
#def calibration(lambdash,lambdanh,Csh,Cnh,C0,gamma,tau_nh_sh_upper,tau_nh_sh_lower):
#--only some tunale parameters
def calibration(lambdash,lambdanh,tau_nh_sh_upper,tau_nh_sh_lower):
  #
  gsh=np.zeros((t5))
  gnh=np.zeros((t5))
  #
  #--CASE INJECTION nh puis sh
  #--initialise more stuff
  T_SRM=[] ; T_SRM_SH=[] ; T_SRM_NH=[] ; g_SH=[] ; g_NH=[]
  TSRMsh=0 ; T0SRMsh=0 ; TSRMnh=0 ; T0SRMnh=0
  #
  gsh[0:dy]=0.0
  gnh[0:dy]=aod2rf(saod)
  gsh[dy:2*dy]=aod2rf(saod)
  gnh[dy:2*dy]=0.0
  #
  #--loop on time
  for t in range(t0,t5):
    #
    #TSRM, TSRMsh,TSRMnh,T0SRMsh,T0SRMnh = clim_sh_nh_from_rf_v2(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh[t],gnh[t],\
    #                                      f=0.0,lambdash=lambdash,lambdanh=lambdanh,Csh=Csh,Cnh=Cnh,C0=C0,gamma=gamma,Tsh_noise=0,Tnh_noise=0,\
    #                                      tau_nh_sh_upper=tau_nh_sh_upper,tau_nh_sh_lower=tau_nh_sh_lower)
    TSRM, TSRMsh,TSRMnh,T0SRMsh,T0SRMnh = clim_sh_nh_from_rf_v2(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh[t],gnh[t],\
                                          f=0.0,lambdash=lambdash,lambdanh=lambdanh,Csh=Csh_00,Cnh=Cnh_00,C0=C0_00,gamma=gamma_00,Tsh_noise=0,Tnh_noise=0,\
                                          tau_nh_sh_upper=tau_nh_sh_upper,tau_nh_sh_lower=tau_nh_sh_lower)
    T_SRM.append(TSRM) ; T_SRM_SH.append(TSRMsh) ; T_SRM_NH.append(TSRMnh)  ; g_SH.append(gsh[t]) ; g_NH.append(gnh[t])
  #
  #--save NH and SH means
  T_SRM_nh_SH=T_SRM_SH
  T_SRM_nh_NH=T_SRM_NH
  #--globe average 
  T_SRM_nh_GLOBE=[(x+y)/2. for x,y in zip(T_SRM_NH,T_SRM_SH)]
  #--interhemispheric difference in T
  T_SRM_nh_DELTA=[x-y for x,y in zip(T_SRM_NH,T_SRM_SH)]
  #--interhemispheric difference in AOD
  aod_DELTA_nh=[rf2aod(x)-rf2aod(y) for x,y in zip(g_NH,g_SH)]
  #
  #--CASE INJECTION sh puis nh
  #--initialise more stuff
  T_SRM=[] ; T_SRM_SH=[] ; T_SRM_NH=[] ; g_SH=[] ; g_NH=[]
  TSRMsh=0 ; T0SRMsh=0 ; TSRMnh=0 ; T0SRMnh=0
  #
  gsh[0:dy]=aod2rf(saod)
  gnh[0:dy]=0.0
  gsh[dy:2*dy]=0.0
  gnh[dy:2*dy]=aod2rf(saod)
  #
  #--loop on time
  for t in range(t0,t5):
    #
    #TSRM, TSRMsh,TSRMnh,T0SRMsh,T0SRMnh = clim_sh_nh_from_rf_v2(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh[t],gnh[t],\
    #                                      f=0.0,lambdash=lambdash,lambdanh=lambdanh,Csh=Csh,Cnh=Cnh,C0=C0,gamma=gamma,Tsh_noise=0,Tnh_noise=0,\
    #                                      tau_nh_sh_upper=tau_nh_sh_upper,tau_nh_sh_lower=tau_nh_sh_lower)
    TSRM, TSRMsh,TSRMnh,T0SRMsh,T0SRMnh = clim_sh_nh_from_rf_v2(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh[t],gnh[t],\
                                          f=0.0,lambdash=lambdash,lambdanh=lambdanh,Csh=Csh_00,Cnh=Cnh_00,C0=C0_00,gamma=gamma_00,Tsh_noise=0,Tnh_noise=0,\
                                          tau_nh_sh_upper=tau_nh_sh_upper,tau_nh_sh_lower=tau_nh_sh_lower)
    T_SRM.append(TSRM) ; T_SRM_SH.append(TSRMsh) ; T_SRM_NH.append(TSRMnh)  ; g_SH.append(gsh[t]) ; g_NH.append(gnh[t])
  #
  #--save NH and SH means
  T_SRM_sh_SH=T_SRM_SH
  T_SRM_sh_NH=T_SRM_NH
  #--globe average 
  T_SRM_sh_GLOBE=[(x+y)/2. for x,y in zip(T_SRM_NH,T_SRM_SH)]
  #--interhemispheric difference in T
  T_SRM_sh_DELTA=[x-y for x,y in zip(T_SRM_NH,T_SRM_SH)]
  #--interhemispheric difference in AOD
  aod_DELTA_sh=[rf2aod(x)-rf2aod(y) for x,y in zip(g_NH,g_SH)]
  #
  return T_SRM_nh_GLOBE,T_SRM_nh_NH,T_SRM_nh_SH,T_SRM_nh_DELTA,aod_DELTA_nh,T_SRM_sh_GLOBE,T_SRM_sh_NH,T_SRM_sh_SH,T_SRM_sh_DELTA,aod_DELTA_sh
#
#----MAIN--------------
#
#--all tunable parameters
#x0=[lambdash_00,lambdanh_00,Csh_00,Cnh_00,C0_00,gamma_00,tau_nh_sh_upper_00,tau_nh_sh_lower_00] #--initial conditions
#--only some tunable parameters
x0=[lambdash_00,lambdanh_00,tau_nh_sh_upper_00,tau_nh_sh_lower_00] #--initial conditions
#--call model once
T_SRM_nh_GLOBE,T_SRM_nh_NH,T_SRM_nh_SH,T_SRM_nh_DELTA,aod_DELTA_nh,T_SRM_sh_GLOBE,T_SRM_sh_NH,T_SRM_sh_SH,T_SRM_sh_DELTA,aod_DELTA_sh=calibration(*x0)
#
#--minimize cost function
#
print('INITIAL COST=',cost(x0))
#print('l_SH,l_NH,C_SH,C_NH,C0,gamma,tau_NH_SH_upper,tau_NH_SH_lower')
print('l_SH,l_NH,tau_NH_SH_upper,tau_NH_SH_lower')
print('x0=',x0)
#--all tunable parameters
bnds=((0.2,2.0),(0.2,2.0),(2,10),(2,10),(50,200),(0.5,2),(5,20),(5,100))
bnds=((None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None))
#--only some tunable parameters
bnds=((None,None),(None,None),(5,20),(10,200))
print('bounds=',bnds)
res=minimize(cost,x0,method=method,bounds=bnds,options={'disp':False})
x=res['x']
print('FINAL COST=',cost(x))
print('x=',x)
T_SRM_nh_GLOBE,T_SRM_nh_NH,T_SRM_nh_SH,T_SRM_nh_DELTA,aod_DELTA_nh,T_SRM_sh_GLOBE,T_SRM_sh_NH,T_SRM_sh_SH,T_SRM_sh_DELTA,aod_DELTA_sh=calibration(*x)

#
#--basic plot with results - nh first / NH
fig, ax1 = plt.subplots(figsize=(10,13))
title='nh first runs'
fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_nh1_NH_yr'].values,color='black')
ax1.plot(yrs,df['t_nh2_NH_yr'].values,color='black')
ax1.plot(yrs,df['t_nh3_NH_yr'].values,color='black')
ax1.plot(yrs,T_SRM_nh_NH,color='green')
ax2.plot(yrs,aod_DELTA_nh,color='blue')
ax1.set_xlim(0.5,10.5)
ax2.set_xlim(0.5,10.5)
ax1.set_xticks(range(1,11))
ax1.set_ylim(-2.5,0)
ax2.set_ylim(-0.5,0.5)
ax1.set_xlabel('Years',fontsize=15)
ax1.set_ylabel('$\Delta$T (NH) in °C',fontsize=15,color='black')
ax2.set_ylabel('$\Delta$SAOD (NH-SH)',fontsize=15,color='blue')
ax2.spines['right'].set_color('blue')
ax1.tick_params(axis='both', which='major', labelsize=13)
ax2.tick_params(axis='both', which='major', labelsize=13, colors='blue')
plt.savefig('compare_T_NH_nh.png',bbox_inches='tight')
plt.show()
#
#--basic plot with results - nh first / SH
fig, ax1 = plt.subplots(figsize=(10,13))
title='nh first runs'
fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_nh1_SH_yr'].values,color='black')
ax1.plot(yrs,df['t_nh2_SH_yr'].values,color='black')
ax1.plot(yrs,df['t_nh3_SH_yr'].values,color='black')
ax1.plot(yrs,T_SRM_nh_SH,color='green')
ax2.plot(yrs,aod_DELTA_nh,color='blue')
ax1.set_xlim(0.5,10.5)
ax2.set_xlim(0.5,10.5)
ax1.set_xticks(range(1,11))
ax1.set_ylim(-2.5,0.5)
ax2.set_ylim(-0.5,0.5)
ax1.set_xlabel('Years',fontsize=15)
ax1.set_ylabel('$\Delta$T (SH) in °C',fontsize=15,color='black')
ax2.set_ylabel('$\Delta$SAOD (NH-SH)',fontsize=15,color='blue')
ax2.spines['right'].set_color('blue')
ax1.tick_params(axis='both', which='major', labelsize=13)
ax2.tick_params(axis='both', which='major', labelsize=13, colors='blue')
plt.savefig('compare_T_SH_nh.png',bbox_inches='tight')
plt.show()
#
#--basic plot with results - nh first / GLOBE
fig, ax1 = plt.subplots(figsize=(10,13))
title='nh first runs'
fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_nh1_GLOBE_yr'].values,color='black')
ax1.plot(yrs,df['t_nh2_GLOBE_yr'].values,color='black')
ax1.plot(yrs,df['t_nh3_GLOBE_yr'].values,color='black')
ax1.plot(yrs,T_SRM_nh_GLOBE,color='green')
ax2.plot(yrs,aod_DELTA_nh,color='blue')
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
#--basic plot with results - nh first / DIFF
fig, ax1 = plt.subplots(figsize=(10,13))
title='nh first runs'
fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_nh1_DIFF_yr'].values,color='black')
ax1.plot(yrs,df['t_nh2_DIFF_yr'].values,color='black')
ax1.plot(yrs,df['t_nh3_DIFF_yr'].values,color='black')
ax1.plot(yrs,T_SRM_nh_DELTA,color='green')
ax2.plot(yrs,aod_DELTA_nh,color='blue')
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
#--basic plot with results - sh first / NH
fig, ax1 = plt.subplots(figsize=(10,13))
title='sh first runs'
fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_sh1_NH_yr'].values,color='black')
ax1.plot(yrs,df['t_sh2_NH_yr'].values,color='black')
ax1.plot(yrs,df['t_sh3_NH_yr'].values,color='black')
ax1.plot(yrs,T_SRM_sh_NH,color='green')
ax2.plot(yrs,aod_DELTA_sh,color='blue')
ax1.set_xlim(0.5,10.5)
ax2.set_xlim(0.5,10.5)
ax1.set_xticks(range(1,11))
ax1.set_ylim(-3,0)
ax2.set_ylim(-0.5,0.5)
ax1.set_xlabel('Years',fontsize=15)
ax1.set_ylabel('$\Delta$T (NH) in °C',fontsize=15,color='black')
ax2.set_ylabel('$\Delta$SAOD (NH-SH)',fontsize=15,color='blue')
ax2.spines['right'].set_color('blue')
ax1.tick_params(axis='both', which='major', labelsize=13)
ax2.tick_params(axis='both', which='major', labelsize=13, colors='blue')
plt.savefig('compare_T_NH_nh.png',bbox_inches='tight')
plt.show()
#
#--basic plot with results - sh first / SH
fig, ax1 = plt.subplots(figsize=(10,13))
title='sh first runs'
fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_sh1_SH_yr'].values,color='black')
ax1.plot(yrs,df['t_sh2_SH_yr'].values,color='black')
ax1.plot(yrs,df['t_sh3_SH_yr'].values,color='black')
ax1.plot(yrs,T_SRM_sh_SH,color='green')
ax2.plot(yrs,aod_DELTA_sh,color='blue')
ax1.set_xlim(0.5,10.5)
ax2.set_xlim(0.5,10.5)
ax1.set_xticks(range(1,11))
ax1.set_ylim(-2,0)
ax2.set_ylim(-0.5,0.5)
ax1.set_xlabel('Years',fontsize=15)
ax1.set_ylabel('$\Delta$T (SH) in °C',fontsize=15,color='black')
ax2.set_ylabel('$\Delta$SAOD (NH-SH)',fontsize=15,color='blue')
ax2.spines['right'].set_color('blue')
ax1.tick_params(axis='both', which='major', labelsize=13)
ax2.tick_params(axis='both', which='major', labelsize=13, colors='blue')
plt.savefig('compare_T_SH_nh.png',bbox_inches='tight')
plt.show()
#
#--basic plot with results - sh first / GLOBE
fig, ax1 = plt.subplots(figsize=(10,13))
title='sh first runs'
fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_sh1_GLOBE_yr'].values,color='black')
ax1.plot(yrs,df['t_sh2_GLOBE_yr'].values,color='black')
ax1.plot(yrs,df['t_sh3_GLOBE_yr'].values,color='black')
ax1.plot(yrs,T_SRM_sh_GLOBE,color='green')
ax2.plot(yrs,aod_DELTA_sh,color='blue')
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
plt.savefig('compare_T_GLOBE_sh.png',bbox_inches='tight')
plt.show()
#
#--basic plot with results - nh first / DIFF
fig, ax1 = plt.subplots(figsize=(10,13))
title='sh first runs'
fig.suptitle(title,fontsize=16)
ax2 = ax1.twinx()
ax1.plot([0.5,10.5],[0,0],linestyle='dashed',linewidth=1,color='black')
ax1.plot([5.5,5.5],[-2,2],linestyle='dashed',linewidth=1,color='black')
ax1.plot(yrs,df['t_sh1_DIFF_yr'].values,color='black')
ax1.plot(yrs,df['t_sh2_DIFF_yr'].values,color='black')
ax1.plot(yrs,df['t_sh3_DIFF_yr'].values,color='black')
ax1.plot(yrs,T_SRM_sh_DELTA,color='green')
ax2.plot(yrs,aod_DELTA_sh,color='blue')
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
plt.savefig('compare_T_DIFF_sh.png',bbox_inches='tight')
plt.show()
#
