import json
from openai import AsyncOpenAI
from app.config import get_settings
from app.services.ai.prompt_builder import build_optimization_prompt

settings = get_settings()
client = AsyncOpenAI(api_key="ollama", base_url=settings.ollama_base_url)


async def get_optimization_suggestions(sql, total_cost, execution_time_ms, seq_scans, expensive_nodes) -> dict:
    system_prompt, user_prompt = build_optimization_prompt(
        sql, total_cost, execution_time_ms, seq_scans, expensive_nodes
    )

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0,
        max_tokens=1500,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"severity": "ok", "suggestions": [], "rewritten_sql": None, "cost_comparison": None}
