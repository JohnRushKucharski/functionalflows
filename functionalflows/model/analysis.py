import pandas as pd

from dataclasses import dataclass
from typing import List

from functionalflows.model.data import Input
from functionalflows.model.component import Component

@dataclass
class Analysis:
    data: Input
    components: List[Component]
    
    def run(self, output_path: str = ''):
        outputs = []
        for component in self.components:
            outputs.append(component.evaluate(self.data))
        if output_path:
            df = self.data.to_df(reset_index=True)
            for output in outputs:
                df = df.join(output.to_df())
            df.to_csv(output_path)  
        return outputs
            