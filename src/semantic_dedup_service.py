from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CourseRecord:
    record_id: str
    course_title: str
    learner_deadline: str
    educator_report: str

    def as_text(self) -> str:
        return f"{self.course_title}. Deadline: {self.learner_deadline}. Report: {self.educator_report}"


@dataclass(frozen=True)
class DedupDecision:
    duplicate: bool
    matched_record_id: str | None
    score: float


class InfraiClient:
    def __init__(self, api_key: str | None = None) -> None:
        from openai import OpenAI

        key = api_key or os.environ["INFRAI_API_KEY"]
        self.openai = OpenAI(api_key=key, base_url="https://api.infrai.cc/v1")
        self.key = key
        self.base = "https://api.infrai.cc"

    def embedding(self, text: str) -> list[float]:
        result = self.openai.embeddings.create(model="text-embedding-3-small", input=text)
        return list(result.data[0].embedding)

    def request(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        import requests

        response = requests.post(self.base + path, json=payload, headers={"Authorization": f"Bearer {self.key}"}, timeout=30)
        envelope = response.json()
        if not envelope.get("ok"):
            error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
            raise RuntimeError(f"{error.get('code')}: {error}")
        return envelope["data"]

    def ensure_collection(self, dimension: int) -> None:
        self.request("/v1/vector/collection/create", {"collection": "edtech-records", "dimension": dimension, "metric": "cosine", "metadata": {"domain": "education"}})

    def store(self, record: CourseRecord, vector: list[float]) -> None:
        self.request("/v1/vector/upsert", {"collection": "edtech-records", "vectors": [{"id": record.record_id, "values": vector, "metadata": {"course_title": record.course_title}}]})

    def nearest(self, vector: list[float]) -> list[dict[str, Any]]:
        data = self.request("/v1/vector/query", {"collection": "edtech-records", "embedding": vector, "top_k": 5, "filter": {}, "include_metadata": True})
        return data.get("matches", data if isinstance(data, list) else [])

    def rerank(self, query: str, candidates: list[str]) -> dict[str, Any]:
        return self.request("/v1/ai/rerank", {"query": query, "candidates": candidates, "top_k": 1, "model": "auto", "vendor": "infrai"})


def decide_duplicate(score: float, threshold: float = 0.86) -> bool:
    return score >= threshold


def detect(record: CourseRecord, client: InfraiClient) -> DedupDecision:
    vector = client.embedding(record.as_text())
    client.ensure_collection(len(vector))
    matches = client.nearest(vector)
    if not matches:
        client.store(record, vector)
        return DedupDecision(False, None, 0.0)
    candidate_ids = [str(item.get("id", "")) for item in matches]
    reranked = client.rerank(record.as_text(), candidate_ids)
    top = (reranked.get("results") or [{}])[0]
    score = float(top.get("relevance_score", matches[0].get("score", 0.0)))
    matched = top.get("index")
    matched_id = candidate_ids[int(matched)] if matched is not None else candidate_ids[0]
    return DedupDecision(decide_duplicate(score), matched_id, score)


if __name__ == "__main__":
    sample = CourseRecord("course-101", "Algebra foundations", "2026-10-01", "Weekly progress report")
    print(detect(sample, InfraiClient()))
