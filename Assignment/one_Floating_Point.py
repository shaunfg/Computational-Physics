# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 11:40:47 2019

@author: sfg17
"""

import numpy as np

def machineEps_check(float_type):
    """
    Verifies the machine epsilon of local hardware, by finding the value in
        which the the float of a value, is no longer equal to itself.

            float(1) + epsilon == float(1)

        This occurs when the value, or machine epsilon, is smaller than the
        precision that can be obtained by the float, displaying the
        floats as equal.
    ----------
    Parameters:
    ----------
    float_type : inputs the type of float function (e.g. float32, float64)

    """

    machine_eps = float_type(1)

    # Condition stated above in docstring.
    while float_type(1) + float_type(machine_eps) != float_type(1):
        # Saves penultimate value to encompass full range
        machine_eps_last = machine_eps
        # Reduce machine epsilon by smallest factor (2)
        machine_eps = float_type(machine_eps) / float_type(2)

    print("{}\nMachine Epsilon = {},\n(Machine Epsilon Rounding = {})\n".format(
        float_type, machine_eps_last, machine_eps))
    return


def machineEps(float_type):
    """
    Finds the machine epsilon, based on theoretical equation.
    
        E = base ^ -(precision - 1)
    
    where E is the machine epsilon, base is 2 for binary and precision is based
    on the length of the mantissa. 
    ----------
    Parameters:
    ----------
    float_type : inputs the type of float function (e.g. float32, float64)
    """
    base = 2
    
    if float_type == "32bit":
        # One implicit bit
        precision = 24
    elif float_type == "64bit":
        # One implicit bit
        precision = 53
    elif float_type == "extended":
        precision = 64
    
    # Finds machine epsilon for each float type, based on theoretical equation
    eps = base**(-(precision-1))
    eps_abs_rounding = eps/2
    
    print("CHECK1: {}, Machine Epsilon = {}, \n(Machine Epsilon Rounding = {})\n".format(
            float_type,eps,eps_abs_rounding))
    return

if __name__ == "__main__":
    print("----------- Hardware Machine Epsilon --------------\n")
    # For loop to test all float types.
    for float_type in [np.float32,np.float64,np.longdouble]:
        machineEps_check(float_type)
    print("      * Note, np.longdouble is padded to 128 bits on mac\n")   
    print("----------- Theoretical Machine Epsilon ------------\n")

    for float_type in ["32bit","64bit","extended"]:
        machineEps(float_type)
    
    print("------------- Numpy Machine Epsilon ---------------\n")
    print("CHECK2: Machine Epsilon = ",np.finfo(float).eps,"\n")
    print("---------------------------------------------------\n")
