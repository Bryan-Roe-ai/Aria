```instructions
---
name: "LoRA-AzureML"
description: "Guidance for lora/azureml/ AzureML job YAMLs, environment files, and cloud training configs"
applyTo: "lora/azureml/**"
---
# LoRA – AzureML

- `lora/azureml/` contains AzureML job definitions, environment specs, and cloud training configurations.
- Job YAMLs define compute targets, datasets, and entry scripts for cloud-based LoRA training.
- Environment files specify Docker base images and pip/conda dependencies.
- Keep compute target names parameterized (not hardcoded to a specific workspace).
- Use registered datasets in AzureML rather than local file paths.
- Pin dependency versions in environment files for reproducibility.
- Store AzureML workspace credentials in env vars or defaulting to `az login` CLI auth.
- Test jobs with small data/epochs before submitting full runs to save compute costs.
- Follow config precedence: base YAML < per-job overrides < env vars.
```
