Fine-Tuning & Model Ops
=======================

Fine-Tuning Strategy
--------------------

- Use LoRA/QLoRA for cost-efficient adaptation.
- Maintain strict data lineage and evaluation gates.

Model Registry
--------------

- **MLflow** or **Weights & Biases** as artifact registry.
- Model cards and dataset references required.

Serving
-------

- **vLLM** or **TGI** for production serving.
- Canary rollouts with automated rollback on eval failure.
