# Copyright (c) Microsoft. All rights reserved.

from typing import Any


def custom_code_evaluator(sample: dict[str, Any], item: dict[str, Any]) -> float:
    """
    A simple custom evaluator.
    
    Arguments:
    - sample (dict): The output from the agent. Contains:
        - 'output_text': The string response.
        - 'tool_calls': List of tool calls made.
        - 'tool_definitions': List of tools available.
    - item (dict): The input data row. Contains keys from your dataset (e.g., 'query').
    
    Returns:
    - A float score from 0.0 to 1.0.
    """
    return 0.0
