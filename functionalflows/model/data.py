from functools import partial
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from functionalflows.utilities import day_of_water_year

@dataclass
class Input:
    dates: pd.Series
    flows: np.ndarray
    start_of_water_year: int = 274
    dsowy: np.ndarray = field(init=False)

    def __post_init__(self):
        self.dsowy = self.dates.apply(partial(day_of_water_year,
                                              start=self.start_of_water_year)).to_numpy()

    @classmethod
    def from_df(cls, df: pd.DataFrame, start_of_water_year: int = 274):
        return cls(pd.to_datetime(df['dates']), df['flows'].to_numpy(), start_of_water_year)

    @classmethod
    def from_csv(cls, path: str, start_of_water_year: int = 274):
        return cls.from_df(pd.read_csv(path), start_of_water_year)

    def to_df(self, reset_index=False):
        df = pd.DataFrame(data=self.flows, index=self.dates, columns=['flows'])
        df['day_of_water_year'] = self.dsowy
        return df.reset_index() if reset_index else df

@dataclass
class Output:
    component_name: str
    characteristic_names: list[str]
    data: np.ndarray

    def to_df(self):
        output = {}
        for i in range(0, len(self.characteristic_names)):
            output[f'{self.component_name}_{self.characteristic_names[i]}'] = self.data[:, i]
        #output[self.component_name] = self.data[:,i] #self.vulnerability()
        return pd.DataFrame.from_dict(output)

    # def vulnerability(self):
    #     output = np.ones(len(self.data), dtype=np.int32)
    #     for i in range(0, self.data.shape[1]):
    #         output = np.multiply(output, self.data[:,i])
    #     return output
