README two-actor-SRM

we use python3 on spirit

https://pypi.org/project/simple-pid/
pip install simple-pid

test.py  = simple test of the climate model and 1 or 2 global actors for SRM

MacMartin et al. 2014 
High gain Kp=1.2 %solar/°C   Ki=1.8 %solar/°C/yr
Low  gain Kp=0.6 %solar/°C   Ki=0.9 %solar/°C/yr 

1 %solar = 0.01 * 1370 / 4 * 0.7 = 2.4 Wm-2
High gain ==> Kp = 2.88 Wm-2/°C  et Ki = 4.32 Wm-2/°C/yr
Low gain  ==> Kp = 1.44 Wm-2/°C  et Ki = 2.16 Wm-2/°C/yr

We take typically Kp=4 Wm-2/°C and Ki=3 Wm-2/°C/yr
2°C <=> 3 Wm-2 <=> 10 TgS/yr 
It can be translated for emissions in Tg S : Kp=0.8 (TgS/yr)/°C and Ki=0.6 (TgS/yr)/°C/yr

<=> 10% monsoon change

and Kp=0.8 (TgS/yr)/% monsoon and Ki=0.6 (TgS/yr)/%/yr

precip change [%] = -78.6*(AOD_NH-AOD_SH)-10.6 
