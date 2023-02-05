import numpy as np

from dataclasses import dataclass, field
from typing import List, OrderedDict, Callable, Any

from functionalflows.model.data import Input, Output

@dataclass
class ScoringCriteria:
    scoring_pattern: List['Any']
    is_success_pattern: bool = True
    matching_pattern: np.array = field(init=False)  
    wildcard_positions: np.ndarray = field(init=False)
    
    def __post_init__(self) -> None:
        self.matching_pattern = np.array([v for v in self.scoring_pattern if v !='*'], dtype=np.int32)
        self.wildcard_positions = np.array([i for i in range(0, len(self.scoring_pattern)) if self.scoring_pattern[i]=='*'], dtype=np.int32)
        
    def score(self, outputs: np.ndarray) -> np.ndarray:
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
    characteristics: OrderedDict[str, Callable[[Input, np.ndarray, int], np.ndarray]]
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