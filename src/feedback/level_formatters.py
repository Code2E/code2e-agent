"""
Feedback formatters — Evaluator 결과를 L1/L2/L3 텍스트로 변환.
Orchestrator가 Evaluator → Executor 스트림에서 사용.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

MAX_FAILURES = 5


@dataclass
class FailureResult:
    test_id: str
    description: str
    request_method: str
    request_path: str
    request_body: Optional[dict]
    expected_status: int
    expected_json_contains: Optional[list[str]]
    actual_status: int
    error_message: Optional[str]
    failure_category: str
    interpretation: Optional[str] = field(default=None)  # L3 only

    def _expected_line(self) -> str:
        if self.expected_json_contains:
            fields = ", ".join(f'"{f}"' for f in self.expected_json_contains)
            return f"{self.expected_status} with JSON containing {fields}"
        return str(self.expected_status)

    def _input_line(self) -> str:
        if self.request_body:
            return f"{self.request_method} {self.request_path}  {json.dumps(self.request_body)}"
        return f"{self.request_method} {self.request_path}"


def format_l1(total: int, passed: int, failures: list[FailureResult]) -> str:
    """
    L1: 실패 개수 + 카테고리별 집계만.
    """
    failed = total - passed
    if failed == 0:
        return f"All {total} evaluator tests passed."

    counts: dict[str, int] = {}
    for f in failures:
        counts[f.failure_category] = counts.get(f.failure_category, 0) + 1

    cats = ", ".join(f"{cat} ({n})" for cat, n in sorted(counts.items()))
    return f"{failed} of {total} evaluator tests failed.\nFailure categories: {cats}"


def format_l2(total: int, passed: int, failures: list[FailureResult]) -> str:
    """
    L2: L1 + 실패 test별 (입력, 기대값, 실제값, 에러 메시지).
    """
    failed = total - passed
    if failed == 0:
        return f"All {total} evaluator tests passed."

    lines: list[str] = [f"{failed} of {total} evaluator tests failed.", ""]
    capped = failures[:MAX_FAILURES]

    for i, f in enumerate(capped, 1):
        lines.append(f"[Test {i}] {f.failure_category}")
        lines.append(f"  Input:    {f._input_line()}")
        lines.append(f"  Expected: {f._expected_line()}")
        lines.append(f"  Actual:   {f.actual_status}")
        lines.append(f"  Error:    {f.error_message if f.error_message else '(none — assertion failed)'}")
        lines.append("")

    if len(failures) > MAX_FAILURES:
        lines.append(f"+{len(failures) - MAX_FAILURES} more failures not shown.")

    return "\n".join(lines).rstrip()


def format_l3(total: int, passed: int, failures: list[FailureResult]) -> str:
    """
    L3: L2 + 각 실패에 대한 행동 기반 interpretation (사용자 관점 의미 서술).
    """
    failed = total - passed
    if failed == 0:
        return f"All {total} evaluator tests passed."

    lines: list[str] = [f"{failed} of {total} evaluator tests failed.", ""]
    capped = failures[:MAX_FAILURES]

    for i, f in enumerate(capped, 1):
        lines.append(f"[Test {i}] {f.failure_category}")
        lines.append(f"  Input:    {f._input_line()}")
        lines.append(f"  Expected: {f._expected_line()}")
        lines.append(f"  Actual:   {f.actual_status}")
        lines.append(f"  Error:    {f.error_message if f.error_message else '(none — assertion failed)'}")
        if f.interpretation:
            lines.append(f"  Interpretation: {f.interpretation}")
        lines.append("")

    if len(failures) > MAX_FAILURES:
        lines.append(f"+{len(failures) - MAX_FAILURES} more failures not shown.")

    return "\n".join(lines).rstrip()
