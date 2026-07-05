# Copyright (c) Microsoft. All rights reserved.

from typing import Any

custom_prompt_evaluator = """
You are an AI assistant that ...
Score the response on a scale of 1 to 5, where 1 is ... and 5 is ...
Provide a brief reason for your score.

### Input:
Query:
{{query}}
Response:
{{response}}

You must output your result in the following JSON format:
{
    "result": <integer from 1 to 5>,
    "reason": "<brief explanation>"
}
Do not output markdown code blocks. Output raw JSON only.
"""

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
