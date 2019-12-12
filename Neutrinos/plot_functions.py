#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 23:28:48 2019

@author: ShaunGan
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_mass(func,theta = np.pi/4,val = "$\pi$ / 4"):
    masses = np.linspace(0,5e-3,1000)
    NLL_masses = func(theta,masses)
    
    plt.figure()
    plt.plot(masses,NLL_masses)
    plt.xlabel("$\Delta m^2_{23}$")
    plt.ylabel("NLL")
    plt.title("NLL against $\Delta m^2_{23}$ for $\Theta_{23}$= %s" %val)
        
def plot_theta(func,mass = 2.4e-3,cross_a = 0,val = "2.4e-3"):
    
    thetas = np.arange(0,np.pi,0.002)
    # Calculate NLL 
    NLL_thetas = func(thetas,mass,cross_a)
    
    # NLL against theta    
    plt.figure()
    plt.xlabel("$\Theta_{23}$")
    plt.ylabel("NLL")
    plt.plot(thetas, NLL_thetas)
    
    if cross_a == 0:
        plt.title("NLL against $\Theta_{23}$ for $\Delta m^2_{23}$ = %s" %val)
    else:
        plt.title("NLL against $\Theta_{23}$ for $\Delta m^2_{23}$ = %s" 
                  r", $\frac{dCS}{dE}$ = %s"%val)


def plot_color_map(x,y,func):
    Z = []
    for i in range(len(x)):
        Z.append([func(x[j],y[i]) for j in range(len(y))])
    
    fig,axes = plt.subplots(1,1,figsize=(10,8))
    
    c = axes.imshow(Z,origin="lower",interpolation = "None",aspect = "auto",
                    extent = [min(x),max(x),min(y),max(y)],cmap = 'viridis')
    
    plt.xlabel("$\Theta$")
    plt.ylabel("$\Delta m^2$")
    plt.title("NLL colour map of $\Delta m^2$ and $\Theta$")
    
    fig.colorbar(c,ax=axes, label='NLL')
#    print("\n",Z)
#plot_color_map(np.linspace(0,np.pi/2,100),np.linspace(0,5e-3,100),NLL)    

def plot_steps(t_values,m_values,xlabel,ylabel,title,font_size ="big"):
#    plt.figure(figsize = (10,8))
    plt.plot(t_values,m_values,color = '#1f77b4',label = "Min-Trajectory")    
    plt.plot(t_values,m_values,'o',ms = 2,color = '#ff7f0e',label = "Step point")    
    plt.plot(t_values[-1],m_values[-1],'o', color = '#17becf',label = "Minimum point")  
    if font_size == "big":
        plt.xlabel(xlabel,fontsize = 18)
        plt.ylabel(ylabel,fontsize = 18)
        plt.title(title,fontsize= 18)
    else:
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
    return

def plot_steps_univariate(theta_step,mass_step):
    plt.figure()
    plt.plot(theta_step,mass_step)
    plt.plot(theta_step,mass_step,'o',ms = 2)
    plt.xlabel("$\Theta$")
    plt.ylabel("$\Delta m^2$")
    plt.title("Steps taken for Univariate minimisation of NLL")
    
def plot_std(min_theta_1D,del_m_square,std_t_abs,std_t_curv,std_t_dev,
             NLL,thetas,NLL_thetas,min_NLL_1D):
    
    points_abs = [min_theta_1D + x for x in std_t_abs]
    NLL_points_abs = NLL(np.array(points_abs),del_m_square)
    
    points_curv = [min_theta_1D + x for x in [std_t_curv,-std_t_curv]]
    NLL_points_curv = NLL(np.array(points_curv),del_m_square)
    
    points_dev = [min_theta_1D + x for x in [std_t_dev,-std_t_dev]]
    NLL_points_dev = NLL(np.array(points_dev),del_m_square)

    # NLL against theta    
    plt.figure()
    plt.title("NLL against $ \Theta_{23}$ for $\Delta m^2 = 2.4e-3$")
    plt.xlabel("Thetas")
    plt.ylabel("NLL")
    plt.plot(thetas, NLL_thetas,)
    plt.plot(min_theta_1D,min_NLL_1D,'x',label = "Min NLL")
    plt.plot(points_abs,NLL_points_abs,'x',label = "Absolute Error")
    plt.plot(points_curv,NLL_points_curv,'x',label = "Curvature Error")
    plt.plot(points_dev,NLL_points_dev,'x',label = "2nd Dev Curvature Error")
    plt.legend(loc = 'upper right')
    
    plt.xlim(0.6,0.8)

def plot_rates(energies,unoscillated,oscillated,predicted,min_p):
    val = tuple([round(x,4) for x in min_p])

    fig,axes = plt.subplots(2,1,figsize = (9,10),sharex = True)
    
    title = fig.suptitle("Rates against energies for $\Theta_{23} = $%s, "
                "$\Delta m_{23}^2 = $ %s, " r"$\frac{dCS}{dE}$ = %s, "
                "C = %s"%val,fontsize=18)
    fig.tight_layout()
    title.set_y(1.05)
#    fig.subplots_adjust(top=0.8)
    
    # Unoscillated simulated data 
    axes[0].bar(energies,unoscillated,width = 0.05)
#    axes[0].set_xlabel("Energies/GeV")
    axes[0].set_ylabel("Rates")
    axes[0].set_title("Unoscillated Rates")
    
    # Measured oscillated data
    axes[1].bar(energies,oscillated,width = 0.05,alpha = 0.5,label = "Measured Oscillated Data")
    axes[1].set_xlabel("Energies/GeV")
    axes[1].set_ylabel("Rates")
    axes[1].set_title("Measured Data after oscillation")
    axes[1].plot(energies,predicted[0],color = '#ff7f0e',label = "Predicted Oscillation Data")
    axes[1].legend()
    return
