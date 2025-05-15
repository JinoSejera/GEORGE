from enum import Enum

from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig, PromptExecutionSettings
from semantic_kernel.core_plugins import ConversationSummaryPlugin

class Config(str, Enum):
    """
    Enum for Prompt Template Config.
    """
    CONVERSATION_SUMMARIZER = "conversation_summarizer"
    
def get_prompt_template_config(prompt_template_config_name: Config):
    """
    Retrieve the prompt template configuration by name.

    Args:
        prompt_template_config_name (Config): The name of the prompt template config.

    Returns:
        PromptTemplateConfig: The corresponding prompt template configuration.

    Raises:
        ValueError: If the config name is not supported.
    """
    configs = {
        Config.CONVERSATION_SUMMARIZER: lambda: get_conversation_summarizer_config()
    }
    
    if prompt_template_config_name not in configs:
        raise ValueError(f"Unsupported service name: {prompt_template_config_name}")
    return configs[prompt_template_config_name]()

def get_conversation_summarizer_config()->PromptTemplateConfig:
    """
    Get the prompt template config for conversation summarization.

    Returns:
        PromptTemplateConfig: The summarizer prompt template configuration.
    """
    execution_settings = PromptExecutionSettings(
        service_id="conversation_summary",
        max_tokens=ConversationSummaryPlugin._max_tokens,
        temperature=0.1,
        top_p=0.5
    )
    return PromptTemplateConfig(
        name="summarizer",
        template=ConversationSummaryPlugin._summarize_conversation_prompt_template,
        description="Given as section of a conversation transcript, summarize the part of the conversation.",
        execution_settings={"default":execution_settings}
    )