'''Defines the functional flow component and scoring criteria classes.

Following the template in:

Yarnell, S. M., Stein, E. D., Webb, J. A., Grantham, T., Lusardi, R. A., Zimmerman, J.,
Peek, R. A., Lane, B. A., Howard, J., & Sandoval-Solis, S. (2020). 
A functional flows approach to selecting ecologically relevant flow metrics
for environmental flow applications. 
River Research and Applications, 36(2), 318–324. 
https://doi.org/10.1002/rra.3575 
'''
from typing import Any
from dataclasses import dataclass, field

import numpy as np

from functionalflows.model.data import Input, Output
from functionalflows.model.characteristic import EvaluationFx

@dataclass
class ScoringCriteria:
    '''
    Defines how success of failure of a component is determined.
    '''
    scoring_pattern: list['Any']
    '''Elements corresponding with success/failure values of characteristic
    evaluation functions that collectively determine component success or failure.'''
    is_success_pattern: bool = True
    '''True if the scoring pattern describes success, False if it describes failure.'''
    matching_pattern: np.array = field(init=False)
    '''Created from the scoring pattern by removing wildcard elements,
    used to describes component succes or failure.'''
    wildcard_positions: np.ndarray = field(init=False)
    '''Int positions of wildcard elements (i.e. '*'s) in the scoring pattern.'''

    def __post_init__(self) -> None:
        self.matching_pattern = np.array(
            [v for v in self.scoring_pattern if v !='*'], dtype=np.int32)
        self.wildcard_positions = np.array(
            [i for i in range(0, len(self.scoring_pattern)) if self.scoring_pattern[i]=='*'],
            dtype=np.int32)

    def score(self, outputs: np.ndarray) -> np.ndarray:
        '''Scores component by matching characteristic scores to the component scoring pattern.'''
        c = len(self.scoring_pattern)
        for i in range(0, outputs.shape[0]):
            outputs[i,c] = 1 if self.match(outputs[i,:c]) else 0
            #outputs[i,c] = 1 if np.array_equal(outputs[i,:c], self.scoring_pattern) else 0
        return outputs

    def match(self, output: np.ndarray) -> bool:
        if len(self.wildcard_positions) > 0:
            patterned = np.delete(output, self.wildcard_positions)
            return np.array_equal(patterned, self.matching_pattern)
        else:
            return np.array_equal(output, self.matching_pattern)

    def name(self):
        return 'success' if self.is_success_pattern else 'failure'

@dataclass
class Component:
    name: str
    characteristics: dict[str, EvaluationFx] # order of key, item pairs is preserved in python 3.7+
    scoring_criteria: ScoringCriteria

    def evaluate(self, data: Input) -> Output:
        i = 0
        rows, columns =len(data.flows), len(self.characteristics)+1
        outputs = np.zeros(shape=(rows, columns), dtype=np.int32)       
        for _, v in self.characteristics.items():
            outputs[:, i] = v(data, outputs)
            i += 1
        output_names = list(self.characteristics.keys()) + [self.scoring_criteria.name()]
        return Output(component_name=self.name, characteristic_names=output_names, data=self.scoring_criteria.score(outputs))
