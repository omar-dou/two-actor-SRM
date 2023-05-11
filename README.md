README two-actor-SRM

we use python3 on spirit

module load python/3.6-anaconda50
conda create --name mypython36 python=3.6 -y
source activate mypython36

https://pypi.org/project/simple-pid/
pip install simple-pid

test.py  = simple test of the climate model and 2 global actor for SRM

MacMartin et al. 2014 
High gain Kp=1.2 %solar/°C   Ki=1.8 %solar/°C/yr
Low  gain Kp=0.6 %solar/°C   Ki=0.9 %solar/°C/yr 

1 %solar = 0.01 * 1370 / 4 * 0.7 = 2.4 Wm-2
High gain ==> Kp = 2.88 Wm-2/°C  et Ki = 4.32 Wm-2/°C/yr
Low gain  ==> Kp = 1.44 Wm-2/°C  et Ki = 2.16 Wm-2/°C/yr

We take typically Kp=4 Wm-2/°C and Ki=3 Wm-2/°C/yr
It can be translated for emissions in Tg S : Kp=0.8 Wm-2/TgS Ki=0.6 Wm-2/TgS/yr

monsoons change
precip change [%] = -78.6*(AOD_NH-AOD_SH)-10.6 
ie 10 TgS => AOD=0.1 => 10% change
Kp = 1 %/TgS    Ki = 1 %/TgS/yr
