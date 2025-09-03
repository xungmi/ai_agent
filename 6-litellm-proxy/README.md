https://docs.litellm.ai/docs/providers/gemini

uv run python .\track_cost_callback.py

pip install langfuse, helicone, lunary

lock dependencies:
    uv pip compile pyproject.toml -o requirements.txt

 uv run python .\image_classification_litellm_sagemaker.py