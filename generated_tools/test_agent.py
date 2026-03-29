# Copyright (c) Microsoft. All rights reserved.

import os

from dotenv import load_dotenv
from pytest_agent_evals import (AzureOpenAIModelConfig, BuiltInEvaluatorConfig,
                                CustomCodeEvaluatorConfig,
                                CustomPromptEvaluatorConfig, EvaluatorResults,
                                FoundryAgentConfig, evals)

load_dotenv()

# Configuration for the Evaluator (Judge)
# We use standard AOAI environment variables for the evaluator
EVAL_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
EVAL_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Configuration for the Agent
# The endpoint for the Foundry Project where the agent is hosted
PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

from evaluators import custom_code_evaluator, custom_prompt_evaluator

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

    @evals.evaluator(BuiltInEvaluatorConfig("intent_resolution"))
    def test_intent_resolution(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'intent_resolution' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.intent_resolution.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("tool_call_accuracy"))
    def test_tool_call_accuracy(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'tool_call_accuracy' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.tool_call_accuracy.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("task_adherence"))
    def test_task_adherence(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'task_adherence' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.task_adherence.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("relevance"))
    def test_relevance(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'relevance' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.relevance.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("coherence"))
    def test_coherence(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'coherence' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.coherence.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("fluency"))
    def test_fluency(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'fluency' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.fluency.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("similarity"))
    def test_similarity(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'similarity' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.similarity.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("f1_score"))
    def test_f1_score(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'f1_score' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.f1_score.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("bleu_score"))
    def test_bleu_score(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'bleu_score' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.bleu_score.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("gleu_score"))
    def test_gleu_score(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'gleu_score' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.gleu_score.result == "pass"

    @evals.evaluator(BuiltInEvaluatorConfig("meteor_score"))
    def test_meteor_score(self, evaluator_results: EvaluatorResults):
        """
        Tests the 'meteor_score' of the agent's response.
        The evaluator is automatically run and the results are populated to evaluator_results.<evaluator_name>
        """
        # Assert that the result is pass
        assert evaluator_results.meteor_score.result == "pass"

    @evals.evaluator(
        CustomPromptEvaluatorConfig(
            name="custom_prompt_evaluator", prompt=custom_prompt_evaluator, threshold=3
        )
    )
    def test_custom_prompt_evaluator(self, evaluator_results: EvaluatorResults):
        """
        Tests a custom criteria using a custom prompt template.
        The `custom_prompt_evaluator` defines the instructions for the LLM judge.
        """
        # Result is automatically calculated as "pass" if the LLM judged score meets the threshold
        assert evaluator_results.custom_prompt_evaluator.result == "pass"

    @evals.evaluator(
        CustomCodeEvaluatorConfig(
            name="custom_code_evaluator", grader=custom_code_evaluator, threshold=0.5
        )
    )
    def test_custom_code_evaluator(self, evaluator_results: EvaluatorResults):
        """
        Tests a custom criteria using a Python function.
        The `custom_code_evaluator` defines the grading logic.
        """
        # Result is automatically calculated as "pass" if the grading score meets the threshold
        assert evaluator_results.custom_code_evaluator.result == "pass"
