"""
Evaluator agent — 블라인드 상태에서 task prompt만 보고 HTTP test case 생성 + 실패 해석.
실행: python -m src.agents.evaluator
stdin:  JSON 요청 1건
stdout: JSON 응답 1건
"""
import json
import sys

from anthropic import Anthropic

_client = Anthropic()
_MODEL = "claude-sonnet-4-6"
_TEMPERATURE = 0.2


def _generate_tests(params: dict) -> dict:
    prompt = params["prompt"]
    task_metadata = params.get("task_metadata", {})

    system = (
        "You are a blind test generator for a REST API evaluation system.\n"
        "You generate HTTP test cases based only on the task description — you never see the implementation.\n\n"
        "Output valid JSON only, no markdown fences, no explanation:\n"
        "{\n"
        '  "tests": [\n'
        "    {\n"
        '      "id": "eval_t1",\n'
        '      "description": "...",\n'
        '      "type": "http",\n'
        '      "request": {\n'
        '        "method": "POST",\n'
        '        "path": "/...",\n'
        '        "headers": {"Content-Type": "application/json"},\n'
        '        "body": {}\n'
        "      },\n"
        '      "expected": {\n'
        '        "status": 201,\n'
        '        "json_contains": ["field"]\n'
        "      },\n"
        '      "failure_category": "spec_violation"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "failure_category must be one of: spec_violation, runtime, edge_case, security, performance\n"
        "Generate tests that cover all stated conditions. Omit json_contains when not applicable."
    )

    user = (
        f"Task prompt:\n{prompt}\n\n"
        f"Task metadata: {json.dumps(task_metadata)}\n\n"
        "Generate comprehensive HTTP test cases covering every condition."
    )

    response = _client.messages.create(
        model=_MODEL,
        max_tokens=4096,
        temperature=_TEMPERATURE,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    result = json.loads(response.content[0].text.strip())
    return {
        "result": result,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


def _interpret_failures(params: dict) -> dict:
    prompt = params["prompt"]
    failures = params["failures"]

    system = (
        "You are a blind test interpreter for a REST API evaluation system.\n"
        "You observe HTTP test failures and interpret them from a user's perspective.\n"
        "You do NOT see the implementation code.\n\n"
        "Output valid JSON only, no markdown fences, no explanation:\n"
        "{\n"
        '  "interpretations": [\n'
        "    {\n"
        '      "test_id": "eval_t1",\n'
        '      "interpretation": "From a user\'s perspective, ..."\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Each interpretation must describe the observed failure in user-facing behavioral terms."
    )

    user = (
        f"Task prompt:\n{prompt}\n\n"
        f"Test failures:\n{json.dumps(failures, ensure_ascii=False, indent=2)}\n\n"
        "Interpret each failure from a user's perspective."
    )

    response = _client.messages.create(
        model=_MODEL,
        max_tokens=2048,
        temperature=_TEMPERATURE,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    result = json.loads(response.content[0].text.strip())
    return {
        "result": result,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


_DISPATCH = {
    "generate_tests": _generate_tests,
    "interpret_failures": _interpret_failures,
}


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
