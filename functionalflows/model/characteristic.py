import numpy as np
import pandas as pd

import operator
from typing import List, Callable, Any

from functionalflows.model.data import Input

def match_symbol(symbol: str = ">"):
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

def factory(name: str, params: List[Any]) -> Callable[[Input, np.ndarray, int], np.ndarray]:
    match name:
        case 'timing':
            return timing(params[0], params[1])
        case 'magnitude':
            return magnitude(params[0], params[1], params[2])
        case 'duration':
            return duration(params[0], params[1], params[2])
        case 'rate_of_change':
            return rate_of_change(params[0], params[1], params[2])
        case _:
            raise NotImplementedError(f'The {name} characteristic is not implemented, in the characteristic factory method.')

def timing(start: int = 0, end: int = 367):
    def evaluate(data: Input, outputs: np.ndarray, order=1) -> np.ndarray:
        @np.vectorize
        def f(day: int) -> np.int32:
            return 1 if start <= day < end else 0
        return f(data.dsowy)
    return evaluate

def magnitude(ma_nperiods: int = 1, threshold: float = 0, symbol: str = '>'):
    _operator = match_symbol(symbol)
    def evaluate(data: Input, outputs: np.ndarray, order=2) -> np.ndarray:
        flows = data.flows if ma_nperiods == 1 else pd.Series(data.flows).rolling(ma_nperiods, min_periods=1).mean().to_numpy() 
        @np.vectorize
        def f(flow: float) -> np.int32:
            return 1 if _operator(flow, threshold) else 0
        return f(flows)
    return evaluate

def duration(nperiods: int = 1, row_pattern: np.ndarray = None, symbol: str = ">"):
    _operator = match_symbol(symbol)
    def evaluate(data: Input, outputs: np.ndarray, order=3):
        n, rows = 0, len(data.flows)
        out = np.zeros(rows, dtype=np.int32)
        pattern = np.ones(order-1, dtype=np.int32) if row_pattern is None else row_pattern
        for i in range(0, len(out)):
            if np.array_equal(outputs[i,:order-1], pattern):
                n+=1 
            else:
                if _operator(n, nperiods):  # for instance n ">" n_periods (row pattern has been met enough times), or n "<" n_periods (row pattern not met enough times)
                    out[i-n:i] = 1          # entire period when duration condition is met
                n = 0
        return out
    return evaluate
    
    # def evaluate(data: Input, outputs: np.ndarray, order=3) -> np.ndarray:
    #     n, rows = 0, len(data.flows)
    #     out = np.zeros(rows, dtype=np.int32)
    #     for i in range(0, len(out)):
    #         if outputs[i,:].sum() == order:
    #             n += 1
    #         else:
    #             if n > nperiods:
    #                 out[i-n:i] = 1
    #             n = 0
    #     return out
    # return evaluate

def rate_of_change(ma_nperiods: int = 1, threshold_factor: float = 2, symbol: str = '>'):
    _operator = match_symbol(symbol)
    def evaluate(data: Input, outputs: np.ndarray, order=3) -> np.ndarray:
        flows = data.flows if ma_nperiods == 1 else pd.Series(data.flows).rolling(ma_nperiods, min_periods=1).mean().to_numpy() 
        out = np.zeros(len(data.flows), dtype=np.int32)
        for i in range(1, len(out)):
            if flows[i-1] == 0:
                # so there is no divide by zero error
                change = 0 if flows[i] == 0 else 1
            else:
                # min function prevents very tiny previous day values to evaluating toward infinity.
                change = min((flows[i] - flows[i-1]) / flows[i-1], 100)
            out[i] = 1 if _operator(change, threshold_factor) else 0
        return out
    return evaluate