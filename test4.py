from simple_pid import PID
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
from myclim import clim, clim_nh_sh
from scipy.optimize import curve_fit

#--initialise PID controller for each actor A and B
#--PID(Kp, Ki, Kd, setpoint)
#--Kp: proportional gain 
#--Ki: integral gain
#--Kd: derivative gain
#--setpoint: objective (temperature change in K)
#--gmin, gmax: bounds of SRM forcing
#--t0= start of model integration (in years)
#--t1: start of ramping up SRM intervention
#--t2: end of ramping up SRM intervention
#--t3-t4: period of SRM interruption (use 0 and 0 not to stop)
#--t5= time of end of SRM intervention (in years)
#--fmax: max value for GHG forcing (Wm-2)
#--noise: noise level for T0 (in K)

#--example of inputs
## parameters for actor A : aims to setpointA for Tnh
#KpA=4.0 ; KiA=3.0 ; KdA=0.0 ; setpointA=0.0
#gAmin=-4 ; gAmax=0
#t1A=50 ; t2A=70 ; t3A=80 ; t4A=100
## parameters for actor B : aims to setpointB for Tsh-Tnh
#KpB=4.0 ; KiB=3.0 ; KdB=0.0 ; setpointB=-1.0
#gBmin=-4 ; gBmax=0
#t1B=50 ; t2B=70 ; t3B=0 ; t4B=0
#fmax=3.
#t0=0 ; t5=200
#noise=0.05

#--directory for plots
dirout='plots/'
pltshow=True

#--fit pulse with exp decay
#ab,cov=curve_fit(expdecay,years,modeldt)
#a=ab[0] ; b=ab[1]

#--read input files
inputs=pd.read_csv('test3.csv',dtype={'t0':'Int32','t1A':'Int32','t2A':'Int32','t3A':'Int32','t4A':'Int32',\
                                      't1B':'Int32','t2B':'Int32','t3B':'Int32','t4B':'Int32','t5':'Int32'})

for index,row in inputs.iterrows():

  KpA=row['KpA'] ; KpB=row['KpB']
  KiA=row['KiA'] ; KiB=row['KiB']
  KdA=row['KdA'] ; KdB=row['KdB']
  setpointA=row['setpointA'] ; setpointB=row['setpointB']
  gAmin=row['gAmin'] ; gBmin=row['gBmin']
  gAmax=row['gAmax'] ; gBmax=row['gBmax']
  t0=row['t0']
  t1A=row['t1A'] ; t1B=row['t1B']
  t2A=row['t2A'] ; t2B=row['t2B']
  t3A=row['t3A'] ; t3B=row['t3B']
  t4A=row['t4A'] ; t4B=row['t4B']
  t5=row['t5']
  fmax=row['fmax']
  noise=row['noise']
  
  #--filename
  filename='test3'
  for key in row.keys():
    filename=filename+'_'+str(row[key])
  filename=filename+'.png'

  #--define pid for actor A
  pidA_nh = PID(KpA, KiA, KdA, setpoint=setpointA)
  pidA_sh = PID(KpA, KiA, KdA, setpoint=setpointA)
  #--define pid for actor B 
  #pidB_nh = PID(KpB, KiB, KdB, setpoint=0)
  #pidB_sh = PID(KpB, KiB, KdB, setpoint=setpointB)
  pidB_diff = PID(KpB, KiB, KdB, setpoint=setpointB)

  #--GHG forcing scenario, increases linearly for 100 yrs then constant then decrease slowly
  f=np.zeros((t5))
  f[0:100]=np.linspace(0.,fmax,100)
  f[100:150]=fmax
  f[150:]=np.linspace(fmax,3*fmax/4,50)

  #--define scenarios of bounds of SRM intervention
  #--Actor A
  ggAmin=np.zeros((t5))
  ggAmax=np.zeros((t5))
  ggAmin[t1A:t2A]=np.linspace(0.,gAmin,t2A-t1A)
  ggAmax[t1A:t2A]=np.linspace(0.,gAmax,t2A-t1A)
  ggAmin[t2A:]=gAmin
  ggAmax[t2A:]=gAmax
  ggAmin[t3A:t4A]=0
  ggAmax[t3A:t4A]=0
  #--Actor B
  ggBmin=np.zeros((t5))
  ggBmax=np.zeros((t5))
  ggBmin[t1B:t2B]=np.linspace(0.,gBmin,t2B-t1B)
  ggBmax[t1B:t2B]=np.linspace(0.,gBmax,t2B-t1B)
  ggBmin[t2B:]=gBmin
  ggBmax[t2B:]=gBmax
  ggBmin[t3B:t4B]=0
  ggBmax[t3B:t4B]=0

  #--initialise stuff
  T_SRM_nh=[] ; T_SRM_sh=[] ; T_noSRM_nh=[] ; T_noSRM_sh=[]
  gA_SRM_nh=[] ; gA_SRM_sh=[] ; gB_SRM_nh=[] ; gB_SRM_sh=[]
  TnoSRMnh=0 ; T0noSRMnh=0 ; TnoSRMsh=0 ; T0noSRMsh=0
  TSRMnh=0 ; T0SRMnh=0 ; TSRMsh=0 ; T0SRMsh=0
  gA_nh=0 ; gA_sh=0 ; gB_nh=0 ; gB_sh=0

  #--loop on time
  for t in range(t0,t5):
    #
    #--reference calculation with no SRM 
    TnoSRMnh,TnoSRMsh,T0noSRMnh,T0noSRMsh=clim_nh_sh(TnoSRMnh,TnoSRMsh,T0noSRMnh,T0noSRMsh,f=f[t],gnh=0,gsh=0,noise=noise)
    T_noSRM_nh.append(TnoSRMnh) ; T_noSRM_sh.append(TnoSRMsh)
    #--calculation with SRM
    #--setting limits on g
    pidA_nh.output_limits = (ggAmin[t], ggAmax[t])
    pidA_sh.output_limits = (ggAmin[t], ggAmax[t])
    ##pidB_nh.output_limits = (ggBmin[t], ggBmax[t])
    ##pidB_sh.output_limits = (ggBmin[t], ggBmax[t])
    pidB_diff.output_limits = (ggBmin[t], ggBmax[t])
    #--A injects in NH, B injects in NH and SH
    #TSRMnh,TSRMsh,T0SRMnh,T0SRMsh=clim_nh_sh(TSRMnh,TSRMsh,T0SRMnh,T0SRMsh,f=f[t],gnh=gA,gsh=gB,noise=noise)
    #--A injects in both NH & SH, B injects in NH and SH
    TSRMnh,TSRMsh,T0SRMnh,T0SRMsh=clim_nh_sh(TSRMnh,TSRMsh,T0SRMnh,T0SRMsh,f=f[t],gnh=gA_nh,gsh=gA_sh+gB_sh,noise=noise)
    #--report T and RF into lists for plots
    T_SRM_nh.append(TSRMnh) ; T_SRM_sh.append(TSRMsh)
    gA_SRM_nh.append(gA_nh) ; gA_SRM_sh.append(gA_sh)
    gB_SRM_nh.append(gB_nh) ; gB_SRM_sh.append(gB_sh)
    # compute new ouput from the PID according to the systems current value
    # here A and B have no knowledge of what each other does
    # note: the pid needs to be Tsh-Tnh and not the other way around because decrease in input must lead to decrease in output
    gA_nh = pidA_nh(TSRMnh,dt=1)
    gA_sh = pidA_sh(TSRMsh,dt=1)
    ##gB_nh = pidB_nh(TSRMnh,dt=1)
    ##gB_sh = pidB_sh(TSRMsh-TSRMnh,dt=1)
    gB_sh = pidB_diff(TSRMsh-TSRMnh,dt=1)
  #
  #--basic plot
  myformat="{0:3.1f}"
  title='Controlling global SAI intervention with two actors A and B\n'
  title=title+'Kp A='+myformat.format(KpA)+' Ki A='+myformat.format(KiA)+' Kd A='+myformat.format(KdA)+' setpoint A='+myformat.format(setpointA)+'°C\n'
  title=title+'Kp B='+myformat.format(KpB)+' Ki B='+myformat.format(KiB)+' Kd B='+myformat.format(KdB)+' setpoint B='+myformat.format(setpointB)+'°C\n'
  title=title+'gAmin='+myformat.format(gAmin)+' gAmax='+myformat.format(gAmax)+' gBmin='+myformat.format(gBmin)+' gBmax='+myformat.format(gBmax)
  plt.title(title,fontsize=10)
  plt.plot([t0,t5],[0,0],zorder=0,linewidth=0.4)
  plt.plot(f,label='GHG RF',c='red')
  plt.plot(gA_SRM_nh,label='SAI RF actor A',c='blue')
  plt.plot(gA_SRM_sh,label='SAI RF actor A',c='blue',linestyle='dashed')
  plt.plot(gB_SRM_nh,label='SAI RF actor B',c='purple')
  plt.plot(gB_SRM_sh,label='SAI RF actor B',c='purple',linestyle='dashed')
  plt.plot(T_noSRM_nh,label='NH dT w/o SRM',c='darkorange')
  plt.plot(T_noSRM_sh,label='SH dT w/o SRM',c='darkorange',linestyle='dashed')
  plt.plot(T_SRM_nh,label='NH dT w SRM',c='darkgreen')
  plt.plot(T_SRM_sh,label='SH dT w SRM',c='darkgreen',linestyle='dashed')
  plt.legend(loc='upper left',fontsize=8)
  plt.xlabel('Years',fontsize=14)
  plt.ylabel('T change ($^\circ$C) / RF (Wm$^{-2}$)',fontsize=14)
  plt.xlim(t0,t5)
  plt.ylim(-4,4)
  plt.show()
  plt.savefig(dirout+filename)
