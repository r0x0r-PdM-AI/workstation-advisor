import json

SCALE_LABELS = {1: "Starter", 2: "Professional", 3: "Enterprise"}


def format_taxonomy_for_prompt(workloads: list[dict]) -> str:
    lines = [f"{n}. {w['name']} (ID: {w['id']})" for n, w in enumerate(workloads, start=1)]
    return "\n".join(lines)


def build_extraction_system_prompt(taxonomy_str: str) -> str:
    return f"""You are a workload classification assistant for a Dell workstation recommendation system.

Read the user's description and map it to exactly one workload from the taxonomy below.
Also select exactly one scale_level integer based on the following definitions:
  1 (Starter): entry-level use — simple workflows, small datasets, single user, basic compute needs
  2 (Professional): mid-range use — moderate complexity, typical professional workloads, team-level scale
  3 (Enterprise): high-end use — large datasets, complex workflows, maximum compute, organisation-scale

Return only valid JSON. No explanation, no markdown, no preamble.

On a successful match return:
{{"workload_id": <int>, "scale_level": <int>, "matched_workload_name": "<str>", "confidence": "high"}}

If you cannot map the description confidently, return:
{{"confidence": "low"}}

## Taxonomy
{taxonomy_str}"""


def build_reasoning_system_prompt() -> str:
    return """You are a Dell workstation recommendation assistant.

For each recommended product write 2-3 sentences explaining why it is a good fit.
Reference the user's actual description — do not use generic product copy.
Focus on why this product matches this workload at this scale level.
Write in second person ("For your use case...").
Do not use marketing language or superlatives.

Return only valid JSON. No markdown, no preamble.

Output format:
{"reasoning": [
    {"product_id": <int>, "explanation": "<2-3 sentences>"},
    ...
]}"""


def build_reasoning_user_message(
    user_description: str,
    workload_name: str,
    scale_level: int,
    products: list[dict],  # keys: product_id, name, max_cpu_cores, max_ram_gb, max_gpu_vram_gb, gpu_vram_range
) -> str:
    return (
        f'User description: "{user_description}"\n'
        f'Matched workload: "{workload_name}" at {SCALE_LABELS.get(scale_level, str(scale_level))} scale (level {scale_level})\n'
        f"Recommended products: {json.dumps(products, indent=2)}"
    )
