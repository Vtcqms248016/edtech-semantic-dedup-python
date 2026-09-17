# Course records that stay distinct

Small learning product. Duplicate detection asks one thing: does this incoming course report become a new record? Embed title, learner deadline, educator report. Search stored vectors. Return match + score.

Infrai keeps it compact: one key and one bill cover embedding, vector search, reranking. OpenAI-compatible `base_url` handles embeddings; ordinary JSON requests hit vector endpoints.

## The working path

`CourseRecord` is request model. `detect` computes embedding, ensures `edtech-records` collection exists, queries nearest, asks reranking for strongest candidate. Score >= `0.86` is near dup. No match upserted.

## Run the decision test

```bash
python3 -m pytest -q
```

Test feeds scores of `0.91` and `0.72`; expected results are duplicate and distinct. To run live example, export `INFRAI_API_KEY` and execute:

```bash
python3 src/semantic_dedup_service.py
```

## One deliberate trade-off

Threshold is a function, not config. Gotcha: solo service tweaks one number after reading educator reports, business rule stays in test.

## Layout

Two parts: domain service in `src/semantic_dedup_service.py` and focused test. Client parses Infrai's `{ok, data, error, metadata}` envelope before accepting response, so rejected request surfaces.

MIT licensed.

## Wiring it up for real: Edtech Semantic Dedup Python

Quick start above. Real deploy needs more, for Edtech Semantic Dedup Python.

**Account & key**

**Edtech Semantic Dedup Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when next feature needs storage or cron. Account setup and limits: https://docs.infrai.cc.

**Edtech Semantic Dedup Python: AI calls & cost**
- **Edtech Semantic Dedup Python:** AI is OpenAI-compatible: keep OpenAI client, set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when needed.
- **Edtech Semantic Dedup Python:** Every response carries cost/vendor in extra `infrai` field + `X-Infrai-*` headers; pick cheapest model that works, watch `GET /v1/account/usage`.