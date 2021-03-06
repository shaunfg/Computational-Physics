# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 13:04:57 2019

@author: sfg17
"""

import numpy as np
import matplotlib.pyplot as plt
from two_Matrices import Crout,Forward_Backward

def Linear(x,y,N_density):
    """
    Forms Linear plot by creating a linear regression between each point, 
        and subsequent relevant points. [ y = mx + c ]
    
    ----------
    Parameters:
    ----------
    N_density: Number of extra data points, between each point. 
    x,y: Input arrays of x and y values. 
    """
    x_values = []
    y_values = []

    # Finds gradient and c between each point.
    for i in range(len(x)-1):
        m = (y[i+1] - y[i])/ (x[i+1] - x[i])
        c = y[i] - m * x[i]

        # Plots points between a pair of points, following the m and c found above
        for j in range(N_density):
            x_tmp = np.linspace(x[i],x[i+1],N_density)
            y_tmp = m * x_tmp + c
            
            x_values.append(list(x_tmp))
            y_values.append(list(y_tmp))
            
    # Flattens Lists
    x_values = [item for sublist in x_values for item in sublist]
    y_values = [item for sublist in y_values for item in sublist]

    # Plot
    plt.figure(figsize = (8,5))
    plt.plot(x,y,'x',label = "Original Points")
    plt.plot(x_values,y_values,label = "Linear Interpolation")
    plt.title("Linear Plot")
    plt.legend()
    return

#%%
def _Form_Matrix(x,y):
    """
    Forms Matrix of coefficients, corresponding to the 2nd derivatives of the
        function, for the number of points.
        
    If there are N points, we will need N+1 equations to solve, but we will
        only obtain N-1 equations. In this nature, the natural spline boundary
        condition was used. 
        
        --> In applying this, I removed the first and last column of the
            M-2 * M matrix, in order Sto solve using crouts method. These 
            variables are tehn added back later to solve for the 2nd 
            derivatives
            
    Boundary Conditions: f"o = f"n = 0 
    -----------------------------------
    ----------
    Parameters:
    ----------
    x,y: Input arrays of x and y values.
    """
    N_samples = len(x) 
    matrix = []
    B  = []

    for i in range(1,N_samples-1):
        # Create row of empty values to solve.
        row = [0]*N_samples
        # Calculated all four terms (LHS & RHS) of cubic spline equation
        row[i-1] = (x[i] - x[i-1])/6
        row[i] = (x[i+1] - x[i-1])/3
        row[i+1] = (x[i+1] - x[i])/6
        b = (y[i+1] - y[i]) / (x[i+1] - x[i]) - (y[i] - y[i-1]) / (x[i] - x[i-1])
        
        matrix.append(row)        
        B.append(b)

    # Apply Boundary Condition here, allowing use to delete the 1st and last col
    matrix = np.delete(matrix,0,1)
    matrix = np.delete(matrix,-1,1)

    # Solve the square matrix using Crouts Algorithm
    lower_b,upper_b = Crout(matrix,det = False)
    second_dev = Forward_Backward(lower_b,upper_b,B)
    
    # Including Boundary Conditions back into solutions.
    second_dev.append(0)
    second_dev.insert(0,0)    

    return second_dev



def Cubic_Spline(x,x_i,y_i,title):
    """
    For an input value x, find its closest two x_i points, in order to fit
        it with its suitable cubic spline values. If it is equal to a lower
        bound of x_i, this function selects the next x_i value to perform
        the cubic spline interpolation. 
        
    For example, if x = 3.5, out of x_i = [1,2,3,4,5], we pick x_i = {3,4} 
        in order to perform the interpolations.
        
        or if x = 3, we pick x_i = {3,4} also. 
    
    ----------
    Parameters:
    ----------
    x: array of values to fit using cubic spline interpolation 
    x_i,y_i: array of x,y values used to find the parameters to make cubic 
                spline interpolation
    title: title of graph plot
    
    """
    
    # Calculates all the variables in the cubic spline equation
    def Interpolate(xi_bottom,xi_top,x,f_dash):
        # Calculates the coefficients A,B,C,D
        A = (xi_top - x)/(xi_top - xi_bottom)
        B = 1- A
        C = 1/6 * (A**3 - A)*(xi_top - xi_bottom)**2
        D = 1/6 * (B**3 - B)*(xi_top - xi_bottom)**2

        # Selects f_i values form indexing the input solutions vector
        f_i_bot = y_i[x_i.index(xi_bottom)]
        f_i_top = y_i[x_i.index(xi_top)]

        # Selects the second derivative values from indexing the vector
        f_dash_bot =  f_dash[x_i.index(xi_bottom)]
        f_dash_top =  f_dash[x_i.index(xi_top)]

        #Combines all values
        final = A*f_i_bot + B * f_i_top + C * f_dash_bot + D * f_dash_top

        return final

    f_dash_values = _Form_Matrix(x_i,y_i)
    
    spline_x = []
    spline_y = []
        
    # Selects appropriate range that x will fall into
    for i in range(len(x)):
        for j in range(len(x_i)):
            # Skip if larger than final x_i value, so out of range
            if x[i] >= x_i[-1] or x[i] <= x_i[0]:
                pass
            # Select pair of points x_i that encompass the input x
            elif x[i] >= x_i[j] and x[i] <= x_i[j+1]:
                
                xi_bottom = x_i[j]
                xi_top = x_i[j+1]
                y_value = Interpolate(xi_bottom,xi_top,x[i],f_dash_values)
                
                spline_x.append(x[i])
                spline_y.append(y_value)

    plt.figure(figsize = (8,5))
    plt.title(title)
    plt.plot(x_i,y_i,'x',label = "Original plots")
    plt.plot(x_i,y_i,label = "Linear")

    plt.plot(spline_x,spline_y,label = "Spline")
    plt.legend()

if __name__ == "__main__":

    # Values given in assignment
    x_i = [-2.1,-1.45,-1.3,-0.2,0.1,0.15,0.9,1.1,1.5,2.8,3.8]
    y_i = [0.012155,0.122151,0.184520,0.960789,0.990050,0.977751,0.422383,0.298197,
         0.105399,3.936690e-4,5.355348e-7]

    # Linear Interpolation
    N_points_between_plots = 3
    Linear(x_i,y_i,N_points_between_plots)

    # Cubic Spline Interpolation
    x = np.arange(min(x_i),max(x_i),0.001)
    Cubic_Spline(x,x_i,y_i,"Spline with Data from Assignment")

    # Sample data to verify validity of cubic spline plot
#    sample_data_x = [1,2,3,5,8,10,18,20,25,45]
#    sample_data_y = [4,7,9,12,15,1,3,4,5,3]
#    x = np.arange(min(sample_data_x),max(sample_data_x),0.001)
#    Cubic_Spline(x,sample_data_x,sample_data_y,"Spline with Sample Data")
