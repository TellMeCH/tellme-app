"""
LiteLLM configuration for TellMe call processing.

This module configures LiteLLM with fallback settings and Langfuse integration.
All AI processing components should use this configuration for consistent
fallback behavior and observability.
"""

import os
import litellm
from django.conf import settings
from .llm_configs import (
    ENRICHMENT_PIPELINE,
    DIARIZATION_CONFIG,
    SUMMARIZER_CONFIGS,
    META_SUMMARIZATION_MODEL_GEMINI
)


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
    openai_model = openai_config["model"]["openai"]
    openai_litellm_params = {k: v for k, v in openai_config.items() if k != "model"}
    # Add additionalProperties: false for OpenAI (required for strict mode)
    if "response_format" in openai_litellm_params:
        schema = openai_litellm_params["response_format"]["json_schema"]["schema"]
        _add_additional_properties_false(schema)

    # LiteLLM fallback format: each model entry has model + params
    openai_entry = {"model": f"openai/{openai_model}"}
    openai_entry.update(openai_litellm_params)
    models.append(openai_entry)

    # VertexAI model
    vertexai_config = step_config["config"].copy()
    vertexai_model = vertexai_config["model"]["vertexai"]
    vertexai_litellm_params = {k: v for k, v in vertexai_config.items() if k != "model"}
    # Convert response_format for Vertex AI (remove strict mode)
    if "response_format" in vertexai_litellm_params:
        vertexai_litellm_params["response_format"]["json_schema"].pop("strict", None)

    # LiteLLM fallback format: each model entry has model + params
    vertexai_entry = {"model": f"vertex_ai/{vertexai_model}"}
    vertexai_entry.update(vertexai_litellm_params)
    models.append(vertexai_entry)

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


def get_enrichment_config(enrichment_method: str, step_name: str, enrichment_prompt=None):
    """
    Get the appropriate fallback configuration for enrichment steps.
    Uses Langfuse prompt config if available, otherwise falls back to ENRICHMENT_PIPELINE.

    Args:
        enrichment_method (str): Preferred method ('openai' or 'vertexai')
        step_name (str): Name of the enrichment step
        enrichment_prompt: Optional Langfuse prompt object

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

    # If Langfuse prompt provided and not fallback, use its config
    if enrichment_prompt and not enrichment_prompt.is_fallback:
        # Create modified step_config with Langfuse config
        step_config = {
            "name": step_config["name"],
            "config": enrichment_prompt.config
        }

    models = _convert_enrichment_config_to_litellm(step_config)

    # Prioritize the preferred method
    if enrichment_method == "vertexai":
        # Put vertex_ai first
        vertex_models = [m for m in models if m["model"].startswith("vertex_ai")]
        openai_models = [m for m in models if m["model"].startswith("openai")]
        models = vertex_models + openai_models
    elif enrichment_method == "openai":
        # Put openai first
        openai_models = [m for m in models if m["model"].startswith("openai")]
        vertex_models = [m for m in models if m["model"].startswith("vertex_ai")]
        models = openai_models + vertex_models

    return {"model": models}


def get_diarization_config(diarization_prompt):
    """
    Get the fallback configuration for diarization.
    Uses Langfuse prompt config if available, otherwise falls back to DIARIZATION_CONFIG.

    Args:
        diarization_prompt: Langfuse prompt object

    Returns:
        dict: LiteLLM fallback configuration
    """
    # Determine base config (Langfuse or fallback)
    if diarization_prompt.is_fallback:
        base_config = DIARIZATION_CONFIG
    else:
        base_config = diarization_prompt.config

    # Extract values with fallback defaults
    primary_model = base_config.get('model', DIARIZATION_CONFIG['model'])
    fallback_model = base_config.get('fallback_model', DIARIZATION_CONFIG['fallback_model'])
    temperature = base_config.get('temperature', DIARIZATION_CONFIG['temperature'])

    models = [
        {
            "model": primary_model,
            "temperature": temperature
        },
        {
            "model": fallback_model,
            "temperature": temperature
        }
    ]

    return {"model": models}


def get_meta_summarization_config(meta_prompt, prompt_category: str):
    """
    Get the fallback configuration for meta summarization.
    Uses Langfuse prompt config if available, otherwise falls back to SUMMARIZER_CONFIGS.
    Primary: OpenAI
    Fallback: Gemini (from META_SUMMARIZATION_MODEL_GEMINI)

    Args:
        meta_prompt: Langfuse prompt object
        prompt_category (str): Category of summarization prompt

    Returns:
        dict: LiteLLM fallback configuration
    """
    if prompt_category not in SUMMARIZER_CONFIGS:
        raise ValueError(f"No configuration found for meta summarization category: {prompt_category}")

    # Determine base config (Langfuse or fallback)
    if meta_prompt.is_fallback:
        base_config = SUMMARIZER_CONFIGS[prompt_category]
    else:
        base_config = meta_prompt.config

    # Extract model with fallback default
    primary_model = base_config.get('model', SUMMARIZER_CONFIGS[prompt_category]['model'])

    # OpenAI model (primary) - with strict mode support
    openai_params = {k: v for k, v in base_config.items() if k != "model"}
    # Add additionalProperties: false for OpenAI (required for strict mode)
    if "response_format" in openai_params:
        schema = openai_params["response_format"]["json_schema"]["schema"]
        _add_additional_properties_false(schema)

    openai_entry = {"model": f"openai/{primary_model}"}
    openai_entry.update(openai_params)

    # Gemini model (fallback) - without strict mode
    gemini_params = {k: v for k, v in base_config.items() if k != "model"}
    if "response_format" in gemini_params:
        gemini_params["response_format"]["json_schema"].pop("strict", None)

    gemini_entry = {"model": f"vertex_ai/{META_SUMMARIZATION_MODEL_GEMINI}"}
    gemini_entry.update(gemini_params)

    models = [openai_entry, gemini_entry]

    return {"model": models}