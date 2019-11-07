#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 17:57:22 2019

@author: ShaunGan
"""
#TODO: Sampling, Aliasing, Padding

import numpy as np
import matplotlib.pyplot as plt

def g(t):
    """
    Gaussian Function, takes in an array of discrete data points. 
    
    Returns a normalized Gaussian
    """
    values = 1/np.sqrt(2*np.pi) * np.exp(-t**2/2)
#    values_normalized = values * (max(values) - min(values))/sum(values)
    return values#_normalized

def h(t):
    """
    Tophat function, takes in an array of discrete data points
    """
    values = []
    for i in range(len(t)):
        if t[i]>=3 and t[i]<=5:
            h = 4
        else:
            h = 0
        values.append(h)
    return values

def Convolution(time_values,func_1,func_2,time_min,time_max,plot = True):
    """
    Performs a convolutions using the convolution theroem:
        F(f*g) = F(f)F(g)
    Thus finds convolutions of both functions separately, find the product, 
        and completes and inverse fourier transform
    
    The convoluted result is then required to undergo an fftshift, to shift
        the negative values to the beginning of the array. This is
        due to the nature of the algorithm
    
    -----------
    Parameters:
    -----------
    time_values: Array of discrete time values
    func1 : Tophat function
    func2 : Gaussian function
    plot : True/False, to plot the graphs. 
    """
    
    # Fourier transform of tophat and gaussian
    
    fft_first = np.fft.fft(func_1(time_values))
    fft_second = np.fft.fft(func_2(time_values))
                       
    # Product of Fourier transforms
    fft_convoluted = fft_first * fft_second
    
    # Inverse Fourier Transform and shift for accurate plotting
    convoluted = np.fft.ifft(fft_convoluted)
    convoluted = convoluted /np.sqrt(len(convoluted))#1/√N to ensure amplitudes match expected.
    convoluted = np.fft.fftshift(np.abs(convoluted))

    if plot == True:
        
        sample_x = np.linspace(time_min,time_max,1000)
        
        # Shift fourier transforms of tophat and gaussian, for correct plotting
        fft_first_plot = np.fft.fftshift(fft_first)/np.sqrt(len(fft_first))
        fft_second_plot = np.abs(np.fft.fftshift(fft_second)/np.sqrt(len(fft_second)))
        
        # Plots tophat, gaussian and the convolution 
        fig,(ax1,ax2,ax3) = plt.subplots(3,1,figsize = (8,8))
        ax1.set_title("Fourier Transforms")
    
        ax1.plot(sample_x,func_1(sample_x),label = "Tophat")
        ax1.plot(time_values,fft_first_plot,label = "F(Tophat)")
        ax1.legend()
    
        ax2.plot(sample_x,func_2(sample_x),label = "Gaussian")
        ax2.plot(time_values,fft_second_plot,label = "F(Gaussian)")
        ax2.legend()
    
        ax3.plot(time_values,convoluted,label = "Convoluted Gauss * Tophat")
        ax3.plot(time_values,func_1(time_values),label = "Tophat")
        ax3.legend()

    else:
        pass
    
if __name__ == "__main__":

    # Parameters
    min_time = -10
    max_time = 10
    period = max_time - min_time
    
    # Padding to increase speed of fft
    N_samples = 2**(9)
    
    
    Nyquist = 1/N_samples * 2*np.pi
    
    maximum_frequency = 2*np.pi / (period) * N_samples/2
    minimum_frequency = 2 * np.pi/period
    
    print(Nyquist,maximum_frequency,minimum_frequency)
    
    time = np.linspace(min_time,max_time,N_samples)
    Convolution(time,h,g,min_time,max_time,plot = True)
    
    
    
#%% Verify 
    
def gaussian(t):
    a= 1
    values =1/np.sqrt(2*np.pi)* np.exp(-t**2/2*a**2)
    return values#_normalized

def h(t):
    """
    Tophat function, takes in an array of discrete data points
    """
    values = []
    for i in range(len(t)):
        if t[i]>=-1 and t[i]<=1:
            h = 1
        else:
            h = 0
        values.append(h)
    return values

N = 100

sample_x = np.linspace(-5,5,N)
dt = (max(sample_x)-min(sample_x))/N
array = gaussian(sample_x)

fourier = np.fft.fft(array)
shift = np.abs(np.fft.fftshift(fourier)) * 1/np.sqrt(N)

plt.plot(sample_x,gaussian(sample_x),label = 'original')
plt.plot(sample_x,shift)
plt.legend()

plt.figure()
tophat = h(sample_x)
tophat_fourier= np.fft.fft(tophat)
shift = np.fft.fftshift(tophat_fourier) * 1/np.sqrt(N)

plt.plot(sample_x,h(sample_x),label = 'original')
plt.plot(sample_x,shift)
plt.legend()

#print(np.fft.fftfreq(tophat_fourier,2))


