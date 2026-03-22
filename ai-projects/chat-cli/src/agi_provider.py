"""
AGI (Artificial General Intelligence) Enhanced Chat Provider

This module implements advanced reasoning capabilities for the Aria platform:
- Multi-step reasoning (chain-of-thought)
- Goal-oriented task decomposition
- Self-reflection and response improvement
- Memory/context management

The AGI provider wraps an underlying provider (Azure/OpenAI/Local) and enhances
responses with structured reasoning processes.

Security considerations:
- Input is sanitized to prevent injection attacks
- Content length is limited to prevent DoS
- Error messages are sanitized to prevent information leakage
"""
from __future__ import annotations

import html
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Iterable, List, Optional

from chat_providers import (
    BaseChatProvider,
    ProviderChoice,
    RoleMessage,
    detect_provider,
)

# Configure logger for security events
_logger = logging.getLogger(__name__)

# Security constants
MAX_INPUT_LENGTH = 10000  # Maximum characters per input
MAX_HISTORY_SIZE = 50  # Maximum conversation history entries
MAX_GOALS = 5  # Maximum active goals
MAX_REASONING_CHAINS = 10  # Maximum stored reasoning chains

# ---------------------------------------------------------------------------
# Agent Registry
# ---------------------------------------------------------------------------
# Each entry drives agent selection, subtask generation, reasoning hints,
# response validation, and fallback generation for the AGI reasoning pipeline.
#
# Trigger scoring in _select_agent():
#   domain  match → weight 3  (matches analysis["domain"])
#   intent  match → weight 2  (matches analysis["intent"])
#   keyword match → weight 1  per keyword found in query
#
_AGENT_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ---------------------------------------------------------------- Aria --
    "aria-character": {
        "description": "Interactive 3D character — movement, gestures, world generation",
        "triggers": {
            "intent": {"movement"},
            "domain": {"aria"},
            "keywords": {
                "move", "walk", "jump", "wave", "dance", "spin", "pickup",
                "drop", "throw", "animate", "gesture", "world", "stage",
            },
        },
        "subtasks": {
            "movement": [
                "parse direction/action intent",
                "select animation tag",
                "generate natural acknowledgement",
                "embed [aria:tag] in response",
            ],
            "creation": [
                "identify environment theme",
                "list objects and props",
                "generate world configuration",
                "confirm world created",
            ],
            "default": [
                "parse action intent",
                "select appropriate animation",
                "compose response with action tag",
            ],
        },
        "reasoning_hints": [
            "Aria context: always embed [aria:action] tags for movement or gesture requests.",
            "Full tag set: [aria:walk:left/right/up/down], [aria:jump], [aria:wave], [aria:dance], [aria:spin], [aria:idle].",
        ],
        "validation": {
            "require_aria_tag": True,
        },
        "fallback": {
            "left":  "Moving left! [aria:walk:left]",
            "right": "Moving right! [aria:walk:right]",
            "up":    "Moving up! [aria:walk:up]",
            "down":  "Moving down! [aria:walk:down]",
            "jump":  "Jumping! [aria:jump]",
            "wave":  "Hello there! [aria:wave]",
            "dance": "Time to dance! [aria:dance]",
            "spin":  "Spinning! [aria:spin]",
            "idle":  "Returning to idle. [aria:idle]",
        },
        "fallback_generic": "I'm ready! Tell me what to do. [aria:idle]",
    },
    # ------------------------------------------------------------- Quantum --
    "quantum": {
        "description": "Quantum computing — circuits, algorithms, Qiskit, Azure Quantum",
        "triggers": {
            "domain": {"quantum"},
            "keywords": {
                "quantum", "qubit", "circuit", "gate", "superposition",
                "entanglement", "qiskit", "pennylane", "azure quantum",
                "variational", "vqe", "grover", "shor", "hadamard",
            },
        },
        "subtasks": {
            "explanation": [
                "define the quantum concept clearly",
                "use a classical analogy",
                "show Qiskit or PennyLane code",
                "compare to classical equivalent",
            ],
            "coding": [
                "identify algorithm type (VQE, Grover, Shor, etc.)",
                "design qubit layout and gate sequence",
                "implement circuit with Qiskit",
                "add measurement and sampling",
                "estimate gate depth and complexity",
            ],
            "creation": [
                "clarify QPU target (simulator vs real hardware)",
                "design and validate circuit locally first",
                "implement Azure Quantum job submission",
                "add job-status monitoring",
            ],
            "default": [
                "identify quantum vs classical scope",
                "choose simulation or hardware approach",
                "structure hybrid quantum-classical pipeline if needed",
            ],
        },
        "reasoning_hints": [
            "Quantum context: always distinguish simulation from real QPU execution.",
            "Quantify speedup claims precisely (quadratic vs. exponential).",
            "Reference Qiskit or PennyLane syntax for all code examples.",
        ],
        "validation": {},
        "fallback": (
            "Quantum quick start:\n"
            "  from qiskit import QuantumCircuit\n"
            "  qc = QuantumCircuit(2)\n"
            "  qc.h(0); qc.cx(0, 1)\n"
            "  print(qc.draw())\n"
            "MCP server: python ai-projects/quantum-ml/quantum_mcp_server.py"
        ),
        "fallback_generic": None,
    },
    # --------------------------------------------------- Autonomous Trainer --
    "autonomous-trainer": {
        "description": "LoRA fine-tuning, dataset curation, model promotion, continuous learning",
        "triggers": {
            "keywords": {
                "train", "fine-tune", "finetune", "lora", "training", "dataset",
                "epoch", "checkpoint", "adapter", "promote", "overfitting",
                "autotrain", "autonomous training",
            },
        },
        "subtasks": {
            "creation": [
                "dry-run: python scripts/autotrain.py --dry-run",
                "verify dataset format (JSONL messages list)",
                "launch training job",
                "monitor data_out/autotrain/status.json",
                "auto-promote if accuracy > 0.90",
            ],
            "explanation": [
                "describe the 6-stage cycle (discovery → collection → training → analysis → optimization → deployment)",
                "explain adaptive epoch selection [25, 50, 100, 200]",
                "show monitoring: tail -f data_out/autonomous_training.log",
            ],
            "coding": [
                "identify base model (TinyLlama, Mistral, etc.)",
                "configure LoRA rank, alpha, and target_modules",
                "set up data collator and Trainer",
                "add checkpointing and early stopping",
            ],
            "default": [
                "dry-run orchestrator first",
                "check dataset availability",
                "run quick training pass",
                "evaluate output metrics",
            ],
        },
        "reasoning_hints": [
            "Training context: always dry-run before GPU/QPU execution.",
            "Datasets are read-only — all outputs go to data_out/<orchestrator>/.",
            "LoRA adapters require both adapter_config.json + adapter_model.safetensors.",
        ],
        "validation": {},
        "fallback": (
            "Training quick start:\n"
            "  python scripts/autotrain.py --dry-run            # validate first\n"
            "  python scripts/automated_training_pipeline.py --quick\n"
            "  nohup python scripts/autonomous_training_orchestrator.py \\\n"
            "        > data_out/autonomous_training.log 2>&1 &"
        ),
        "fallback_generic": None,
    },
    # --------------------------------------------------------------- LLM Maker --
    "llm-maker": {
        "description": "Safe tool and website generation — ToolMaker and WebsiteMaker pipelines",
        "triggers": {
            "keywords": {
                "generate a tool", "create a function", "build a website",
                "make a web page", "tool maker", "website maker", "safe code generation",
            },
        },
        "subtasks": {
            "creation": [
                "define function name, parameters, and return type",
                "build safety-constrained generation prompt",
                "generate code and run AST safety validation",
                "retry with feedback if validation fails (max 3×)",
                "save validated tool to generated output",
            ],
            "coding": [
                "specify input/output contract",
                "enforce banned imports (os, sys, subprocess, socket)",
                "verify no eval/exec/open calls",
                "confirm function signature matches spec",
            ],
            "default": [
                "identify tool vs website vs function request",
                "gather name, description, and parameter spec",
                "invoke ToolMaker or WebsiteMaker pipeline",
            ],
        },
        "reasoning_hints": [
            "LLM-Maker context: all generated code is AST-validated for safety.",
            "Banned imports: os, sys, subprocess, socket, pickle, threading.",
            "Banned builtins: eval, exec, compile, __import__, open.",
        ],
        "validation": {},
        "fallback": (
            "Code/website generation:\n"
            "  ToolMaker:    ai-projects/llm-maker/src/tool_maker.py\n"
            "  WebsiteMaker: ai-projects/llm-maker/src/website_maker.py\n"
            "Both enforce AST-based safety validation before output."
        ),
        "fallback_generic": None,
    },
    # ---------------------------------------------------------------- AI/ML --
    "ai-ml": {
        "description": "AI/ML engineering — transformers, LoRA, RAG, embeddings, inference",
        "triggers": {
            "domain": {"ai"},
            "keywords": {
                "machine learning", "neural network", "transformer", "attention",
                "embedding", "rag", "retrieval", "huggingface", "pytorch",
                "diffusion", "llm inference", "model architecture",
            },
        },
        "subtasks": {
            "explanation": [
                "identify the model architecture",
                "explain the core mechanism (attention, LoRA ranks, etc.)",
                "compare trade-offs vs alternatives",
                "provide a concrete implementation example",
            ],
            "coding": [
                "identify framework (PyTorch / HuggingFace)",
                "design architecture with layer dimensions",
                "implement training loop with optimizer and scheduler",
                "add evaluation loop with metrics (loss, accuracy, perplexity)",
                "note GPU/memory requirements",
            ],
            "creation": [
                "choose base model and downstream task type",
                "configure adapters or LoRA parameters",
                "prepare data loading pipeline",
                "launch training and monitor metrics",
                "evaluate and iterate on results",
            ],
            "default": [
                "clarify model type and downstream task",
                "identify data requirements",
                "suggest implementation approach with framework reference",
            ],
        },
        "reasoning_hints": [
            "AI/ML context: distinguish fine-tuning vs RAG vs prompting clearly.",
            "Include GPU/memory requirements when recommending training approaches.",
            "Reference HuggingFace Transformers or PyTorch idioms in examples.",
        ],
        "validation": {},
        "fallback": (
            "For AI/ML I can cover transformers, LoRA, RAG, embeddings, and inference.\n"
            "Quick environment check: python scripts/fast_validate.py"
        ),
        "fallback_generic": None,
    },
    # ----------------------------------------------------- Full-Stack Debug --
    "full-stack-debugger": {
        "description": "Cross-stack debugging — Python, Azure Functions, JavaScript, SQL",
        "triggers": {
            "keywords": {
                "bug", "error", "exception", "traceback", "debug",
                "not working", "fails", "crash", "broken", "stack trace",
            },
        },
        "subtasks": {
            "coding": [
                "reproduce with a minimal repro case",
                "inspect traceback from the most specific frame first",
                "check recent changes: git diff",
                "add targeted logging",
                "verify fix with a targeted test",
            ],
            "explanation": [
                "categorise error type (TypeError, ValueError, ImportError, etc.)",
                "identify root cause",
                "describe the correct pattern and how to avoid the issue",
            ],
            "default": [
                "isolate the failing component",
                "check logs in data_out/",
                "run python scripts/test_runner.py --unit",
                "verify environment (venv activated, env vars set)",
            ],
        },
        "reasoning_hints": [
            "Debug context: start from the most specific traceback frame.",
            "Health check: curl http://localhost:7071/api/ai/status | jq",
            "Run tests: python scripts/test_runner.py --unit",
        ],
        "validation": {},
        "fallback": (
            "To debug, share the full traceback. Quick checks:\n"
            "  python scripts/fast_validate.py\n"
            "  python scripts/test_runner.py --unit\n"
            "  curl http://localhost:7071/api/ai/status | jq"
        ),
        "fallback_generic": None,
    },
    # ---------------------------------------------------------- Vision AI --
    "vision-ai": {
        "description": "Vision AI — expression classification, TinyConvNet, CNN inference",
        "triggers": {
            "keywords": {
                "vision", "image", "expression", "emotion", "classify",
                "cnn", "convnet", "face", "recognition", "detect", "camera", "photo",
            },
        },
        "subtasks": {
            "explanation": [
                "describe TinyConvNet architecture",
                "explain the 7-class expression label mapping",
                "walk through the inference pipeline",
            ],
            "coding": [
                "load TinyConvNet checkpoint",
                "preprocess input image (resize to 48×48, normalise)",
                "run forward pass through the network",
                "decode top-k predictions with confidence scores",
            ],
            "default": [
                "check scripts/vision_inference.py availability",
                "identify the classification task and label set",
                "suggest appropriate model size for the use case",
            ],
        },
        "reasoning_hints": [
            "Vision context: Aria's TinyConvNet is in scripts/vision_inference.py.",
            "Expression classes (7): neutral, happy, surprised, sad, angry, fear, disgust.",
        ],
        "validation": {},
        "fallback": (
            "Vision AI: scripts/vision_inference.py — TinyConvNet expression classifier.\n"
            "7 classes: neutral, happy, surprised, sad, angry, fear, disgust."
        ),
        "fallback_generic": None,
    },
    # ------------------------------------------------------- Data Pipeline --
    "data-pipeline": {
        "description": "Batch evaluation, dataset management, benchmarking, metrics",
        "triggers": {
            "keywords": {
                "evaluate", "benchmark", "batch eval", "batch evaluator",
                "validation set", "test set", "perplexity", "bleu score",
            },
        },
        "subtasks": {
            "creation": [
                "define evaluation config in config/evaluation/",
                "set up batch_evaluator.py job list",
                "run dry-run pass",
                "collect results in data_out/batch_evaluator/",
            ],
            "explanation": [
                "describe evaluation pipeline (batch_evaluator.py)",
                "list available metrics (accuracy, perplexity, BLEU, etc.)",
                "show reporting commands",
            ],
            "default": [
                "identify evaluation targets (models, datasets)",
                "configure evaluation YAML",
                "launch evaluation run",
                "review data_out/batch_evaluator/status.json",
            ],
        },
        "reasoning_hints": [
            "Evaluation context: all outputs go to data_out/batch_evaluator/.",
            "Use python scripts/batch_evaluator.py for model evaluation runs.",
            "Training analytics: python scripts/training_analytics.py",
        ],
        "validation": {},
        "fallback": (
            "Batch evaluation:\n"
            "  python scripts/batch_evaluator.py\n"
            "  python scripts/training_analytics.py    # performance trends\n"
            "  python scripts/evaluation_autorun.py --dry-run"
        ),
        "fallback_generic": None,
    },
}

def _sanitize_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Raw input text.
        max_length: Maximum allowed length.

    Returns:
        Sanitized text.
    """
    if not isinstance(text, str):
        return ""

    # Truncate to max length
    text = text[:max_length]

    # Remove null bytes and other control characters (except newlines/tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text


def _sanitize_for_logging(text: str, max_length: int = 200) -> str:
    """
    Sanitize text for safe logging (no sensitive data exposure).

    Args:
        text: Text to sanitize.
        max_length: Maximum length for logs.

    Returns:
        Sanitized text safe for logging.
    """
    if not isinstance(text, str):
        return "[invalid]"

    # Truncate for logging
    text = text[:max_length]
    if len(text) == max_length:
        text += "..."

    # Escape any special characters
    text = html.escape(text)

    return text


@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning chain."""
    step_type: str  # 'decompose', 'analyze', 'synthesize', 'reflect', 'refine'
    content: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AGIContext:
    """Manages context and memory for AGI reasoning."""
    conversation_history: List[RoleMessage] = field(default_factory=list)
    reasoning_chains: List[List[ReasoningStep]] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    learned_patterns: Dict[str, Any] = field(default_factory=dict)
    max_history: int = MAX_HISTORY_SIZE

    def add_message(self, message: RoleMessage) -> None:
        """Add a message to conversation history with pruning and sanitization."""
        # Sanitize message content
        sanitized_msg = {
            "role": _sanitize_input(str(message.get("role", "user")), max_length=20),
            "content": _sanitize_input(str(message.get("content", "")))
        }
        self.conversation_history.append(sanitized_msg)
        if len(self.conversation_history) > self.max_history:
            # Keep system messages and recent messages
            system_msgs = [
                m for m in self.conversation_history if m.get("role") == "system"]
            other_msgs = [
                m for m in self.conversation_history if m.get("role") != "system"]
            # Keep last N messages
            keep_count = self.max_history - len(system_msgs)
            self.conversation_history = system_msgs + other_msgs[-keep_count:]

    def add_reasoning_chain(self, chain: List[ReasoningStep]) -> None:
        """Store a reasoning chain for future reference with limits."""
        self.reasoning_chains.append(chain)
        # Keep only last N chains to prevent memory issues
        if len(self.reasoning_chains) > MAX_REASONING_CHAINS:
            self.reasoning_chains = self.reasoning_chains[-MAX_REASONING_CHAINS:]

    def get_relevant_context(self, query: str) -> str:
        """Extract relevant context for the current query."""
        # Sanitize query input
        query = _sanitize_input(query)

        context_parts = []

        # Add recent conversation context
        recent = self.conversation_history[-6:]  # Last 3 exchanges
        if recent:
            context_parts.append("Recent conversation:")
            for msg in recent:
                role = _sanitize_for_logging(
                    str(msg.get("role", "unknown")), 20)
                content = _sanitize_for_logging(
                    str(msg.get("content", "")), 200)
                context_parts.append(f"  {role}: {content}")

        # Add active goals if any (limit to prevent injection)
        if self.goals:
            safe_goals = [_sanitize_for_logging(g, 50) for g in self.goals[:3]]
            context_parts.append(f"Active goals: {', '.join(safe_goals)}")

        return "\n".join(context_parts)


class AGIProvider(BaseChatProvider):
    """
    AGI-enhanced chat provider with advanced reasoning capabilities.

    This provider wraps an underlying chat provider (Azure/OpenAI/Local) and
    enhances responses through:

    1. Chain-of-Thought Reasoning: Breaks down complex queries into steps
    2. Task Decomposition: Identifies sub-goals for complex tasks  
    3. Self-Reflection: Evaluates and improves responses
    4. Context Management: Maintains relevant memory across interactions

    Usage:
        provider = AGIProvider()
        response = provider.complete([{"role": "user", "content": "Explain quantum computing"}])
    """

    def __init__(
        self,
        base_provider: Optional[BaseChatProvider] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        enable_chain_of_thought: bool = True,
        enable_self_reflection: bool = True,
        enable_task_decomposition: bool = True,
        reasoning_depth: int = 3,
        verbose: bool = False,
    ):
        """
        Initialize AGI provider.

        Args:
            base_provider: Underlying provider for LLM calls. Auto-detected if None.
            temperature: Sampling temperature for responses.
            max_output_tokens: Maximum tokens in output.
            enable_chain_of_thought: Enable step-by-step reasoning.
            enable_self_reflection: Enable response self-evaluation.
            enable_task_decomposition: Enable goal decomposition.
            reasoning_depth: Maximum reasoning chain depth.
            verbose: Include reasoning steps in output.
        """
        self.base_provider = base_provider
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.enable_chain_of_thought = enable_chain_of_thought
        self.enable_self_reflection = enable_self_reflection
        self.enable_task_decomposition = enable_task_decomposition
        self.reasoning_depth = min(max(1, reasoning_depth), 5)
        self.verbose = verbose
        self.context = AGIContext()

        self._base_provider_choice: Optional[ProviderChoice] = None
        self._last_agent_used: str = "general"

    def _get_base_provider(self) -> BaseChatProvider:
        """Lazily initialize and return the base provider."""
        if self.base_provider is None:
            # Use 'local' as default to avoid recursion - 'auto' could select 'agi'
            provider, choice = detect_provider(explicit="local")
            self.base_provider = provider
            self._base_provider_choice = choice
        return self.base_provider

    def complete(self, messages: List[RoleMessage], stream: bool = True) -> Iterable[str] | str:
        """
        Generate an AGI-enhanced response with security validation.

        Args:
            messages: Conversation history including the new user message.
            stream: Whether to stream the response.

        Returns:
            Response string or generator of response chunks.

        Security:
            - Input is sanitized to prevent injection attacks
            - Message count is limited to prevent DoS
            - Exceptions are caught without exposing internal details
        """
        # Validate and limit message count to prevent DoS
        if len(messages) > MAX_HISTORY_SIZE:
            messages = messages[-MAX_HISTORY_SIZE:]
            _logger.warning(
                "Message count exceeded limit, truncating to %d", MAX_HISTORY_SIZE)

        # Update context with new messages (use content comparison to avoid duplicates)
        existing_contents = {m.get("content", "")
                             for m in self.context.conversation_history}
        for msg in messages:
            content = msg.get("content", "")
            # Sanitize content before storage
            sanitized_content = _sanitize_input(str(content))
            if sanitized_content not in existing_contents:
                self.context.add_message(
                    {"role": msg.get("role", "user"), "content": sanitized_content})
                existing_contents.add(sanitized_content)

        # Extract and sanitize the latest user query
        user_query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_query = _sanitize_input(str(msg.get("content", "")))
                break

        if not user_query.strip():
            response = "I'm ready to help. What would you like to discuss?"
            return self._stream_text(response) if stream else response

        try:
            # Perform AGI reasoning pipeline
            reasoning_chain = self._reason(user_query, messages)

            # Generate final response
            response = self._generate_response(
                user_query, reasoning_chain, messages)

            # Self-reflection and improvement
            if self.enable_self_reflection:
                response = self._reflect_and_improve(
                    user_query, response, reasoning_chain)

            # Store reasoning chain
            self.context.add_reasoning_chain(reasoning_chain)
        except Exception as e:
            # Log error securely without exposing details to user
            _logger.error("AGI processing error: %s",
                          _sanitize_for_logging(str(e)))
            response = self._generate_fallback_response(
                user_query, {"intent": "general", "domain": "general"})

        if stream:
            return self._stream_text(response)
        return response

    def _reason(self, query: str, messages: List[RoleMessage]) -> List[ReasoningStep]:
        """
        Perform multi-step reasoning on the query.

        Args:
            query: The user's query.
            messages: Full conversation history.

        Returns:
            List of reasoning steps.
        """
        chain: List[ReasoningStep] = []

        # Step 1: Analyze query complexity and intent
        analysis = self._analyze_query(query)
        chain.append(ReasoningStep(
            step_type="analyze",
            content=analysis["summary"],
            confidence=analysis["confidence"],
            metadata=analysis
        ))

        # Step 2: Task decomposition for complex queries
        if self.enable_task_decomposition and analysis["complexity"] == "complex":
            subtasks = self._decompose_task(query, analysis)
            chain.append(ReasoningStep(
                step_type="decompose",
                content=f"Subtasks: {', '.join(subtasks)}",
                metadata={"subtasks": subtasks}
            ))

        # Step 3: Chain-of-thought reasoning
        if self.enable_chain_of_thought:
            thought_steps = self._chain_of_thought(query, analysis, messages)
            for step in thought_steps:
                chain.append(ReasoningStep(
                    step_type="synthesize",
                    content=step
                ))

        return chain

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine intent, complexity, and approach.

        Args:
            query: The user's query.

        Returns:
            Analysis dictionary with intent, complexity, etc.
        """
        query_lower = query.lower()
        words = query.split()

        # Determine complexity based on query characteristics
        complexity = "simple"
        if len(words) > 20:
            complexity = "complex"
        elif any(word in query_lower for word in ["explain", "compare", "analyze", "how", "why"]):
            complexity = "moderate"
        elif any(phrase in query_lower for phrase in ["step by step", "detailed", "comprehensive"]):
            complexity = "complex"

        # Identify intent using weighted scoring (handles overlapping signals)
        intent_scores: Dict[str, int] = {
            "movement": 0,
            "coding": 0,
            "explanation": 0,
            "creation": 0,
            "question": 0,
            "general": 0,
        }
        intent_signals = {
            "movement": ["move", "walk", "go", "jump", "dance", "wave", "run", "turn", "look at"],
            "coding": ["code", "program", "function", "debug", "implement", "refactor", "class", "bug", "error"],
            "explanation": ["explain", "what is", "how does", "why does", "describe", "what are", "define"],
            "creation": ["create", "generate", "make", "build", "write", "produce", "design"],
            "question": ["?"],
        }
        for intent_key, signals in intent_signals.items():
            for signal in signals:
                if signal in query_lower:
                    intent_scores[intent_key] += 1
        intent = max(intent_scores, key=lambda k: intent_scores[k])
        if intent_scores[intent] == 0:
            intent = "general"

        # Determine topic domain using weighted score to avoid first-match bias
        domain_keywords: Dict[str, List[str]] = {
            "quantum": ["quantum", "qubit", "entanglement", "superposition", "circuit", "qiskit", "pennylane"],
            "ai": ["ai", "machine learning", "neural", "model", "training", "llm", "lora", "fine-tun"],
            "aria": ["aria", "animation", "character", "gesture", "expression", "avatar"],
            "technical": ["code", "program", "api", "function", "database", "sql", "http", "endpoint"],
        }
        domain_scores: Dict[str, int] = {dom: 0 for dom in domain_keywords}
        for dom, keywords in domain_keywords.items():
            for kw in keywords:
                if kw in query_lower:
                    domain_scores[dom] += 1
        best_domain = max(domain_scores, key=lambda k: domain_scores[k])
        domain = best_domain if domain_scores[best_domain] > 0 else "general"

        # Confidence is higher when signals are unambiguous
        total_intent_signals = sum(intent_scores.values())
        confidence = min(
            0.95, 0.5 + 0.1 * total_intent_signals) if total_intent_signals > 0 else 0.5

        return {
            "query": query,
            "complexity": complexity,
            "intent": intent,
            "domain": domain,
            "word_count": len(words),
            "has_question": "?" in query,
            "confidence": confidence,
            "summary": f"{complexity.capitalize()} {intent} query about {domain}",
        }

    def _decompose_task(self, query: str, analysis: Dict[str, Any]) -> List[str]:
        """
        Break down a complex task into subtasks.

        Args:
            query: The user's query.
            analysis: Query analysis results.

        Returns:
            List of subtask descriptions.
        """
        subtasks = []
        intent = analysis.get("intent", "general")
        domain = analysis.get("domain", "general")

        # Generate subtasks based on intent
        if intent == "explanation":
            subtasks = [
                "Define key concepts",
                "Provide examples",
                "Explain relationships",
                "Summarize key points"
            ]
        elif intent == "coding":
            subtasks = [
                "Understand requirements",
                "Design solution approach",
                "Implement core logic",
                "Handle edge cases",
                "Provide usage examples"
            ]
        elif intent == "creation":
            subtasks = [
                "Clarify requirements",
                "Plan structure",
                "Create content",
                "Review and refine"
            ]
        elif intent == "movement" and domain == "aria":
            subtasks = [
                "Parse movement command",
                "Validate action type",
                "Generate movement tag"
            ]
        else:
            # Generic decomposition
            subtasks = [
                "Understand the request",
                "Gather relevant information",
                "Formulate response",
                "Verify accuracy"
            ]

        return subtasks[:self.reasoning_depth]

    def _chain_of_thought(
        self,
        query: str,
        analysis: Dict[str, Any],
        messages: List[RoleMessage]
    ) -> List[str]:
        """
        Generate chain-of-thought reasoning steps.

        Args:
            query: The user's query.
            analysis: Query analysis results.
            messages: Conversation history.

        Returns:
            List of thought steps.
        """
        thoughts = []
        intent = analysis.get("intent", "general")
        domain = analysis.get("domain", "general")

        # Context-aware thought generation
        thoughts.append(
            f"Understanding: This is a {analysis['complexity']} {intent} request.")

        if domain == "aria":
            thoughts.append(
                "Aria context: Need to consider character movement and animation.")
        elif domain == "quantum":
            thoughts.append(
                "Quantum context: Should explain concepts clearly with appropriate depth.")
        elif domain == "coding":
            thoughts.append(
                "Coding context: Focus on practical, working solutions.")

        # Add relevant context from memory
        relevant_context = self.context.get_relevant_context(query)
        if relevant_context and "Recent conversation" in relevant_context:
            thoughts.append("Considering conversation context for continuity.")

        thoughts.append(
            f"Approach: Will provide a {analysis['complexity']}-appropriate response.")

        return thoughts[:self.reasoning_depth]

    def _generate_response(
        self,
        reasoning_chain: List[ReasoningStep],

            def _select_agent(self, analysis: Dict[str, Any]) -> str:
                """
                Select the best specialist agent for the given query.

                Scores each registered agent against the query analysis:
                  - domain match  → weight 3
                  - intent match  → weight 2
                  - keyword match → weight 1 per keyword found in the raw query

                Returns the highest-scoring agent name, or ``"general"`` when no
                agent scores above zero.
                """
                query_lower = analysis.get("query", "").lower()
                intent = analysis.get("intent", "general")
                domain = analysis.get("domain", "general")

                best_agent = "general"
                best_score = 0

                for agent_name, agent_data in _AGENT_REGISTRY.items():
                    triggers = agent_data.get("triggers", {})
                    score = 0

                    if domain in triggers.get("domain", set()):
                        score += 3
                    if intent in triggers.get("intent", set()):
                        score += 2
                    for kw in triggers.get("keywords", set()):
                        if kw in query_lower:
                            score += 1

                    if score > best_score:
                        best_score = score
                        best_agent = agent_name

                return best_agent

            def _dispatch_to_agent(
                self, query: str, analysis: Dict[str, Any]
            ) -> Dict[str, Any]:
                """
                Select a specialist agent and return its dispatch context.

                Side-effect: updates ``self._last_agent_used`` so that
                ``_reflect_and_improve``, ``_build_agi_system_prompt``, and
                ``get_reasoning_summary`` can read the active agent without extra
                parameters.

                Returns a dict with:
                  ``agent_name``      — selected agent key (or ``"general"``)
                  ``description``     — human-readable agent purpose
                  ``subtasks``        — ordered subtask list for this query
                  ``reasoning_hints`` — context hints for chain-of-thought
                  ``validation``      — validation rules for ``_reflect_and_improve``
                  ``fallback``        — fallback response (str, dict, or None)
                """
                agent_name = self._select_agent(analysis)
                self._last_agent_used = agent_name

                if agent_name == "general":
                    return {
                        "agent_name": "general",
                        "description": "General-purpose assistant",
                        "subtasks": [
                            "understand the request",
                            "gather relevant information",
                            "formulate response",
                            "verify accuracy",
                        ],
                        "reasoning_hints": [],
                        "validation": {},
                        "fallback": None,
                        "fallback_generic": None,
                    }

                agent = _AGENT_REGISTRY[agent_name]
                intent = analysis.get("intent", "default")
                subtasks_map = agent.get("subtasks", {})
                subtasks = subtasks_map.get(intent) or subtasks_map.get("default", [])

                return {
                    "agent_name": agent_name,
                    "description": agent.get("description", ""),
                    "subtasks": subtasks,
                    "reasoning_hints": agent.get("reasoning_hints", []),
                    "validation": agent.get("validation", {}),
                    "fallback": agent.get("fallback"),
                    "fallback_generic": agent.get("fallback_generic"),
                }

            def _decompose_task(self, query: str, analysis: Dict[str, Any]) -> List[str]:
                """
                Break down a complex task into subtasks using the agent registry.

                Selects the specialist agent for this query and returns its tailored
                subtask sequence, falling back to generic steps for general queries.
                """
                dispatch = self._dispatch_to_agent(query, analysis)
                subtasks = dispatch.get("subtasks") or [
                    "understand the request",
                    "gather relevant information",
                    "formulate response",
                    "verify accuracy",
                ]
                return subtasks[: self.reasoning_depth]

        messages: List[RoleMessage]
    ) -> str:
        """
        Generate the final response based on reasoning.
                            """
                            Generate chain-of-thought reasoning steps.
                            Seeds thoughts from the active specialist agent's reasoning hints so
                            the chain is domain-aware rather than generic.
                            """
                            thoughts = []
                            intent = analysis.get("intent", "general")
        Args:
                            thoughts.append(
                                f"Understanding: This is a {analysis['complexity']} {intent} request."
                            )

                            # Inject specialist agent reasoning hints
                            dispatch = self._dispatch_to_agent(query, analysis)
                            for hint in dispatch.get("reasoning_hints", []):
                                thoughts.append(hint)

                            # Add prior conversation context signal
                            relevant_context = self.context.get_relevant_context(query)
                            if relevant_context and "Recent conversation" in relevant_context:
                                thoughts.append("Considering prior conversation context for continuity.")

                            thoughts.append(
                                f"Approach: Will provide a {analysis['complexity']}-appropriate response."
                            )

                            return thoughts[: self.reasoning_depth]
            query: The user's query.
            reasoning_chain: Completed reasoning steps.
            messages: Conversation history.

        Returns:
            Generated response text.
        """
        # Build enhanced prompt with reasoning context
        analysis = {}
        for step in reasoning_chain:
            if step.step_type == "analyze":
                analysis = step.metadata
                break

        # Prepare system prompt for AGI reasoning
        agi_system_prompt = self._build_agi_system_prompt(
            analysis, reasoning_chain)

        # Build messages for base provider
        enhanced_messages: List[RoleMessage] = []

        # Add AGI system prompt
        enhanced_messages.append({
            "role": "system",
            "content": agi_system_prompt
        })

        # Add conversation history (excluding old system prompts)
        for msg in messages:
            if msg.get("role") != "system":
                enhanced_messages.append(msg)
            elif msg.get("role") == "system" and msg not in enhanced_messages:
                # Append user's system prompt after AGI prompt
                enhanced_messages[0][
                    "content"] += f"\n\nAdditional context: {msg.get('content', '')}"

        # Get response from base provider with secure exception handling
        try:
            provider = self._get_base_provider()
            result = provider.complete(enhanced_messages, stream=False)
            if isinstance(result, str):
                response = result
            else:
                # Consume the generator
                response = "".join(result)
        except Exception as e:
            # Log error securely without exposing internal details to user
            _logger.error("Base provider error: %s",
                          _sanitize_for_logging(str(e)))
            # Fallback to rule-based response if provider fails
            response = self._generate_fallback_response(query, analysis)

        # Add verbose reasoning output if enabled
        if self.verbose and reasoning_chain:
            reasoning_text = self._format_reasoning_chain(reasoning_chain)
            response = f"{reasoning_text}\n\n---\n\n{response}"

        return response

    def _build_agi_system_prompt(
        self,
        analysis: Dict[str, Any],
        reasoning_chain: List[ReasoningStep]
    ) -> str:
        """Build the AGI-enhanced system prompt."""
        intent = analysis.get("intent", "general")
        domain = analysis.get("domain", "general")
        complexity = analysis.get("complexity", "simple")

        prompt_parts = [
            "You are Aria, an intelligent AI assistant with advanced reasoning capabilities.",
            "Answer thoroughly and naturally. Do not include meta-commentary about your reasoning process.",
            "",
            "## Core Principles",
            "- Be accurate, concise, and genuinely helpful.",
            "- Match response depth to the complexity of the question.",
            "- When uncertain, say so rather than speculating without disclosure.",
        ]

        # Domain-specific expert context
        domain_guidance: Dict[str, list] = {
            "quantum": [
                "",
                "## Quantum Computing Context",
                "You have expert knowledge in quantum computing. When relevant:",
                "- Explain qubits, superposition, and entanglement clearly with analogies.",
                "- Describe quantum gates and circuit diagrams step by step.",
                "- Distinguish clearly between simulation and real quantum hardware.",
                "- Reference Qiskit, PennyLane, or Azure Quantum syntax when showing code.",
                "- Quantify speedup claims accurately (quadratic vs. exponential).",
            ],
            "ai": [
                "",
                "## AI / Machine Learning Context",
                "You have expert knowledge in ML and LLM engineering. When relevant:",
                "- Explain model architectures (transformers, attention, LoRA) concisely.",
                "- Include training tips: learning rate, epochs, overfitting signs.",
                "- Distinguish fine-tuning from RAG from prompting when the distinction matters.",
                "- Mention GPU/CPU requirements and memory constraints where practical.",
            ],
            "aria": [
                "",
                "## Aria Character Actions",
                "Aria is a 3D animated character. Include action tags when the user requests movement or gestures:",
                "- [aria:walk:left] / [aria:walk:right] — lateral movement",
                "- [aria:jump] — jump",
                "- [aria:wave] — wave greeting",
                "- [aria:dance] — dance animation",
                "- [aria:idle] — return to idle stance",
                "Acknowledge the action naturally (e.g. 'Sure, moving left! [aria:walk:left]').",
            ],
            "technical": [
                "",
                "## Technical / Engineering Context",
                "Focus on practical, production-quality answers:",
                "- Prefer idiomatic patterns for the language shown in the query.",
                "- Flag security, performance, or scalability concerns explicitly.",
                "- Show full working examples over pseudocode unless pseudocode is explicitly requested.",
                "- Include error handling for any non-trivial code.",
            ],
        }
        if domain in domain_guidance:
            prompt_parts.extend(domain_guidance[domain])

        # Add intent-specific guidance
        intent_guidance: Dict[str, list] = {
            "explanation": [
                "",
                "## Explanation Style",
                "- Start with a one-sentence plain-language definition.",
                "- Use an analogy before diving into technical depth.",
                "- Progress from simple → complex.",
                "- Close with a concrete real-world example.",
            ],
            "coding": [
                "",
                "## Coding Guidelines",
                "- Produce complete, runnable code (not fragments) unless the user asks otherwise.",
                "- Include inline comments for non-obvious logic.",
                "- Handle common edge cases.",
                "- Mention any required imports or dependencies.",
            ],
            "creation": [
                "",
                "## Content Creation",
                "- Ask one clarifying question if the scope is ambiguous — otherwise proceed.",
                "- Structure output clearly (sections, bullets, or numbered steps as appropriate).",
                "- Tailor tone to the apparent audience.",
            ],
        }
        if intent in intent_guidance:
            prompt_parts.extend(intent_guidance[intent])

        # Add complexity-appropriate guidance
        if complexity == "complex":
            prompt_parts.extend([
                "",
                "## Handling Complexity",
                "- Break the answer into clearly labeled sections.",
                "- Address each sub-question or aspect in order.",
                "- Provide a brief summary at the end for long answers.",
            ])

        # Add subtasks if decomposed
        for step in reasoning_chain:
            if step.step_type == "decompose":
                subtasks = step.metadata.get("subtasks", [])
                if subtasks:
                    prompt_parts.extend([
                        "",
                        "## Suggested Approach",
                        *[f"- {task}" for task in subtasks]
                    ])
                break

        return "\n".join(prompt_parts)

    def _generate_fallback_response(self, query: str, analysis: Dict[str, Any]) -> str:
        """Generate a fallback response when the base provider fails."""
        intent = analysis.get("intent", "general")
        domain = analysis.get("domain", "general")

        if intent == "movement" and domain == "aria":
            # Parse movement commands
            query_lower = query.lower()
            if "left" in query_lower:
                return "I'll move to the left! [aria:walk:left]"
            elif "right" in query_lower:
                return "Moving to the right! [aria:walk:right]"
            elif "jump" in query_lower:
                return "Here I go! [aria:jump]"
            elif "wave" in query_lower:
                return "Hello there! [aria:wave]"
            elif "dance" in query_lower:
                return "Time to dance! [aria:dance]"
            else:
                return "I'm ready to move! Just tell me which direction."

        if analysis.get("has_question"):
            return (
                "That's an interesting question! While I'm currently in fallback mode, "
                "I can help with various topics including Aria movements, quantum computing, "
                "and general assistance. How can I help you today?"
            )

        return (
            "I understand your request. I'm Aria, an AGI-enhanced assistant. "
            "I can help with movement commands, explanations, coding tasks, and more. "
            "What would you like to explore?"
        )

    def _reflect_and_improve(
        self,
        query: str,
        response: str,
        reasoning_chain: List[ReasoningStep]
    ) -> str:
        """
        Self-reflect on the response and improve if needed.

        Args:
            query: Original user query.
            response: Generated response.
            reasoning_chain: Reasoning steps used.

        Returns:
            Improved response.
        """
        # Quick quality checks
        issues = []

        # Check response length appropriateness
        analysis = {}
        for step in reasoning_chain:
            if step.step_type == "analyze":
                analysis = step.metadata
                break

        complexity = analysis.get("complexity", "simple")
        word_count = len(response.split())

        if complexity == "complex" and word_count < 50:
            issues.append("response_too_short")
        elif complexity == "simple" and word_count > 300:
            issues.append("response_too_long")

        # Check if question was answered
        if analysis.get("has_question") and "?" not in query[-10:]:
            # Question detected but response might not address it
            if not any(phrase in response.lower() for phrase in ["the answer", "yes", "no", "because", "means", "is"]):
                issues.append("question_not_addressed")

        # Check for Aria movement commands
        if analysis.get("intent") == "movement" and analysis.get("domain") == "aria":
            if "[aria:" not in response:
                # Add movement tag if missing (optimize: accumulate and join)
                query_lower = query.lower()
                tag = None
                if "left" in query_lower:
                    tag = " [aria:walk:left]"
                elif "right" in query_lower:
                    tag = " [aria:walk:right]"
                elif "jump" in query_lower:
                    tag = " [aria:jump]"

                if tag:
                    response = response + tag

        # Store reflection for learning
        if issues:
            self.context.learned_patterns[f"reflection_{len(self.context.reasoning_chains)}"] = {
                "issues": issues,
                "query_type": analysis.get("intent"),
                "improvements_applied": True
            }

        return response

    def _format_reasoning_chain(self, chain: List[ReasoningStep]) -> str:
        """Format reasoning chain for verbose output."""
        parts = ["🧠 **AGI Reasoning Process**", ""]

        step_icons = {
            "analyze": "🔍",
            "decompose": "📋",
            "synthesize": "💡",
            "reflect": "🪞",
            "refine": "✨"
        }

        for i, step in enumerate(chain, 1):
            icon = step_icons.get(step.step_type, "•")
            parts.append(f"{icon} Step {i} ({step.step_type}): {step.content}")

        return "\n".join(parts)

    def _stream_text(self, text: str) -> Generator[str, None, None]:
        """Stream text with adaptive pacing.

        - Short responses (< 20 words): stream character-by-character for a
          natural typing feel.
        - Long responses: stream word-by-word with a faster base delay so the
          user isn't waiting ages for a large answer.
        """
        words = text.split()
        word_count = len(words)

        if word_count < 20:
            # Character-level streaming for short snappy replies
            for ch in text:
                yield ch
                time.sleep(0.012)
        else:
            # Word-level streaming with adaptive delay that scales down as
            # responses get longer (floor at 0.002s, cap at 0.018s).
            delay = max(0.002, min(0.018, 0.8 / (word_count + 10)))
            for i, word in enumerate(words):
                yield (word if i == 0 else " " + word)
                time.sleep(delay)

    def set_goal(self, goal: str) -> None:
        """Add a goal to the active goals list with input sanitization."""
        # Sanitize goal input
        sanitized_goal = _sanitize_input(str(goal), max_length=200)
        if not sanitized_goal:
            return

        if sanitized_goal not in self.context.goals:
            self.context.goals.append(sanitized_goal)
            if len(self.context.goals) > MAX_GOALS:
                self.context.goals = self.context.goals[-MAX_GOALS:]

    def clear_goals(self) -> None:
        """Clear all active goals."""
        self.context.goals.clear()

    def get_reasoning_summary(self) -> Dict[str, Any]:
        """Get a summary of recent reasoning activity."""
        return {
            "total_reasoning_chains": len(self.context.reasoning_chains),
            "active_goals": self.context.goals.copy(),
            "learned_patterns_count": len(self.context.learned_patterns),
            "conversation_length": len(self.context.conversation_history),
        }


def create_agi_provider(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    verbose: bool = False,
    **kwargs
) -> tuple[AGIProvider, ProviderChoice]:
    """
    Factory function to create an AGI-enhanced chat provider.

    Args:
        model: Model identifier (passed to underlying provider).
        temperature: Response randomness.
        max_output_tokens: Maximum tokens in response.
        verbose: Include reasoning steps in output.
        **kwargs: Additional provider-specific arguments.

    Returns:
        Tuple of (provider instance, provider info).
    """
    # Get base provider first - use 'local' to avoid selecting 'agi' recursively
    base_provider = None
    base_choice = None

    if model:
        # Try to use specified model with a non-agi provider
        try:
            base_provider, base_choice = detect_provider(
                explicit="local", model_override=model)
        except Exception:
            pass

    provider = AGIProvider(
        base_provider=base_provider,
        temperature=temperature or 0.7,
        max_output_tokens=max_output_tokens or 2048,
        verbose=verbose,
        **kwargs
    )

    # If we got a base provider, use its info
    model_name = "agi-enhanced"
    if base_choice:
        model_name = f"agi-{base_choice.name}-{base_choice.model}"
    elif model:
        model_name = f"agi-{model}"

    info = ProviderChoice(
        name="agi",
        model=model_name,
    )

    return provider, info
