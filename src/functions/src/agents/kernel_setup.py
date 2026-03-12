"""
kernel_setup.py — Semantic Kernel configuration for ExamOps.

Builds a Kernel wired to Azure OpenAI and registers the three pipeline
plugins (FileHandler, Formatting, DiffGenerator).

Usage::

    from src.agents.kernel_setup import build_kernel

    kernel = build_kernel(file_handler, formatting_engine, diff_generator)
"""

import logging
import os

logger = logging.getLogger(__name__)


def build_kernel(file_handler, formatting_engine, diff_generator):
    """
    Create and configure a Semantic Kernel instance.

    Reads Azure OpenAI credentials from environment variables:
        AZURE_OPENAI_ENDPOINT   — Azure OpenAI resource endpoint
        AZURE_OPENAI_DEPLOYMENT — Deployment name (e.g. gpt-4o-mini)
        AZURE_OPENAI_KEY        — API key

    Registers plugins:
        FileHandler   — FileHandlerPlugin(file_handler)
        Formatting    — FormattingPlugin(formatting_engine)
        DiffGenerator — DiffPlugin(diff_generator)

    Args:
        file_handler:      FileHandlerAgent instance.
        formatting_engine: FormattingEngineAgent instance.
        diff_generator:    DiffGeneratorAgent instance.

    Returns:
        Configured Kernel ready for ChatCompletionAgent.
    """
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
    from src.agents.plugins.file_handler_plugin import FileHandlerPlugin
    from src.agents.plugins.formatting_plugin import FormattingPlugin
    from src.agents.plugins.diff_plugin import DiffPlugin

    kernel = Kernel()

    kernel.add_service(
        AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            api_key=os.getenv("AZURE_OPENAI_KEY", ""),
        )
    )

    kernel.add_plugin(FileHandlerPlugin(file_handler), plugin_name="FileHandler")
    kernel.add_plugin(
        FormattingPlugin(formatting_engine), plugin_name="Formatting"
    )
    kernel.add_plugin(
        DiffPlugin(diff_generator), plugin_name="DiffGenerator"
    )

    logger.info(
        "Semantic Kernel configured with FileHandler, Formatting, DiffGenerator plugins"
    )
    return kernel
