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
#from parabolic import Parabolic_minimise


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

def survival_probability(E,theta,del_mass_square,L):
    
    coeff = 1.267 * del_mass_square * L  / E
    P = 1 - np.sin(2*theta)**2 * np.sin(coeff) **2
    return P
    
def oscillated_prediction(thetas):
    # Calculate probabiliites of oscillation
    
    if isinstance(thetas,np.ndarray) == True:
        probs = [survival_probability(energies,thetas[i],del_m,L) for i in
                 range(len(thetas))]
    elif isinstance(thetas,list) == True:
        probs = [survival_probability(energies,thetas[i],del_m,L) for i in
                 range(len(thetas))]
    else:
        probs = survival_probability(energies,thetas,del_m,L)
    
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

def NLL(theta_values,data):
#    print(theta_values)
    rates = oscillated_prediction(thetas=theta_values)
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

def Parabolic_minimise(measured_data,guess_x = [-2.2,0.1,2]):
    """
    generate f(x) from a set of x values
    append the new x_3 value
    
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

    random_x = guess_x#[random.uniform(x_bottom,x_top) for x in range(3)]
    random_y = NLL(np.array(random_x),measured_data)

#    print(random_x)
    x_3 = _find_next_point(random_x,random_y)
    x_3_last = x_3 +10
    random_x.append(x_3)
    random_y = NLL(np.array(random_x),measured_data)

    while abs(x_3-x_3_last)>1e-10:  
        # Find maximum f(x) values
        max_idx = np.argmax(random_y)
        
        # delete the smallest x value
        del random_x[max_idx]
#        print("-",random_y)
                
        # Finds the new f(x) values
        random_y = NLL(np.array(random_x),measured_data)

        # Finds the next minimum value
        x_3_last = x_3
        x_3 = _find_next_point(random_x, random_y)
        
        # Check for negative curvature
        if NLL([x_3],measured_data)[0] > all(random_y):
            warnings.warn("Interval has positive & negative curvature", Warning) 
            
            random_x.append(x_3)

            # finds 2 additional values from max and min of interval
            x_values = np.linspace(min(random_x),max(random_x),4)[1:3]
            x_values = np.append(x_values,random_x)
            
            # finds f(x)
            y_values = list(NLL(x_values,measured_data))
            # Gets indices of a sorted array
            indices = np.argsort(y_values)
            
            #picks the 4 smallest values to carry on with
            random_x = [x_values[i] for i in indices][0:4]
            random_y = [y_values[i] for i in indices][0:4]                        

           # random_x = [random.uniform(min(random_x),max(random_x)) for x in range(4)]
#            random_y = NLL(np.array(random_x))

        else:
            # Stores the next smallest value
            random_x.append(x_3)
            # Calculates the f(x) of four x values
            print(measured_data)
            random_y = NLL(np.array(random_x),measured_data)
    min_y_value = NLL([x_3],measured_data)[0]


    return x_3,min_y_value

def Error_abs_addition(thetas,NLL_values, min_theta):
    """
    Finds error by +/- 0.5, on the first minimum. 
    """
    comparison_df = pd.DataFrame({"Thetas":thetas,"NLL":NLL_values})
    check = comparison_df.loc[(comparison_df.Thetas < 2 * min_theta)]

    value = check.loc[check.Thetas == min(check.Thetas, key=lambda x:abs(x-min_theta))]
    min_NLL = value.NLL.values[0]
    theta_plus_row = check.loc[check.NLL == min(check.NLL, key=lambda x:abs(x-min_NLL+0.5))]
    theta_minus_row = check.loc[check.NLL == min(check.NLL, key=lambda x:abs(x-min_NLL-0.5))]
    
    theta_plus = theta_plus_row.Thetas.values[0]
    theta_minus = theta_minus_row.Thetas.values[0]

    std_dev = (theta_plus - theta_minus) / 2
    
    return std_dev

    
if __name__ == "__main__":    
    data = read_data("data.txt")
#    data = read_data("chris_data.txt")
    
    #  Plot hist
#    data["oscillated_rate"].hist(bins = 50)
    
    # Guess Parameters
    del_m = 2.915e-3 # adjusted to fit code data better
    L = 295
    
    # Energies and Theta values to vary
    energies = np.array(data['energy'].tolist())
    thetas = np.arange(0,np.pi,0.002)
    oscillated_rates = np.array(data["oscillated_rate"].tolist())
    unoscillated = np.array(data["unoscillated_rate"].tolist())
    predicted = oscillated_prediction([np.pi/4])
    
    
    NLL_array = NLL(thetas,oscillated_rates)
    min_x,min_y = Parabolic_minimise(oscillated_rates,guess_x = [0.2,0.5,1])
    print(min_x,min_y)
    
    comparison_df = pd.DataFrame({"Thetas":thetas,"NLL":NLL_array})
    check = comparison_df.loc[(comparison_df.NLL < 87.5) & (comparison_df.Thetas <2)]
    
    std_theta = Error_abs_addition(thetas,NLL_array,min_x)
#    plt.figure()
#    print(check)
#    plt.plot(check.Thetas,check.NLL)
    
    # First minimum


#    NLL_value = comparison_df.loc[(comparison_df.NLL < min_y + 0.1) & (comparison_df.Thetas < 2)]
    


#    print(comparison_df.loc[(comparison_df.NLL < min_1 + 0.5) | (comparison_df.NLL > min_1 - 0.5)])
    
    # Second minimum
#    Parabolic_minimise(oscillated_rates,guess_x = [2.0,2.5,2.3])


# PLOTTT    
    # Measured oscillated data
#    plt.figure(figsize = (8,5))
#    plt.bar(energies,oscillated_rates,width = 0.05,alpha = 0.5)
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
    plt.plot(thetas, NLL_array)


    

    



    
    
