# Agent Interface (v0.1)

Orchestrator ↔ Agent 통신 규약. Week 7 구현의 단일 출처.

> 본 문서는 v0.1 초안. 구현 중 발견되는 issue는 이 문서에 PR로 반영 후 팀에 공유.

---

## 1. 공통 원칙

- **Agent는 stateless**: 모든 상태(코드 버전, iteration count, run config 등)는 Orchestrator가 보유. Agent는 매 호출마다 새로 시작.
- **Agent는 텍스트 입출력만**: 파일 I/O, 네트워크 호출, 서브프로세스 생성 금지. Anthropic SDK 호출은 허용 (LLM 추론 목적).
- **Orchestrator가 모든 side effect 수행**: 코드 파일 작성, 서버 기동/종료, HTTP 요청, Playwright 실행, DB 검증 등.
- **One-shot subprocess**: Orchestrator가 매 호출마다 agent subprocess를 띄우고, JSON 한 번 주고받고, 종료. (장수형 subprocess 아님. 단순성 우선.)

---

## 2. Wire Protocol

### 2.1 Subprocess 기동 방식

```bash
python -m src.agents.<agent_name>
```

- 작업 디렉토리: 프로젝트 루트
- 환경 변수: `ANTHROPIC_API_KEY` 필수
- stdin: JSON 요청 1건 (한 줄, EOF로 종료)
- stdout: JSON 응답 1건 (한 줄)
- stderr: 자유 로깅 (Orchestrator가 디버그용으로 캡처)
- exit code: `0` 정상, `1` 실패

### 2.2 요청 형식

```json
{"method": "<method_name>", "params": { ... }}
```

### 2.3 응답 형식

성공:
```json
{"result": { ... }, "usage": {"input_tokens": N, "output_tokens": N}}
```

실패:
```json
{"error": {"type": "<error_type>", "message": "<msg>"}}
```

`usage`는 비용 추적용. Anthropic SDK 응답의 `usage` 그대로 전달.

### 2.4 코드 표현 (공통 타입)

여러 파일을 다루는 task(특히 Task-L)를 위해 코드는 항상 **path → content 딕셔너리**로 표현:

```json
{
  "files": {
    "main.py": "from fastapi import FastAPI\n...",
    "templates/index.html": "<!DOCTYPE html>\n...",
    "static/app.js": "..."
  }
}
```

Task-S/M은 보통 `main.py` 단일 키만 사용. 형식은 동일.

---

## 3. Agent별 인터페이스

### 3.1 Planner

**역할**: prompt.txt를 5-section 구조화 plan으로 변환.

**Method**: `plan`

**Input**:
```json
{"method": "plan", "params": {"prompt": "<prompt.txt 원문>"}}
```

**Output**:
```json
{"result": {"plan": "[Task Goal]: ...\n\n[Conditions to satisfy]:\n  1. ...\n\n[Suggested Architecture]:\n  ...\n\n[Implementation Notes]:\n  ...\n\n[Build Sequence]:\n  1. ...\n  2. ..."}}
```

`plan` 문자열은 experimental_design.md 3.2.3의 5-section 포맷을 그대로 따름. 마지막 `[Build Sequence]` 섹션은 Executor의 scaffold loop이 순회할 step list.

---

### 3.2 Executor

**역할**: 코드 생성 및 수정. 4가지 method (`scaffold` + 3 revise).

#### 3.2.1 `scaffold`

Run 시작 시 plan의 `build_sequence`를 순회하며 각 step마다 1회씩 호출. 첫 호출에서 `files_so_far`는 빈 dict, 이후 호출은 직전 호출의 출력을 그대로 입력으로 받음. 모든 step 완료 후의 누적 결과가 v1.

**Input**:
```json
{
  "method": "scaffold",
  "params": {
    "plan": "<Planner output 전체>",
    "files_so_far": {"main.py": "..."},
    "current_step": "<step 설명 한 줄>",
    "step_index": 0,
    "total_steps": 3
  }
}
```

- 첫 호출: `files_so_far = {}`, `step_index = 0`
- 마지막 호출: `step_index = total_steps - 1`

**Output**:
```json
{"result": {"files": {"main.py": "...", "...": "..."}}}
```

전체 누적 dict (delta 아님). Executor는 받은 `files_so_far` 위에 `current_step`만큼 추가/수정하고, 이전 step의 결과는 임의로 재작성하지 않음.

`step_index` / `total_steps`는 LLM 컨텍스트용 (예: 시스템 프롬프트에 "지금 step 2/4를 진행 중" 명시).

#### 3.2.2 `revise_for_advisor`

**Input**:
```json
{
  "method": "revise_for_advisor",
  "params": {
    "files": {"main.py": "..."},
    "advisor_feedback": "<Advisor의 raw_text>"
  }
}
```

**Output**: `{"result": {"files": {...}}}`

#### 3.2.3 `fix_runtime_error`

**Input**:
```json
{
  "method": "fix_runtime_error",
  "params": {
    "files": {"main.py": "..."},
    "error": "<raw error string>"
  }
}
```

**Output**: `{"result": {"files": {...}}}`

피드백 포맷은 raw error 그대로. L1/L2/L3 무관 (통제 변수).

#### 3.2.4 `revise_for_evaluator`

**Input**:
```json
{
  "method": "revise_for_evaluator",
  "params": {
    "files": {"main.py": "..."},
    "evaluator_feedback": "<L1/L2/L3 포맷팅된 텍스트>"
  }
}
```

**Output**: `{"result": {"files": {...}}}`

Executor는 자신이 어떤 level의 feedback을 받았는지 모름. 받은 텍스트만 보고 수정.

---

### 3.3 Advisor

**역할**: Whitebox static review (3-category structured).

**Method**: `review`

**Input**:
```json
{"method": "review", "params": {"files": {"main.py": "..."}}}
```

**Output**:
```json
{
  "result": {
    "structural": ["설명 1", "설명 2"],
    "ai_slop": ["설명 1"],
    "potential_bug": ["설명 1"],
    "verdict": "PASSED",
    "raw_text": "[Advisor Review of Code]\n\nStructural issues (2):\n  - ...\n..."
  }
}
```

- `verdict`: `"PASSED"` 또는 `"NEEDS_REVISION"`
- `raw_text`: experimental_design.md 3.2.2 포맷의 전체 문자열. Executor에 전달할 때 그대로 사용.
- 세 카테고리 list는 Orchestrator가 metric 집계할 때 사용.

---

### 3.4 Evaluator

**역할**: 블라인드 상태에서 task 조건만 보고 test case 생성 + (옵션) 실패 결과 해석.

**중요**: Evaluator는 코드를 보지 않음. 코드 실행은 Orchestrator가 수행하고 결과만 다시 전달.

#### 3.4.1 `generate_tests`

Run 시작 시 1회만 호출. 같은 run의 모든 iteration이 동일 test set 사용.

**Input**:
```json
{
  "method": "generate_tests",
  "params": {
    "prompt": "<task prompt.txt 원문>",
    "task_metadata": {"tier": "S", "stack": "backend"}
  }
}
```

**Output**:
```json
{
  "result": {
    "tests": [
      {
        "id": "eval_t1",
        "description": "POST /shorten with valid URL returns 201 with code",
        "type": "http",
        "request": {
          "method": "POST",
          "path": "/shorten",
          "headers": {"Content-Type": "application/json"},
          "body": {"url": "https://example.com"}
        },
        "expected": {
          "status": 201,
          "json_contains": ["code"]
        },
        "failure_category": "spec_violation"
      }
    ]
  }
}
```

- `type`: `"http"` (Task-S/M), `"playwright"` (Task-L FE만)
- `failure_category`: Evaluator 본인의 self-classification은 참고용. 최종 분류는 Orchestrator의 heuristic rule이 담당 (experimental_design.md 3.1.2).
- Playwright test 형식은 별도 sub-schema. Task-L 구현 직전에 추가 정의.

#### 3.4.2 `interpret_failures` (L3 전용)

L3 level run에서만 호출. L1/L2는 Orchestrator가 raw 결과만 포맷팅하므로 호출 불필요.

**Input**:
```json
{
  "method": "interpret_failures",
  "params": {
    "prompt": "<task prompt.txt>",
    "failures": [
      {
        "test_id": "eval_t1",
        "description": "POST /shorten with valid URL returns 201",
        "request": {...},
        "expected": {...},
        "actual": {"status": 500, "body": "Internal Server Error"},
        "failure_category": "spec_violation"
      }
    ]
  }
}
```

**Output**:
```json
{
  "result": {
    "interpretations": [
      {
        "test_id": "eval_t1",
        "interpretation": "엔드포인트가 응답 전에 크래시. 사용자 관점에서는 정상 URL에 대해 단축 작업 자체가 실패하는 것처럼 보임."
      }
    ]
  }
}
```

---

## 4. Orchestrator의 책임 (참고)

Agent 인터페이스를 사용하는 쪽이 어떻게 동작하는지 명시:

1. **서버 기동/종료**: 매 Evaluator iteration 시작 시 새 subprocess로 서버 기동, 끝나면 종료. Code는 임시 디렉토리에 풀어서 실행.
2. **Test 실행**: Evaluator가 반환한 `tests` list를 Orchestrator가 직접 `requests` (또는 Playwright)로 실행하고 actual 결과 수집.
3. **Failure category 판정**: experimental_design.md 3.1.2의 heuristic rule을 Orchestrator가 적용. Evaluator의 self-classification은 무시 (재현성 확보).
4. **Feedback 포맷팅**: L1/L2/L3 변환은 `src/feedback/level_formatters.py` 가 담당. Evaluator → Orchestrator → formatter → Executor 순서.
5. **State persistence**: Run config, iteration count, code 버전 history, metric 등 모두 Orchestrator만 보유.

---

## 5. 에러 처리

| 상황 | Orchestrator 처리 |
|---|---|
| Agent subprocess가 exit code 1로 종료 | `error` JSON 파싱하여 metric에 기록, 해당 단계 실패로 처리 |
| Agent subprocess가 timeout (default: 90s) | kill 후 timeout error로 기록 |
| stdout이 valid JSON 아님 | parse error로 기록, 해당 호출 실패 |
| Anthropic API rate limit / 일시적 에러 | Agent 내부에서 1회 retry, 그래도 실패하면 `error` 응답 |

---

## 6. 예시: Scaffolding Loop (v1 생성 전체 흐름)

Orchestrator 측 pseudocode:
```python
import subprocess, json

def call_executor(method: str, params: dict) -> dict:
    req = {"method": method, "params": params}
    proc = subprocess.run(
        ["python", "-m", "src.agents.executor"],
        input=json.dumps(req),
        capture_output=True,
        text=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise AgentError(proc.stderr)
    resp = json.loads(proc.stdout)
    if "error" in resp:
        raise AgentError(resp["error"])
    return resp["result"]

# Plan에서 build sequence 추출 (Planner가 구조화 텍스트로 반환)
build_sequence = parse_build_sequence(plan_text)  # List[str]
files = {}
for i, step in enumerate(build_sequence):
    result = call_executor("scaffold", {
        "plan": plan_text,
        "files_so_far": files,
        "current_step": step,
        "step_index": i,
        "total_steps": len(build_sequence),
    })
    files = result["files"]
# 모든 step 완료 후 files == v1
```

Agent 측 pseudocode (`src/agents/executor/__main__.py`):
```python
import sys, json
from anthropic import Anthropic

req = json.loads(sys.stdin.read())
method = req["method"]
params = req["params"]

client = Anthropic()  # ANTHROPIC_API_KEY 환경 변수 사용
# method에 따라 시스템 프롬프트 분기, client.messages.create(...) 호출
# 응답 파싱하여 files dict 생성

resp = {"result": {"files": files}, "usage": {...}}
print(json.dumps(resp))
```

---

## 7. TBD (Week 7 구현 중 확정)

- 시스템 프롬프트 (각 agent별, method별) — 정혁준/고기호 구현 시 작성
- Planner가 task 복잡도에 맞춰 `[Build Sequence]`를 일관되게 출력하게 하는 프롬프팅 패턴 (Task-S=1 step, Task-L=3-4 step) — Planner 구현 시 결정
- `parse_build_sequence` 헬퍼 위치 및 구현 (Planner 출력 텍스트에서 step list 추출) — Orchestrator 구현 시 결정
- Playwright test sub-schema — Task-L 구현 직전 (Week 8 후반 예상)
- Multi-file 코드를 LLM이 안정적으로 출력하게 하는 프롬프팅 패턴 (특히 scaffold step 간 이전 파일 보존) — Executor 구현 시 결정
- Timeout 기본값 조정 — smoke test 결과로 보정
- Anthropic SDK retry 정책 — 구현 시 결정
