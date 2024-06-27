from simple_pid import PID
import matplotlib.pyplot as plt
import colorednoise as cn
import numpy as np
import random
import argparse
import sys
import os
from myclim import clim_sh_nh, initialise_aod_responses, emi2aod, emi2rf, Monsoon, Monsoon_IPSL
from matplotlib.widgets import Button
from matplotlib.figure import Figure
import streamlit as st
import numpy as np


#--call script as: python test.py --exp=4 --noise=mixed

parser = argparse.ArgumentParser()
parser.add_argument('--exp', type=str, default='4a', help='experiment number')
parser.add_argument('--noise', type=str, default='mixed', choices=['white','red','mixed'],help='Noise type')
args = parser.parse_args()
exp=args.exp
noise_type=args.noise

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
#--t1: start of ramping up SRM intervention
#--t2: end of ramping up SRM intervention
#--t5: time of end of SRM intervention (in years)
#--stops: periods of SRM interruption, list of tuples (t3,t4) and targets exceeded
#--fmax: max value for GHG forcing (Wm-2)
#--noise: noise level for T0 (in K)

#--directory for plots
dirout='plots/'
if not os.path.exists(dirout): os.makedirs(dirout)
#--show plots while running
pltshow=True
#--period 
t0=0 ; t5=200
#--volcano
volcano=True
#--max GHG forcing
fmax=4.0
#--noise level
noise_T=0.15       #--in K
noise_monsoon=5.   #--in % change
#noise_monsoon=1.  #--in % change
#--interhemispheric timescales (in years)
tau_nh_sh_upper=20.
tau_nh_sh_lower=20.
#
#--List of experiments with list of actors, type of setpoint, setpoint, emissions min/max and emission points
#--single actor in NH emitting in his own hemisphere

def setup_actor1(types, emipoints):
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':types,'setpoint': 0.0, 'emimin':0.0,'emimax':10.0,'emipoints':emipoints,'t1':50,'t2':70,'stops':[]}
  P={'A':A}
  # if 'D' in vars(): P['D']=D 

  return P

def setup_actor2(types1, emipoints1, types2, 
emipoints2):
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':types1,'setpoint': 0.0, 'emimin':0.0,'emimax':10.0,'emipoints':emipoints1,'t1':50,'t2':70,'stops':[]}
  B={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':types2,'setpoint': 0.0, 'emimin':0.0,'emimax':10.0,'emipoints':emipoints2,'t1':50,'t2':70,'stops':[]}
  P={'A':A}
  if 'B' in vars(): P['B']=B
  return P
def setup_actor3(types1, emipoints1, types2, emipoints2, types3, emipoints3):
  A={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':types1,'setpoint': 0.0, 'emimin':0.0,'emimax':10.0,'emipoints':emipoints1,'t1':50,'t2':70,'stops':[]}
  B={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':types2,'setpoint': 0.0, 'emimin':0.0,'emimax':10.0,'emipoints':emipoints2,'t1':50,'t2':70,'stops':[]}
  C={'Kp':0.8, 'Ki':0.6, 'Kd':0.0,'type':types3,'setpoint': 0.0, 'emimin':0.0,'emimax':10.0,'emipoints':emipoints3,'t1':50,'t2':70,'stops':[]}
  P={'A':A}
  if 'B' in vars(): P['B']=B
  if 'C' in vars(): P['C']=C
  return P

  # else: 
  #   sys.exit('This scenario is not parametrized')
  #
  #--Initialise properties of Actors
def setup_plots(P):
  global Actors, title
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
  global T_SRM_sh, T_SRM_nh, g_SRM_nh, g_SRM_sh, filename, monsoon_noSRM, monsoon_SRM, T_noSRM_sh, T_noSRM_sh, monsoon_noise, Tsh_noise, Tnh_noise, f, emi_SRM, colors, markers, sizes, emissmin, T_noSRM_nh
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
    t1=P[Actor]['t1'] ; t2=P[Actor]['t2'] ; stops=P[Actor]['stops']
    emissmin[Actor]=np.zeros((t5))
    emissmax[Actor]=np.zeros((t5))
    emissmin[Actor][t1:t2]=np.linspace(0.0,emimin,t2-t1)
    emissmax[Actor][t1:t2]=np.linspace(0.0,emimax,t2-t1)
    emissmin[Actor][t2:]=emimin
    emissmax[Actor][t2:]=emimax
    for stop in stops:
      if type(stop)==type(()):
        t3=stop[0] ; t4=stop[1]
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
  st.write(f"t0, t5: {t0}, {t5}" )

  for t in range(t0,t5):
    #
    #--reference calculation with no SRM 
    #-----------------------------------
    TnoSRM, TnoSRMsh,TnoSRMnh,T0noSRMsh,T0noSRMnh,gsh,gnh = clim_sh_nh(TnoSRMsh,TnoSRMnh,T0noSRMsh,T0noSRMnh,{},aod_strat_sh,aod_strat_nh,nbyr_irf,\
                                                                      f=f[t],Tsh_noise=Tsh_noise[t],Tnh_noise=Tnh_noise[t], \
                                                                      tau_nh_sh_upper=tau_nh_sh_upper,tau_nh_sh_lower=tau_nh_sh_lower)
    T_noSRM.append(TnoSRM) ; T_noSRM_sh.append(TnoSRMsh) ; T_noSRM_nh.append(TnoSRMnh) 
    ##monsoon=Monsoon(0.0,0.0,noise=monsoon_noise[t]) ; monsoon_noSRM.append(monsoon)
    monsoon=Monsoon_IPSL(0.0,0.0,0.0,0.0,noise=monsoon_noise[t]) ; monsoon_noSRM.append(monsoon)
    #
    #--calculation with SRM
    #----------------------
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
    #--iterate climate model with emits as input
    TSRM, TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,gsh,gnh = clim_sh_nh(TSRMsh,TSRMnh,T0SRMsh,T0SRMnh,emits,aod_strat_sh,aod_strat_nh,nbyr_irf,\
                                                            f=f[t],Tsh_noise=Tsh_noise[t],Tnh_noise=Tnh_noise[t])
    #
    #--compute monsoon change
    ##monsoon=Monsoon(*emi2aod(emits,aod_strat_sh,aod_strat_nh,nbyr_irf),noise=monsoon_noise[t])
    monsoon=Monsoon_IPSL(*emi2aod(emits,aod_strat_sh,aod_strat_nh,nbyr_irf),TSRMsh,TSRMnh,noise=monsoon_noise[t])
    #
    #--report climate model output into lists for plots
    T_SRM.append(TSRM) ; T_SRM_sh.append(TSRMsh) ; T_SRM_nh.append(TSRMnh) ; g_SRM_sh.append(gsh) ; g_SRM_nh.append(gnh) ; monsoon_SRM.append(monsoon)
    #
    # compute new ouput from the PID according to the systems current value
    #--loop on emission points of Actor
    for Actor in Actors:
      #--check for additional interactive stops
      stops=[stop for stop in P[Actor]['stops'] if type(stop)==type(0.0)]
      #--loop on emission points
      for emipoint in P[Actor]['emipoints']:
        #--checking for additional interactive limits if target is overshoot => 5-yr stop in SRM
        for stop in stops: 
            if t > t1:
                if P[Actor]['type']=='GMST' and TSRM <= stop: 
                    emissmin[Actor][t:t+5]=0.0 ; emissmax[Actor][t:t+5]=0.0
                if P[Actor]['type']=='NHST' and TSRMnh <= stop: 
                    emissmin[Actor][t:t+5]=0.0 ; emissmax[Actor][t:t+5]=0.0
                if P[Actor]['type']=='SHST' and TSRMsh <= stop: 
                    emissmin[Actor][t:t+5]=0.0 ; emissmax[Actor][t:t+5]=0.0
                if P[Actor]['type']=='monsoon' and monsoon >= -1*stop: 
                    emissmin[Actor][t:t+5]=0.0 ; emissmax[Actor][t:t+5]=0.0 
        #--setting limits on emissions for each Actor's PID
        PIDs[Actor][emipoint].output_limits = (emissmin[Actor][t],emissmax[Actor][t])
        #--append the emission arrays
        if P[Actor]['type']=='GMST':
            emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](TSRM+TSRM_noise_obs[t],dt=1))
        if P[Actor]['type']=='NHST':
            emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](TSRMnh+TSRMnh_noise_obs[t],dt=1))
        if P[Actor]['type']=='SHST':
            emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](TSRMsh+TSRMsh_noise_obs[t],dt=1))
        if P[Actor]['type']=='monsoon':
            emi_SRM[Actor][emipoint].append(PIDs[Actor][emipoint](-1*monsoon+monsoon_noise_obs[t],dt=1))
  st.write(f"emi_SRM: {emi_SRM[Actor][emipoint]}" )
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
  title ='Controlling global SAI'+title

# Function to create the first plot
def graph1():
    fig, ax = plt.subplots(figsize=(11,6.5))
    fig.suptitle(title, fontsize=16)
    ax.plot([t0, t5], [0, 0], zorder=0, linewidth=0.4)
    ax.plot(f, label='GHG RF', c='red')
    ax.legend(loc='upper left', fontsize=12)
    ax.set_ylabel('RF (Wm$^{-2}$)', fontsize=14)
    ax.set_xlim(t0, t5)
    ax.set_xticks(np.arange(t0, t5+1, 25))
    ax.tick_params(size=14)
    fig.tight_layout()
    fig.savefig(dirout + 'graph1_' + filename)
    return fig

# Function to create the second plot
def graph2():
    fig, ax = plt.subplots(figsize=(11,6.5))
    fig.suptitle(title, fontsize=16)
    ax.plot([t0, t5], [0, 0], zorder=0, linewidth=0.4)
    ax.plot(Tnh_noise, label='NHST noise', c='black')
    ax.plot(Tsh_noise, label='SHST noise', c='green')
    ax.plot(monsoon_noise / 100., label='Monsoon noise', c='red')
    ax.legend(loc='lower right', fontsize=12)
    ax.set_ylabel('Noise level', fontsize=14)
    ax.set_xlim(t0, t5)
    ax.set_xticks(np.arange(t0, t5+1, 25))
    ax.tick_params(size=14)
    fig.tight_layout()
    fig.savefig(dirout + 'graph2_' + filename)
    return fig

# Function to create the third plot
def graph3(P):
    fig, ax = plt.subplots(figsize=(11,6.5))
    fig.suptitle(title, fontsize=16)
    for Actor in Actors:
        for emipoint in P[Actor]['emipoints']:
            ax.plot(emi_SRM[Actor][emipoint], linestyle='solid', c=colors[Actor])
            ax.scatter(range(t0, t5+1, 10), emi_SRM[Actor][emipoint][::10], label='Emissions '+Actor+' '+emipoint, c=colors[Actor], marker=markers[emipoint], s=sizes[emipoint])
            ax.plot(-1 * emissmin[Actor], linestyle='dashed', linewidth=0.5, c=colors[Actor])
    ax.legend(loc='upper left', fontsize=12)
    ax.set_ylabel('Emi (TgS yr$^{-1}$)', fontsize=14)
    ax.set_xlim(t0, t5)
    ax.set_xticks(np.arange(t0, t5+1, 25))
    ax.tick_params(size=14)
    fig.tight_layout()
    fig.savefig(dirout + 'graph3_' + filename)
    return fig

# Function to create the fourth plot
def graph4():
    fig, ax = plt.subplots(figsize=(11,6.5))
    fig.suptitle(title, fontsize=16)
    ax.plot(g_SRM_nh, label='NH SRM g', c='blue')
    ax.plot(g_SRM_sh, label='SH SRM g', c='blue', linestyle='dashed')
    ax.legend(loc='upper left', fontsize=12)
    ax.set_ylabel('RF SRM (Wm$^{-2}$)', fontsize=14)
    ax.set_xlim(t0, t5)
    ax.set_xticks(np.arange(t0, t5+1, 25))
    ax.tick_params(size=14)
    fig.tight_layout()
    fig.savefig(dirout + 'graph4_' + filename)
    return fig

# Function to create the fifth plot
def graph5():
    fig, ax = plt.subplots(figsize=(11,6.5))
    fig.suptitle(title, fontsize=16)
    ax.plot(T_noSRM_nh, label='NH dT w/o SRM', c='red', zorder=100)
    ax.plot(T_noSRM_sh, label='SH dT w/o SRM', c='red', linestyle='dashed', zorder=100)
    ax.plot(T_SRM_nh, label='NH dT w SRM', c='blue', zorder=0)
    ax.plot(T_SRM_sh, label='SH dT w SRM', c='blue', linestyle='dashed', zorder=0)
    ax.plot([t0, t5], [0, 0], c='black', linewidth=0.5)
    ax.legend(loc='upper left', fontsize=12)
    ax.set_xlabel('Years', fontsize=14)
    ax.set_ylabel('Temp. ($^\circ$C)', fontsize=14)
    ax.set_xlim(t0, t5)
    ax.set_xticks(np.arange(t0, t5+1, 25))
    ax.tick_params(size=14)
    fig.tight_layout()
    fig.savefig(dirout + 'graph5_' + filename)
    return fig

# Function to create the sixth plot
def graph6():
    fig, ax = plt.subplots(figsize=(11,6.5))
    fig.suptitle(title, fontsize=16)
    ax.plot(monsoon_noSRM, label='monsoon w/o SRM', c='red', zorder=100)
    ax.plot(monsoon_SRM, label='monsoon w SRM', c='blue', zorder=0)
    ax.plot([t0, t5], [0, 0], c='black', linewidth=0.5)
    ax.legend(loc='lower left', fontsize=12)
    ax.set_xlabel('Years', fontsize=14)
    ax.set_ylabel('Monsoon (%)', fontsize=14)
    ax.set_xlim(t0, t5)
    ax.set_xticks(np.arange(t0, t5+1, 25))
    ax.tick_params(size=14)
    fig.tight_layout()
    fig.savefig(dirout + 'graph6_' + filename)
    return fig
#
# graph6()
#graph3()
# fig1 = graph1()
# fig1.tight_layout()
# fig1.savefig(dirout+filename)
# #print(graph6())
# if pltshow: plt.show()