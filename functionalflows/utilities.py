from datetime import datetime

import numpy as np

def day_of_water_year(dt, start: int = 274) -> int:
    '''Computes day of water year for a given date. 
    Provided a integer day of year starting day for normal (non-leap year) water years.
    
    Parameters
    ----------
    dt: pandas.datetime
        The date to be evaluated.
    start: int 
        The day of the year in which a new water year begins during non-leap years.
        
    Returns
    -----------
    int
        The day in the water year for the provided date time parameter.
    
    Raises
    -----------
    ValueError
        if start > 365
    
    '''
    if start > 365:
        raise ValueError('The start date is invalid.')
    else:
        end = 366 if dt.is_leap_year else 365
        start = start + 1 if start < 60 and dt.is_leap_year else start
        return dt.dayofyear + (end - start) if dt.dayofyear < start else dt.dayofyear - (start - 1)
    
def days_to_hours(days: float) -> float:
    return days * 24
def hours_to_minutes(hours: float) -> float:
    return hours * 60
def minutes_to_seconds(mins: float) -> float:
    return mins * 60
def liters_to_m3(liters: float) -> float:
    return liters / 1000
def liters_per_day_to_m3_per_second(lpd: float) -> float:
    return liters_to_m3(lpd) / (days_to_hours(1) * hours_to_minutes(1) * minutes_to_seconds(1))

# def dowy(dt: datetime) -> np.ndarray:
#     oct1 = 275 if dt.is_leap_year else 274
#     return dt + 92 if dt < oct1 else dt - (oct1 - 1)

# def dsowy(ts: np.ndarray) -> np.ndarray:
#     f = np.vectorize(dowy)
#     return f(ts)