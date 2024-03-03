'''Defines the functional flow characteristic functions.

The following characteristics are implemented:
- magnitude
- timing
- duration
- frequency
- rate_of_change

Following the template in:

Yarnell, S. M., Stein, E. D., Webb, J. A., Grantham, T., Lusardi, R. A., Zimmerman, J.,
Peek, R. A., Lane, B. A., Howard, J., & Sandoval-Solis, S. (2020). 
A functional flows approach to selecting ecologically relevant flow metrics
for environmental flow applications. 
River Research and Applications, 36(2), 318–324. 
https://doi.org/10.1002/rra.3575 
'''

import operator
from typing import Callable, Optional, Any

import numpy as np
import pandas as pd

from functionalflows.model.data import Input

def match_symbol(symbol: str = ">") -> Callable[[Any, Any], bool]:
    '''Converts text symbols to python operators.

    Args:
        symbol (str): comparison symbol. Defaults to ">".

    Raises:
        NotImplementedError: if the symbol is not recognized.

    Returns:
        Callable[[Any, Any], bool]: Function comparing two values using the specified symbol
        and returning boolean.
    '''
    match symbol:
        case ">":
            return operator.gt
        case ">=":
            return operator.ge
        case "=":
            return operator.eq
        case "<=":
            return operator.le
        case "<":
            return operator.lt
        case _:
            raise NotImplementedError(f'The operator symbol {symbol} is not recognized.')

type EvaluationFx = Callable[[Input, Optional[np.ndarray], Optional[int]], np.ndarray]

def factory(name: str, params: list[Any]) -> EvaluationFx:
    '''Factory method for creating characteristic functions.

    Args:
        name (str): implemented characteristics...
            [timing, magnitude, duration, rate_of_change, frequency]
        params (list[Any]): required parameters for the characteristic function.
            i.e. [start, end] for timing, [ma_nperiods, threshold, symbol] for magnitude, etc.

    Raises:
        NotImplementedError: if the characteristic is not implemented.

    Returns:
        EvaluationFx: Charactersitic evaluation function.
    '''
    match name:
        case 'timing':
            return timing(params[0], params[1])
        case 'magnitude':
            return magnitude(params[0], params[1], params[2])
        case 'duration':
            return duration(params[0], params[1], params[2])
        case 'rate_of_change':
            return rate_of_change(params[0], params[1], params[2])
        case 'frequency':
            return frequency(params[0], params[1], params[2], params[3])
        case _:
            raise NotImplementedError(
                f'''The {name} characteristic is not implemented,
                in the characteristic factory method.''')

def timing(start: int = 0, end: int = 367) -> EvaluationFx:
    '''Closure for evaluating timing characteristics.

    Args:
        start (int): Day of water year. Defaults to 0.
        end (int): Day of water year. Defaults to 367.
    
    Returns:
        EvaluationFx: Timing characteristic evaluation function.
    '''
    # pylint: disable=unused-argument
    def evaluate(data: Input,
                 outputs: np.ndarray|None = None, order: int|None = None) -> np.ndarray:
        @np.vectorize
        def f(day: int) -> int:
            return 1 if start <= day < end else 0
        return f(data.dsowy)
    return evaluate

def magnitude(ma_nperiods: int = 1, threshold: float = 0, symbol: str = '>') -> EvaluationFx:
    '''Closure for evaluating magnitude characteristics.

    Args:
        ma_nperiods (int): Periods over which to average (moving average) flow. Defaults to 1.
        threshold (float): Magnitude threshold. Defaults to 0.
        symbol (str): Magnitude comparision operator(i.e., <, <=, ...). Defaults to '>'.

    Returns:
        EvaluationFx: Magnitude characteristic evaluation function.
    '''
    _operator = match_symbol(symbol)
    # pylint: disable=unused-argument
    def evaluate(data: Input,
                 outputs: np.ndarray|None = None, order: int|None = None) -> np.ndarray:
        flows = (data.flows if ma_nperiods == 1
                 else pd.Series(data.flows).rolling(ma_nperiods, min_periods=1).mean().to_numpy())
        @np.vectorize
        def f(flow: float) -> np.int32:
            return 1 if _operator(flow, threshold) else 0
        return f(flows)
    return evaluate

def duration(nperiods: int = 1,
             row_pattern: np.ndarray|None = None, symbol: str = ">") -> EvaluationFx:
    '''Closure for evaluating duration characteristics.

    Args:
        nperiods (int): Periods of which pattern duration is evaluated. Defaults to 1.
        row_pattern (Optional[np.ndarray]): Timestep pattern to search. Defaults to None.
        symbol (str): Duration comparison operator (i.e., <, <=, ...). Defaults to ">".

    Returns:
        EvaluationFx: Duration characteristic evaluation function.
    '''
    _operator = match_symbol(symbol)
    def evaluate(data: Input, outputs: np.ndarray, order: int = 3) -> np.ndarray:
        n, rows = 0, len(data.flows)
        out = np.zeros(rows, dtype=np.int32)
        pattern = np.ones(order-1, dtype=np.int32) if row_pattern is None else row_pattern
        for i in range(0, len(out)):
            if np.array_equal(outputs[i,:order-1], pattern):
                n+=1
            else:
                # IF pattern has met comparision (<, >, ...), duration condition.
                if _operator(n, nperiods):
                    out[i-n:i] = 1  # Marks entire period over which duration condition is met.
                n = 0
        return out
    return evaluate

def rate_of_change(ma_nperiods: int = 1,
                   threshold_factor: float = 2, symbol: str = '>') -> EvaluationFx:
    '''Closure for evaluating rate of change characteristics.

    Args:
        ma_nperiods (int): Periods over which to average (moving average) flow. Defaults to 1.
        threshold_factor (float): Flow delta threshold as portion of previous flow. Defaults to 2.
        symbol (str): Rate of change comparison operator. Defaults to '>'.

    Returns:
        EvaluationFx: Rate of change characteristic evaluation function.
    '''
    _operator = match_symbol(symbol)
    # pylint: disable=unused-argument
    def evaluate(data: Input,
                 outputs: np.ndarray|None = None, order: int|None = None) -> np.ndarray:
        flows = (data.flows if ma_nperiods == 1
                 else pd.Series(data.flows).rolling(ma_nperiods, min_periods=1).mean().to_numpy())
        out = np.zeros(len(data.flows), dtype=np.int32)
        for i in range(1, len(out)):
            if flows[i-1] == 0:
                # so there is no divide by zero error
                change = 0 if flows[i] == 0 else 1
            else:
                # min function prevents tiny previous day values from evaluating toward infinity.
                change = min((flows[i] - flows[i-1]) / flows[i-1], 100)
            out[i] = 1 if _operator(change, threshold_factor) else 0
        return out
    return evaluate

def frequency(n_times: int, n_years: int,
              row_pattern: np.ndarray, symbol: str = '>') -> EvaluationFx:
    '''Closure for evaluating frequency characteristics.

    Args:
        n_times (int): Number of times pattern must occur in n_years. Defaults to 1.
        n_years (int): Number of years over which pattern is evaluated. Defaults to 1.
        row_pattern (np.ndarray): Pattern to search.
        symbol (str, optional): Comparision operator for frequency of pattern. Defaults to '>'.

    Returns:
        EvaluationFx: Frequency characteristic evaluation function.
    '''
    _operator = match_symbol(symbol)
    def evaluate(data: Input, outputs: np.ndarray, order = 2) -> np.ndarray:
        # pylint: disable=invalid-name
        T, n, yrs = len(data.flows), 0, []
        # count number of occurances each year
        for i in range(0, T):
            if data.dsowy[i] == 1 or i == T-1:
                yrs.append(n)
                n = 0
            if np.array_equal(outputs[i,:order-1], row_pattern):
                n += 1
        # count rolling sum of ntimes per nyear period, if n_times < ntimes then 1 o/w 0.
        out_yrs = np.where(pd.Series(
            np.array(yrs, dtype=np.int32)).rolling(n_years, min_periods=1).sum() < n_times, 0, 1)
        # if criteria was met for year then fill in ones for each day in year, otherwise 0.
        t, out = 0, np.zeros(len(data.flows), dtype=np.int32)
        for i, _ in enumerate(out):
            if data.dsowy[i] == 1:
                t += 1
            out[i] = out_yrs[t]
        return out
    return evaluate

