"""LLM and embedding providers: local Ollama or Azure OpenAI, behind one interface."""

from typing import Protocol

import numpy as np
import requests

from .config import Settings


class Provider(Protocol):
    name: str

    def embed_documents(self, texts: list[str]) -> np.ndarray: ...
    def embed_query(self, text: str) -> np.ndarray: ...
    def chat(self, system: str, user: str) -> str: ...


def _normalise(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, 1e-12, None)


class OllamaProvider:
    def __init__(self, settings: Settings):
        self.s = settings
        self.name = f"Ollama ({settings.ollama_chat_model} + {settings.ollama_embed_model})"

    def _embed(self, texts: list[str]) -> np.ndarray:
        r = requests.post(
            f"{self.s.ollama_url}/api/embed",
            json={"model": self.s.ollama_embed_model, "input": texts},
            timeout=300,
        )
        r.raise_for_status()
        return _normalise(np.array(r.json()["embeddings"], dtype=np.float32))

    # nomic-embed-text expects task prefixes on documents and queries.
    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self._embed([f"search_document: {t}" for t in texts])

    def embed_query(self, text: str) -> np.ndarray:
        return self._embed([f"search_query: {text}"])[0]

    def chat(self, system: str, user: str) -> str:
        r = requests.post(
            f"{self.s.ollama_url}/api/chat",
            json={
                "model": self.s.ollama_chat_model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=300,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()


class AzureOpenAIProvider:
    def __init__(self, settings: Settings):
        from openai import AzureOpenAI

        missing = [
            k for k, v in {
                "AZURE_OPENAI_ENDPOINT": settings.azure_endpoint,
                "AZURE_OPENAI_API_KEY": settings.azure_api_key,
                "AZURE_OPENAI_CHAT_DEPLOYMENT": settings.azure_chat_deployment,
                "AZURE_OPENAI_EMBED_DEPLOYMENT": settings.azure_embed_deployment,
            }.items() if not v
        ]
        if missing:
            raise ValueError(f"Missing Azure OpenAI settings: {', '.join(missing)}")
        self.s = settings
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_endpoint,
            api_key=settings.azure_api_key,
            api_version=settings.azure_api_version,
        )
        self.name = f"Azure OpenAI ({settings.azure_chat_deployment} + {settings.azure_embed_deployment})"

    def _embed(self, texts: list[str]) -> np.ndarray:
        resp = self.client.embeddings.create(model=self.s.azure_embed_deployment, input=texts)
        return _normalise(np.array([d.embedding for d in resp.data], dtype=np.float32))

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self._embed(texts)

    def embed_query(self, text: str) -> np.ndarray:
        return self._embed([text])[0]

    def chat(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.s.azure_chat_deployment,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0,
        )
        return resp.choices[0].message.content.strip()


def get_provider(settings: Settings) -> Provider:
    if settings.provider == "azure":
        return AzureOpenAIProvider(settings)
    if settings.provider == "ollama":
        return OllamaProvider(settings)
    raise ValueError(f"Unknown RAG_PROVIDER '{settings.provider}' (use 'ollama' or 'azure')")
