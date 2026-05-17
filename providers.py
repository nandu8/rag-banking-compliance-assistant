import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

_MODELS = {
    "gemini":    "gemini-2.5-flash",
    "anthropic": "claude-sonnet-4-6",
    "openai":    "gpt-4o",
}


def get_llm(provider: str):
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=_MODELS["gemini"],
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3,
        )
    if provider == "anthropic":
        return ChatAnthropic(
            model=_MODELS["anthropic"],
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.3,
        )
    if provider == "openai":
        return ChatOpenAI(
            model=_MODELS["openai"],
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.3,
        )
    raise ValueError(
        f"Unknown LLM provider: '{provider}'. Valid options: gemini, anthropic, openai"
    )


def get_embeddings(provider: str):
    if provider == "gemini":
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    if provider == "openai":
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
    if provider == "anthropic":
        raise ValueError(
            "Anthropic does not provide an embedding model. "
            "Set EMBEDDING_PROVIDER=gemini or EMBEDDING_PROVIDER=openai."
        )
    raise ValueError(
        f"Unknown embedding provider: '{provider}'. Valid options: gemini, openai"
    )
