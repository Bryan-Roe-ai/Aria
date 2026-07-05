# Copyright (c) Microsoft. All rights reserved.

import os

from dotenv import load_dotenv
from pytest_agent_evals import (
    AzureOpenAIModelConfig,
    CustomCodeEvaluatorConfig,
    EvaluatorResults,
    FoundryAgentConfig,
    evals,
)

load_dotenv()

# Configuration for the Evaluator (Judge)
# We use standard AOAI environment variables for the evaluator
EVAL_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
EVAL_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Configuration for the Agent
# The endpoint for the Foundry Project where the agent is hosted
PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")


from evaluators import custom_code_evaluator

# --- Tests ---

# The Test Class is the main entry point for defining your evaluation suite.
# We use decorators to configure the agent, dataset, and judge model.


@evals.dataset("data.jsonl")  # Specifies the input dataset file (JSONL format)
@evals.judge_model(
    AzureOpenAIModelConfig(deployment_name=EVAL_DEPLOYMENT, endpoint=EVAL_ENDPOINT)
)  # Configures the LLM used for "Judge" evaluators
@evals.agent(
    FoundryAgentConfig(agent_name="agent", project_endpoint=PROJECT_ENDPOINT)
)  # Links this test class to the Foundry agent
class Test_agent:
    """
    Test class for the Agent: agent.
    Each method represents a specific evaluation criteria (e.g., Relevance, Coherence).
    """

    @evals.evaluator(
        CustomCodeEvaluatorConfig(name="custom_code_evaluator", grader=custom_code_evaluator, threshold=0.5)
    )
    def test_custom_code_evaluator(self, evaluator_results: EvaluatorResults):
        """
        Tests a custom criteria using a Python function.
        The `custom_code_evaluator` defines the grading logic.
        """
        # Result is automatically calculated as "pass" if the grading score meets the threshold
        assert evaluator_results.custom_code_evaluator.result == "pass"
