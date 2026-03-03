import re
from openai import AsyncOpenAI
from app.config import get_settings
from app.services.ai.prompt_builder import build_nl_to_sql_prompt
from app.services.ai.validator import validate_sql

settings = get_settings()
client = AsyncOpenAI(api_key="ollama", base_url=settings.ollama_base_url)


async def generate_sql(natural_language: str) -> str:
    system_prompt, user_prompt = build_nl_to_sql_prompt(natural_language)

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0,
        max_tokens=1000,
    )

    sql = response.choices[0].message.content.strip()

    # Extract SQL from markdown code block if model adds one
    match = re.search(r"```[\w]*\n?(.*?)```", sql, re.DOTALL)
    if match:
        sql = match.group(1).strip()
    else:
        sql = sql.strip()

    is_valid, error = validate_sql(sql)
    if not is_valid:
        raise ValueError(f"AI generated invalid SQL: {error}\nSQL: {sql}")

    return sql
