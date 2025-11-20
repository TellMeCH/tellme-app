"""
LiteLLM configuration for TellMe call processing.

This module configures LiteLLM with fallback settings and Langfuse integration.
All AI processing components should use this configuration for consistent
fallback behavior and observability.
"""

import os
import litellm
from django.conf import settings
from .llm_configs import ENRICHMENT_PIPELINE, DIARIZATION_CONFIG, SUMMARIZER_CONFIGS


def setup_litellm():
    """
    Configure LiteLLM with Langfuse integration and global settings.

    This should be called once during application startup to:
    - Set up Langfuse OTEL integration for observability
    - Configure global LiteLLM settings
    - Set API keys for different providers
    """
    # Configure Langfuse integration
    if hasattr(settings, 'LANGFUSE_PUBLIC_KEY') and settings.LANGFUSE_PUBLIC_KEY:
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
    if hasattr(settings, 'LANGFUSE_SECRET_KEY') and settings.LANGFUSE_SECRET_KEY:
        os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
    if hasattr(settings, 'LANGFUSE_HOST') and settings.LANGFUSE_HOST:
        os.environ["LANGFUSE_OTEL_HOST"] = settings.LANGFUSE_HOST
    else:
        # Default to EU region
        os.environ["LANGFUSE_OTEL_HOST"] = "https://cloud.langfuse.com"

    # Enable Langfuse OTEL callback
    litellm.callbacks = ["langfuse_otel"]

    # Configure API keys
    if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    if hasattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS'):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS

    # Configure global LiteLLM settings
    litellm.drop_params = True  # Drop unsupported parameters
    litellm.set_verbose = False  # Reduce logging noise

    # Configure retry settings
    litellm.num_retries = 3  # Number of retries
    litellm.request_timeout = 300  # Timeout in seconds


def _convert_enrichment_config_to_litellm(step_config):
    """Convert enrichment pipeline config to LiteLLM format."""
    models = []

    # OpenAI model
    openai_config = step_config["config"].copy()
    openai_config["model"] = openai_config["model"]["openai"]
    openai_litellm_params = {k: v for k, v in openai_config.items() if k != "model"}
    # Add additionalProperties: false for OpenAI (required for strict mode)
    if "response_format" in openai_litellm_params:
        schema = openai_litellm_params["response_format"]["json_schema"]["schema"]
        _add_additional_properties_false(schema)

    models.append({
        "model_name": f"openai/{openai_config['model']}",
        "litellm_params": openai_litellm_params
    })

    # VertexAI model
    vertexai_config = step_config["config"].copy()
    vertexai_config["model"] = vertexai_config["model"]["vertexai"]
    vertexai_litellm_params = {k: v for k, v in vertexai_config.items() if k != "model"}
    # Convert response_format for Vertex AI (remove strict mode)
    if "response_format" in vertexai_litellm_params:
        vertexai_litellm_params["response_format"]["json_schema"].pop("strict", None)

    models.append({
        "model_name": f"vertex_ai/{vertexai_config['model']}",
        "litellm_params": vertexai_litellm_params
    })

    return models


def _add_additional_properties_false(schema):
    """
    Recursively add 'additionalProperties': false to all object schemas.
    OpenAI's structured output requires this for strict mode.
    """
    if isinstance(schema, dict):
        # If this is an object schema, add additionalProperties: false
        if schema.get('type') == 'object' and 'properties' in schema:
            schema['additionalProperties'] = False

        # Recursively process all values
        for key, value in schema.items():
            if isinstance(value, (dict, list)):
                _add_additional_properties_false(value)
    elif isinstance(schema, list):
        # Recursively process list items
        for item in schema:
            if isinstance(item, (dict, list)):
                _add_additional_properties_false(item)

    return schema


def get_enrichment_config(enrichment_method: str, step_name: str):
    """
    Get the appropriate fallback configuration for enrichment steps.

    Args:
        enrichment_method (str): Preferred method ('openai' or 'vertexai')
        step_name (str): Name of the enrichment step

    Returns:
        dict: LiteLLM fallback configuration
    """
    # Find the step in the pipeline
    step_config = None
    for step in ENRICHMENT_PIPELINE:
        if step["name"] == step_name:
            step_config = step
            break

    if not step_config:
        raise ValueError(f"No configuration found for enrichment step: {step_name}")

    models = _convert_enrichment_config_to_litellm(step_config)

    # Prioritize the preferred method
    if enrichment_method == "vertexai":
        # Put vertex_ai first
        vertex_models = [m for m in models if m["model_name"].startswith("vertex_ai")]
        openai_models = [m for m in models if m["model_name"].startswith("openai")]
        models = vertex_models + openai_models
    elif enrichment_method == "openai":
        # Put openai first
        openai_models = [m for m in models if m["model_name"].startswith("openai")]
        vertex_models = [m for m in models if m["model_name"].startswith("vertex_ai")]
        models = openai_models + vertex_models

    return {"model": models}


def get_diarization_config():
    """
    Get the fallback configuration for diarization.

    Returns:
        dict: LiteLLM fallback configuration
    """
    models = [
        {
            "model_name": f"vertex_ai/{DIARIZATION_CONFIG['model']}",
            "litellm_params": {
                "temperature": DIARIZATION_CONFIG["temperature"]
            }
        },
        {
            "model_name": "openai/gpt-4o-mini",
            "litellm_params": {
                "temperature": DIARIZATION_CONFIG["temperature"]
            }
        }
    ]

    return {"model": models}


def get_meta_summarization_config(prompt_category: str):
    """
    Get the fallback configuration for meta summarization.

    Args:
        prompt_category (str): Category of summarization prompt

    Returns:
        dict: LiteLLM fallback configuration
    """
    if prompt_category not in SUMMARIZER_CONFIGS:
        raise ValueError(f"No configuration found for meta summarization category: {prompt_category}")

    config = SUMMARIZER_CONFIGS[prompt_category]

    # OpenAI model
    openai_params = {k: v for k, v in config.items() if k != "model"}
    # Add additionalProperties: false for OpenAI (required for strict mode)
    if "response_format" in openai_params:
        schema = openai_params["response_format"]["json_schema"]["schema"]
        _add_additional_properties_false(schema)

    # VertexAI model
    vertexai_params = {k: v for k, v in config.items() if k != "model"}
    # Remove strict mode for Vertex AI
    if "response_format" in vertexai_params:
        vertexai_params["response_format"]["json_schema"].pop("strict", None)

    models = [
        {
            "model_name": f"openai/{config['model']}",
            "litellm_params": openai_params
        },
        {
            "model_name": "vertex_ai/gemini-2.0-flash-001",
            "litellm_params": vertexai_params
        }
    ]

    return {"model": models}