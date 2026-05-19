import json
from typing import Dict
from app.modules.decision_assistant.utils import oai_client, tavily_client
from pydantic import BaseModel


class Constraints(BaseModel):
    options: list[str]
    constraints: list[str]


class Query(BaseModel):
    query: str
    constraint: str


class Queries(BaseModel):
    queries: list[Query]


class Comparison(BaseModel):
    comparison: Dict[str, list[str]]


EXTRACT_INTENT_PROMPT = """
You are an AI assistant that extracts structured decision-making information from user queries.

Your task:
Given a user query, extract:
1. options (things being compared)
2. constraints (criteria for comparison)

Rules:
- If constraints are not explicitly mentioned, infer 3-5 relevant ones
- Keep constraints concise (1-3 words each)
"""

EXTRACT_QUERIES_PROMPT = """
You are an AI assistant that generates search queries for comparing technologies.

Your task:
Given:
- a list of options
- a list of constraints

Generate ONE search query per constraint that compares ALL options.
"""

EXTRACT_COMPARISON_PROMPT = """
You are an AI assistant that extracts structured comparisons from web content.

Your task:
Given:
- a constraint
- multiple web content snippets

Extract a fair comparison between the options.

Rules:
- Focus ONLY on the given constraint
- Do NOT add external knowledge
- Summarize based ONLY on the provided content
- Be concise (max 3 points per option)

Output format:
{
  "comparison": {
    "<option1>": ["point1", "point2"],
    "<option2>": ["point1", "point2"]
  }
}
"""

SYNTHESIS_PROMPT = """
You are an AI assistant that helps users make decisions based on structured comparisons.

Your task:
Given multiple constraint comparisons, generate a final recommendation report.

Rules:
- Use a markdown format
- Provide a clear recommendation
- Explain reasoning briefly
- Be neutral and helpful

Includes:
- Comparison table
- Recommendation
- Reasoning
"""


def generate_constraints(topic: str) -> Constraints:
    res = oai_client.chat.completions.parse(
        model="google/gemini-3.1-flash-lite",
        messages=[
            {"role": "system", "content": EXTRACT_INTENT_PROMPT},
            {"role": "user", "content": topic},
        ],
        response_format=Constraints,
    )

    content = res.choices[0].message.parsed

    if content is None:
        raise ValueError("No intent generated")

    return content


def generate_queries(options: list[str], constraints: list[str]) -> Queries:
    json_content = json.dumps({"options": options, "constraints": constraints})

    res = oai_client.chat.completions.parse(
        model="google/gemini-3.1-flash-lite",
        messages=[
            {"role": "system", "content": EXTRACT_QUERIES_PROMPT},
            {
                "role": "user",
                "content": f"""Generate queries based on the following JSON input:\n\n {json_content}""",
            },
        ],
        response_format=Queries,
    )

    content = res.choices[0].message.parsed

    if content is None:
        raise ValueError("No queries generated")

    return content


def generate_comparison(constraint: str, search_results: list[str]) -> Comparison:
    json_content = json.dumps(
        {"constraint": constraint, "search_results": search_results}
    )

    res = oai_client.chat.completions.parse(
        model="google/gemini-3.1-flash-lite",
        messages=[
            {"role": "system", "content": EXTRACT_COMPARISON_PROMPT},
            {
                "role": "user",
                "content": f"""Generate a structured comparison based on the following JSON input:\n\n {json_content}""",
            },
        ],
        response_format=Comparison,
    )

    content = res.choices[0].message.parsed

    if content is None:
        raise ValueError("No comparison generated")

    return content


def search_internet(query: str, constraint: str) -> Comparison:
    response = tavily_client.search(query=query)

    results = response.get("results", [])

    comparison = generate_comparison(constraint=constraint, search_results=results)

    return comparison


def synthesis_answer(topic: str, constraints: list[str], comparisons: list[Comparison]):
    json_content = json.dumps(
        {
            "topic": topic,
            "constraints": constraints,
            "comparisons": [comparison.model_dump() for comparison in comparisons],
        }
    )

    res = oai_client.chat.completions.create(
        model="google/gemini-3.1-flash-lite",
        messages=[
            {"role": "system", "content": SYNTHESIS_PROMPT},
            {
                "role": "user",
                "content": f"Generate a final synthesized answer based on the JSON input below.\n\n {json_content}",
            },
        ],
    )

    content = res.choices[0].message.content

    if content is None:
        raise ValueError("No synthesis answer generated")

    return content
