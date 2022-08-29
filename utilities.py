from datetime import datetime

import numpy as np

def dowy(dt):
    oct1 = 275 if dt.is_leap_year else 274
    return dt.dayofyear + 92 if dt.dayofyear < oct1 else dt.dayofyear - (oct1 - 1) 

# def dowy(dt: datetime) -> np.ndarray:
#     oct1 = 275 if dt.is_leap_year else 274
#     return dt + 92 if dt < oct1 else dt - (oct1 - 1)

# def dsowy(ts: np.ndarray) -> np.ndarray:
#     f = np.vectorize(dowy)
#     return f(ts)