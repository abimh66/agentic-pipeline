from app.modules.decision_assistant.services import (
    generate_constraints,
    generate_queries,
    search_internet,
    Comparison,
    synthesis_answer,
)
from app.worker import celery_app


@celery_app.task
def start_process(topic: str):
    print("Generate constraints...")
    constraints_result = generate_constraints(topic)

    print("Generate queries...")
    queries = generate_queries(
        constraints=constraints_result.constraints, options=constraints_result.options
    )

    full_comparison: list[Comparison] = []

    for data in queries.queries:
        print(f"Search internet with query {data.query}...")
        response = search_internet(query=data.query, constraint=data.constraint)

        full_comparison.append(response)

    print("Synthesizing Answer...")
    raw_answer = synthesis_answer(
        topic=topic,
        comparisons=full_comparison,
        constraints=constraints_result.constraints,
    )

    print("Writing report...")
    with open("report.md", "w") as file:
        file.write(raw_answer)
