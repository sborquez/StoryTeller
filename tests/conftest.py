import json
import os
from typing import Any, Dict

from pytest import fixture


@fixture
def sample_data() -> Dict[str, Any]:
    # Get this file folder
    folder = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(folder, "data", "sample.json")
    with open(data_folder) as json_file:
        data = json.load(json_file)
    return data


@fixture
def node_data(sample_data: Dict[str, Any]) -> Dict[str, Any]:
    return sample_data["root"]


@fixture
def pages_data(sample_data: Dict[str, Any]) -> Dict[str, Any]:
    return sample_data["pages"]
