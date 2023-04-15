from simple_pid import PID
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
from myclim import clim

#--initialise PID controller
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

#--example of input parameters
#Kp=4.0 ; Ki=3.0 ; Kd=0.0 ; setpoint=0.5
#gmin=-4 ; gmax=0
#t0=0 ; t1=50 ; t2=70 ; t3=80 ; t4=100 ; t5=200
#fmax=3. 
#noise=0.05

#--directory for plots
dirout='plots/'
pltshow=True

#--read input files
inputs=pd.read_csv('test1.csv',dtype={'t0':'Int32','t1':'Int32','t2':'Int32','t3':'Int32','t4':'Int32','t5':'Int32'})

for index,row in inputs.iterrows():
  Kp=row['Kp']
  Ki=row['Ki']
  Kd=row['Kd']
  setpoint=row['setpoint']
  gmin=row['gmin']
  gmax=row['gmax']
  t0=row['t0']
  t1=row['t1']
  t2=row['t2']
  t3=row['t3']
  t4=row['t4']
  t5=row['t5']
  fmax=row['fmax']
  noise=row['noise']

  #--filename
  filename='test1'
  for key in row.keys()[:-1]:
    filename=filename+'_'+str(row[key])
  filename=filename+'.png'

  #--GHG forcing scenario, increases linearly for 100 yrs then constant then decrease slowly
  f=np.zeros((t5))
  f[0:100]=np.linspace(0.,fmax,100)
  f[100:150]=fmax
  f[130]=fmax-1.5  #--volcano
  f[131]=fmax-0.8  #--volcano
  f[150:]=np.linspace(fmax,3*fmax/4,50)

  #--define pid
  pid = PID(Kp, Ki, Kd, setpoint=setpoint)

  #--define scenarios of bounds of SRM intervention
  ggmin=np.zeros((t5))
  ggmax=np.zeros((t5))
  ggmin[t1:t2]=np.linspace(0.,gmin,t2-t1)
  ggmax[t1:t2]=np.linspace(0.,gmax,t2-t1)
  ggmin[t2:]=gmin
  ggmax[t2:]=gmax
  ggmin[t3:t4]=0
  ggmax[t3:t4]=0

  #--initialise stuff
  T_SRM=[] ; g_SRM=[] ; T_noSRM=[]
  g=0 ; TnoSRM=0 ; T0noSRM=0 ; TSRM=0 ; T0SRM=0

  #--loop on time
  for t in range(t0,t5):
    #--reference calculation with no SRM 
    TnoSRM,T0noSRM=clim(TnoSRM,T0noSRM,f=f[t],g=0,noise=noise)
    T_noSRM.append(TnoSRM)
    #--calculation with SRM 
    #--setting limits on g 
    pid.output_limits = (ggmin[t], ggmax[t])
    # feed the PID output to the system and get its current value
    TSRM,T0SRM=clim(TSRM,T0SRM,f=f[t],g=g,noise=noise)
    T_SRM.append(TSRM) ; g_SRM.append(g)
    # compute new ouput from the PID according to the systems current value
    g = pid(TSRM,dt=1)
  #
  
  #--compute std of T
  print('std T after ramping up=',np.std(T_SRM[t2:]))

  #--basic plot
  myfloat="{0:3.1f}"
  myint="{0:3d}"
  title='Controlling global SAI intervention\n'
  title=title+'Kp='+myfloat.format(Kp)+' Ki='+myfloat.format(Ki)+' Kd='+myfloat.format(Kd)+' setpoint='+myfloat.format(setpoint)+'\n'
  title=title+'Ramp up='+myint.format(t1)+' to'+myint.format(t2)+' Interruption='+myint.format(t3)+' to '+myint.format(t4)
  plt.title(title,fontsize=10)
  plt.plot([t0,t5],[0,0],zorder=0,c='black',linewidth=0.4)
  plt.plot([t1,t1],[-4,4],zorder=0,c='black',linewidth=0.4)
  plt.plot([t2,t2],[-4,4],zorder=0,c='black',linewidth=0.4)
  plt.plot([t3,t3],[-4,4],zorder=0,c='black',linewidth=0.4)
  plt.plot([t4,t4],[-4,4],zorder=0,c='black',linewidth=0.4)
  plt.plot(f,label='GHG forcing',c='red',linestyle='solid')
  plt.plot(g_SRM,label='SAI forcing',c='blue',linestyle='solid')
  plt.plot(T_noSRM,label='dT w/o SRM',c='orange',linestyle='solid')
  plt.plot(T_SRM,label='dT w SRM',c='green',linestyle='solid')
  plt.legend(loc='upper left',fontsize=8)
  plt.xlabel('Years',fontsize=12)
  plt.ylabel('T change ($^\circ$C) / RF (Wm$^{-2}$)',fontsize=12)
  plt.xlim(t0,t5)
  plt.ylim(-4,4)
  if pltshow: plt.show()
  plt.savefig(dirout+filename)
