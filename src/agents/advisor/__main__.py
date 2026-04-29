"""
Advisor agent — 코드를 보고 3-category 구조화 리뷰 수행.
실행: python -m src.agents.advisor
stdin:  JSON 요청 1건
stdout: JSON 응답 1건
"""
import json
import sys

from anthropic import Anthropic

_client = Anthropic()
_MODEL = "claude-sonnet-4-6"
_TEMPERATURE = 0.2


def _review(params: dict) -> dict:
    files: dict[str, str] = params["files"]

    files_block = "\n".join(
        f"--- {path} ---\n{content}" for path, content in files.items()
    )

    system = (
        "You are a code reviewer in a blind multi-agent system.\n"
        "Review the provided code and output a structured 3-category review.\n\n"
        "Output valid JSON only, no markdown fences, no explanation:\n"
        "{\n"
        '  "structural": ["issue 1"],\n'
        '  "ai_slop": ["warning 1"],\n'
        '  "potential_bug": ["bug 1"],\n'
        '  "verdict": "PASSED"\n'
        "}\n\n"
        "Categories:\n"
        "  structural   — architecture problems, missing abstractions, bad organization\n"
        "  ai_slop      — generic boilerplate, unnecessary complexity, over-engineering\n"
        "  potential_bug — logic errors, unhandled edge cases, security holes\n\n"
        'verdict must be "PASSED" (no actionable issues) or "NEEDS_REVISION" (actionable issues found).\n'
        "Empty lists are allowed. Only include real issues."
    )

    response = _client.messages.create(
        model=_MODEL,
        max_tokens=2048,
        temperature=_TEMPERATURE,
        system=system,
        messages=[{"role": "user", "content": f"Review this code:\n\n{files_block}"}],
    )

    parsed = json.loads(response.content[0].text.strip())
    structural: list[str] = parsed.get("structural", [])
    ai_slop: list[str] = parsed.get("ai_slop", [])
    potential_bug: list[str] = parsed.get("potential_bug", [])
    verdict: str = parsed.get("verdict", "PASSED")

    raw_lines = [
        "[Advisor Review of Code]",
        "",
        f"Structural issues ({len(structural)}):",
        *[f"  - {item}" for item in structural],
        "",
        f"AI slop warnings ({len(ai_slop)}):",
        *[f"  - {item}" for item in ai_slop],
        "",
        f"Potential bugs ({len(potential_bug)}):",
        *[f"  - {item}" for item in potential_bug],
        "",
        f"Overall: {verdict}",
    ]

    return {
        "result": {
            "structural": structural,
            "ai_slop": ai_slop,
            "potential_bug": potential_bug,
            "verdict": verdict,
            "raw_text": "\n".join(raw_lines),
        },
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


_DISPATCH = {"review": _review}


def main() -> None:
    req = json.loads(sys.stdin.read())
    method = req.get("method", "")
    params = req.get("params", {})

    handler = _DISPATCH.get(method)
    if handler is None:
        print(json.dumps({"error": {"type": "unknown_method", "message": f"Unknown method: {method}"}}))
        sys.exit(1)

    try:
        resp = handler(params)
    except Exception as exc:
        print(json.dumps({"error": {"type": "agent_error", "message": str(exc)}}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(resp, ensure_ascii=False))


if __name__ == "__main__":
    main()
