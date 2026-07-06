# Dependency Graph

## code_generation_quickstart.py

- pathlib
- runpy
- sys

## chat_providers.py

- **future**
- importlib.util
- pathlib
- sys

## function_app.py

- PIL
- asyncio
- azure.cognitiveservices.speech
- azure.functions
- base64
- chat_providers
- collections
- datetime
- function_app_domains
- gtts
- hmac
- importlib.util
- io
- json
- logging
- numpy
- openai
- opentelemetry
- os
- pathlib
- pennylane
- pyttsx3
- qiskit
- quantum_ai.scripts.validate_qiskit_env
- quantum_ai.src.azure_quantum_integration
- quantum_classifier
- quantum_llm
- quantum_llm_trainer
- re
- requests
- shared
- shared.agi_backend_status
- shared.azure_utils
- shared.chat_memory
- shared.config
- shared.core.module_registry
- shared.db_logging
- shared.email_notifications
- shared.file_cache
- shared.import_helpers
- shared.json_utils
- shared.logging
- shared.referral_system
- shared.runtime_env
- shared.stripe_webhooks
- shared.subscription_manager
- shared.telemetry
- subprocess
- sys
- tempfile
- threading
- tiktoken
- time
- torch
- types
- typing
- vision_inference
- wave

## blueprint.py

- azure.functions

## LMSTUDIO_AGI_INTEGRATION_IMPL.py

- os
- urllib.request

## run_main_if_referenced.py

- sys

## run_continuous_automation.py

- argparse
- datetime
- os
- pathlib
- signal
- subprocess
- sys
- time

## app.py

- **future**
- argparse
- importlib
- json
- logging
- math
- openai
- os
- re
- shared.local_summary
- sys
- typing
- urllib

## autotrain.py

- **future**
- scripts.autotrain
- warnings

## setup_monetization.py

- json
- pathlib
- subprocess
- subscription_manager
- sys

## lora_infer_bridge.py

- **future**
- importlib.util
- pathlib
- sys

## token_utils.py

- **future**
- importlib.util
- pathlib
- sys

## agi_provider.py

- **future**
- importlib.util
- pathlib
- sys
- types
- typing

## main.py

## code_generation_demo.py

- pathlib
- runpy
- sys

## run_automation.py

- argparse
- os
- pathlib
- signal
- subprocess
- sys

## website_generator_demo.py

- pathlib
- runpy
- sys

## local_dev_adapter.py

- **future**
- argparse
- azure.functions
- dotenv
- flask
- function_app
- http.server
- json
- logging
- os
- pathlib
- shared.local_settings
- sys
- types
- typing

## aria_bot/**init**.py

- **future**
- importlib.util
- pathlib
- sys

## aria_bot/**main**.py

- **future**
- importlib

## generated_tools/data_datetime_utils.py

- **future**
- collections.abc
- datetime

## generated_tools/data_table_utils.py

- collections
- collections.abc
- typing

## generated_tools/data_record_utils.py

- **future**
- collections.abc
- typing

## generated_tools/data_compare_utils.py

- collections.abc
- typing

## generated_tools/data_stats_utils.py

- **future**
- collections.abc

## generated_tools/data_text_utils.py

- **future**
- collections
- collections.abc
- re
- typing

## generated_tools/data_validation_utils.py

- **future**
- collections.abc
- re
- typing

## generated_tools/data_struct_utils.py

- **future**
- collections.abc
- typing

## ai_projects/**init**.py

## ai_projects/quantum_ml/**init**.py

- pathlib

## core/agent.py

- **future**
- abc
- core.task
- typing

## core/notifications.py

- **future**
- json
- typing
- urllib.error
- urllib.request

## core/**init**.py

- agent
- core.agent
- core.registry
- core.task
- pathlib
- registry
- sys
- task

## core/cycle_observer.py

- **future**
- core.bus
- core.memory.store
- time
- typing

## core/task.py

- **future**
- dataclasses
- typing
- uuid

## core/queue.py

- **future**
- asyncio
- collections.abc
- contextlib
- typing

## core/runner.py

- **future**
- core.agents.critique_agent
- core.agents.debate_agent
- core.agents.goal_evolution_agent
- core.agents.human_feedback_agent
- core.agents.hypothesis_agent
- core.agents.llm_agent
- core.agents.planner_agent
- core.agents.reasoning_agent
- core.agents.reflection_agent
- core.agents.summarizer_agent
- core.agents.tool_agent
- core.agents.training_agent
- core.bus
- core.cycle_observer
- core.knowledge.graph
- core.memory.store
- core.registry
- core.router
- core.task
- time
- typing

## core/router.py

- **future**
- core.agent
- core.registry
- core.task
- typing

## core/registry.py

- **future**
- collections.abc
- core.agent

## core/bus.py

- **future**
- collections
- collections.abc
- threading
- typing

## core/**main**.py

- **future**
- argparse
- collections.abc
- core.runner
- json
- pathlib
- sys

## core/ingestion/**init**.py

- core.ingestion.pipeline

## core/ingestion/pipeline.py

- **future**
- abc
- core.memory.store
- csv
- json
- typing
- urllib.request

## core/knowledge/**init**.py

- core.knowledge.graph

## core/knowledge/graph.py

- **future**
- collections
- core.memory.store
- json
- typing
- yaml

## core/memory/store.py

- collections
- collections.abc
- copy
- datetime
- sqlite_backend
- threading
- typing
- uuid

## core/memory/**init**.py

- **future**
- core.memory.store
- datetime
- json
- store

## core/memory/sqlite_backend.py

- **future**
- json
- sqlite3
- typing

## core/llm/**init**.py

- core.llm.client

## core/llm/client.py

- **future**
- collections.abc
- importlib
- json
- os

## core/agents/debate_agent.py

- **future**
- core.agent
- core.llm.client
- core.memory.store
- core.task
- json
- logging
- re
- typing

## core/agents/**init**.py

- core.agents.critique_agent
- core.agents.debate_agent
- core.agents.goal_evolution_agent
- core.agents.hypothesis_agent
- core.agents.llm_agent
- core.agents.planner_agent
- core.agents.reasoning_agent
- core.agents.reflection_agent
- core.agents.summarizer_agent
- core.agents.tool_agent
- core.agents.training_agent

## core/agents/hypothesis_agent.py

- **future**
- core.agent
- core.llm.client
- core.memory.store
- core.task
- json
- logging
- re
- typing

## core/agents/summarizer_agent.py

- **future**
- core.agent
- core.llm.client
- core.memory.store
- core.task
- json
- logging
- re
- typing

## core/agents/critique_agent.py

- **future**
- core.agent
- core.llm.client
- core.memory.store
- core.task
- json
- logging
- re
- typing

## core/agents/human_feedback_agent.py

- **future**
- core.agent
- core.bus
- core.memory.store
- core.task
- typing

## core/agents/goal_evolution_agent.py

- **future**
- collections.abc
- core.agent
- core.llm.client
- core.memory.store
- core.task
- json
- logging
- re

## core/agents/reasoning_agent.py

- **future**
- core.agent
- core.llm.client
- core.memory.store
- core.task
- json
- logging
- re
- typing

## core/agents/reflection_agent.py

- **future**
- core.agent
- core.llm.client
- core.memory.store
- core.task
- json
- logging
- re
- typing

## core/agents/tool_agent.py

- **future**
- collections.abc
- core.agent
- core.task
- json
- typing
- urllib.request

## core/agents/planner_agent.py

- **future**
- core.agent
- core.llm.client
- core.memory.store
- core.task
- json
- typing
- uuid

## core/agents/llm_agent.py

- **future**
- core.agent
- core.llm.client
- core.task
- dataclasses
- json
- typing

## core/agents/training_agent.py

- **future**
- core.agent
- core.task
- json
- pathlib
- typing

## scripts/check_docs_for_cli_note.py

- pathlib
- re
- sys

## scripts/auto_bootstrap.py

- **future**
- argparse
- datetime
- json
- pathlib
- subprocess
- sys
- time

## scripts/validate_mcp_suite.py

- **future**
- argparse
- json
- pathlib
- subprocess
- sys
- typing

## scripts/autonomous_training_demo.py

- argparse
- datetime
- json
- logging
- math
- os
- pathlib
- random
- sys
- time

## scripts/system_health_check.py

- **future**
- argparse
- dataclasses
- datetime
- importlib
- json
- pathlib
- shutil
- socket
- subprocess
- sys
- typing

## scripts/repo_automation.py

- argparse
- config_paths
- config_validator
- dataclasses
- datetime
- importlib
- json
- pathlib
- psutil
- shared.config_validator
- shlex
- signal
- subprocess
- sys
- threading
- time
- typing

## scripts/validate_mcp_setup.py

- **future**
- argparse
- asyncio
- dataclasses
- json
- mcp
- mcp.client.stdio
- os
- pathlib
- re
- typing

## scripts/aria_demo.py

- pathlib
- peft
- re
- sys
- torch
- transformers

## scripts/parallel_train.py

- argparse
- asyncio
- datetime
- fnmatch
- json
- math
- os
- pathlib
- peft
- re
- shutil
- sys
- torch
- transformers
- typing
- yaml

## scripts/ignore_verify.py

- **future**
- pathlib
- subprocess

## scripts/autonomous_training_orchestrator.py

- **future**
- argparse
- atexit
- config_validator
- datetime
- json
- logging
- math
- os
- pathlib
- quantum_llm_trainer
- random
- shared.config_validator
- signal
- sys
- tenacity
- time
- typing
- yaml

## scripts/benchmark_performance.py

- json
- pathlib
- performance_utils
- sys
- tempfile
- time

## scripts/test_ai_improvements.py

- hybrid_qnn
- pathlib
- pytest
- sys
- torch
- traceback
- train_lora

## scripts/agi_persistence_prune.py

- **future**
- argparse
- json
- os
- sqlite3
- sys
- time
- typing

## scripts/setup_env_check.py

- json
- os
- pathlib
- subprocess
- sys
- urllib.request

## scripts/evaluate_local_model.py

- **future**
- argparse
- evaluation_utils
- json
- pathlib
- sys
- time
- typing

## scripts/**init**.py

## scripts/generate_site_bundle.py

- **future**
- argparse
- datetime
- json
- pathlib

## scripts/job_queue.py

- dataclasses
- datetime
- enum
- heapq
- json
- pathlib
- uuid

## scripts/config_paths.py

- **future**
- pathlib

## scripts/sql_local_tools.py

- **future**
- argparse
- collections.abc
- json
- os
- pathlib
- shared.sql_engine
- sqlalchemy
- sys
- typing

## scripts/repair_data_out_status.py

- **future**
- argparse
- datetime
- json
- pathlib
- re

## scripts/cleanup_artifacts.py

- argparse
- datetime
- json
- pathlib
- time

## scripts/aria_test.py

- pathlib
- peft
- sys
- torch
- transformers
- typing

## scripts/distributed_benchmark.py

- argparse
- datetime
- functools
- json
- multiprocessing
- numpy
- pandas
- pathlib
- sklearn.decomposition
- sklearn.model_selection
- sklearn.preprocessing
- sys
- time
- torch
- torch.nn
- torch.optim
- warnings

## scripts/aria_test_debug.py

- pathlib
- peft
- sys
- torch
- transformers

## scripts/evaluate_azure_model.py

- **future**
- argparse
- json
- openai
- os
- pathlib
- shared.evaluation_utils
- sys
- time
- typing

## scripts/fast_validate.py

- **future**
- argparse
- collections.abc
- datetime
- importlib
- importlib.util
- json
- os
- pathlib
- subprocess
- sys
- typing

## scripts/generate_github_actions_dataset.py

- **future**
- argparse
- dataclasses
- datetime
- hashlib
- json
- pathlib
- random
- typing
- yaml

## scripts/vram_calculator.py

- **future**
- argparse
- json
- subprocess
- torch

## scripts/test_aria_automation.py

- os
- pathlib
- pytest
- subprocess
- sys

## scripts/repo_health_automation.py

- **future**
- argparse
- collections.abc
- dataclasses
- datetime
- json
- pathlib
- subprocess
- sys
- time

## scripts/generate_evaluation_set.py

- **future**
- hashlib
- json
- pathlib
- typing

## scripts/vision_inference.py

- PIL
- **future**
- argparse
- base64
- io
- json
- logging
- numpy
- pathlib
- torch

## scripts/final_validation.py

- functools
- pathlib
- re

## scripts/check_cli_scripts_sys_path.py

- pathlib
- re
- sys

## scripts/setup_local_llm.py

- **future**
- argparse
- importlib.util
- io
- json
- pathlib
- shared.chat_providers
- shared.local_settings
- shutil
- subprocess
- sys
- time
- urllib.error
- urllib.request

## scripts/gradio_demo.py

- collections
- contextlib
- datetime
- gradio
- gradio_webhook
- gtts
- html
- importlib
- importlib.util
- json
- os
- pathlib
- pyttsx3
- re
- shared.chat_providers
- subprocess
- sys
- threading
- time
- typing
- uuid
- wave

## scripts/watch_continuous_automation.py

- **future**
- argparse
- collections.abc
- dataclasses
- datetime
- os
- pathlib
- re
- time

## scripts/gradio_maintenance.py

- os
- time

## scripts/validate_eval_artifacts.py

- **future**
- argparse
- dataclasses
- json
- pathlib
- typing

## scripts/sql_demo.py

- pathlib
- shared.sql_engine
- sys
- typing

## scripts/aria_automation.py

- argparse
- dataclasses
- datetime
- json
- pathlib
- psutil
- signal
- socket
- subprocess
- sys
- threading
- time
- typing

## scripts/validate_dashboard.py

- pathlib
- re

## scripts/evaluate_quantum_model.py

- **future**
- argparse
- json
- pathlib
- shared.evaluation_utils
- sys
- typing

## scripts/backup_manager.py

- argparse
- datetime
- hashlib
- json
- os
- pathlib
- shutil
- sys
- tarfile
- torch
- typing

## scripts/lmstudio_chat_fix.py

- **future**
- argparse
- datetime
- json
- os
- pathlib
- sys
- typing
- urllib.error
- urllib.parse
- urllib.request

## scripts/validate_optimizations.py

- aria_web.server
- batch_evaluator
- pathlib
- shared.chat_memory
- sys
- tempfile
- time

## scripts/notification_system.py

- argparse
- json
- pathlib
- platform
- subprocess
- time
- win10toast

## scripts/dashboard.py

- datetime
- os
- pathlib
- shared.json_utils
- sys
- time
- typing

## scripts/test_runner.py

- argparse
- datetime
- importlib.util
- json
- pathlib
- re
- subprocess
- sys
- time

## scripts/quantum_llm_status_check.py

- **future**
- argparse
- json
- pathlib
- sys
- time
- typing

## scripts/status_dashboard.py

- argparse
- datetime
- json
- os
- pathlib
- shared.json_utils
- socket
- sys
- time
- typing

## scripts/training_analytics.py

- argparse
- datetime
- os
- pathlib
- shared.json_utils
- statistics
- sys

## scripts/provider_smoke.py

- **future**
- json
- pathlib
- shared.core.module_registry
- shared.local_settings
- sys

## scripts/autotrain.py

- **future**
- argparse
- config_paths
- dataclasses
- datetime
- json
- os
- pathlib
- shlex
- subprocess
- sys
- typing
- yaml

## scripts/master_orchestrator.py

- **future**
- argparse
- config_paths
- config_validator
- dataclasses
- datetime
- json
- pathlib
- psutil
- shared.config_validator
- signal
- subprocess
- sys
- time
- typing
- yaml

## scripts/quantum_llm_trainer.py

- argparse
- datetime
- hybrid_qnn
- json
- logging
- numpy
- pathlib
- quantum_transformer
- random
- signal
- sys
- time
- torch
- torch.nn
- torch.utils.data
- typing
- yaml

## scripts/run_pytest_parallel.py

- **future**
- argparse
- collections.abc
- math
- os
- pathlib
- subprocess
- sys
- typing

## scripts/self_learning_chat.py

- scripts.training.cli.self_learning_chat

## scripts/train_quantum_llm_chat.py

- argparse
- datetime
- inspect
- json
- logging
- pathlib
- quantum_transformer
- sys
- torch
- torch.nn
- torch.utils.data

## scripts/ci_orchestrator.py

- **future**
- argparse
- concurrent.futures
- config_paths
- dataclasses
- datetime
- json
- pathlib
- subprocess
- sys
- time
- typing

## scripts/quantum_llm_health_check.py

- **future**
- argparse
- json
- pathlib
- sys
- typing

## scripts/gradio_webhook.py

- json
- os
- time

## scripts/azureml_ci_validate.py

- **future**
- os
- pathlib
- shutil
- subprocess

## scripts/model_deployer.py

- **future**
- argparse
- datetime
- json
- pathlib
- shutil
- sys
- typing

## scripts/task_complete_mcp_server.py

- json
- sys

## scripts/aria_test_final.py

- pathlib
- peft
- re
- sys
- torch
- transformers

## scripts/evaluate_openai_model.py

- **future**
- argparse
- json
- openai
- os
- pathlib
- shared.evaluation_utils
- sys
- time
- typing

## scripts/validate_eval_workflow_setup.py

- **future**
- argparse
- dataclasses
- json
- pathlib

## scripts/test_autonomous_agent.py

- pathlib
- pytest
- subprocess
- sys

## scripts/resource_monitor.py

- **future**
- argparse
- datetime
- json
- os
- pathlib
- psutil
- subprocess
- time
- typing

## scripts/sync_docs_chat.py

- **future**
- pathlib
- shutil

## scripts/monitor_autonomous_training.py

- argparse
- csv
- datetime
- json
- os
- pathlib
- subprocess
- time

## scripts/run_repo_agents.py

- **future**
- argparse
- collections.abc
- dataclasses
- importlib
- json
- pathlib
- scripts.agents.base
- sys

## scripts/generate_synthetic_autonomous_datasets.py

- **future**
- argparse
- json
- pathlib

## scripts/gradio_hello.py

- **future**
- datetime
- gradio
- gtts
- hashlib
- importlib
- json
- os
- pathlib
- pyttsx3
- sys
- time
- typing

## scripts/autonomous_code_agent.py

- **future**
- argparse
- dataclasses
- datetime
- glob
- importlib
- json
- logging
- os
- pathlib
- re
- subprocess
- sys
- time
- traceback
- typing
- urllib.error
- urllib.request

## scripts/multi_agent.py

- **future**
- argparse
- concurrent.futures
- dataclasses
- datetime
- importlib
- json
- logging
- pathlib
- sys
- time
- typing

## scripts/quantum_autorun.py

- **future**
- argparse
- config_paths
- dataclasses
- datetime
- json
- logging
- pathlib
- sys
- tempfile
- typing
- yaml

## scripts/generate_aria_schema.py

- **future**
- json
- pathlib
- server
- sys

## scripts/integration_smoke.py

- **future**
- argparse
- config_paths
- dataclasses
- json
- pathlib
- subprocess
- sys
- time
- typing
- urllib.error
- urllib.parse
- urllib.request

## scripts/dab_verify.py

- **future**
- argparse
- json
- os
- pathlib
- typing

## scripts/demo_quantum_llm.py

- json
- pathlib
- sys
- traceback
- yaml

## scripts/automate_core_files.py

- **future**
- argparse
- datetime
- json
- pathlib
- subprocess
- sys
- typing

## scripts/batch_evaluator.py

- **future**
- argparse
- concurrent.futures
- dataclasses
- datetime
- json
- pathlib
- performance_utils
- shutil
- subprocess
- sys
- time
- typing
- yaml

## scripts/gradio_utils.py

- datetime

## scripts/lm_studio_analyzer.py

- argparse
- json
- os
- pathlib
- subprocess

## scripts/generate_ai_tokens.py

- **future**
- argparse
- dataclasses
- json
- logging
- os
- pathlib
- re
- secrets
- subprocess
- sys
- time
- typing
- urllib.error
- urllib.parse
- urllib.request

## scripts/cleanup_query_metrics.py

- **future**
- re

## scripts/test_repo_automation.py

- importlib.util
- pathlib
- pytest
- repo_automation
- subprocess
- sys

## scripts/evaluate_model.py

- argparse
- collections
- datetime
- evaluate_lora_model
- json
- pathlib
- sys

## scripts/validate_site_bundles.py

- **future**
- json
- pathlib
- sys

## scripts/validate_mcp_suite_drift.py

- **future**
- argparse
- json
- pathlib
- typing

## scripts/autonomous_agent_tasks.py

- **future**
- dataclasses
- enum
- typing

## scripts/evaluation_autorun.py

- **future**
- argparse
- datetime
- json
- pathlib
- sys
- typing
- yaml

## scripts/test_watcher.py

- argparse
- pathlib
- shlex
- subprocess
- time

## scripts/validate_composite_actions.py

- **future**
- pathlib
- yaml

## scripts/extract_chat_logs_dataset.py

- **future**
- argparse
- hashlib
- json
- pathlib
- random

## scripts/pre_commit_check.py

- argparse
- os
- pathlib
- re
- subprocess
- sys

## scripts/validate_foundry_config.py

- **future**
- json
- pathlib
- re

## scripts/local_llm_server.py

- datetime
- http.server
- json
- sys
- threading
- time

## scripts/sql_demo_simple.py

- pathlib
- sqlite3

## scripts/pid_auto_edit_agent.py

- **future**
- argparse
- dataclasses
- datetime
- json
- os
- pathlib
- signal
- subprocess
- sys
- time
- typing

## scripts/quantum_llm_metrics_analyzer.py

- **future**
- argparse
- json
- pathlib
- statistics
- typing

## scripts/inference/vision_avatar_integration.py

- **future**
- argparse
- json
- pathlib
- scripts.training.train_vision
- sys
- torch
- torch.utils.data

## scripts/inference/**init**.py

## scripts/agents/agents_md_audit_agent.py

- **future**
- argparse
- collections.abc
- datetime
- json
- pathlib
- re
- scripts.agents.base
- sys

## scripts/agents/**init**.py

- **future**
- scripts.agents.base

## scripts/agents/status_freshness_agent.py

- **future**
- argparse
- collections.abc
- datetime
- json
- pathlib
- scripts.agents.base
- sys

## scripts/agents/agi_health_agent.py

- **future**
- agi_provider
- argparse
- collections.abc
- json
- pathlib
- scripts.agents.base
- shared.agi_backend_status
- sys
- typing

## scripts/agents/docstring_audit_agent.py

- **future**
- argparse
- ast
- collections.abc
- dataclasses
- json
- pathlib
- scripts.agents.base
- sys

## scripts/agents/base.py

- **future**
- collections.abc
- dataclasses
- datetime
- json
- pathlib

## scripts/agents/marker_audit_agent.py

- **future**
- argparse
- collections.abc
- json
- pathlib
- re
- scripts.agents.base
- sys

## scripts/evaluation/**init**.py

## scripts/evaluation/evaluate_vision.py

- **future**
- argparse
- json
- numpy
- pathlib
- scripts.training.train_vision
- sys
- torch
- torch.utils.data

## scripts/training/**init**.py

## scripts/training/train_vision.py

- PIL
- **future**
- argparse
- numpy
- pathlib
- random
- sys
- torch
- torch.nn
- torch.utils.data

## AI/evaluators.py

- typing

## AI/test_agent.py

- dotenv
- evaluators
- os
- pytest_agent_evals

## AI/microsoft_phi-silica-3.6_v1/scripts/otel_callback.py

- **future**
- importlib.util
- pathlib
- sys

## ai-projects/cooking-ai/src/**init**.py

## ai-projects/cooking-ai/src/main.py

- **future**
- agents.recipe_agent
- argparse
- os
- providers.github_models
- providers.local

## ai-projects/cooking-ai/src/utils/json_utils.py

- **future**
- json
- jsonschema
- re

## ai-projects/cooking-ai/src/providers/github_models.py

- **future**
- openai
- os
- typing

## ai-projects/cooking-ai/src/providers/**init**.py

## ai-projects/cooking-ai/src/providers/local.py

- **future**
- json
- re

## ai-projects/cooking-ai/src/agents/recipe_agent.py

- **future**
- typing
- utils.json_utils

## ai-projects/cooking-ai/tests/test_agent.py

- **future**
- agents.recipe_agent
- json
- pathlib
- providers.local
- pytest
- sys
- utils.json_utils

## ai-projects/cooking-ai/tests/run_tests.py

- **future**
- importlib
- pathlib
- sys

## ai-projects/cooking-ai/tests/test_schemas.py

- **future**
- json
- pathlib
- pytest
- sys
- utils.json_utils

## ai-projects/cooking-ai/tests/debug_run_local.py

- pathlib
- providers.local
- sys

## ai-projects/cooking-ai/tests/debug_agent_extract.py

- agents.recipe_agent
- pathlib
- providers.local
- sys

## ai-projects/cooking-ai/tests/_debug_local.py

- providers.local

## ai-projects/cooking-ai/tests/debug_extract_local.py

- pathlib
- providers.local
- sys

## ai-projects/chat-cli/src/**init**.py

## ai-projects/chat-cli/src/chat_providers.py

- **future**
- agi_provider
- collections.abc
- dataclasses
- json
- local_agi_provider
- logging
- openai
- os
- pathlib
- peft
- quantum_provider
- random
- shared.azure_utils
- shared.local_calc
- shared.local_settings
- shared.local_summary
- subprocess
- sys
- threading
- time
- torch
- transformers
- typing
- urllib.error
- urllib.request

## ai-projects/chat-cli/src/quantum_provider.py

- chat_providers
- collections.abc
- json
- logging
- pathlib
- quantum_transformer
- sys
- torch
- torch.nn.functional
- typing

## ai-projects/chat-cli/src/local_agi_provider.py

- **future**
- collections.abc
- core.llm.client
- json
- typing

## ai-projects/chat-cli/src/test_chat_cli.py

- **future**
- chat_cli
- contextlib
- io
- pathlib
- sys
- types
- unittest
- unittest.mock

## ai-projects/chat-cli/src/_smoke_test.py

- **future**
- importlib
- typing

## ai-projects/chat-cli/src/chat_cli.py

- **future**
- argparse
- colorama
- datetime
- importlib
- json
- os
- pathlib
- sys
- time
- typing

## ai-projects/chat-cli/src/api.py

- agi_provider
- chat_providers
- token_utils

## ai-projects/chat-cli/src/lora_infer_bridge.py

- **future**
- json
- pathlib
- peft
- sys
- torch
- transformers

## ai-projects/chat-cli/src/token_utils.py

- **future**
- collections.abc
- dataclasses
- math
- tiktoken
- transformers

## ai-projects/chat-cli/src/agi_provider.py

- **future**
- asyncio
- chat_providers
- collections.abc
- dataclasses
- html
- logging
- math
- os
- re
- shared.agi_memory_redis
- shared.agi_persistence
- shared.agi_persistence_sqlite
- time
- typing

## ai-projects/chat-cli/src/test_chat_providers.py

- **future**
- agi_provider
- chat_cli
- chat_providers
- json
- os
- pathlib
- pytest
- sys
- tempfile
- time
- typing
- unittest
- unittest.mock

## ai-projects/lmstudio-mcp/lmstudio_agent_integration.py

- **future**
- asyncio
- collections.abc
- json
- lmstudio_mcp_server
- logging
- os
- pathlib
- sys
- traceback
- typing

## ai-projects/lmstudio-mcp/**init**.py

- lmstudio_mcp_server

## ai-projects/lmstudio-mcp/privacy_deployment_config.py

- typing

## ai-projects/lmstudio-mcp/lmstudio_agi_integration.py

- asyncio
- json
- lmstudio_agent_integration
- logging
- re
- traceback
- typing

## ai-projects/lmstudio-mcp/agi_mcp_tools.py

- **future**
- agi_provider
- pathlib
- sys
- typing

## ai-projects/lmstudio-mcp/agi_provider_examples.py

- asyncio
- lmstudio_agi_integration
- pathlib
- sys
- traceback

## ai-projects/lmstudio-mcp/privacy_first_ai.py

- asyncio
- dataclasses
- datetime
- enum
- hashlib
- json
- lmstudio_agent_integration
- lmstudio_agi_integration
- logging
- pathlib
- traceback
- typing

## ai-projects/lmstudio-mcp/test_lmstudio_mcp.py

- asyncio
- lmstudio_mcp_server
- os
- pathlib
- sys
- traceback

## ai-projects/lmstudio-mcp/quickstart.py

- asyncio
- httpx
- pathlib
- subprocess
- sys
- traceback

## ai-projects/lmstudio-mcp/verify_agent_integration.py

- asyncio
- lmstudio_agent_integration
- lmstudio_mcp_server
- os
- pathlib
- sys
- traceback

## ai-projects/lmstudio-mcp/lmstudio_mcp_server.py

- agi_mcp_tools
- asyncio
- httpx
- json
- logging
- mcp.server
- mcp.server.stdio
- mcp.types
- os
- sys
- typing

## ai-projects/my-agent-230a13f1/main.py

- asyncio
- azure.ai.agentserver.responses

## ai-projects/quantum-ml/train_ionosphere.py

- joblib
- matplotlib.pyplot
- numpy
- pandas
- pathlib
- sklearn.decomposition
- sklearn.model_selection
- sklearn.preprocessing
- src.hybrid_qnn
- sys
- torch
- torch.utils.data

## ai-projects/quantum-ml/benchmark_all_datasets.py

- datetime
- json
- matplotlib.pyplot
- numpy
- pandas
- pathlib
- sklearn.decomposition
- sklearn.impute
- sklearn.model_selection
- sklearn.preprocessing
- src.hybrid_qnn
- sys
- torch
- torch.utils.data

## ai-projects/quantum-ml/validate_quantum_llm.py

- argparse
- importlib
- json
- logging
- pathlib
- src.quantum_llm_advanced
- src.quantum_llm_datasets
- src.quantum_llm_integrated
- src.quantum_llm_monitor
- sys
- time
- torch
- typing

## ai-projects/quantum-ml/demo_dashboard.py

- requests
- sys
- time

## ai-projects/quantum-ml/quick_test_datasets.py

- datetime
- json
- numpy
- pandas
- pathlib
- sklearn.decomposition
- sklearn.impute
- sklearn.model_selection
- sklearn.preprocessing
- src.hybrid_qnn
- sys
- time
- torch
- torch.utils.data

## ai-projects/quantum-ml/train_pennylane_simple.py

- argparse
- datetime
- json
- numpy
- pandas
- pathlib
- pennylane
- sklearn.decomposition
- sklearn.impute
- sklearn.model_selection
- sklearn.preprocessing
- time

## ai-projects/quantum-ml/dataset_architecture_analyzer.py

- datetime
- json
- numpy
- pandas
- pathlib
- sklearn.preprocessing

## ai-projects/quantum-ml/train_custom_dataset.py

- argparse
- joblib
- json
- matplotlib.pyplot
- numpy
- os
- pandas
- pathlib
- sklearn.datasets
- sklearn.decomposition
- sklearn.impute
- sklearn.model_selection
- sklearn.preprocessing
- src.hybrid_qnn
- sys
- torch
- torch.utils.data
- yaml

## ai-projects/quantum-ml/submit_qsharp_circuit.py

- azure.quantum
- time
- traceback

## ai-projects/quantum-ml/example_mcp_client.py

- asyncio
- azure.ai.inference
- azure.ai.inference.models
- azure.core.credentials
- contextlib
- mcp
- mcp.client.stdio
- os

## ai-projects/quantum-ml/deploy_banknote_to_azure.py

- azure.identity
- azure.quantum
- datetime
- json
- pathlib
- qiskit
- qiskit_qir
- sys
- time
- yaml

## ai-projects/quantum-ml/deploy_quantum_models_azure.py

- pathlib
- pickle
- qiskit
- src.azure_quantum_integration
- time
- torch
- yaml

## ai-projects/quantum-ml/web_app.py

- datetime
- flask
- flask_cors
- io
- json
- logging
- numpy
- os
- pandas
- pathlib
- pennylane
- re
- sklearn.decomposition
- sklearn.impute
- sklearn.metrics
- sklearn.model_selection
- sklearn.preprocessing
- src.dataset_loader
- sys
- threading
- time

## ai-projects/quantum-ml/test_quantum_hardware.py

- azure.quantum
- logging
- numpy
- pathlib
- pytest
- qiskit
- sys

## ai-projects/quantum-ml/test_entanglement_patterns.py

- datetime
- hybrid_qnn
- matplotlib.pyplot
- numpy
- pandas
- pathlib
- pytest
- sklearn.decomposition
- sklearn.impute
- sklearn.model_selection
- sklearn.preprocessing
- sys
- torch
- torch.utils.data

## ai-projects/quantum-ml/train_heart_disease.py

- joblib
- matplotlib.pyplot
- numpy
- pandas
- pathlib
- sklearn.decomposition
- sklearn.impute
- sklearn.model_selection
- sklearn.preprocessing
- src.hybrid_qnn
- sys
- torch
- torch.utils.data

## ai-projects/quantum-ml/hyperparameter_optimization.py

- datetime
- itertools
- json
- matplotlib.pyplot
- numpy
- pathlib
- sklearn.model_selection
- src.dataset_loader
- src.hybrid_qnn
- sys
- torch
- torch.utils.data
- warnings

## ai-projects/quantum-ml/test_azure_quantum.py

- **future**
- argparse
- azure_quantum_integration
- datetime
- logging
- numpy
- pathlib
- pytest
- qiskit
- sys
- typing
- yaml

## ai-projects/quantum-ml/submit_circuit_azure.py

- azure.quantum
- qiskit
- qiskit_qir
- time
- traceback

## ai-projects/quantum-ml/run_azure_quantum_free.py

- qiskit
- src.azure_quantum_integration

## ai-projects/quantum-ml/quantum_mcp_server.py

- asyncio
- azure_quantum_integration
- collections
- concurrent.futures
- hashlib
- logging
- mcp.server
- mcp.server.stdio
- mcp.types
- numpy
- os
- pathlib
- qiskit
- qiskit_aer
- quantum_classifier
- random
- re
- sklearn.datasets
- sklearn.model_selection
- sklearn.preprocessing
- sys
- tempfile
- time
- typing
- yaml

## ai-projects/quantum-ml/quantum_llm_demo.py

- ai_projects.quantum_ml.src.quantum_llm
- asyncio
- collections
- json
- numpy
- pathlib
- sys
- traceback

## ai-projects/quantum-ml/hyperparameter_tuning.py

- dataset_loader
- datetime
- hybrid_qnn
- itertools
- json
- pathlib
- sklearn.model_selection
- sys
- torch
- torch.utils.data

## ai-projects/quantum-ml/quantum_llm_quickstart.py

- **future**
- argparse
- json
- logging
- pathlib
- src.quantum_llm_datasets
- src.quantum_llm_integrated
- sys
- time
- torch
- typing

## ai-projects/quantum-ml/classical_baseline_comparison.py

- datetime
- json
- matplotlib.pyplot
- numpy
- pandas
- pathlib
- seaborn
- sklearn.decomposition
- sklearn.ensemble
- sklearn.impute
- sklearn.metrics
- sklearn.model_selection
- sklearn.neural_network
- sklearn.preprocessing
- sklearn.svm
- warnings

## ai-projects/quantum-ml/quantum_llm_integration.py

- argparse
- json
- logging
- pathlib
- sys

## ai-projects/quantum-ml/deploy_to_azure_quantum.py

- argparse
- datetime
- json
- pathlib
- qiskit
- src.azure_quantum_integration

## ai-projects/quantum-ml/scripts/test_provider_gates.py

- **future**
- argparse
- azure_quantum_integration
- datetime
- json
- numpy
- pathlib
- pytest
- qiskit
- sys
- yaml

## ai-projects/quantum-ml/scripts/upgrade_qiskit_to_1x.py

- **future**
- argparse
- datetime
- pathlib
- qiskit
- re
- shutil
- subprocess
- sys

## ai-projects/quantum-ml/scripts/run_hardware_tests.py

- **future**
- argparse
- pathlib
- sys
- test_azure_quantum

## ai-projects/quantum-ml/scripts/run_experiment_grid.py

- **future**
- pathlib
- subprocess
- sys

## ai-projects/quantum-ml/scripts/submit_small_stabilizer.py

- **future**
- argparse
- azure_quantum_integration
- datetime
- json
- numpy
- pathlib
- qiskit
- sys
- yaml

## ai-projects/quantum-ml/scripts/validate_qiskit_env.py

- **future**
- importlib
- json
- pkgutil
- sys

## ai-projects/quantum-ml/scripts/run_simulated_circuit.py

- **future**
- argparse
- datetime
- json
- numpy
- pathlib
- qiskit
- qiskit_aer
- qiskit_aer.noise
- yaml

## ai-projects/quantum-ml/scripts/train_from_dataset.py

- argparse
- json
- numpy
- pandas
- pathlib
- quantum_classifier
- sklearn.decomposition
- sklearn.model_selection
- sklearn.preprocessing
- sys
- yaml

## ai-projects/quantum-ml/scripts/visualize_hardware_results.py

- **future**
- json
- matplotlib.pyplot
- pandas
- pathlib
- subprocess
- yaml

## ai-projects/quantum-ml/scripts/submit_variational_hardware.py

- **future**
- argparse
- azure_quantum_integration
- datetime
- json
- numpy
- pathlib
- qiskit
- sys
- yaml

## ai-projects/quantum-ml/src/dataset_loader.py

- numpy
- pandas
- pathlib
- sklearn.decomposition
- sklearn.impute
- sklearn.preprocessing
- typing

## ai-projects/quantum-ml/src/**init**.py

## ai-projects/quantum-ml/src/quantum_circuit_optimizer.py

- collections
- dataclasses
- logging
- numpy
- pennylane
- time
- torch
- torch.nn
- typing

## ai-projects/quantum-ml/src/automate_quantum_job.py

- azure.quantum
- azure.quantum.qiskit
- qiskit
- time

## ai-projects/quantum-ml/src/quantum_llm_hybrid_trainer.py

- dataclasses
- json
- logging
- numpy
- pathlib
- time
- torch
- torch.nn
- torch.optim
- torch.utils.data
- typing

## ai-projects/quantum-ml/src/quantum_code_llm.py

- **future**
- dataclasses
- pathlib
- string
- torch
- torch.nn
- torch.nn.functional
- typing

## ai-projects/quantum-ml/src/hybrid_qnn.py

- logging
- pennylane
- torch
- torch.nn
- yaml

## ai-projects/quantum-ml/src/api.py

- automate_quantum_job
- azure_quantum_integration
- quantum_classifier
- quantum_llm_integrated

## ai-projects/quantum-ml/src/quantum_llm_datasets.py

- json
- logging
- numpy
- pathlib
- random
- torch
- torch.utils.data
- typing

## ai-projects/quantum-ml/src/quantum_transformer.py

- hybrid_qnn
- logging
- math
- pathlib
- sys
- torch
- torch.nn
- torch.nn.functional

## ai-projects/quantum-ml/src/quantum_classifier.py

- logging
- numpy
- pathlib
- pennylane
- sklearn.datasets
- sklearn.model_selection
- torch
- torch.nn
- yaml

## ai-projects/quantum-ml/src/quantum_llm_advanced.py

- collections
- dataclasses
- hybrid_qnn
- logging
- math
- torch
- torch.nn
- torch.nn.functional

## ai-projects/quantum-ml/src/azure_ml_integration.py

- azureml.core
- azureml.core.compute
- azureml.core.model
- azureml.core.runconfig
- azureml.core.webservice
- logging
- pathlib
- typing

## ai-projects/quantum-ml/src/quantum_llm_monitor.py

- collections
- dataclasses
- json
- logging
- numpy
- pathlib
- psutil
- time
- torch
- typing

## ai-projects/quantum-ml/src/quantum_llm_integrated.py

- argparse
- json
- logging
- pathlib
- quantum_circuit_optimizer
- quantum_llm_advanced
- quantum_llm_hybrid_trainer
- quantum_llm_monitor
- torch
- torch.nn
- torch.utils.data
- typing
- yaml

## ai-projects/quantum-ml/src/azure_quantum_integration.py

- azure.identity
- azure.quantum
- azure.quantum.qiskit
- json
- logging
- pathlib
- qiskit
- typing
- yaml

## ai-projects/quantum-ml/src/quantum_classifier_enhanced.py

- logging
- numpy
- pathlib
- pennylane
- sklearn.datasets
- sklearn.model_selection
- sklearn.preprocessing
- torch
- torch.nn
- yaml

## ai-projects/quantum-ml/src/quantum_llm/**init**.py

- circuit_cache
- config
- pipeline
- quantum_embeddings
- quantum_router
- quantum_sampler

## ai-projects/quantum-ml/src/quantum_llm/config.py

- **future**
- dataclasses
- math
- os
- typing

## ai-projects/quantum-ml/src/quantum_llm/quantum_router.py

- **future**
- logging
- numpy
- pennylane
- quantum_sampler

## ai-projects/quantum-ml/src/quantum_llm/circuit_cache.py

- **future**
- collections
- hashlib
- logging
- numpy
- time
- typing

## ai-projects/quantum-ml/src/quantum_llm/quantum_embeddings.py

- **future**
- logging
- numpy
- pennylane
- qiskit
- qiskit.circuit
- qiskit_aer
- quantum_sampler

## ai-projects/quantum-ml/src/quantum_llm/quantum_sampler.py

- **future**
- circuit_cache
- collections.abc
- logging
- numpy
- pennylane
- qiskit
- qiskit.circuit
- qiskit_aer
- warnings

## ai-projects/quantum-ml/src/quantum_llm/pipeline.py

- **future**
- asyncio
- chat_providers
- collections.abc
- config
- json
- logging
- numpy
- pathlib
- quantum_embeddings
- quantum_router
- quantum_sampler
- sys
- time
- typing

## ai-projects/quantum-ml/production/test_api.py

- datetime
- json
- pytest
- requests
- time

## ai-projects/quantum-ml/production/banknote_api.py

- datetime
- flask
- flask_cors
- joblib
- json
- numpy
- os
- pathlib
- src.hybrid_qnn
- sys
- torch

## ai-projects/quantum-ml/experiments/auto_optimize.py

- matplotlib.pyplot
- numpy
- pathlib
- sklearn.datasets
- sklearn.model_selection
- sklearn.preprocessing
- src.quantum_classifier
- sys
- torch
- torch.nn
- torch.optim
- torch.utils.data
- yaml

## ai-projects/quantum-ml/experiments/parameter_tuning.py

- matplotlib
- matplotlib.pyplot
- numpy
- pathlib
- quantum_classifier
- sklearn.datasets
- sklearn.model_selection
- sklearn.preprocessing
- src.quantum_classifier
- sys
- yaml

## ai-projects/quantum-ml/experiments/extended_datasets.py

- matplotlib
- matplotlib.pyplot
- numpy
- pathlib
- quantum_classifier
- sklearn.datasets
- sklearn.decomposition
- sklearn.model_selection
- sklearn.preprocessing
- src.quantum_classifier
- sys

## ai-projects/quantum-ml/experiments/analyze_plots.py

- pathlib

## ai-projects/quantum-ml/experiments/quick_demo.py

- extended_datasets
- pathlib
- sys
- time
- traceback

## ai-projects/quantum-ml/experiments/run_all_experiments.py

- datetime
- experiments.analyze_plots
- experiments.extended_datasets
- experiments.parameter_tuning
- pathlib
- sys
- time

## ai-projects/quantum-ml/examples/train_models.py

- matplotlib
- matplotlib.pyplot
- numpy
- pathlib
- quantum_classifier
- sklearn.datasets
- sklearn.model_selection
- sklearn.preprocessing
- src.quantum_classifier
- sys

## ai-projects/quantum-ml/examples/create_circuits.py

- numpy
- pathlib
- pennylane
- qiskit
- qiskit.circuit
- src.quantum_classifier
- sys

## ai-projects/quantum-ml/examples/azure_integration.py

- pathlib
- qiskit
- src.azure_quantum_integration
- sys
- yaml

## ai-projects/quantum-ml/examples/run_simulations.py

- matplotlib
- matplotlib.pyplot
- numpy
- pathlib
- pennylane
- qiskit
- qiskit_aer
- qiskit_aer.noise

## ai-projects/llm-maker/web_server.py

- http.server
- json
- logging
- os
- pathlib
- sys
- tool_executor
- tool_maker
- tool_registry
- tool_validator
- urllib.parse
- website_maker

## ai-projects/llm-maker/llm_maker_mcp_server.py

- asyncio
- json
- logging
- mcp.server
- mcp.server.stdio
- mcp.types
- pathlib
- src.tool_executor
- src.tool_maker
- src.tool_registry
- src.tool_validator
- sys

## ai-projects/llm-maker/src/**init**.py

- tool_executor
- tool_maker
- tool_registry
- tool_validator
- website_maker

## ai-projects/llm-maker/src/tool_maker.py

- logging
- pathlib
- shared.chat_providers
- sys
- tool_registry
- tool_validator
- yaml

## ai-projects/llm-maker/src/tool_validator.py

- ast
- logging
- pathlib
- yaml

## ai-projects/llm-maker/src/tool_executor.py

- RestrictedPython
- RestrictedPython.Guards
- contextlib
- importlib
- logging
- signal
- threading
- traceback
- typing

## ai-projects/llm-maker/src/website_maker.py

- argparse
- datetime
- json
- os
- re
- shared.chat_providers
- shutil
- sys

## ai-projects/llm-maker/src/tool_registry.py

- dataclasses
- datetime
- json
- logging
- pathlib
- typing
- uuid

## ai-projects/llm-maker/tests/test_validator.py

- pathlib
- pytest
- sys
- tool_validator

## ai-projects/llm-maker/tests/test_executor.py

- pathlib
- pytest
- src.tool_executor
- sys
- tool_executor

## ai-projects/llm-maker/tests/test_validate_perf.py

- pathlib
- sys
- time
- tool_validator

## ai-projects/llm-maker/tests/test_registry.py

- pathlib
- pytest
- sys
- tempfile
- tool_registry

## ai-projects/llm-maker/examples/fibonacci.py

## ai-projects/llm-maker/examples/text_processor.py

- re

## ai-projects/llm-maker/examples/quick_start.py

- pathlib
- sys
- tool_executor
- tool_maker
- tool_registry

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/python mcp.py

- asyncio
- azure.ai.inference
- azure.ai.inference.models
- azure.core.credentials
- contextlib
- json
- mcp
- mcp.client.sse
- mcp.client.stdio
- mcp.client.streamable_http
- os

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azure_ml_training.py

- argparse
- azure.ai.ml
- azure.ai.ml.constants
- azure.ai.ml.entities
- azure.identity
- pathlib
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azure_foundry_deploy.py

- argparse
- azure.ai.ml
- azure.ai.ml.constants
- azure.ai.ml.entities
- azure.identity
- pathlib
- time

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/lr_finder.py

- argparse
- json
- matplotlib.pyplot
- numpy
- pathlib
- scipy.ndimage
- torch
- torch.utils.data
- transformers
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/otel_callback.py

- **future**
- logging
- opentelemetry
- opentelemetry.exporter.otlp.proto.grpc.trace_exporter
- opentelemetry.sdk.trace
- opentelemetry.sdk.trace.export
- os
- sys
- transformers
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/model_exporter.py

- argparse
- huggingface_hub
- onnx
- onnxruntime.transformers
- pathlib
- time
- torch
- transformers

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/train_sentence_transformer.py

- **future**
- argparse
- contextlib
- datasets
- huggingface_hub
- logging
- os
- pathlib
- sentence_transformers
- sentence_transformers.base.sampler
- sentence_transformers.sentence_transformer.evaluation
- sentence_transformers.sentence_transformer.losses
- torch
- traceback

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/data_augmenter.py

- argparse
- dataclasses
- json
- pathlib
- random
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/gpu_optimizer.py

- argparse
- dataclasses
- pathlib
- subprocess
- torch
- typing
- yaml

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/dataset_analyzer.py

- argparse
- collections
- dataclasses
- json
- matplotlib.pyplot
- numpy
- pathlib
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/auto_eval.py

- argparse
- dataclasses
- datasets
- json
- numpy
- pathlib
- peft
- rouge_score
- sacrebleu
- time
- torch
- transformers
- typing
- yaml

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/model_server.py

- argparse
- asyncio
- datetime
- fastapi
- os
- pathlib
- pydantic
- time
- torch
- transformers
- typing
- uvicorn

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/semantic_pruning.py

- argparse
- dataclasses
- json
- numpy
- pathlib
- sentence_transformers
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/prepare_dataset.py

- argparse
- collections.abc
- csv
- json
- pathlib
- random
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/train_lora.py

- argparse
- collections.abc
- dataclasses
- datasets
- ipaddress
- json
- math
- metrics_logger
- os
- otel_callback
- pathlib
- peft
- re
- shared.tracing
- socket
- torch
- traceback
- transformers
- typing
- urllib.parse
- urllib.request
- yaml

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/run_pipeline.py

- argparse
- json
- pathlib
- subprocess
- sys
- time
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/metrics_logger.py

- applicationinsights
- base64
- datetime
- hashlib
- hmac
- json
- opentelemetry
- opentelemetry.exporter.otlp.proto.grpc.trace_exporter
- opentelemetry.sdk.trace
- opentelemetry.sdk.trace.export
- os
- pathlib
- sys
- typing
- urllib.request

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/training_monitor.py

- argparse
- dataclasses
- datetime
- json
- pathlib
- queue
- threading
- time
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/rag_pipeline.py

- argparse
- dataclasses
- json
- numpy
- pathlib
- sentence_transformers
- torch
- transformers
- typing

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azureml/submit_sentence_transformer_azureml.py

- **future**
- argparse
- os
- pathlib
- shutil
- subprocess
- sys

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/local_train/train_local.py

- argparse
- dataclasses
- datasets
- json
- math
- pathlib
- peft
- torch
- transformers
- yaml

## ai-projects/lora-training/microsoft_phi-silica-3.6_v1/foundry/score_foundry.py

- json
- os
- pathlib
- peft
- torch
- transformers

## ai-projects/lora-training/quantum-ai/src/hybrid_qnn.py

- logging
- numpy
- qiskit
- qiskit.circuit
- qiskit.primitives
- qiskit_machine_learning.connectors
- qiskit_machine_learning.neural_networks
- sklearn.datasets
- sklearn.model_selection
- sklearn.preprocessing
- torch
- torch.nn
- torch.optim
- torch.utils.data

## ai-projects/lora-training/quantum-ai/src/quantum_classifier.py

- logging
- numpy
- qiskit
- qiskit.circuit
- qiskit.circuit.library
- qiskit.primitives
- qiskit_algorithms.optimizers
- qiskit_machine_learning.algorithms
- qiskit_machine_learning.neural_networks
- sklearn.datasets
- sklearn.model_selection
- sklearn.preprocessing

## ai-projects/lora-training/quantum-ai/src/azure_quantum_integration.py

- azure.quantum
- azure.quantum.qiskit
- logging
- os
- qiskit
- qiskit.providers
- typing

## ai-projects/email-spam-workflow/workflow.py

- **future**
- agent_framework
- agent_framework.azure
- azure.identity.aio
- collections.abc
- os
- typing

## ai-projects/email-spam-workflow/main.py

- **future**
- agent_framework
- argparse
- asyncio
- azure.ai.agentserver.agentframework
- dotenv
- sys
- workflow

## ai-projects/writer-reviewer-workflow/workflow.py

- agent_framework
- agent_framework.azure
- azure.identity.aio
- os

## ai-projects/writer-reviewer-workflow/main.py

- agent_framework
- argparse
- asyncio
- azure.ai.agentserver.agentframework
- dotenv
- pathlib
- prototype_workflow
- sys
- workflow

## ai-projects/writer-reviewer-workflow/prototype_workflow.py

- **future**
- dataclasses
- json
- keyword
- pathlib
- re
- shutil
- subprocess
- sys
- time
- typing

## aria-bot/aria_bot/validator.py

- **future**
- collections.abc
- dataclasses
- logging
- pathlib
- shutil
- subprocess

## aria-bot/aria_bot/**init**.py

- **future**
- analyzer
- commit_system
- defaults
- executor
- orchestrator
- planner
- registry
- risk_manager
- validator

## aria-bot/aria_bot/analyzer.py

- **future**
- collections.abc
- dataclasses
- logging
- pathlib
- registry
- risk_manager

## aria-bot/aria_bot/executor.py

- **future**
- collections.abc
- dataclasses
- logging
- planner
- registry
- risk_manager

## aria-bot/aria_bot/commit_system.py

- **future**
- collections.abc
- dataclasses
- logging
- pathlib
- shutil
- subprocess

## aria-bot/aria_bot/defaults.py

- **future**

## aria-bot/aria_bot/planner.py

- **future**
- analyzer
- collections.abc
- dataclasses
- defaults
- logging
- pathlib
- risk_manager

## aria-bot/aria_bot/registry.py

- **future**

## aria-bot/aria_bot/cli.py

- **future**
- argparse
- collections.abc
- defaults
- json
- logging
- orchestrator
- pathlib
- sys

## aria-bot/aria_bot/orchestrator.py

- **future**
- analyzer
- collections.abc
- commit_system
- dataclasses
- datetime
- defaults
- executor
- json
- logging
- os
- pathlib
- planner
- risk_manager
- time
- validator

## aria-bot/aria_bot/**main**.py

- **future**
- cli

## aria-bot/aria_bot/risk_manager.py

- **future**
- collections.abc
- dataclasses
- os
- pathlib

## function_app_domains/**init**.py

## function_app_domains/subscriptions.py

- **future**
- function_app_domains.access
- shared.email_notifications
- shared.stripe_webhooks
- shared.subscription_manager

## function_app_domains/agi.py

- **future**
- agi_provider
- function_app_domains.access
- shared.agi_persistence_sqlite

## function_app_domains/referrals.py

- **future**
- function_app_domains.access
- shared.referral_system

## function_app_domains/access.py

- **future**

## function_app_domains/aria_proxy.py

- **future**
- function_app_domains.access

## function_app_domains/quantum.py

- **future**
- function_app_domains.access
- numpy
- pennylane
- quantum_classifier
- quantum_llm_trainer
- torch

## function_app_domains/chat.py

- **future**
- function_app_domains.access
- tiktoken

## functions/http_ai_routes/**init**.py

- azure.functions
- json
- pathlib

## functions/http_ai_runner/**init**.py

- azure.functions
- chat_providers
- json
- logging
- os
- pathlib
- sys
- typing

## functions/http_chat_web/function_app.py

- azure.functions
- pathlib
- shared.http_utils
- sys

## functions/http_ai_status/**init**.py

- azure.functions
- chat_providers
- importlib.util
- json
- os
- pathlib
- runtime_env
- shared.runtime_env
- subprocess
- sys
- threading
- time
- yaml

## functions/http_ai_provider_probe/**init**.py

- azure.functions
- chat_providers
- json
- os
- pathlib
- sys

## functions/http_chat/function_app.py

- azure.functions
- chat_providers
- json
- logging
- pathlib
- shared.http_utils
- sys

## functions/timer_ai_runner/**init**.py

- azure.functions
- chat_providers
- datetime
- logging
- os
- pathlib
- sys

## shared/agi_persistence.py

- **future**
- json
- os
- threading
- time
- typing
- uuid

## shared/db_logging.py

- **future**
- json
- os
- pathlib
- pyodbc
- typing
- yaml

## shared/email_notifications.py

- datetime
- enum
- json
- logging
- pathlib
- re
- typing

## shared/**init**.py

- shared.file_cache
- shared.http_utils
- shared.import_helpers
- shared.json_utils
- shared.performance_utils
- shared.script_utils

## shared/config_validator.py

- **future**
- argparse
- dataclasses
- pathlib
- re
- sys
- typing
- yaml

## shared/agi_memory_redis.py

- **future**
- collections.abc
- json
- logging
- os
- redis
- threading
- typing

## shared/request_validator.py

- **future**
- json
- logging

## shared/chat_providers.py

- **future**
- importlib.util
- pathlib
- shared.local_settings
- sys

## shared/import_helpers.py

- collections.abc
- logging
- typing

## shared/runtime_env.py

- **future**
- collections.abc
- functools
- json
- pathlib
- subprocess
- sys
- textwrap

## shared/consensus_engine.py

- **future**
- collections.abc
- dataclasses

## shared/config.py

- **future**
- azure.identity
- azure.keyvault.secrets
- functools
- logging
- os
- pydantic
- pydantic_settings
- shared.local_settings
- typing

## shared/chat_memory.py

- **future**
- collections.abc
- hashlib
- logging
- math
- openai
- os
- pyodbc
- struct
- threading
- time
- types
- typing

## shared/performance_utils.py

- collections
- collections.abc
- functools
- hashlib
- json
- pathlib
- tempfile
- time
- typing

## shared/stripe_webhooks.py

- datetime
- json
- logging
- pathlib
- shared.email_notifications
- shared.subscription_manager
- typing

## shared/evaluation_utils.py

- **future**
- json
- pathlib
- typing

## shared/local_calc.py

- **future**
- ast
- math
- operator
- re

## shared/sql_engine.py

- **future**
- collections
- hashlib
- logging
- os
- sqlalchemy
- sqlite3
- time
- typing
- urllib.parse

## shared/cosmos_client.py

- **future**
- azure.cosmos
- logging
- os
- time
- typing
- uuid

## shared/json_utils.py

- **future**
- json
- pathlib
- time
- typing

## shared/script_utils.py

- **future**
- pathlib
- sys

## shared/telemetry.py

- **future**
- azure.monitor.opentelemetry
- logging
- os

## shared/logging.py

- **future**
- json
- logging
- os
- sys
- time
- typing

## shared/file_cache.py

- **future**
- json
- pathlib
- threading
- time
- typing

## shared/token_utils.py

- **future**
- importlib.util
- pathlib
- sys

## shared/ai_safety_middleware.py

- **future**
- collections.abc
- dataclasses
- datetime
- re
- typing

## shared/local_settings.py

- **future**
- collections.abc
- json
- os
- pathlib

## shared/http_utils.py

- logging
- pathlib
- typing

## shared/subscription_manager.py

- datetime
- enum
- json
- logging
- pathlib
- typing

## shared/agi_backend_status.py

- **future**
- os
- typing

## shared/ai_runner.py

- **future**
- datetime
- logging
- os
- pathlib
- re
- shared.local_settings
- subprocess
- sys

## shared/local_summary.py

- **future**
- collections
- re

## shared/sql_repository.py

- **future**
- datetime
- logging
- os
- sql_engine
- sqlalchemy
- sqlite3

## shared/referral_system.py

- datetime
- json
- logging
- pathlib
- secrets
- shared.email_notifications
- typing

## shared/agi_persistence_sqlite.py

- **future**
- json
- os
- sqlite3
- threading
- time
- typing
- uuid

## shared/core/entrypoints_registry.py

- logging
- pathlib
- typing
- yaml

## shared/core/**init**.py

- module_registry

## shared/core/module_registry.py

- importlib
- importlib.util
- logging
- pathlib
- sys
- typing

## shared/domain/**init**.py

## shared/utilities/**init**.py

## shared/infrastructure/**init**.py

## shared/premium/**init**.py

## mount/quantum_integration.py

- json
- pathlib
- re
- subprocess
- sys
- typing
- yaml

## mount/**init**.py

## mount/train_max_performance.py

- argparse
- os
- pathlib
- psutil
- subprocess
- sys
- time
- torch
- typing

## mount/app.py

- asyncio
- chat_integration
- contextlib
- datetime
- fastapi
- fastapi.exception_handlers
- fastapi.middleware.cors
- fastapi.responses
- fastapi.staticfiles
- logging
- path_resolver
- pathlib
- pydantic
- quantum_integration
- time
- training_integration
- uuid
- uvicorn

## mount/training_integration.py

- asyncio
- json
- logging
- os
- pathlib
- re
- subprocess
- sys
- typing

## mount/path_resolver.py

- **future**
- copy
- pathlib
- typing
- yaml

## mount/chat_integration.py

- datetime
- json
- os
- pathlib
- subprocess
- sys
- typing

## aria_web/**init**.py

## aria_web/server.py

- **future**
- importlib.util
- pathlib
- sys

## quantum-ai/web_app.py

- **future**
- collections.abc
- importlib.util
- logging
- numpy
- pathlib
- sys
- typing

## quantum-ai/scripts/smoke_quantum_code_llm.py

- **future**
- api
- argparse
- pathlib
- sys

## quantum-ai/scripts/validate_qiskit_env.py

- **future**
- importlib.util
- pathlib

## quantum-ai/src/**init**.py

- api

## quantum-ai/src/quantum_code_llm.py

- **future**
- dataclasses
- importlib.util
- math
- numpy
- pathlib
- pennylane
- random
- time
- torch
- torch.nn
- torch.utils.data
- typing

## quantum-ai/src/api.py

- quantum_code_llm
- typing

## quantum-ai/examples/quantum_code_llm_demo.py

- **future**
- os
- quantum_code_llm
- sys

## quantum-ai/examples/quantum_code_chat.py

- **future**
- argparse
- os
- quantum_code_llm
- sys

## tests/test_setup_verify_workflow_wiring.py

- **future**
- pathlib
- pytest
- yaml

## tests/test_train_quantum_llm_chat.py

- **future**
- importlib.util
- pathlib
- types

## tests/test_sql_repository_extended.py

- **future**
- os
- pytest
- shared.sql_engine
- shared.sql_repository
- unittest.mock

## tests/test_watch_continuous_automation.py

- **future**
- datetime
- importlib
- os
- pathlib
- sys

## tests/test_status_schema_fixtures.py

- **future**
- json
- pathlib
- pytest
- re
- scripts.ci_orchestrator
- scripts.integration_smoke

## tests/test_consolidated_html.py

- pathlib
- pytest
- re

## tests/test_multi_agent.py

- **future**
- importlib
- json
- pathlib
- pytest
- sys
- types

## tests/test_provider_response_handling.py

- chat_providers
- pathlib
- sys
- unittest.mock

## tests/test_local_dev_adapter.py

- **future**
- json
- local_dev_adapter
- pytest

## tests/workflow_test_helpers.py

- **future**

## tests/test_autonomous_code_agent.py

- **future**
- autonomous_code_agent
- pathlib
- pytest
- subprocess
- sys
- types

## tests/test_agi_smoke.py

- function_app
- json
- pytest
- unittest.mock

## tests/test_quantum_autorun_dry_run_behavior.py

- **future**
- pathlib
- quantum_autorun
- sys

## tests/test_hypothesis_agent.py

- **future**
- core.agents.hypothesis_agent
- core.memory.store
- core.task
- json
- typing

## tests/test_aria_index_provider_wiring.py

- pathlib

## tests/test_lmstudio_cache_thread_safety.py

- chat_providers
- pathlib
- sys
- threading
- time
- unittest

## tests/test_training_integration.py

- asyncio
- mount.training_integration
- pathlib
- subprocess
- sys
- types
- unittest.mock

## tests/test_agent_mode_delegation_contracts.py

- **future**
- pathlib
- pytest
- re

## tests/test_status_dashboard.py

- **future**
- datetime
- importlib.util
- json
- pathlib

## tests/test_root_shims.py

- **future**
- importlib.util
- pathlib

## tests/test_gradio_autoimprove.py

- importlib.util
- os

## tests/test_agi_stream_utils_js.py

- **future**
- pathlib
- pytest
- shutil
- subprocess

## tests/test_quantum_command_gate_hook.py

- **future**
- json
- os
- pathlib
- subprocess
- sys

## tests/test_sql_engine_extended.py

- **future**
- os
- pytest
- shared.sql_engine
- time
- unittest.mock

## tests/test_requirements_security_gate_hook.py

- **future**
- importlib.util
- io
- json
- pathlib
- sys

## tests/test_quantum_mcp_server_security.py

- **future**
- asyncio
- os
- pathlib
- pytest
- qiskit
- quantum_mcp_server
- sys
- tempfile
- time
- unittest.mock

## tests/test_docstring_audit_agent.py

- **future**
- json
- pathlib
- scripts.agents.base
- scripts.agents.docstring_audit_agent
- sys

## tests/test_lmstudio_agi_integration_impl.py

- **future**
- importlib.util
- pathlib
- urllib.request

## tests/test_provider_gates.py

- **future**
- importlib.util
- pathlib
- pytest

## tests/test_agi_backend_status.py

- shared.agi_backend_status

## tests/test_azure_openai_provider_resilience.py

- **future**
- importlib
- pytest
- typing
- unittest.mock

## tests/test_gradio_hello.py

- importlib.util
- os
- pathlib

## tests/test_config.py

- **future**
- os
- pathlib
- pytest
- shared.config
- sys
- unittest.mock

## tests/test_ai_runner.py

- **future**
- os
- pathlib
- pytest
- shared.ai_runner
- subprocess
- unittest.mock

## tests/test_quantum_provider.py

- **future**
- importlib.util
- json
- pathlib
- pytest
- sys
- torch

## tests/test_test_runner.py

- **future**
- datetime
- json
- pathlib
- pytest
- scripts.test_runner
- subprocess
- sys

## tests/test_qai_path_resolver.py

- **future**
- mount.path_resolver
- pathlib
- pytest

## tests/test_chat_web_embedded_script.py

- **future**
- pathlib

## tests/test_job_queue.py

- **future**
- importlib.util
- pathlib
- pytest
- sys
- time

## tests/test_training_integration_validation.py

- asyncio
- mount.training_integration
- pathlib
- sys
- types
- unittest.mock

## tests/test_module_registry.py

- **future**
- pathlib
- pytest
- shared.core.module_registry
- sys
- unittest.mock

## tests/test_cosmos_client.py

- **future**
- os
- shared.cosmos_client
- unittest.mock

## tests/test_quantum_provider_checkpoint_loading.py

- **future**
- json
- pathlib
- pytest
- quantum_provider
- sys
- typing

## tests/test_connection_pool_mock.py

- shared.chat_memory

## tests/test_setup_env_check.py

- **future**
- importlib.util
- json
- pathlib

## tests/test_orchestrator_health_integration.py

- datetime
- importlib.util
- json
- pathlib
- pytest
- sys
- types

## tests/test_local_summary.py

- shared.local_summary
- unittest

## tests/test_lmstudio_mcp_agi_tools.py

- **future**
- agi_mcp_tools
- importlib.util
- pathlib
- pytest
- sys
- types

## tests/test_gradio_webhook_ui.py

- importlib.util
- os

## tests/test_auto_fix_workflow.py

- **future**
- pathlib
- pytest
- yaml

## tests/test_lora_cleanup.py

- json
- pathlib
- pytest

## tests/test_core_models.py

- **future**
- core
- core.agent
- core.registry
- core.task
- pathlib
- pytest
- subprocess
- sys

## tests/test_orchestrator_backoff.py

- **future**
- json
- pathlib
- pytest
- scripts.autonomous_training_orchestrator
- shared.config
- sys
- tenacity

## tests/test_secrets_leak_guard_hook.py

- **future**
- json
- os
- pathlib
- subprocess
- sys

## tests/test_training_analytics_cli.py

- **future**
- pathlib
- pytest
- subprocess
- sys
- tempfile

## tests/test_training_analytics.py

- importlib.util
- json
- pathlib
- pytest
- sys

## tests/test_gradio_focused_workflow.py

- **future**
- pathlib
- pytest
- tests.workflow_test_helpers
- yaml

## tests/test_script_utils.py

- **future**
- pathlib
- shared.script_utils
- sys

## tests/test_quantum_cost_gate_hook.py

- **future**
- json
- os
- pathlib
- subprocess
- sys

## tests/test_route_access_gates.py

- **future**
- function_app
- json
- pathlib
- pytest
- sys
- unittest.mock

## tests/test_local_dev_adapter_http.py

- **future**
- json
- local_dev_adapter
- pytest

## tests/test_request_validator.py

- **future**
- json
- pytest
- shared.request_validator
- unittest.mock

## tests/test_validate_qiskit_env.py

- importlib.util
- pathlib

## tests/test_azureml_submission_gating.py

- importlib
- pathlib

## tests/test_gradio_maintenance.py

- os
- scripts
- time

## tests/test_mount_app_health.py

- **future**
- datetime
- fastapi.testclient
- importlib

## tests/test_aria_tests_workflow.py

- **future**
- pathlib
- pytest

## tests/test_generate_ai_tokens.py

- **future**
- json
- pathlib
- pytest
- scripts.generate_ai_tokens
- subprocess
- sys
- unittest.mock

## tests/test_agent_with_tools_example.py

- **future**
- importlib.util
- pathlib
- pytest
- sys

## tests/test_core_infra.py

- **future**
- core.agents.human_feedback_agent
- core.bus
- core.memory.store
- core.queue
- core.task
- datetime
- pytest

## tests/test_master_orchestrator_schedule.py

- **future**
- datetime
- pytest
- scripts.master_orchestrator

## tests/test_http_ai_status_function.py

- **future**
- importlib.util
- json
- pathlib
- pytest
- time
- types

## tests/test_vision_inference.py

- PIL
- **future**
- base64
- binascii
- importlib.util
- io
- numpy
- pathlib
- pytest
- scripts.vision_inference
- sys
- time
- torch
- typing
- unittest.mock

## tests/test_aria_command_presets.py

- json
- pathlib

## tests/test_quantum_mcp_server_qiskit_compat.py

- **future**
- asyncio
- pathlib
- pytest
- qiskit
- quantum_mcp_server
- sys
- types

## tests/test_agi_panel_integration.py

- pathlib

## tests/test_server_start_sys_executable.py

- pathlib
- pytest
- socket
- subprocess
- sys
- time

## tests/test_config_validation_gates.py

- os
- pathlib
- subprocess
- sys

## tests/test_integration_smoke_schema.py

- **future**
- pytest
- re
- scripts.integration_smoke
- sys
- typing

## tests/test_quantum_llm_trainer.py

- json
- pathlib
- pytest
- quantum_llm_trainer
- sys
- tempfile

## tests/test_aria_bot_dev_entrypoints.py

- **future**
- json
- pathlib
- pytest

## tests/validate_performance_optimizations.py

- pathlib
- server
- shared.chat_memory
- sys
- time
- traceback

## tests/test_aria_auto_execute.py

- pytest
- requests

## tests/test_quantum_provider_checkpoint_metadata.py

- json
- pathlib
- pytest
- sys

## tests/test_dataset_write_guard_hook.py

- **future**
- json
- os
- pathlib
- subprocess
- sys

## tests/test_agi_launcher_task.py

- **future**
- json
- pathlib
- pytest

## tests/test_quantum_llm_health_check.py

- json
- pathlib
- pytest
- subprocess
- sys

## tests/test_aria_accessibility_html.py

- pathlib
- re

## tests/test_lmstudio_http_fallback.py

- **future**
- chat_providers
- json
- pathlib
- sys
- unittest.mock

## tests/test_scorecard_workflow.py

- **future**
- pathlib
- pytest
- yaml

## tests/test_writer_reviewer_prototype_workflow.py

- **future**
- importlib.util
- json
- pathlib
- pytest
- subprocess
- sys

## tests/test_lora_adapter_completeness_guard_hook.py

- **future**
- json
- os
- pathlib
- subprocess
- sys
- tempfile

## tests/test_merge_gate_setup_guardrails.py

- **future**
- pathlib
- pytest
- yaml

## tests/test_monitor_autonomous_training.py

- importlib.util
- io
- json
- pathlib
- re
- sys

## tests/test_app_main.py

- **future**
- app
- os
- pytest
- sys

## tests/test_performance_critical_fixes.py

- aria_web.server
- pathlib
- shared.chat_memory
- sys
- time
- traceback
- unittest.mock

## tests/test_agi_persistence_auth.py

- function_app
- json
- pathlib
- pytest
- sys
- time
- unittest.mock

## tests/test_import_helpers.py

- pathlib
- shared.import_helpers
- sys

## tests/test_quantum_llm_stream_errors.py

- **future**
- asyncio
- pathlib
- quantum_llm
- sys

## tests/test_subscription_manager.py

- **future**
- datetime
- json
- pytest
- shared.subscription_manager

## tests/test_pr_checklist_guard_hook.py

- **future**
- importlib.util
- io
- json
- pathlib
- sys

## tests/test_site_bundle_validation_workflow.py

- **future**
- pathlib
- pytest
- tests.workflow_test_helpers
- yaml

## tests/test_quantum_integration.py

- **future**
- asyncio
- json
- mount.quantum_integration
- pathlib
- pytest
- types

## tests/test_quantum_web_ui.py

- **future**
- importlib.util
- pathlib
- pytest
- sys

## tests/test_app_local_logic.py

- **future**
- app
- builtins
- os
- pytest
- sys

## tests/test_repair_data_out_status.py

- **future**
- datetime
- json
- pathlib
- scripts.repair_data_out_status
- sys

## tests/test_gradio_utils.py

- scripts

## tests/test_reflection_agent.py

- **future**
- core.agents.reflection_agent
- core.memory.store
- core.task
- json
- typing

## tests/test_provider_fallback.py

- **future**
- os
- pathlib
- pytest
- shared.config
- shared.import_helpers
- sys
- unittest.mock

## tests/test_token_utils.py

- **future**
- shared.token_utils

## tests/test_dab_verify.py

- **future**
- json
- os
- pathlib
- pytest
- scripts.dab_verify

## tests/test_quantum_provider_selection.py

- **future**
- importlib
- pytest
- sys
- types
- typing

## tests/test_notification_system.py

- importlib.util
- pathlib
- scripts.notification_system
- subprocess
- sys
- unittest.mock

## tests/test_avatar_integration.py

- importlib
- pathlib
- pytest

## tests/test_quantum_llm_metrics_analyzer.py

- **future**
- importlib
- importlib.util
- pathlib
- pytest
- sys

## tests/test_scope_drift_guard_hook.py

- **future**
- json
- os
- pathlib
- subprocess
- sys

## tests/test_aria_bot_root_shim.py

- **future**
- importlib.util
- pathlib
- subprocess
- sys

## tests/test_fast_validate.py

- **future**
- importlib
- importlib.util
- pathlib
- pytest

## tests/test_azureml_validation.py

- importlib
- pathlib

## tests/test_local_agi_sse_integration.py

- importlib.util
- json
- pathlib
- sys
- unittest.mock

## tests/test_git_commit_hygiene_hook.py

- **future**
- importlib.util
- io
- json
- pathlib
- sys

## tests/test_performance_utils.py

- **future**
- json
- pathlib
- shared.performance_utils
- sys
- time
- types

## tests/test_run_repo_agents.py

- **future**
- json
- pathlib
- scripts
- scripts.agents.base
- sys

## tests/test_aria_server.py

- http
- importlib.util
- json
- pathlib
- re
- sys

## tests/test_provider_detection_cache.py

- **future**
- chat_providers
- pathlib
- sys
- time
- unittest.mock

## tests/test_core_cli.py

- **future**
- core.**main**
- json
- pytest

## tests/test_quantum_code_llm.py

- **future**
- pathlib
- pytest
- quantum_code_llm
- sys

## tests/test_db_logging.py

- **future**
- json
- os
- pathlib
- pytest
- shared.db_logging
- unittest.mock

## tests/test_ai_safety_middleware.py

- **future**
- shared.ai_safety_middleware

## tests/test_quantum_llm_quickstart.py

- **future**
- importlib.util
- pathlib
- pytest
- subprocess
- sys

## tests/test_stage_state_store.py

- **future**
- importlib.util
- json
- pathlib
- sys

## tests/test_task_complete_stub.py

- **future**
- os
- pathlib
- subprocess

## tests/test_parallel_train.py

- **future**
- asyncio
- importlib.util
- json
- pathlib
- pytest
- sys

## tests/test_phase_optimizations.py

- aria_web.server
- batch_evaluator
- pathlib
- pytest
- shared.chat_memory
- sys
- time
- unittest.mock

## tests/test_evaluation_utils.py

- evaluation_utils
- json
- pathlib
- sys
- tempfile

## tests/test_object_api_integration.py

- **future**
- http.server
- json
- pathlib
- pytest
- server
- socket
- sys
- threading
- time
- urllib.error
- urllib.request

## tests/test_quantum_llm_local_smoke.py

- **future**
- asyncio
- pathlib
- quantum_llm
- sys

## tests/test_ci_orchestrator_integration_baseline.py

- **future**
- pytest
- scripts.ci_orchestrator

## tests/test_dry_run_reminder_hook.py

- **future**
- json
- os
- pathlib
- subprocess
- sys

## tests/test_file_cache.py

- **future**
- json
- pathlib
- pytest
- shared.file_cache
- sys
- threading
- time

## tests/test_core_runtime.py

- **future**
- core.agents.tool_agent
- core.runner
- core.task

## tests/test_agents_base.py

- **future**
- json
- pathlib
- pytest
- scripts.agents.base
- sys

## tests/test_evaluation_framework.py

- json
- pathlib
- subprocess
- sys

## tests/test_local_calc.py

- shared.local_calc
- unittest

## tests/test_quantum_web_app.py

- importlib.util
- logging
- numpy
- pathlib
- pytest
- sys
- types

## tests/test_agents_md_audit_agent.py

- **future**
- json
- pathlib
- scripts.agents.agents_md_audit_agent
- scripts.agents.base
- sys

## tests/test_aria_auto_execute_html.py

- pathlib

## tests/test_system_health_check.py

- **future**
- importlib.util
- json
- pathlib
- sys
- types

## tests/test_validate_site_bundles.py

- **future**
- json
- scripts.validate_site_bundles

## tests/test_app_providers.py

- **future**
- app
- json
- os
- pytest
- sys
- types

## tests/test_github_actions_dataset.py

- json
- pathlib
- pytest
- subprocess
- sys

## tests/test_agi_persistence_endpoint.py

- function_app
- json
- pytest
- shared.agi_persistence_sqlite
- time
- unittest.mock

## tests/test_pages_workflow.py

- **future**
- pathlib
- pytest
- yaml

## tests/test_vram_calculator.py

- **future**
- pathlib
- pytest
- sys
- vram_calculator

## tests/test_train_vision.py

- importlib
- pathlib
- pytest

## tests/test_app_validation.py

- **future**
- app
- io
- os
- pytest
- sys
- types

## tests/test_openai_provider_resilience.py

- **future**
- importlib
- pytest
- typing
- unittest.mock

## tests/test_quantum_autorun_unit.py

- importlib
- pathlib
- sys
- unittest.mock

## tests/test_agi_features.py

- **future**
- core.agents.critique_agent
- core.agents.debate_agent
- core.agents.goal_evolution_agent
- core.agents.human_feedback_agent
- core.agents.hypothesis_agent
- core.agents.llm_agent
- core.agents.reasoning_agent
- core.agents.reflection_agent
- core.agents.summarizer_agent
- core.agents.tool_agent
- core.agents.training_agent
- core.bus
- core.ingestion.pipeline
- core.knowledge.graph
- core.llm.client
- core.memory.store
- core.notifications
- core.registry
- core.router
- core.runner
- core.task
- datetime
- http.server
- json
- pathlib
- sys
- threading
- types
- uuid

## tests/test_ui_selenium.py

- json
- logging
- os
- pathlib
- pytest
- requests
- selenium
- selenium.webdriver.chrome.options
- selenium.webdriver.support.ui
- socket
- subprocess
- sys
- time
- urllib.parse

## tests/test_shared_config.py

- **future**
- shared.config

## tests/test_validate_mcp_setup.py

- pathlib
- scripts.validate_mcp_setup

## tests/test_cleanup_query_metrics.py

- cleanup_query_metrics
- pathlib
- pytest
- sys

## tests/test_train_lora_model_resolution.py

- **future**
- importlib.util
- pathlib

## tests/test_keep_working_config.py

- **future**
- importlib.util
- json
- pathlib
- pytest

## tests/test_database_integration.py

- **future**
- math
- pathlib
- shared.chat_memory
- sys

## tests/test_regex_optimizations.py

- email_notifications
- final_validation
- function_app
- local
- pathlib
- pytest
- re
- sys
- time
- validate_dashboard

## tests/conftest.py

- json
- pathlib
- pytest
- sys
- unittest.mock
- websockets
- websockets.client

## tests/test_codeql_workflow_paths_ignore.py

- **future**
- pathlib
- pytest
- subprocess
- yaml

## tests/test_aria_bot.py

- **future**
- aria_bot
- aria_bot.commit_system
- aria_bot.defaults
- aria_bot.executor
- aria_bot.planner
- aria_bot.registry
- aria_bot.validator
- json
- pathlib
- pytest
- subprocess
- sys

## tests/test_config_paths.py

- **future**
- pathlib
- pytest
- scripts.config_paths

## tests/test_quantum_llm.py

- **future**
- asyncio
- json
- numpy
- pathlib
- pytest
- quantum_llm
- sys

## tests/test_chat_memory_unit.py

- pytest
- shared
- threading
- unittest.mock

## tests/test_evaluate_vision.py

- importlib
- pathlib
- pytest

## tests/test_quantum_autorun_integration.py

- json
- pathlib
- pytest
- subprocess
- sys

## tests/test_agi_memory_redis.py

- agi_provider
- shared.agi_memory_redis

## tests/test_no_orphaned_gitlinks.py

- **future**
- pathlib
- subprocess

## tests/test_email_notifications.py

- **future**
- json
- pytest
- shared.email_notifications

## tests/test_quantum_llm_status_check.py

- **future**
- json
- pathlib
- pytest
- subprocess
- sys

## tests/test_ui_pyppeteer.py

- **future**
- asyncio
- contextlib
- json
- logging
- os
- pathlib
- pyppeteer
- pytest
- requests
- socket
- subprocess
- sys
- time

## tests/test_qai_app_startup.py

- **future**
- importlib.util
- pathlib
- pytest
- sys

## tests/test_quantum_llm_provider_result_normalization.py

- **future**
- asyncio
- pathlib
- quantum_llm
- sys

## tests/test_cleanup_artifacts.py

- **future**
- importlib
- importlib.util
- os
- pathlib
- sys
- time

## tests/test_runtime_env.py

- **future**
- json
- shared.runtime_env
- subprocess

## tests/test_parallel_status.py

- json
- pathlib
- pytest

## tests/test_copilot_setup_workflow.py

- **future**
- pathlib
- pytest

## tests/test_autonomous_training_orchestrator.py

- **future**
- datetime
- importlib.util
- json
- os
- pathlib
- pytest
- signal

## tests/test_azure_quantum_integration.py

- enum
- importlib
- json
- pathlib
- pytest
- sys
- unittest.mock

## tests/test_telemetry.py

- **future**
- os
- shared.telemetry
- sys
- unittest.mock

## tests/test_agi_prune.py

- json
- pathlib
- scripts.agi_persistence_prune
- shared.agi_persistence_sqlite
- sys
- time

## tests/test_autotrain_root_shim.py

- **future**
- importlib.util
- pathlib
- scripts.autotrain
- warnings

## tests/test_data_struct_utils.py

- **future**
- generated_tools.data_struct_utils
- pathlib
- sys

## tests/test_referral_system.py

- **future**
- json
- pytest
- shared.referral_system
- unittest.mock

## tests/test_ui_playwright.py

- json
- os
- pathlib
- playwright.sync_api
- pytest
- requests
- shutil
- socket
- subprocess
- time

## tests/test_dependabot_alert_gate_hook.py

- **future**
- importlib.util
- io
- json
- os
- pathlib
- sys
- time

## tests/test_run_main_if_referenced.py

- **future**
- importlib.util
- pathlib
- pytest

## tests/test_best_model_selection.py

## tests/test_run_continuous_automation.py

- **future**
- datetime
- importlib.util
- pathlib
- subprocess

## tests/test_ignore_verify.py

- **future**
- pathlib
- pytest
- scripts.ignore_verify
- sys
- typing

## tests/test_status_freshness_agent.py

- **future**
- datetime
- json
- pathlib
- scripts.agents.base
- scripts.agents.status_freshness_agent
- sys

## tests/test_chat_memory.py

- **future**
- math
- os
- random
- shared.chat_memory
- unittest.mock

## tests/test_quantum_llm_circuit_cache.py

- **future**
- asyncio
- json
- numpy
- pathlib
- pytest
- quantum_llm
- sys
- time

## tests/test_agi_provider.py

- agi_provider
- asyncio
- chat_providers
- collections.abc
- pathlib
- pytest
- sys

## tests/test_resource_monitor.py

- **future**
- importlib.util
- json
- pathlib

## tests/test_config_validator.py

- config_validator
- pathlib
- pytest
- sys
- tempfile

## tests/test_cycle_observer.py

- **future**
- core.bus
- core.cycle_observer
- core.memory.store
- core.runner
- pytest

## tests/test_ollama_provider.py

- **future**
- chat_providers
- pathlib
- pytest
- sys
- unittest.mock
- urllib.error

## tests/test_http_utils.py

- os
- pathlib
- shared.http_utils
- sys
- tempfile

## tests/test_quantum_sampler_nonfinite.py

- **future**
- pathlib
- quantum_llm
- sys

## tests/test_core_agents.py

- **future**
- collections.abc
- core.agents.critique_agent
- core.agents.debate_agent
- core.agents.goal_evolution_agent
- core.agents.human_feedback_agent
- core.agents.hypothesis_agent
- core.agents.llm_agent
- core.agents.planner_agent
- core.agents.reasoning_agent
- core.agents.reflection_agent
- core.agents.summarizer_agent
- core.agents.tool_agent
- core.agents.training_agent
- core.bus
- core.memory.store
- core.task
- pytest

## tests/test_performance_keyword_sets.py

- pyodbc
- pytest
- server
- shared.chat_memory
- time

## tests/test_integration_contract_gate_script.py

- **future**
- pathlib
- pytest

## tests/test_autotrain.py

- datetime
- importlib.util
- pathlib
- pytest
- sys

## tests/test_agi_persistence_sqlite.py

- agi_provider

## tests/test_azure_quantum_runner.py

- importlib
- pathlib
- pytest
- sys

## tests/test_setup_monetization.py

- **future**
- importlib.util
- json
- pathlib

## tests/test_serve_api_routes.py

- http.server
- importlib.util
- json
- pathlib
- pytest
- socket
- sys
- threading
- time
- unittest.mock
- urllib.parse
- urllib.request

## tests/test_agi_health_agent.py

- **future**
- json
- pathlib
- scripts.agents.agi_health_agent
- sys

## tests/test_backup_manager.py

- json
- os
- pathlib
- scripts.backup_manager

## tests/test_lmstudio_agi_integration.py

- agi_provider
- chat_providers
- os
- pathlib
- sys
- unittest.mock

## tests/test_function_app_endpoints.py

- azure.functions
- function_app
- inspect
- json
- pathlib
- pytest
- requests
- shared.request_validator
- sys
- torch
- types
- unittest.mock

## tests/test_consensus_engine.py

- pathlib
- pytest
- shared.consensus_engine
- sys

## tests/test_job_yaml_schema.py

- pathlib
- pytest
- yaml

## tests/test_no_verify_bypass_guard_hook.py

- **future**
- importlib.util
- io
- json
- pathlib
- sys

## tests/test_core_knowledge.py

- **future**
- core.knowledge.graph
- core.memory.store
- json

## tests/test_json_utils.py

- **future**
- json
- pathlib
- pytest
- shared.json_utils
- sys

## tests/test_run_automation.py

- **future**
- importlib.util
- pathlib
- subprocess
- sys

## tests/test_web_app_security.py

- collections.abc
- flask.testing
- importlib.util
- json
- pathlib
- pytest
- sys
- time
- typing
- unittest.mock

## tests/test_gradio_webhook.py

- os
- scripts

## tests/test_sql_integration.py

- logging
- os
- pytest
- shared.sql_engine
- shared.sql_repository
- sqlalchemy
- typing

## tests/test_sql_local_tools.py

- **future**
- json
- os
- pathlib
- pytest
- scripts.sql_local_tools
- shared.sql_engine
- sys
- typing

## tests/test_local_dev_adapter-v2.py

- **future**
- json
- local_dev_adapter
- os
- pathlib
- pytest

## tests/test_agi_persistence.py

- agi_provider
- json

## tests/test_training_health_report_workflow.py

- **future**
- json
- os
- pathlib
- subprocess
- sys
- textwrap
- yaml

## tests/test_actionlint_shellcheck_workflows.py

- **future**
- pathlib
- pytest

## tests/test_workflow_validation_workflow.py

- **future**
- pathlib
- pytest
- tests.workflow_test_helpers
- yaml

## tests/test_orchestrator_health_in_status_endpoint.py

- importlib.util
- json
- pathlib
- sys
- tests.test_orchestrator_health_integration
- types

## tests/test_performance_optimizations.py

- ai_runner
- chat_memory
- collections
- generate_evaluation_set
- heapq
- json
- lora_infer_bridge
- math
- pathlib
- pytest
- re
- shared.sql_repository
- sys
- time
- token_utils
- training_analytics

## tests/test_dashboard_utils.py

- importlib.util
- json
- pathlib
- sys

## tests/test_auto_create_pr_workflow.py

- **future**
- pathlib
- pytest

## tests/test_gradio_demo.py

- importlib.util
- os
- sys
- types

## tests/test_app_cli.py

- **future**
- app
- os
- pytest
- sys

## tests/test_status_schema.py

- **future**
- json
- pathlib
- pytest
- scripts.ci_orchestrator
- scripts.master_orchestrator
- scripts.repo_automation

## tests/test_notifications.py

- **future**
- core.notifications
- urllib.error

## tests/test_app_local_fallback.py

- app
- os
- sys

## tests/test_marker_audit_agent.py

- **future**
- json
- pathlib
- scripts.agents.base
- scripts.agents.marker_audit_agent
- sys

## tests/test_enforce_task_complete_hook.py

- **future**
- json
- os
- pathlib
- pytest
- subprocess
- sys

## tests/test_core_router.py

- **future**
- core.agent
- core.agents.llm_agent
- core.agents.planner_agent
- core.memory.store
- core.registry
- core.router
- core.runner
- core.task

## tests/integration/test_quantum_llm_pipeline.py

- ai_projects.quantum_ml.src.quantum_llm.config
- ai_projects.quantum_ml.src.quantum_llm.pipeline
- pytest

## tests/keep_working/test_keep_working.py

- json
- notebooks.keep_working_launcher
- pathlib
- sys

## tests/unit/test_aria_schema_endpoint.py

- **future**
- http.server
- importlib.util
- json
- pathlib
- pytest
- sys
- threading
- urllib.request

## tests/unit/test_lm_studio_analyzer.py

- **future**
- importlib.util
- json
- pathlib
- pytest
- subprocess

## tests/unit/test_chat_cli_no_stream.py

- **future**
- argparse
- importlib.util
- pathlib
- types

## tests/unit/test_aria_schema_in_sync.py

- **future**
- json
- pathlib
- server
- sys

## tests/unit/test_quantum_llm_components.py

- ai_projects.quantum_ml.src.quantum_llm.quantum_embeddings
- ai_projects.quantum_ml.src.quantum_llm.quantum_router
- ai_projects.quantum_ml.src.quantum_llm.quantum_sampler
- numpy
- pytest

## tests/unit/test_local_settings.py

- **future**
- json
- os
- pathlib
- pytest
- shared.local_settings

## tests/unit/test_tags_to_actions.py

- pathlib
- server
- sys

## tests/unit/test_circuit_cache.py

- ai_projects.quantum_ml.src.quantum_llm.circuit_cache
- numpy
- pytest
- time

## tests/unit/test_quantum_llm_config.py

- ai_projects.quantum_ml.src.quantum_llm.config
- json
- pytest

## tests/unit/test_fallback_gesture_parser.py

- **future**
- pathlib
- server
- sys

## my-agent-0b2avt/provision_memory_store.py

- azure.ai.projects
- azure.core.exceptions
- azure.identity
- dotenv
- os

## my-agent-0b2avt/main.py

- agent_framework
- agent_framework.foundry
- agent_framework_foundry_hosting
- asyncio
- azure.identity.aio
- dotenv
- logging
- os

## notebooks/evaluators.py

- typing

## notebooks/test_agent.py

- dotenv
- evaluators
- os
- pytest_agent_evals

## notebooks/keep_working_launcher.py

- argparse
- dataclasses
- datetime
- getpass
- importlib
- json
- pathlib
- platform
- shlex
- shutil
- sqlite3
- subprocess
- sys
- textwrap
- time

## notebooks/notebook_utils/utils.py

- json
- numpy
- pathlib
- random

## apps/dashboard/gpu_monitor.py

- json
- psutil
- subprocess

## apps/dashboard/app.py

- csv
- datetime
- flask
- flask_socketio
- io
- json
- os
- pathlib
- re
- scripts.autotrain
- shlex
- signal
- subprocess
- sys
- threading
- time
- traceback
- typing
- yaml

## apps/dashboard/websocket_server.py

- asyncio
- datetime
- json
- pathlib
- watchdog.events
- watchdog.observers
- websockets

## apps/dashboard/serve.py

- collections
- datetime
- gpu_monitor
- http.server
- json
- os
- pathlib
- psutil
- random
- re
- socketserver
- subprocess
- sys
- time
- traceback
- urllib.parse
- vram_calculator
- webbrowser
- yaml

## apps/aria/test_auto_execute.py

- json
- pytest
- requests
- sys
- traceback

## apps/aria/stage_state_store.py

- **future**
- copy
- json
- os
- pathlib
- threading
- typing

## apps/aria/Repository analyzer.py

- **future**
- collections.abc
- dataclasses
- logging
- pathlib
- registry
- risk_manager
- typing

## apps/aria/server.py

- agi_provider
- datetime
- hashlib
- http.server
- importlib.util
- json
- logging
- math
- os
- pathlib
- random
- re
- shared.chat_providers
- shared.local_settings
- socket
- sys
- time
- torch
- traceback
- transformers
- urllib.request

## examples/ai_starters/agent_with_tools.py

- **future**
- ast
- collections.abc
- dataclasses
- pathlib
- re

## examples/ai_starters/local_model_chat.py

- transformers

## examples/ai_starters/fastapi_local_chat.py

- examples.ai_starters.local_model_chat
- fastapi
- fastapi.responses
- functools
- pydantic
- uvicorn

## examples/ai_starters/sql_to_local_ai_orchestrator.py

- **future**
- argparse
- examples.ai_starters.local_model_chat
- importlib
- json
- pathlib
- psycopg
- psycopg2
- sqlite3
- typing
- urllib.parse

## tools/codegen_from_input.py

- **future**
- argparse
- dataclasses
- datetime
- json
- pathlib
- re
- typing

## tools/codegen/code_generation_quickstart.py

- code_generation_templates
- pathlib
- subprocess
- sys
- traceback

## tools/codegen/website_generator_guide.py

- sys
- traceback

## tools/codegen/code_generation_templates.py

- sys

## tools/codegen/code_generation_examples.py

- pathlib
- sys
- tool_maker
- traceback
- website_maker

## tools/codegen/code_generation_demo.py

- sys
- traceback

## tools/codegen/website_generator_demo.py

- sys
- traceback

## tools/repo_cleanup/generate_repo_inventory.py

- pathlib

## tools/repo_cleanup/detect_duplicate_code.py

- collections
- pathlib

## tools/repo_cleanup/detect_large_files.py

- pathlib

## tools/repo_cleanup/generate_dependency_graph.py

- ast
- pathlib

## tools/repo_cleanup/autofix_cleanup.py

- pathlib
- shutil

## tools/repo_cleanup/validate_structure.py

- pathlib

## tools/repo_cleanup/ai_cleanup_agent.py

- pathlib

## tools/repo_cleanup/repo_scorecard.py

- pathlib

## tools/repo_cleanup/detect_dead_code.py

- pathlib

## tools/repo_cleanup/architecture_drift.py

- pathlib

## .github/hooks/scripts/scope_drift_guard.py

- **future**
- collections.abc
- json
- os
- re
- sys
- typing

## .github/hooks/scripts/quantum_command_gate.py

- **future**
- collections.abc
- json
- os
- re
- sys
- typing

## .github/hooks/scripts/dependabot_alert_gate.py

- **future**
- json
- os
- pathlib
- subprocess
- sys
- time
- typing

## .github/hooks/scripts/requirements_security_gate.py

- **future**
- json
- os
- re
- shutil
- subprocess
- sys
- tempfile
- tomli
- tomllib
- typing

## .github/hooks/scripts/dataset_write_guard.py

- **future**
- json
- os
- re
- sys
- typing

## .github/hooks/scripts/enforce_task_complete.py

- **future**
- json
- os
- re
- sys
- typing

## .github/hooks/scripts/git_commit_hygiene.py

- **future**
- collections.abc
- json
- os
- pathlib
- re
- subprocess
- sys
- typing

## .github/hooks/scripts/secrets_leak_guard.py

- **future**
- collections.abc
- json
- os
- re
- sys
- typing

## .github/hooks/scripts/no_verify_bypass_guard.py

- **future**
- collections.abc
- json
- os
- re
- sys
- typing

## .github/hooks/scripts/quantum_cost_gate.py

- collections.abc
- json
- os
- re
- sys
- typing

## .github/hooks/scripts/lora_adapter_completeness_guard.py

- **future**
- collections.abc
- json
- os
- pathlib
- re
- sys
- typing

## .github/hooks/scripts/pr_checklist_guard.py

- **future**
- json
- os
- subprocess
- sys
- typing

## .github/hooks/scripts/dry_run_reminder.py

- **future**
- collections.abc
- json
- os
- re
- sys
- typing
