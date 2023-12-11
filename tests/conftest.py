import json
import os
from typing import Any, Dict

from pytest import fixture


@fixture
def sample_data_file() -> str:
    # Get this file folder
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, "data", "sample.json")


@fixture
def sample_data(sample_data_file: str) -> Dict[str, Any]:
    # Get this file folder
    with open(sample_data_file) as json_file:
        data = json.load(json_file)
    return data


@fixture
def node_data(sample_data: Dict[str, Any]) -> Dict[str, Any]:
    return sample_data["root"]


@fixture
def pages_data(sample_data: Dict[str, Any]) -> Dict[str, Any]:
    return sample_data["pages"]
