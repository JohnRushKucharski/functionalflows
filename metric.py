'''
This module provides methods for evaluating if daily function flow metrics are met.

Based on: 
    Yarnell, S. M., Stein, E. D., Webb, J. A., Grantham, T., Lusardi, R. A., Zimmerman, J., et al. (2020). 
    A functional flows approach to selecting ecologically relevant flow metrics for environmental flow applications. 
    River Research and Applications, 36(2), 318–324. https://doi.org/10.1002/rra.3575
    
    ... for instance table 1 is good template for understanding this code. 
'''

import operator
from enum import Enum
from typing import List, Callable
from dataclasses import dataclass, field

import pandas as pd
import numpy as np

from utilities import dowy

@dataclass
class Metric:
    '''An object to organize daily hydrograph data and evaluate if functional flow characteristic (and metrics) are met.'''
    dates: pd.Series 
    '''A pandas series based on the assumption that hydrograph information would be imported by pandas.'''
    flows: np.ndarray
    '''Flow data.'''
    characteristics: List[Callable[['Metric', int],np.ndarray]]
    '''A list of "characteristic" functions in the order in which they should be evaluated.'''
    dsowy: np.ndarray = field(init=False)
    '''Day of the water year, computed by the object upon import.'''
    output: np.ndarray = field(init=False)
    '''A mxn matrix where m is the number of timesteps in the dates array, and n is the number of characteristics to be evaluated (in the characeristics list). '''
    def __post_init__(self):
        self.dsowy = self.dates.apply(dowy).to_numpy()
        self.output = np.zeros((len(self.dsowy), len(self.characteristics)), dtype=np.int32)
        self.evaluate()

    def evaluate(self):
        '''Loops through timeseries evaluating if each characteristic is met. '''
        for i in range(0, len(self.characteristics)):
            self.output[:,i] = self.characteristics[i](data=self, order=i)

def timing(start: int = 0, end: int = 367):
    '''Returns a function used to evaluate if each time step is in range of specified days in water year.'''
    def evaluate(data: Metric, order=1):
        @np.vectorize
        def f(day: int):
            return 1 if start <= day <= end else 0
        return f(data.dsowy)
    return evaluate

def magnitude(threshold: float = 0, operator = operator.gt):          
    '''Returns a function used to evaluate if flow value in each time step meet a condition specified by an operator (<, =, >, ...) and threshold value.'''
    def evaluate(data: Metric, order=2):
        @np.vectorize
        def f(flow: float):
            return 1 if operator(flow, threshold) else 0
        return f(data.flows)
    return evaluate

def duration(n_periods: int = 2):
    '''Returns a function used to evaluate if conditions specified by previous characteristics were met for a specificed number of consecutive periods.'''
    def evaluate(data: Metric, order=3):
        n = 0
        shp = data.output.shape 
        out = np.zeros(shp[0], dtype=np.int32)
        for i in range(0, len(out)):
            # check if it meets all previous characteristics
            if data.output[i,:].sum() == order:
                n += 1
            else:
                # it has met all criteria for n periods
                if n_periods <= n:           
                    # out[i-n:i] = 1 # each period gets duration (this would be better for plotting) 
                    # below only gets a single '1' (this will make plotting more challenging)
                    out[i-1] = 1
                n = 0
        return out
    return evaluate

def frequency(n_times: int = 1, n_years: int = 1):
    '''Returns a funciton used to evluate if previous characteristics were met a specified number of times, across a specified number of years.'''
    def evaluate(data: Metric, order=4):
        n, yrs = 0, 0
        out = np.zeros(data.metrics.shape[0], dtype=np.int32)
        for i in range(0, len(out)):
            if data.dswy[i] == 1:
                if n < n_times:
                    # end of a frequency streak
                    if n_years < yrs:
                        # out[i-n:i] = 1 # this the the better for plotting example
                        # below gets a single '1' (this will make plotting more challenging)
                        out[i-1] = 1
                    else:
                        yrs = 0
                else:
                    yrs += 1
                n = 0   
            if data.metrics[i,:].sum() == order-1:
                n += 1
        return out
    return evaluate