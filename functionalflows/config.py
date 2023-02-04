from typing import List, Dict, Any

import tomli
import numpy as np

from functionalflows.model.data import Input
from functionalflows.model.analysis import Analysis
from functionalflows.model.component import Component
from functionalflows.model.characteristic import factory

def build_components(data: Dict[str, Any]):
    components = []
    for k, v in data['components'].items():
        components.append(build_component(name=k, data=v))
    return components
 
def build_component(name: str, data: Dict[str, List[Any]]) -> Component:
    characteristics = {}
    for i in range(0, len(data['characteristics'])):
        characteristics[data['characteristics'][i]] = factory(data['characteristics'][i], data['parameters'][i]) 
    return Component(name, characteristics, np.array(data['scoring_pattern'], dtype=np.int32))

def read_config_file(path: str) -> List[Component]:
    with open(path, 'rb') as f:
        data = tomli.load(f)
    return data   

def setup(config_filepath: str, input_filepath: str) -> Analysis:
    config_data = read_config_file(config_filepath)
    return Analysis(Input.from_csv(input_filepath, config_data['first_day_of_water_year']), build_components(config_data))