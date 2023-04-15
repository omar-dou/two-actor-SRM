from simple_pid import PID
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
from myclim import clim

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
## parameters for actor A
#KpA=4.0 ; KiA=3.0 ; KdA=0.0 ; setpointA=0.0
#gAmin=-4 ; gAmax=0
#t1A=50 ; t2A=70 ; t3A=80 ; t4A=100
## parameters for actor B
#KpB=4.0 ; KiB=3.0 ; KdB=0.0 ; setpointB=0.5
#gBmin=-4 ; gBmax=0
#t1B=50 ; t2B=70 ; t3B=0 ; t4B=0
#fmax=3.0
#t0=0 ; t5=200
#noise=0.05

#--directory for plots
dirout='plots/'
pltshow=True

#--read input files
inputs=pd.read_csv('test2.csv',dtype={'t0':'Int32','t1A':'Int32','t2A':'Int32','t3A':'Int32','t4A':'Int32',\
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
  filename='test2'
  for key in row.keys()[:-1]:
    filename=filename+'_'+str(row[key])
  filename=filename+'.png'

  #--define pid for actor A
  pidA = PID(KpA, KiA, KdA, setpoint=setpointA)
  #--define pid for actor B 
  pidB = PID(KpB, KiB, KdB, setpoint=setpointB)
  
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
  T_SRM=[] ; gA_SRM=[] ; gB_SRM=[] ; T_noSRM=[]
  gA=0 ; gB=0 ; TnoSRM=0 ; T0noSRM=0 ; TSRM=0 ; T0SRM=0

  #--loop on time
  for t in range(t0,t5):
    #--reference calculation with no SRM 
    TnoSRM,T0noSRM=clim(TnoSRM,T0noSRM,f=f[t],g=0,noise=noise)
    T_noSRM.append(TnoSRM)
    #--calculation with SRM 
    #--setting limits on g 
    pidA.output_limits = (ggAmin[t], ggAmax[t])
    pidB.output_limits = (ggBmin[t], ggBmax[t])
    # feed the PID output to the system and get its current value
    TSRM,T0SRM=clim(TSRM,T0SRM,f=f[t],g=gA+gB,noise=noise)
    T_SRM.append(TSRM) ; gA_SRM.append(gA) ; gB_SRM.append(gB)
    # compute new ouput from the PID according to the systems current value
    # here A and B have no knowledge of what each other does
    gA = pidA(TSRM,dt=1)
    gB = pidB(TSRM,dt=1)
  #
  #--compute std of T
  print('std T after ramping up=',np.std(T_SRM[t2A:]))

  #--basic plot
  myformat="{0:3.1f}"
  title='Controlling global SAI intervention with two actors A and B\n'
  title=title+'Kp A='+myformat.format(KpA)+' Ki A='+myformat.format(KiA)+' Kd A='+myformat.format(KdA)+' setpoint A='+myformat.format(setpointA)+'°C\n'
  title=title+'Kp B='+myformat.format(KpB)+' Ki B='+myformat.format(KiB)+' Kd B='+myformat.format(KdB)+' setpoint B='+myformat.format(setpointB)+'°C\n'
  title=title+'gAmin='+myformat.format(gAmin)+' gAmax='+myformat.format(gAmax)+' gBmin='+myformat.format(gBmin)+' gBmax='+myformat.format(gBmax)+'\n'
  title=title+'Timings= '+str(t0)+' / '+str(t3A)+' '+str(t4A)+' / '+str(t3B)+' '+str(t4B)
  plt.title(title,fontsize=8)
  plt.plot([t0,t5],[0,0],zorder=0,c='black',linewidth=0.4)
  plt.plot([t1A,t1A],[-4,4],zorder=0,c='black',linewidth=0.4)
  plt.plot([t1B,t1B],[-4,4],zorder=0,c='black',linewidth=0.4)
  plt.plot([t2A,t2A],[-4,4],zorder=0,c='black',linewidth=0.4)
  plt.plot([t2B,t2B],[-4,4],zorder=0,c='black',linewidth=0.4)
  plt.plot(f,label='GHG forcing',c='red',linestyle='solid')
  plt.plot(gA_SRM,label='SAI forcing actor A',c='blue',linestyle='solid')
  plt.plot(gB_SRM,label='SAI forcing actor B',c='purple',linestyle='solid')
  plt.plot(T_noSRM,label='dT w/o SRM',c='orange',linestyle='solid')
  plt.plot(T_SRM,label='dT w SRM',c='green')
  plt.legend(loc='upper left',fontsize=8)
  plt.xlabel('Years',fontsize=12)
  plt.ylabel('T change ($^\circ$C) / RF (Wm$^{-2}$)',fontsize=12)
  plt.xlim(t0,t5)
  plt.ylim(-4,4)
  plt.show()
  plt.savefig(dirout+filename)
