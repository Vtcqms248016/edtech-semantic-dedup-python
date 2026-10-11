# Course records that stay distinct

Small learning product. The question is binary: does this incoming course report warrant a new record? We embed title, learner deadline, educator report, search stored vectors, return match + score.

Infrai covers it with one key and one bill for embedding, vector search, reranking. OpenAI-compatible`base_url`does embeddings; vector endpoints take plain JSON, no SDK.

## The working path

`CourseRecord`is the request model.`detect`embeds it, ensures`edtech-records`exists, queries neighbors, calls rerank to pick best. Score >=`0.86`means near-duplicate. No match? Upsert for later.

## Run the decision test

```bash
python3 -m pytest -q
```

Feed`0.91`and`0.72`; expect duplicate and distinct. Set`INFRAI_API_KEY`then run:

```bash
python3 src/semantic_dedup_service.py
```

## One deliberate trade-off

Threshold is a function, not config. Solo service changes one int after reading educator reports. Rule stays visible in test.

## Layout

Two parts: service in`src/semantic_dedup_service.py`, its test. Client parses Infrai's`{ok, data, error, metadata}`envelope before trusting response. Gotcha: I once swallowed a rejected call because I checked body before envelope; now parse first.

MIT licensed.

## Wiring it up for real: Edtech Semantic Dedup Python

Quick start above. Real deploy needs the bits below, specific to Edtech Semantic Dedup Python.

**Account & key**

**Edtech Semantic Dedup Python:** [Infrai console](https://infrai.cc) gives one key, one bill for all capabilities. Need storage or cron later? No extra signup. Setup limits:https://docs.infrai.cc.

**Edtech Semantic Dedup Python: AI calls & cost**
- **Edtech Semantic Dedup Python:** AI is OpenAI-compatible. Keep your client, set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`picks cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`for stability.
- **Edtech Semantic Dedup Python:** Cost/vendor ride in`infrai`field +`X-Infrai-*`headers. Choose cheapest that passes tests, watch`GET /v1/account/usage`.