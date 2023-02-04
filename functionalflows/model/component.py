import numpy as np

from dataclasses import dataclass
from typing import OrderedDict, Callable

from functionalflows.model.data import Input, Output

@dataclass
class Component:
    name: str
    characteristics: OrderedDict[str, Callable[[Input, np.ndarray, int], np.ndarray]]
    scoring_pattern: np.ndarray
    
    def evaluate(self, data: Input) -> Output:
        i = 0
        rows, columns =len(data.flows), len(self.characteristics)+1
        outputs = np.zeros(shape=(rows, columns), dtype=np.int32)       
        for _, v in self.characteristics.items():
            outputs[:, i] = v(data, outputs)
            i += 1
        return Output(self.name, list(self.characteristics.keys()), self.score(outputs))
    
    def score(self, outputs: np.ndarray):
        c = len(self.scoring_pattern)
        for i in range(0, outputs.shape[0]):
            outputs[i,c] = 1 if np.array_equal(outputs[i,:c], self.scoring_pattern) else 0
        return outputs
