# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 00:58:19 2021

@author: praf_Malla@hotmail.com, Nepal
"""
# Reference M.Scott "Development of Bridge Rating Applications Using OpenSees and Tcl"
#  Units in kip, ft, sec
inch =1 ; ft =12. *inch
ksi = 1; kip = 1;
L = 40*ft
P = 1*kip

E = 4000*ksi
G = 2400*ksi
b = 18*inch 
d = 36*inch
A = b*d 
I = b*d**3/12

import numpy as np
import matplotlib.pyplot as plt
import openseespy.opensees as ops

ops.wipe()
ops.model('basic','-ndm',2,'-ndf',3)

ops.node(1,0,0); ops.fix(1,1,1,0)
ops.node(2,L,0); ops.fix(2,0,1,0)
 
ops.geomTransf('Linear',1)
 
ops.section('Elastic',1,E,A,I,G,5/6)

#ops.beamIntegration('Lobatto',1,1,7)
Criticallocs = [0.1, 0.3, 0.5, 0.7, 0.9]
wts = [0.2, 0.15, 0.3, 0.15, 0.2]
secs = [1, 1, 1, 1, 1]
nIP = len(Criticallocs)                 # no of integration point or critical locations

ops.beamIntegration(' UserDefined',1,len(secs),*secs,*Criticallocs,*wts)
 
ops.element('forceBeamColumn',1,1,2,1,1)
ops.analysis('Static')

ops.timeSeries('Constant',1)

Nsteps = 1000
bM=np.zeros( (Nsteps, nIP+1) )  # Initial variable to store data
sF=np.zeros( (Nsteps, nIP+1) )  # Initial variable to store data

# Type of Truck, specify axle spacing and axle weight
#AxleSpacing =[0,120,48,252,48,72,122,48]; 
#AxleWeight = [12,29.49,29.49,29.49,29.49,29.49,29.49,29.49];
AxleSpacing =[0,48,48]; 
AxleWeight = [15.49,29.49,29.49]
Naxle = len(AxleSpacing); print('No. of Axle',Naxle);
Ltruck = 0; 
for j in range(Naxle):      # To determine Truck length
    Ltruck = Ltruck+AxleSpacing[j]
print('Length of Truck',Ltruck) 

# Main Program for moving load   
dx = (L+Ltruck)/Nsteps
for i in range(Nsteps):
   print(i)
   x = dx*(i)
   ops.pattern('Plain',1,1)
   for k in range(Naxle):
       x = x-AxleSpacing[k]
       if (x <= 0.0 or x >= L):
           print('Vehicle axle k out of Bridge')
           print('i=',i,'dx=',dx,'x=',x,'k=',k)
           continue
       else:
           ops.eleLoad('-ele',1,'-type','beamPoint',-AxleWeight[k],x/L)
           
           print('Loading Bridge length is ',L,'inch')
           print('i=',i,'dx=',dx,'x=',x,'k=',k)
           #break  #Important
      
   ops.analyze(1)
   
# storing data for Bending moment and Shear force
   for j in range(nIP):
       bM[i,0]=i*dx/ft;   
       sF[i,0]=bM[i,0]
       bM[i,j+1]=ops.sectionForce(1, j+1, 2)/ft
       sF[i,j+1]=ops.sectionForce(1, j+1, 3)
   ops.remove('loadPattern',1)

# Plotting Shear Force and Bending moment for all critical locations
for j in range(nIP):
    plt.plot(sF[:,0], sF[:,j+1], linewidth=2.0)
plt.xlabel("Length (ft)")
plt.ylabel("Shear Force (kip)")
plt.title ("Shear Force at Critical locs.")
plt.show()
for j in range(nIP):
    plt.plot(bM[:,0], bM[:,j+1], linewidth=2.0)
plt.xlabel("Length (ft)")
plt.ylabel("Bending moment (kipft)")
plt.title ("Bending moment at Critical locs.")
ops.wipe()

# Envelope BM and SF
envBM=np.zeros( (nIP, 2) )  # Initial variable to store data
envSF=np.zeros( (nIP, 3) )  # Initial variable to store data
for m in range(nIP):     
    envBM[m,0]=Criticallocs[m]*L/ft;
    envBM[m,1]=np.max(np.abs(bM[:,(m+1)])); 
    envSF[m,0]=Criticallocs[m]*L/ft;
    envSF[m,1]=np.max((sF[:,(m+1)]));
    envSF[m,2]=np.min((sF[:,(m+1)]));
    
plt.plot(envBM[:,0], envBM[:,1], linewidth=2.0)
plt.xlabel("Length Bridge (ft)")
plt.ylabel("Bending moment (kipft)")
plt.title ("Bending moment Envelope")
plt.show()

plt.plot(envSF[:,0], envSF[:,1], linewidth=2.0)
plt.plot(envSF[:,0], envSF[:,2], linewidth=2.0)
plt.xlabel("Length Bridge (ft)")
plt.ylabel("Shear Force (kip)")
plt.title ("Shear Force Envelope")
plt.show()
