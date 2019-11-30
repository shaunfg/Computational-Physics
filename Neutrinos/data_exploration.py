#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 19:10:25 2019

@author: ShaunGan
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from scipy.interpolate import lagrange
from scipy.interpolate import interp1d
from numpy.polynomial.polynomial import Polynomial
import random


# 3.1 The data
def read_data(filename):
    # Reads data file into a dataframe
    data = pd.read_csv(filename)
    
    # Splits first 200 and last 200 data points
    df = data.iloc[:200].copy()
    df['unoscillated_flux'] = data.iloc[201:].copy().reset_index(drop = True)
    
    # Rename columns
    df.columns = ["oscillated_rate","unoscillated_rate"]
    
    # Append column for energy bins
    df["energy"] = np.arange(0.025,10.025,0.05)
    
    # Force float type for all data points
    df = df.astype(float)
    return df
#%% One Dimensional Minimisation (Section 3)
def survival_probability(E,theta,del_mass_square,L):
    
    coeff = 1.267 * del_mass_square * L  / E
    P = 1 - np.sin(2*theta)**2 * np.sin(coeff) **2
    return P
    
def oscillated_prediction(thetas,masses,run_type):
    # Calculate probabiliites of oscillation
    
    if run_type == "mass":
        if isinstance(masses, np.ndarray) == True:
            probs = [survival_probability(energies, thetas, masses[i], L) for i in
                     range(len(masses))]
        elif isinstance(masses, list) == True:
            probs = [survival_probability(energies, thetas, masses[i], L) for i in
                     range(len(masses))]
        else:
            probs = survival_probability(energies, thetas, masses, L)
            
    elif run_type == "theta":
    
        if isinstance(thetas,np.ndarray) == True:
            probs = [survival_probability(energies,thetas[i],masses,L) for i in
                     range(len(thetas))]
        elif isinstance(thetas,list) == True:
            probs = [survival_probability(energies,thetas[i],masses,L) for i in
                     range(len(thetas))]
        else:
            probs = survival_probability(energies,thetas,masses,L)
            
    else:
        print(run_type)
    
    # Obtain unoscillated rates from data grame
    unosc_rates = data["unoscillated_rate"].tolist()
    
    # Convert to numpy arrays
    probs = np.array(probs)
    unosc_rates = np.array(unosc_rates)
    
    # Find oscillated rates
    osc_rates = probs * unosc_rates
    
    if isinstance(osc_rates,np.ndarray):
        return osc_rates
    else:
        print(osc_rates)
        return [osc_rates]

def NLL(theta_values,del_m,data,run_type):
#    print(theta_values)
    rates = oscillated_prediction(thetas=theta_values,masses=del_m,run_type = run_type)
    k = data
    
    NLL_value = []
    
    for j in range(len(rates)):
        tmp = []
        l  = rates[j]

        for i in range(len(l)):
            
#            print(k)
            if k[i] != 0:
                value = l[i] - k[i] + k[i] * np.log10(k[i]/l[i])
                tmp.append(value)
            else:   
                pass

        NLL_value.append(sum(tmp))
        
    return NLL_value

def Parabolic_theta(measured_data,IC,guess_x):
    """
    generate f(x) from a set of x values,append the new x_3 value
    
    Parabolic minimiser is based on the intergral of the lagrange polynomial. 
    
    find f(x) with all four values
    save the smallest three values
    """

    def _find_next_point(x_list, y_list):
        """
        accepts list of x and y, each of 3 elements
        """
        x_0, x_1, x_2 = tuple(x_list)
        y_0, y_1, y_2 = tuple(y_list)
        num = (x_2 ** 2 - x_1 ** 2) * y_0 + (x_0 ** 2 - x_2 ** 2) * y_1 + (x_1 ** 2 - x_0 ** 2) * y_2
        denom = (x_2 - x_1) * y_0 + (x_0 - x_2) * y_1 + (x_1 - x_0) * y_2
        if denom != 0:
            x_3 = 1 / 2 * num / denom
        else:
            # if denomiator is zero, pick mid point of x
            x_list = [x for x in x_list if x <= x_list[np.argmax(x_list)]]
            x_list = [x for x in x_list if x >= x_list[np.argmin(x_list)]]
            x_3 = x_list[0]
        return x_3
    
    IC = np.array(IC)
    param = 'theta'

    random_x = guess_x#[random.uniform(x_bottom,x_top) for x in range(3)]
    random_y = NLL(np.array(random_x),IC,measured_data,param)

#    print(random_x)
    x_3 = _find_next_point(random_x,random_y)
    x_3_last = x_3 +10
    random_x.append(x_3)
    random_y = NLL(np.array(random_x),IC,measured_data,param)
    
    end_count = 0
    while end_count<2:  
        # Find maximum f(x) values
        max_idx = np.argmax(random_y)
        
        # delete the smallest x value
        del random_x[max_idx]
#        print("-",random_y)
                
        # Finds the new f(x) values
        random_y = NLL(np.array(random_x),IC,measured_data,param)

        # Finds the next minimum value
        x_3_last = x_3
        x_3 = _find_next_point(random_x, random_y)
        
        # Check for negative curvature
        if NLL([x_3],IC,measured_data,param)[0] > all(random_y):
            warnings.warn("Interval has positive & negative curvature", Warning) 
            
            random_x.append(x_3)

            # finds 2 additional values from max and min of interval
            x_values = np.linspace(min(random_x),max(random_x),4)[1:3]
            x_values = np.linspace(min(random_x),max(random_x),4)[1:3]
            x_values = np.append(x_values,random_x)
            
            # finds f(x)
            y_values = list(NLL(x_values,IC,measured_data,param))
            # Gets indices of a sorted array
            indices = np.argsort(y_values)
            
            #picks the 4 smallest values to carry on with
            random_x = [x_values[i] for i in indices][0:4]
            random_y = [y_values[i] for i in indices][0:4]

        else:
            # Stores the next smallest value
            random_x.append(x_3)
            # Calculates the f(x) of four x values
            print(measured_data)
            random_y = NLL(np.array(random_x),IC,measured_data,param)
        
        if round(x_3,18) == round(x_3_last,18):
            end_count +=1
        else:
            end_count = 0
    
    max_idx = np.argmax(random_y)
    del random_x[max_idx]        
    random_y = NLL(np.array(random_x),IC,measured_data,param)
    random_x = random_x
    
#    min_y_value = NLL([x_3],measured_data)[0]
    
#    print("----",random_x,random_y)

    return random_x,random_y

#%% Finding Errors on minimum

def Error_abs_addition(variables,NLL_values, min_val_x,min_NLL,above_min):
    """
    Finds error by +/- 0.5, on the first minimum for a parabolic fit.
    
    Points are linearly interpolated. 
    
    min_val_x,min_NLL from parabolic minmised fit.
    """
    # Form pandas datraframe
    comparison_df = pd.DataFrame({"Var":variables,"NLL":NLL_values})
    # Localise to first minimum
    comparison_df = comparison_df.loc[(comparison_df.NLL < min_NLL + 2*above_min) & (comparison_df.Var < 1.5)]
#    print(comparison_df)
    
    # Finds LHS and RHS of the minimum
    LHS = comparison_df.loc[comparison_df.Var < min_val_x]
    RHS = comparison_df.loc[comparison_df.Var > min_val_x]
    
    # Interpolate to find continous value
    func_LHS = interp1d(LHS["NLL"],LHS["Var"]) # Flipped to inverse function
    func_RHS = interp1d(RHS["NLL"],RHS["Var"]) # Flipped to inverse function

    #Takes maximum value
    values = np.array([func_LHS(min_NLL + 0.5)-min_val_x,func_RHS(min_NLL + 0.5)-min_val_x])
    std_dev = max(abs(values))
        
    return std_dev

def Error_Curvature(unoscillated_rates,measured_events,del_mass_square,IC,parabolic_x,parabolic_y):
    """
    Calculates error by finding difference in second derivatives. 
    
    Params:
        IC = tuple of del_mass_square,L,energies
    """
    
    # Find minimum theta and minimum NLL
    min_val = min(parabolic_x)
    min_NLL = min(parabolic_y)
    
    L,E = IC
    
    # Calculate second derivative of theoretical NLL value
    t = min_val
    A = np.sin(1.267 * del_mass_square * L  / E) **2
    
    # Calculate probabilities    
    P = 1 - np.sin(2*t)**2 * A
    P_1 = - 4*np.sin(2*t)*np.cos(2*t) * A
    P_2 = - (8* (np.cos(2*t)**2 - np.sin(2*t)**2) * A)
    
    # Calculate rates 
    l = P * unoscillated_rates
    l_1 = P_1 * unoscillated_rates
    l_2 = P_2 * unoscillated_rates
   
    # Calculate second dertivative
    NLL_2 = l_2 - measured_events * (l * l_2 - l_1 **2) / l**2 * 1/ np.log(10)
    
    # Curvature is equal to NLL_2 = 2a
    curvature_original = sum(NLL_2) /2
    
    # Calculate second derivative of Lagrange polynomial fit
    x = parabolic_x# 
    y = parabolic_y
    
    # Based on the parabolic minimiser
    poly = lagrange(x,y)
    coefficients = Polynomial(poly).coef
    
    # Shift polynomial by 0.5 and solve for roots
    coefficients[-1] = coefficients[-1] - min_NLL - 0.5
    roots = np.roots(coefficients)
    
    # Curvature = a
    curvature_fit = roots[0]
    
    # Find difference in curvature value
    curvature_del = curvature_original - curvature_fit
    
    # Just consider curvature, ax**2 = 0.5
    std_theta = np.sqrt(0.5/curvature_del)
    
    return std_theta

#%% Two Dimensional Minimisation (Section 4)
def Parabolic_mass(measured_data,theta_IC, guess_m):
    """
    generate f(x) from a set of x values,append the new x_3 value

    Parabolic minimiser is based on the intergral of the lagrange polynomial.

    find f(x) with all four values
    save the smallest three values
    """

    def _find_next_point(x_list, y_list):
        """
        accepts list of x and y, each of 3 elements
        """
        x_0, x_1, x_2 = tuple(x_list)
        y_0, y_1, y_2 = tuple(y_list)
        num = (x_2 ** 2 - x_1 ** 2) * y_0 + (x_0 ** 2 - x_2 ** 2) * y_1 + (x_1 ** 2 - x_0 ** 2) * y_2
        denom = (x_2 - x_1) * y_0 + (x_0 - x_2) * y_1 + (x_1 - x_0) * y_2
        if denom != 0:
            x_3 = 1 / 2 * num / denom
        else:
            # if denomiator is zero, pick mid point of x
            x_list = [x for x in x_list if x <= x_list[np.argmax(x_list)]]
            x_list = [x for x in x_list if x >= x_list[np.argmin(x_list)]]
            x_3 = x_list[0]
        return x_3

    param = "mass"
    random_x = guess_m  # [random.uniform(x_bottom,x_top) for x in range(3)]
    random_y = NLL(theta_IC,random_x, measured_data,run_type = param)

    #    print(random_x)
    x_3 = _find_next_point(random_x, random_y)
    x_3_last = x_3 + 10
    random_x.append(x_3)
    random_y = NLL(theta_IC,np.array(random_x), measured_data,run_type = param)

    # while abs(x_3 - x_3_last) > 1e-10:
    # while abs(x_3_last - x_3) > 1e-
    end_count = 0
    while end_count <2:
        # Find maximum f(x) values & delete smallest x value
        max_idx = np.argmax(random_y)
        del random_x[max_idx]

        # Finds the new f(x) values
        random_y = NLL(theta_IC,random_x, measured_data,run_type = param)

        # Finds the next minimum value
        x_3_last = x_3
        x_3 = _find_next_point(random_x, random_y)

        # Check for negative curvature
        if NLL(theta_IC,[x_3], measured_data,run_type = param)[0] > all(random_y):
            # warnings.warn("Interval has positive & negative curvature", Warning)
            random_x.append(x_3)

            # finds 2 additional values from max and min of interval
            x_values = np.linspace(min(random_x), max(random_x), 4)[1:3]
            x_values = np.append(x_values, random_x)

            # finds f(x)
            y_values = list(NLL(theta_IC,x_values, measured_data,run_type = param))
            # Gets indices of a sorted array
            indices = np.argsort(y_values)

            # picks the 4 smallest values to carry on with
            random_x = [x_values[i] for i in indices][0:4]
            random_y = [y_values[i] for i in indices][0:4]

        else:
            # Stores the next smallest value
            random_x.append(x_3)
            # Calculates the f(x) of four x values
            print(measured_data)
            random_y = NLL(theta_IC,random_x, measured_data,run_type = param)
        # print(random_x)
        
        # Checks if minimum value is the same three times, stop if true. 
        if round(x_3,18) == round(x_3_last,18):
            end_count +=1
        else:
            end_count = 0
            
    max_idx = np.argmax(random_y)
    del random_x[max_idx]
    random_y = NLL(theta_IC,random_x, measured_data,run_type = param)
    random_x = random_x

    return random_x, random_y

def Univariate(theta_IC, measured_data, guess_m,guess_x):
    min_x_mass,min_y_mass = Parabolic_mass(measured_data, theta_IC=theta_IC, guess_m=guess_m)

#    min_x_mass,min_y_mass = Parabolic_theta(measured_data, IC=theta_IC, guess_x=guess_m,param = 'mass')
    min_x_thetas, min_y_t = Parabolic_theta(measured_data=measured_data, IC=min(min_x_mass), guess_x=guess_x)
    return min_x_mass,min_y_mass,min_x_thetas,min_y_t

#%% Simulated Annealing
 
def NLL_simple(theta_values,del_m):

    def survival_probability_1(E,theta,del_mass_square,L):
        coeff = 1.267 * del_mass_square * L  / E
        P = 1 - np.sin(2*theta)**2 * np.sin(coeff) **2
        return P
    
    def oscillated_prediction_1(thetas,masses):
        # Calculate probabiliites of oscillation
        probs = survival_probability_1(energies,thetas,masses,L)
    
        # Obtain unoscillated rates from data grame
        unosc_rates = data["unoscillated_rate"].tolist()
        
        # Convert to numpy arrays
        probs = np.array(probs)
        unosc_rates = np.array(unosc_rates)
        
        # Find oscillated rates
        osc_rates = probs * unosc_rates
        
        return [osc_rates]
    
    rates = oscillated_prediction_1(thetas=theta_values,masses=del_m)
    k = oscillated
    
    NLL_value = []
    
#    print(rates)
    for j in range(len(rates)):
        tmp = []
        l  = rates[j]

        for i in range(len(l)):
            
#            print(k)
            if k[i] != 0:
                value = l[i] - k[i] + k[i] * np.log10(k[i]/l[i])
                tmp.append(value)
            else:   
                pass

        NLL_value.append(sum(tmp))
        
    return NLL_value[0]  

def Simulated_Annealing(T_start,T_step,guess_t= [0,1],guess_m = [1e-3,3e-3]):
    
    def Thermal(E,T):
        k_b = 0.01
        return np.exp(- E / (k_b * T))
    
    t_values = []
    
    
    h,h_2 = (0.05,1e-3) # step sizes (initial conditions)
    # Set first guess 
    t = random.uniform(guess_t[0],guess_t[1])
    m = random.uniform(guess_m[0],guess_m[1])
    
    T = T_start
    success_count = 0
    count = 0
    while T > 0:
        
        if T% 100 == 0:
            print("Temperature = {}K".format(T))
        t_dash = random.uniform(t-h,t+h)
        m_dash = random.uniform(m-h_2,m+h_2)
        
        if t_dash < 0:
            t_dash = t_dash *-1
        if m_dash < 0:
            m_dash = m_dash *-1
            
        del_f = NLL_simple(t_dash,m_dash)- NLL_simple(t,m) 
        p_acc = Thermal(del_f,T)
        
        if p_acc > 1 : # if next energy value is smaller, then update
            # Changes step size, formula ensures small step size
            h = (t_dash - int(t_dash)) / 2
            h_2 = (m_dash - int(m_dash)) / 2

            t = t_dash
            m = m_dash
            
            success_count +=1
        else:
#            print('----',x_dash,x)
            pass 

        t_values.append(t_dash)

        T-= T_step
        
        T = round(T,10) # Deals with floating point error
        
        count+=1
        
    NLL_value = NLL_simple(t,m) 
    print(m,t,NLL_value)
    print("Efficiency = {:.4f}%".format(success_count/count * 100))
    
#    plt.plot(x_values,func(np.array(x_values),y_dash),'x')
#    plt.figure()
#    plt.hist(x_values,bins = 80)
#Simulated_Annealing(T_start = 1000,T_step = 0.1)

#%%
if __name__ == "__main__":
    data = read_data("data.txt")
#    data = read_data("chris_data.txt")
    
    # Guess Parameters
    del_m_square = 2.915e-3 # adjusted to fit code data better
    L = 295
    
    # Prepare lists to be used in calculations
    energies = np.array(data['energy'].tolist())
    thetas = np.arange(0,np.pi,0.002)
    oscillated = np.array(data["oscillated_rate"].tolist()) # measured
    unoscillated = np.array(data["unoscillated_rate"].tolist()) # simulated
    predicted = oscillated_prediction([np.pi/4],del_m_square,"theta")
    ICs = (L,energies)
    
    # Calculate NLL 
    NLL_thetas = NLL(thetas,del_m_square,oscillated,"theta")
    
    # Parabolic Minimise
    vals_x,vals_y = Parabolic_theta(oscillated,IC=del_m_square,guess_x = [0.2,0.5,1])
    
    # Minimums based on the parabolic minimiser
    min_theta_1D = min(vals_x)
    min_NLL_1D = min(vals_y)
    
    # Calculate both errors, from +/- 0.5 and from difference in curvature
    std_t_abs = Error_abs_addition(thetas,NLL_thetas,min_theta_1D,min_NLL_1D,0.7)
    std_t_curv = Error_Curvature(unoscillated,oscillated,del_m_square,ICs,vals_x,vals_y)
    
    print("\nMin Theta 1D Parabolic Minimiser = {:.4f} +/- {:.4f} or {:.4f}".format(min_theta_1D,std_t_abs,std_t_curv))
    
    # Two dimensional minimisation
    theta = np.array([np.pi / 4])
    masses = np.linspace(1e-3,3e-3,1000)
    NLL_masses = NLL(theta,masses,oscillated,run_type = "mass")
    
    # Obtain Univariate minimisation    
    a,b,c,d = Univariate(theta,oscillated,[1e-3,2e-3,3e-3],guess_x =[0.2, 0.5, 1])
    min_masses_2D,min_NLL_masses,min_thetas_2D,min_NLL_thetas = (a,b,c,d)
    
    # Find Minimum values of masses and thetas
    min_mass_2D = min(min_masses_2D)
    min_theta_2D = min(min_thetas_2D)
    
    # Find errors on univariate
    std_mass_2D = Error_abs_addition(masses,NLL_masses,min_mass_2D,min(min_NLL_masses),0.7)
    std_mass_t = Error_Curvature(unoscillated,oscillated,min_mass_2D,ICs,min_thetas_2D,
                          min_NLL_thetas)
        
    print("Minimum mass 2D Parabolic Minimiser = {:.7f} +/- {:.7f}".format(min_mass_2D,std_mass_2D))
    print("Minimum theta 2D Parabolic Minimiser = {:.4f} +/- {:.4f}".format(min_theta_2D,std_mass_t))

    #TODO: Test functions for minimisers
    #TODO: Verify step sizes

    Simulated_Annealing(T_start = 1000,T_step = 0.1)
    

# ===================================PLOT======================================
    
#    # Plot hist
#    data["oscillated_rate"].hist(bins = 50)
    
#    # Measured oscillated data
#    plt.figure(figsize = (8,5))
#    plt.bar(energies,oscillated,width = 0.05,alpha = 0.5)
#    plt.xlabel("Energies/GeV")
#    plt.ylabel("Rates")
#    plt.title("Measured Data after oscillation")
#    plt.plot(energies,predicted[0])
#     
#    # Unoscillated simulated data 
#    plt.figure()
#    plt.bar(energies,unoscillated,width = 0.05)
#    plt.xlabel("Energies/GeV")
#    plt.ylabel("Rates")
#    plt.title("unoscillated")
#    
    # NLL against theta    
    plt.figure()
    plt.xlabel("Thetas")
    plt.ylabel("NLL")
    plt.plot(thetas, NLL_thetas)
#    plt.plot(samp_x,abc(samp_x))


    

    



    
    
