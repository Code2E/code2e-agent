# Code2E 실험 설계 v0.8 (초안)

> **v0.8 변경**: 측정 + 데모 dual-track 구조로 전면 재편.
> - 동기: 예산($400) 안에서 (1) 깨끗한 level 효과 측정과 (2) 큰 규모 풀스택 시연을 동시에 달성하기 위함. 기존 50-run 매트릭스는 큰 규모 task 도입 시 비용 폭발 위험.
> - **매트릭스 축소**: 50 runs → **16 runs** (측정 15 + 데모 1)
>   - 측정: Task-M × L1/L2/L3 × 5 repeats = 15 runs (sweet-spot tier에서 level 효과 측정)
>   - 데모: Task-L × L2 × 1 run = 1 run (큰 규모 풀스택, 측정과 별개의 시연)
> - **Task scope 변화**:
>   - Task-M: 측정 본체. middle-tier (auth + DB)
>   - Task-L: 데모 only, 큰 규모로 확대 (단일 run)
>   - Task-S: smoke test 용도만 (시스템 파이프라인 검증, 측정 매트릭스 제외)
> - **Sprint 기반 아키텍처 도입** (큰 task 대응):
>   - 기존 "scaffold loop 전부 끝 → Advisor" → **"sprint별 scaffold + Advisor sub-loop"** (현실 PR 워크플로우 모사)
>   - Section 6.1 pseudocode 재작성, sprint 상한 폐기 (Planner 자유)
> - **Claim 재구조화**: Claim C v0.2 → v0.3 (측정 + 데모 dual)
>   - (a)(b)(c) Task-M에서 비대칭 측정 (기존 (d) tier 의존은 Task 1개라 정성 서술로 약화)
>   - (e) 큰 규모 풀스택 데모 가능성 (신규)
> - **B2 sanity check 폐기**: "within-blind" framing으로 사전 commit
> - **비용 telemetry first-class**: Orchestrator에 token/cost 추적, hard cap (per-run Track 1 $15 / Track 2 $100, total $350)
> - **Sprint 적용 범위 명시 (§6.2.2)**: sprint 구조는 v1 생성 단계에만 적용, v1 이후 revise는 sprint 무관
> - **Playwright failure heuristic 추가 (§3.1.2)**: Task-L 프론트엔드 분류 규칙
> - Section 1, 3, 4, 5, 6, 7, 7.5, 8, 10, 11, 12 전면 갱신
>
> **v0.7 변경** (누적): Scaffolding loop 도입.
> - `Executor.generate_initial` → `Executor.scaffold` (multi-step)
> - Planner 출력에 `[Build Sequence]` 섹션 추가 (4-section → 5-section)
> - Section 3.2.1 통제 변수 표에 `Max scaffold steps per task` 추가
> - Section 3.2.3 (Planner 출력), 6.1 (pseudocode), 6.2 (코드 버전 카운트) 갱신
> - 동기: Task-L (BE+SQLite+FE)을 1회 호출로 생성 시 Sonnet 출력 토큰 한계(기본 8K) 근접 + 각 층 품질 저하 위험.
> - v1의 정의가 "단일 호출 결과"에서 "build sequence 전체 완료 후 누적 결과"로 바뀜. v2~v9 정의는 무변경.
>
> **v0.6 변경** (누적): 문서 내부 일관성 정리 (stale reference 수정).
> - Section 10: `90 runs` → `45 runs`, `30 runs` → `5 runs` (v0.2 scope 축소 반영)
> - Section 10: task 디렉토리에 `canonical.py` 추가 (Section 4.4와 일관성)
> - Section 11 Stage 1: Week 6 → Week 7 초 (현재 시점 보정)
> - Section 11 Stage 2: Week 7 → Week 8 말 (Section 8 timeline과 일관성)
> - Section 11 Stage 4: Week 8 → Week 9 (Section 8 timeline과 일관성)
> - Section 11 Stage 5: `10 repeat` → `5 repeat` (v0.2 scope 축소 반영)
> - Section 12 제목: `v0.1의 알려진 한계` → `알려진 한계`
> - Section 0 Context: "5주차 현 시점" → "6주차 말 현 시점"
> - Section 8 Week 6: "실험 설계 v0.2 확정" → "실험 설계 현행본 확정"
>
> **v0.5 변경** (누적): Loop guard 버그 수정.
> - Advisor loop과 Evaluator loop에 "마지막 iteration에서는 revise 하지 않음" guard 추가
> - **버그 해소**: Evaluator loop에서 마지막 revision이 테스트 없이 만들어지면 hidden test 채점 대상과 Evaluator가 마지막으로 본 코드가 달라서 overfit gap metric이 오염되는 문제
> - Max 코드 버전 수: v11 → **v9**
> - Advisor / Runnability / Evaluator 세 loop 모두 동일한 guard 패턴 적용 (내부 일관성)
>
> **v0.4 변경** (누적): 기대 결과 시나리오 사전 commit.
> - Section 7.5 신설: 7개 outcome scenario와 각각의 claim 층 생존 여부 표
> - 사후 cherry-picking 방지 목적
>
> **v0.3 변경** (누적): Runtime error 처리 개선.
> - Advisor 루프과 Evaluator 루프 사이에 **Runnability Pre-Check** 전용 loop 추가
> - Runtime error는 Evaluator iteration을 낭비하지 않도록 사전 처리
> - Executor에 `fix_runtime_error` 메소드 추가 (raw error 전달, L1-L3와 무관)
>
> **v0.2 변경** (누적): 파란학기제 12주 단축 일정 반영.
> - 반복 수 10 → 5 (Primary)
> - B2 scope: 3 tasks → Task-S only (30 runs → 5 runs)
> - Timeline을 현재 시점(Week 6 말, 4/12) 기준으로 재작성
> - Week 9 비상 체크포인트 추가

## Context

Code2E는 "블라인드 멀티 에이전트 구조를 통한 AI 기반 개발 자동화"를 목표로 하는 학부 연구 프로젝트(2026-1 파란학기제)이며, Anthropic의 두 harness 논문 ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Harness Design for Long-Running Apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)) 을 직접 후속하는 연구를 지향합니다.

1-4주차 동안 시스템 아키텍처는 `Master/Code/Test/Final` 4-agent 구조 → `Planner/Executor/Advisor/Evaluator` 오케스트레이션 구조로 한 차례 피벗했습니다. 7주차 말 현 시점(2026-04-18)에서 시스템 구현이 시작되었으며, v0.8에서 실험 설계가 dual-track 구조로 재편되었습니다.

이 문서는 그 실험 설계의 현행 초안입니다 (v0.1부터 iterative 수정 진행 중, v0.8에서 dual-track 전환). Claim, 방법론, 변수, 태스크, run matrix, 분석 계획, decision gate를 통합 정리합니다. 향후 세부 결정(태스크 prompt 구체화, 시스템 프롬프트, orchestrator 구현 세부 등)은 모두 이 문서를 기준점으로 진행됩니다.

**핵심 통찰** — Code2E는 두 트랙의 dual case study입니다. Track 1은 "피드백 정보 밀도가 정확성과 overfit에 어떻게 비대칭적으로 작용하는가"를 sweet-spot 복잡도 task에서 측정하고, Track 2는 같은 시스템이 큰 규모 풀스택 task에서도 동작 가능함을 시연합니다. 두 트랙은 독립이라 한 트랙의 실패가 다른 트랙을 무너뜨리지 않으며, 방법론은 traditional benchmark가 아닌 **case study** (Anthropic 두 글과 동일 전통)를 채택합니다.

---

## 1. Research Claim

### 1.1 Primary (Claim C v0.3) — 측정 + 데모 dual

> 블라인드 멀티 에이전트 시스템에서 Executor에게 전달되는 Evaluator 피드백의 정보 밀도(L1/L2/L3)는 **풀 수 있는 중간 복잡도 태스크(Task-M)에서 코드의 실질적 정확성(H-PR)과 평가자 적합도(overfit gap)에 비대칭적으로 작용**하며, **같은 시스템은 큰 규모의 풀스택 태스크(Task-L)에서도 의미 있는 산출물을 생성할 수 있음**을 시연한다.

주장의 누적 구조 (Track 1 + Track 2):

**Track 1 — 측정 (Task-M, n=15)**:
- (a) 피드백 밀도가 H-PR에 영향을 준다
- (b) 피드백 밀도가 overfit gap에 영향을 준다
- (c) 두 지표에 대한 영향이 비대칭적이다 (← 프로젝트의 핵심 bet)

**Track 2 — 데모 (Task-L, n=1)**:
- (d) 시스템이 큰 규모 풀스택 (BE + DB + FE) task에서 동작 완료 가능
- (e) 그 산출물이 hidden test로 측정 가능한 품질을 가짐

각 층이 무너져도 바로 아래 층이 정당한 finding으로 남는 robust 구조 + 두 트랙은 서로 독립이라 한 트랙이 실패해도 다른 트랙이 보존됨.

### 1.2 Secondary (Claim B 분해 분석)

Track 1의 hidden test를 failure category(spec_violation / runtime / edge_case / security)별로 분해하여, 비대칭이 어느 카테고리에서 두드러지는지 관찰. 같은 데이터로 추가 분석 가능하므로 비용 부담 없음.

Track 2의 데모에서도 failure mode (어디서 시스템이 약한가)를 정성 분석.

### 1.3 Fallback (정직성 장치)

- **Track 1 null 결과**: "within-blind feedback density characterization at middle-tier" 으로 framing. 데이터·차트는 그대로, 수사만 약화.
- **Track 2 partial failure** (시스템이 끝까지는 도는데 H-PR 낮음): "scaling failure mode case study" 로 framing. 데모 자체가 finding.
- **Track 2 complete failure** (시스템이 안 도는 경우): 디버깅 후 1회 재실행. 그래도 실패면 "current limits of blind multi-agent codegen at scale" 솔직 보고.

본 설계는 **이전 v0.2의 B2 premise validation을 폐기**했으므로 "블라인드의 효과" 자체는 본 실험에서 검증하지 않음. "within-blind" framing이 default.

### 1.4 두 Anthropic 글에 대한 위치

- **글 1 ("단일 vs 멀티 에이전트")**: 멀티 내부에서 "피드백이 어떻게 흐르는가"가 숨은 축임을 측정으로 특성화 (Track 1)
- **글 2 ("QA tuning이 어렵다")**: 그 어려움의 구조를 정량 곡선 + 큰 규모 시연으로 보강 (Track 1 + 2)

---

## 2. Methodology

**Dual-track case study framework** — Anthropic harness 논문과 동일한 방법론적 전통

**Track 1 (측정)**:
- Task-M(중간 복잡도, sweet-spot tier) 1개에 집중
- 독립 변수(feedback level L1/L2/L3)를 체계적으로 조작
- Cell당 5 runs (15 runs 총합)으로 평균 + bootstrap CI 산출 가능한 최소 규모
- 통계는 보조, 메인은 mechanism의 질적 서술

**Track 2 (데모)**:
- Task-L(큰 규모 풀스택) 1개를 1회 실행
- 측정이 아닌 시연: "할 수 있다"의 존재 증명 + failure mode 관찰
- Track 1에서 가장 실용적인 level (L2)로 사전 commit 후 실행

**Benchmark가 아닌 이유**: Code2E의 claim은 평균 성능 비교가 아니라 mechanism characterization + scale demonstration. Case study가 방법론적으로 정합. Anthropic 두 글이 모두 단일 또는 소수의 야심찬 태스크로 연구를 수행한 precedent가 있음.

**Sweet-spot tier 선정 근거**: Task-S는 Sonnet 4.6에 너무 쉬워 ceiling effect로 level 차이가 묻힐 위험, Task-L은 너무 복잡해 floor effect + variance dominance로 신호가 묻힐 위험. Task-M(인증 + DB + 다중 엔드포인트 = 풍부한 failure 다양성, 풀어볼 만한 난이도)이 level 효과를 가장 잘 드러낼 가능성이 높음.

---

## 3. Variables

### 3.1 Independent Variable: Feedback Level (L1-L3)

Evaluator → Executor 피드백의 정보 밀도를 3단계로 조작.

#### 3.1.1 레벨 정의 (요약)

| Level | 포함 정보 |
|---|---|
| **L1 (Minimal)** | 실패 개수 + 카테고리별 집계 |
| **L2 (Structured)** | L1 + 실패 test별 (입력, 기대값, 실제값, 에러 메시지) |
| **L3 (Rich)** | L2 + 각 실패에 대한 행동 기반 interpretation (사용자 관점 의미 서술) |

#### 3.1.2 설계 결정

**직렬화 형식**: 구조화된 plain text (JSON 아님, labeled sections)
- LLM 입력으로 자연스러움, Executor 프롬프트에 직접 삽입
- 로그 디버깅이 용이

**적용 범위**: Evaluator → Executor 스트림에만. Advisor 피드백은 통제 변수로 고정 (별도 연구 주제로 분리)

**시간적 안정성**: Run 단위로 고정. 한 run 안 모든 iteration이 같은 level. Run 간에만 varies. (Within-run dynamic level은 후속 연구로 분리.)

**History 누적 없음**: 각 iteration의 피드백은 현 iteration의 코드에 대한 결과만. 이전 피드백은 컨텍스트에 남지 않음. 이유:
- Level fixed 원칙과 정합 (history가 누적되면 실질 정보량이 iteration마다 증가)
- 컨텍스트 bloat 방지
- Iteration별 effect 독립 분석 가능

**실패 개수 cap**: **최대 5개**. 초과 시 "+N more" 표시만.
- 피드백 길이를 예측 가능하게
- Executor가 한 iteration에 처리 가능한 수정 범위의 현실적 제한
- Prototype 돌려본 후 조정 가능

**Failure category 판정**: **Heuristic rule** (Evaluator self-classification 아님)
- 결정론적, 재현 가능, 분석 일관성 보장
- HTTP 기반 (Task-S/M/L 백엔드):
  | 조건 | Category |
  |---|---|
  | 기대 HTTP status와 다른 status 반환 | spec_violation |
  | HTTP 5xx 반환 | runtime |
  | 경계값/빈 입력에서 서버 잘못 반응 | edge_case |
  | 미인증/권한 없는 접근이 성공 | security |
  | Timeout / 비정상 지연 | performance |
- Playwright 기반 (Task-L 프론트엔드만):
  | 조건 | Category |
  |---|---|
  | 기대 element/text가 DOM에 없음 (selector miss) | spec_violation |
  | JavaScript console에 uncaught exception | runtime |
  | 빈 입력/특수문자에서 화면 깨짐 | edge_case |
  | 인증 없이 보호된 페이지 접근 가능 | security |
  | Element wait timeout (default > 5초) | performance |
  | Page 자체가 로드 실패 (HTTP 4xx/5xx) | runtime |
- 두 카테고리 체계는 동일한 라벨(spec_violation 등)을 공유하므로 분석 시 통합 가능

**L3의 "interpretation" 정체성**: **행동 기반 해석**
- 블라인드 원칙상 Evaluator는 코드를 못 보므로 코드 레벨 힌트 불가
- 대신 Evaluator가 관찰한 행동의 **사용자 관점 의미 서술**
- Anthropic 글 2의 Playwright evaluator 스타일과 유사

#### 3.1.3 L2가 자연 기준점

주차 보고서에서 팀이 원래 제안한 `{type, input, expected, actual, error_msg}` 포맷이 정확히 L2에 해당. L1은 information-starved 조건, L3는 information-rich 조건.

#### 3.1.4 Concrete Examples (단축 URL 서비스 Task-S 맥락)

가정: Executor 코드에서 3개 evaluator test 실패

**L1 출력**:
```
3 of 7 evaluator tests failed.
Failure categories: spec_violation (2), edge_case (1)
```

**L2 출력**:
```
3 of 7 evaluator tests failed.

[Test 1] spec_violation
  Input:    POST /shorten  {"url": "https://example.com"}
  Expected: 201 with JSON containing "code" field
  Actual:   500
  Error:    AttributeError: 'NoneType' object has no attribute 'encode'
            at url_store.py:23

[Test 2] spec_violation
  Input:    POST /shorten  {"url": "https://example.com"}  (second call)
  Expected: same "code" as first call
  Actual:   different code returned
  Error:    (none — assertion failed)

[Test 3] edge_case
  Input:    POST /shorten  {"url": ""}
  Expected: 400 with error message
  Actual:   500
  Error:    TypeError in url_validator.py:8
```

**L3 출력**:
```
3 of 7 evaluator tests failed.

[Test 1] spec_violation
  Input:    POST /shorten  {"url": "https://example.com"}
  Expected: 201 with JSON containing "code" field
  Actual:   500
  Error:    AttributeError: 'NoneType' object has no attribute 'encode'
            at url_store.py:23
  Interpretation: The endpoint crashes before returning a response.
    From a user's perspective, the shorten operation completely fails
    on valid URLs — the server appears broken.

[Test 2] spec_violation
  Input:    POST /shorten  {"url": "https://example.com"}  (second call)
  Expected: same "code" as first call
  Actual:   different code returned
  Error:    (none — assertion failed)
  Interpretation: The system generates a new code each time instead of
    recognizing duplicate URLs. Users would accumulate many codes for
    the same URL, and the same long URL would never consistently map
    to one short form.

[Test 3] edge_case
  Input:    POST /shorten  {"url": ""}
  Expected: 400 with error message
  Actual:   500
  Error:    TypeError in url_validator.py:8
  Interpretation: Empty input should be rejected politely, but the
    server crashes instead. This means the input validation is missing
    or broken for degenerate inputs.
```

#### 3.1.5 가설 — 각 level의 예상 효과

- **L1**: Executor가 "가장 일반적인 재작성" 으로 회귀. 특정 실패에 overfit할 기회 부족. Hidden test 성능 ≈ Executor baseline 능력.
- **L2**: Executor가 구체 실패를 보고 직접 대응. Evaluator test overfit 시작. Hidden test 성능은 Evaluator test coverage에 강하게 의존.
- **L3**: Evaluator 해석이 더해져 Executor가 behavior-level로 수정. Hidden test와 Evaluator test가 같은 behavior에 관심 두면 둘 다 개선, 그렇지 않으면 L2 대비 overfit gap 더 커질 수 있음.

이 가설의 검증/반박이 Claim C의 본론.

### 3.2 Controlled Variables

#### 3.2.1 요약 표

| 변수 | 고정값 |
|---|---|
| LLM 모델 | **Claude Sonnet 4.6 uniform** (모든 agent 동일) |
| Temperature | 0.2 (모든 run) |
| Evaluator 루프 max iterations | 5 (pilot 후 재검토 option) |
| Advisor 루프 max iterations | 3 |
| Advisor 피드백 포맷 | Structured 3-category (아래 3.2.2) |
| Planner 프롬프트 출력 구조 | Structured 5-section (아래 3.2.3) |
| Max sprints per task | Task-M 5, Task-L 15 (Planner가 task 복잡도에 맞춰 결정, 상한) |
| Max Advisor reviews per sprint | 3 (sprint 내부 sub-loop) |
| Per-run budget cap (Track 1, Task-S smoke, P1) | $15 USD (Orchestrator hard kill 기준) |
| Per-run budget cap (Track 2, Task-L 데모) | $100 USD (큰 규모 task 허용 한도) |
| Total experiment budget cap | $350 USD (전체 누적 비용 hard cap) |
| Task 정의 | 한 번 확정 후 수정 금지 |
| Hidden test 내용 | 시스템 구현 시작 전 확정 후 수정 금지 |
| Process isolation | Subprocess 격리 (각 agent가 별도 Python subprocess, stdin/stdout 통신) |

**LLM 모델 선택 근거**:
- 연구 해석 가능성을 위해 uniform model 필수 (섞어 쓰면 confound)
- Sonnet은 Task-S/M/L 모두 충분한 능력
- 예산 현실적 (~$60-120 total)
- Haiku는 Task-L에서 능력 borderline, Opus는 과투자

**Temperature 0.2 근거**:
- 0: 결정론 → 반복 간 variance 없음 → 반복 실험 의미 없음
- 0.2: 최소 확률성으로 variance 측정 가능, 동시에 signal이 묻히지 않음
- 0.7+: 너무 noisy, effect 검출 어려움
- 최근 LLM 연구의 de facto 표준

**Subprocess isolation 근거**:
- 같은 프로세스 내에서는 accidentally 정보 leak 가능 (공유 전역, import, 객체)
- Subprocess면 정보 채널이 구조적으로 명시됨
- Docker까지는 과투자. Subprocess가 "cheap yet meaningful" 격리
- Paper 작성 단계에서 필요시 Docker로 업그레이드 option

#### 3.2.2 Advisor 피드백 포맷 (3-category structured)

```
[Advisor Review of Code v<N>]

Structural issues (<count>):
  - <description 1>
  - <description 2>

AI slop warnings (<count>):
  - <description 1>

Potential bugs (<count>):
  - <description 1>

Overall: <PASSED | NEEDS_REVISION>
```

**원칙**:
- 3개 카테고리로 고정: `structural` / `ai_slop` / `potential_bug`
- 각 카테고리 count + bullet list
- 마지막 verdict가 `PASSED`면 Evaluator 루프로 진행, `NEEDS_REVISION`이면 Executor가 수정 후 재검토
- 포맷은 실험 내내 고정 (통제 변수)

#### 3.2.3 Planner 출력 구조 (5-section structured)

```
[Task Goal]: <한 문장 요약>

[Conditions to satisfy]:
  1. <원문 그대로 인용>
  2. <원문 그대로 인용>
  ...

[Suggested Architecture]:
  - Endpoints: <나열>
  - Data model: <간단 설명>
  - Key logic: <핵심 알고리즘>

[Implementation Notes]:
  - <주의사항, 엣지 케이스>

[Build Sequence]:
  1. <step 1 — 자연어 한 줄, 무엇을 만들지>
  2. <step 2>
  ...
```

**원칙**:
- Conditions는 원문 그대로 인용 (Planner가 해석/축약하지 말 것)
- Planner 자유도는 Architecture + Notes + Build Sequence 섹션에만
- 이 포맷 고정으로 Planner 산출물의 변수성 최소화

**Build Sequence 작성 가이드라인** (이하 "sprint" 와 동의어로 사용):
- Sprint 수는 task 복잡도에 비례
  - Task-S (smoke test): 1 sprint
  - Task-M (측정): 권장 3-5 sprints (예: 데이터 모델 → 인증 → 비즈니스 로직 → 통합 검증)
  - Task-L (데모): 권장 8-15 sprints (BE 데이터 모델 → BE 엔드포인트 그룹별 → FE 페이지별 등)
- 상한: Task-M 5, Task-L 15 (통제 변수, §3.2.1)
- 각 sprint는 자연어 한 줄로 "이 sprint에서 완성할 기능" 명시 (예: "3. 이체 트랜잭션 로직 (atomicity + rollback)")
- Sprint 순서 = 의존성 순. 후속 sprint는 선행 sprint의 산출물에 의존 가능
- 각 sprint는 **자체적으로 review 가능한 단위** (현실 PR 단위에 해당) — 한 sprint 안에서 너무 많은 기능을 묶지 말 것
- Executor의 `scaffold` + Advisor의 sub-loop이 sprint별로 호출됨 (§6.1)

#### 3.2.4 Evaluator 루프 max iterations 재검토 option

v0.1에 5회로 박아두되, Week 7 smoke test 결과에 따라:
- 대부분 run이 5회 안에 수렴 → 5 유지
- Task-L 절반이 수렴 실패 → Task-L만 7회 예외
- 거의 다 수렴 실패 → 7회로 일괄 상향

단, 일괄 상향 시 실험 총 비용 영향 (~40% 증가) 재검토 필요.

### 3.3 Dependent Variables (Metrics)

**Primary metric**:
- **Hidden Test Pass Rate (H-PR)**: Executor도 Evaluator도 보지 못한 canonical test set의 통과율

**Process metric**:
- **Overfit Gap** = `(Evaluator-generated test pass rate) - (Hidden test pass rate)`. 양수가 클수록 overfit
- **Iterations to completion**: 루프 중단 전까지의 반복 수
- **Regression count**: 수정 중 통과했다가 다시 깨진 test 수
- **Token cost / wall clock**: 실용 참고 지표

**Quality metric (optional secondary)**:
- Static analysis warnings (ruff/mypy)
- Cyclomatic complexity, LOC

---

## 4. Tasks (Dual-Track 구조)

각 태스크는 자연어 프로즈 + 명시적 번호 조건의 형태. Hidden test는 조건의 기계적 번역.

**Dual-track 설계 원칙**: 측정용 task와 데모용 task의 역할을 분리. 측정 task(Task-M)는 sweet-spot 복잡도로 level 효과를 깨끗이 측정, 데모 task(Task-L)는 큰 규모로 시스템의 scale 능력 시연. Task-S는 시스템 파이프라인 검증용 smoke test로만 사용.

| 역할 | Task | 스택 | 매트릭스 비중 |
|---|---|---|---|
| **Smoke test** | Task-S | Backend (in-memory) | 측정 X (시스템 검증 1회) |
| **측정 (Track 1)** | Task-M | Backend + SQLite | L1/L2/L3 × 5 = 15 runs |
| **데모 (Track 2)** | Task-L | Backend + SQLite + Frontend | L2 × 1 = 1 run |

### 4.1 Task-S (Smoke test) — **단축 URL 서비스**

- **역할**: 시스템 파이프라인이 end-to-end 동작하는지 검증. 측정 매트릭스에 포함되지 않음
- **스택**: Python REST API, in-memory 저장
- 단일 리소스 CRUD 수준 + 중복/충돌 처리
- 자연어 프롬프트 + **목표 5개 명시 조건** (±1 융통성)
- 핵심 메커니즘: 같은 long URL은 같은 short code, 코드 충돌 처리, redirect 의미
- 예상 hidden test 수: 10-15개
- **사용 시점**: Week 8 초 — Task-M 본 실험 진입 전 시스템 동작 확인용 1회 실행

### 4.2 Task-M (측정 본체) — **로그인 할일 관리**

- **역할**: Track 1 측정의 단일 task. L1/L2/L3 × 5 repeats = 15 runs
- **스택**: Python REST API + SQLite
- 인증 + user isolation + 다중 엔드포인트 + 상태 전이 + 영속 저장
- 자연어 프롬프트 + **목표 7개 명시 조건** (±1 융통성)
- 핵심 메커니즘: 사용자 격리, 토큰 검증, 권한 경계, 완료 상태 변경, DB 스키마 설계
- 예상 hidden test 수: 15-20개
- 주요 failure categories: spec_violation, edge_case, security, runtime
- **선정 근거**: Sweet-spot tier (Task-S는 ceiling, Task-L은 floor 위험). auth + DB + 다중 엔드포인트가 충분한 failure 다양성 제공 + Sonnet 4.6에 풀어볼 만한 난이도 → level 차이가 가장 잘 드러날 가능성 높음 (§2 참고).

### 4.3 Task-L (데모, 큰 규모) — **소규모 풀스택 서비스 (구체 도메인 미정)**

- **역할**: Track 2 데모. L2 × 1 run으로 큰 규모 풀스택 시스템 시연
- **스택**: Python REST API + SQLite + vanilla HTML/CSS/JS Frontend (필요 시 추가)
- **규모 목표**: 본격 풀스택 서비스 (대략 LOC 2000-5000, sprint 8-15개 분량)
  - 기존 v0.7의 "잔고 이체 서비스 + 12 조건"보다 의도적으로 크게
  - 구체 도메인은 Week 9-10 측정 결과 분석 후 확정 (TODO+, 미니 게시판, 미니 협업툴 등 후보)
- 자연어 프롬프트 + **목표 ~20개 이상 명시 조건** (구체 수는 도메인 확정 시 결정)
- 주요 failure categories: 모두 (spec_violation, edge_case, security, runtime, performance)
- **Frontend hidden test**: Playwright 기반 브라우저 테스트
- **Fallback**:
  - 데모 단계 (Week 11)에서 Playwright test 생성이 불안정하면 FE 조건 일부 제거
  - 시스템이 끝까지 못 돌면 디버깅 후 1회 재실행, 그래도 실패면 "scaling failure mode" framing으로 정직 보고 (§1.3)
- **N=1의 의미**: 통계적 검증이 아니라 "할 수 있다"의 존재 증명 + 정성적 failure mode 분석. cherry-pick 방지 위해 L2 사전 commit (Track 1 결과와 무관)

**도메인 선택 근거**: 측정과 데모를 분리함으로써 각 task의 부담을 명확히 함. Task-M은 측정에 최적화된 sweet-spot 그릇, Task-L은 시스템의 한계 시연용 큰 그릇. 두 트랙은 독립이라 한 트랙의 실패가 다른 트랙을 무너뜨리지 않음.

**알려진 한계**: 측정이 Task-M 1개에 의존하므로 "tier에 따른 비대칭 변화" (기존 Claim C v0.2의 (d) 층)는 본 실험에서 검증 불가. Limitations에 명시 (§12).

### 4.4 산출물 형식

```
tasks/task_s/                        # Smoke test 용도
├── prompt.txt          # 자연어 입력 (시스템 공개)
├── hidden_tests.py     # pytest + requests 기반 canonical test (시스템 차단)
├── canonical.py        # 사람이 작성한 이상적 구현 (sanity check용)
└── task_metadata.json  # 역할 = "smoke", 조건 수, failure category 분포

tasks/task_m/                        # 측정 본체
├── prompt.txt
├── hidden_tests.py     # pytest + requests + DB 상태 검증
├── canonical.py
└── task_metadata.json  # 역할 = "measurement", ...

tasks/task_l/                        # 데모 (Week 10-11 도메인 확정 후 작성)
├── prompt.txt
├── hidden_tests.py     # pytest + requests + DB + Playwright
├── canonical/           # FE 포함이므로 디렉토리
│   ├── app.py
│   ├── templates/
│   └── static/
└── task_metadata.json  # 역할 = "demo", ...
```

### 4.5 Hidden test 작성 원칙 및 형식

**원칙**:
- 자연어 조건의 **기계적 번역** — 연구자의 주관적 해석 층 없음
- 조건에 명시되지 않은 기대치(rate limit, 보안, 성능)는 hidden test에 포함하지 않음
- 각 test에 failure category tag 부착 (Claim B 분해 분석용)

**형식**: pytest
- 네이밍 규칙: `test_C<condition_id>_<short_description>`
- Failure category는 decorator로: `@pytest.mark.failure_category("spec_violation")`
- Fixture로 test client / setup 공통화
- 실행 결과는 JSON으로 export 가능 (분석 자동화)

**Backend test 예시** (Task-S, Task-M, Task-L 공통):
```python
@pytest.mark.failure_category("spec_violation")
def test_C1_post_returns_short_code():
    response = client.post("/shorten", json={"url": "https://example.com"})
    assert response.status_code == 201
    assert "code" in response.json()
```

**Frontend test 예시** (Task-L only, Playwright):
```python
@pytest.mark.failure_category("spec_violation")
def test_C10_transfer_form_shows_result(page):
    page.goto("http://localhost:8000")
    page.fill("#from-account", "A")
    page.fill("#to-account", "B")
    page.fill("#amount", "100")
    page.click("#transfer-btn")
    expect(page.locator("#result")).to_contain_text("이체 완료")
```

### 4.6 Canonical reference implementation

**목적**:
1. Hidden test sanity check — 정상 구현이 모든 hidden test를 통과하는지 검증
2. "이상적 구현은 어떤 모습인가" 의 baseline
3. AI Slop이 없는 사람 코드의 참조점

**작성 원칙**: 우아함보다 명료함. 가능한 한 단순하게. 테스트 통과가 목적이고 그 이상은 하지 않음.

**작성 시점**: Hidden test 확정 직후. Test를 돌려서 전부 통과하는지 확인하는 것으로 hidden test 품질을 검증.

### 4.7 교차 검증 프로세스 (독립 작성 후 비교)

**단계**:
1. **작성자**가 prompt.txt + hidden_tests.py 작성
2. **검토자**가 prompt.txt만 보고 자신이 생각하는 hidden test를 짧게 스케치 (5분 이내, 완성 필요 없음)
3. 두 사람이 모여 비교:
   - 작성자의 test가 검토자 스케치보다 많으면 → "조건에 없는 걸 추가했나?" 점검
   - 검토자 스케치가 작성자보다 많으면 → "작성자가 조건 일부를 놓쳤나?" 점검
4. 합의된 set만 최종 hidden_tests.py로 확정
5. 합의 못 한 항목은 **삭제가 기본** (보수적 — 의심스러우면 빼라)

**핵심**: 두 사람이 **독립적으로** 도출 후 비교. "함께 작성하며 합의" 보다 훨씬 객관적.

---

## 5. Experimental Matrix

**v0.8 dual-track 구조**: 측정(Track 1) + 데모(Track 2) 분리. 50 runs → 16 runs로 대폭 축소하고, 절감된 비용을 Track 2 데모의 task 규모에 투자.

### 5.1 Track 1 — 측정 (Task-M)

| 축 | 값 | 개수 |
|---|---|---|
| Task | **Task-M only** | 1 |
| Feedback level | L1, L2, L3 | 3 |
| Repeat | 독립 run | **5** |

**Track 1 runs: 1 × 3 × 5 = 15 runs**

### 5.2 Track 2 — 데모 (Task-L)

| 축 | 값 | 개수 |
|---|---|---|
| Task | **Task-L only** (큰 규모) | 1 |
| Feedback level | **L2** (사전 commit, Track 1 결과와 무관) | 1 |
| Repeat | 1 (단일 run) | 1 |

**Track 2 runs: 1 × 1 × 1 = 1 run**

**N=1 commit 근거**: 데모는 통계 검증이 아니라 시연. 1 run에 큰 system을 만드는 것이 더 가치 있음. 비용 여유를 큰 규모에 투자.

### 5.3 Smoke Test (매트릭스 외)

| 항목 | 값 |
|---|---|
| Task | Task-S |
| Level | L2 |
| Repeat | 1 |
| 목적 | 시스템 파이프라인 동작 확인 (Week 8 초) |

본 실험 매트릭스에 포함되지 않으므로 분석 대상 아님.

### 5.4 합계 + 비용

| 항목 | 수치 |
|---|---|
| 측정 runs (Track 1) | 15 |
| 데모 runs (Track 2) | 1 |
| Smoke test | 1 |
| **총 runs** | **17** (분석 대상은 16) |
| 추정 비용 (사전 추정, P1 후 보정) | Track 1 $75-225 + Track 2 $50-100 + Smoke ~$5 = **$130-330** |
| Total budget cap | $350 USD (hard cap) |
| Wall clock (3 parallel, Track 1) | ~3-6시간 |
| Wall clock (Track 2 단일) | 30분-2시간 |

**비용 측정**: 1 run의 실제 비용은 P1 (Week 8 말 Task-M × L1 + L3 × 1 = 2 runs)에서 측정. 그 데이터로 Track 1 본 실행 진행 가/부 결정. P1 결과로 1 run > $15 면 scope 축소 (repeat 5 → 3) 또는 매트릭스 재검토.

### 5.5 P1 Pilot (본 실험 진입 결정 게이트)

| 항목 | 값 |
|---|---|
| 시점 | Week 8 말 |
| Runs | Task-M × L1 × 1 + Task-M × L3 × 1 = 2 runs |
| 목적 | (1) 1 run당 실제 비용 측정, (2) Task-M의 L 차이가 sweet spot 안에 있는지 (ceiling/floor 회피 확인) |

**P1 결과 → 본 실험 의사결정 표**:

| P1 관찰 | 결정 |
|---|---|
| 1 run < $7, L1↔L3 H-PR 차이 10%p+ | Track 1 그대로 진행 |
| 1 run $7-15, 차이 10%p+ | Track 1 진행, 비용 모니터링 강화 |
| 1 run > $15 | Track 1 repeat 5→3 축소 또는 디버깅 |
| L1↔L3 차이 < 5%p (ceiling/floor 의심) | Task-M scope 보강 (조건 추가) 또는 Task 재선정 검토 |
| 시스템이 끝까지 못 돔 | Track 1 보류, 디버깅 우선 |

---

## 6. Single Run Procedure

### 6.1 전체 흐름 pseudocode

```python
# === Run Start ===

# 1. Planner 단계
plan = Planner.structure(prompt_txt)
# plan.build_sequence == ["sprint 1 설명", "sprint 2 설명", ...]
# Task-M 보통 3-5 sprints, Task-L 보통 8-15 sprints (상한 §3.2.1)

# 2. Sprint loop (v0.8 신설): scaffold + Advisor sub-loop을 sprint 단위로 반복
#    현실 PR 워크플로우 모사 — sprint마다 코드 추가 → 리뷰 → 수정 → 다음 sprint
MAX_ADVISOR_REVIEWS_PER_SPRINT = 3
code = {}
for sprint_idx, sprint in enumerate(plan.build_sequence):
    # 2a. Scaffold: sprint에 해당하는 코드 추가 작성
    code = Executor.scaffold(
        plan, code, sprint, sprint_idx, len(plan.build_sequence)
    )

    # 2b. Advisor sub-loop: 이 sprint까지의 누적 코드를 review
    for review_i in range(MAX_ADVISOR_REVIEWS_PER_SPRINT):
        review = Advisor.review(code)  # whitebox static review
        record_advisor_iteration(sprint_idx, review_i, review)
        if review.verdict == "PASSED":
            break
        if review_i == MAX_ADVISOR_REVIEWS_PER_SPRINT - 1:
            break  # guard: 마지막 review에서는 revise 하지 않음
        code = Executor.revise_for_advisor(code, review.feedback)
    # 다음 sprint로 진행

# 모든 sprint 완료 후 code == v1
# Sprint 내부 scaffold + revise는 v 카운트에 포함 안 됨 — v1 내부 구조

# 3. (구버전 단일 Advisor loop 제거 — sprint sub-loop이 대체)

# 4. Runnability Pre-Check (max 3 attempts)
#    목적: Evaluator 루프에 진입하기 전에 코드가 최소한 실행 가능함을 보장
#    Level과 무관 (통제 변수): 언제나 raw error만 Executor에게 전달
runnability_attempts = 0
MAX_RUNNABILITY_ATTEMPTS = 3
runnable = False
for i in range(MAX_RUNNABILITY_ATTEMPTS):
    try:
        server = start_server(code)
        stop_server(server)  # startup만 검증하고 바로 내림
        runnable = True
        break
    except (SyntaxError, ImportError, ServerStartupError) as e:
        runnability_attempts += 1
        metrics['runnability_attempts'] = runnability_attempts
        if i == MAX_RUNNABILITY_ATTEMPTS - 1:
            # 최종 시도 실패 → Evaluator 루프에 진입하되 모든 test runtime failure로 예상
            metrics['runnability_failed'] = True
            break
        # Executor에게 raw error 전달 (L1/L2/L3와 무관한 고정 포맷)
        code = Executor.fix_runtime_error(code, str(e))
        # i=0 → v4, i=1 → v5 (v3 이후 카운트)

# 5. Evaluator 루프 (max 5 tests, guarded on last)
MAX_EVALUATOR_TESTS = 5
previous_failures = None
previous_passes = set()
final_eval_result = None
for i in range(MAX_EVALUATOR_TESTS):
    # Fresh server instance per iteration
    try:
        start_server(code)
        eval_result = Evaluator.test(code)
    except (SyntaxError, ImportError, ServerStartupError) as e:
        # 이 시점에 runtime error가 나면 비정상 (pre-check 통과했는데 runtime error)
        # 회귀적으로 발생한 runtime error로 기록
        eval_result = FailureResult(failures=[
            Failure(category="runtime", error=str(e), ...)
        ])
    finally:
        stop_server()

    # Regression tracking (metric only, not stop signal)
    regressed = previous_passes - eval_result.passed_tests
    metrics['regression_count'] += len(regressed)
    previous_passes = eval_result.passed_tests

    record_iteration_metrics(eval_result)
    final_eval_result = eval_result  # 마지막으로 측정된 eval_result 저장

    if eval_result.all_pass:
        break

    # Stop condition: A1 (all pass) = break above
    # Stop condition: A2 (max iter) = loop termination
    # Stop condition: B1/B2 (no progress / same error) = off in v0.2

    if i == MAX_EVALUATOR_TESTS - 1:
        break  # guard: 마지막 test에서는 revise 하지 않음
               # → 마지막 test의 code = 최종 code (overfit gap 측정 정합성 확보)

    feedback = format_feedback_at_level(eval_result, run_level)  # L1/L2/L3
    code = Executor.revise_for_evaluator(code, feedback)
    # i=0 → v(prev+1), ..., i=3 → v(prev+4)
# 최종 code는 final_eval_result가 측정한 바로 그 code와 동일

# 6. Hidden test 채점 (시스템 미공개)
hidden_result = run_hidden_tests(code)
record_final(hidden_result, code)

# === Run End ===
```

### 6.2 루프 경계 규칙 (v0.8)

- **3개 외부 phase는 strict sequential**: Sprint loop (scaffold + Advisor sub-loop) → Runnability Pre-Check → Evaluator
- 각 phase는 이전 phase 결과와 무관하게 반드시 실행
- **모든 sub-loop에 "마지막 iteration에는 revise 하지 않음" guard 적용**
  - 이유 1: Evaluator loop에서 마지막 revision이 test 없이 만들어지면 overfit gap metric 오염 (마지막 test된 code ≠ 최종 code)
  - 이유 2: 모든 loop의 구조 일관성
  - 이유 3: "3회 iteration" = "3회 check, 2회 revise" 자연스러운 해석

- **최대 Executor 코드 생성 수 (v0.8)**:
  - v1 (sprint loop 누적 결과; sprint마다 1 scaffold + 최대 2 Advisor revise)
  - + v2~v3 (Runnability pre-check: 3 attempts, max **2 revisions**)
  - + v4~v7 (Evaluator loop: 5 tests, max **4 revisions**)
  - = **최대 v7** (sprint 내부 호출은 v 카운트에 포함 안 됨; v1을 만드는 내부 구조)

- Sprint 내부 호출 수 (별도 metric으로 추적):
  - Task-M 1 run worst case: 5 sprints × (1 scaffold + 2 advisor + 2 revise) = 25 Executor/Advisor 호출
  - Task-L 1 run worst case: 15 sprints × 5 호출 = 75 호출
  - Task-L의 비용이 큰 이유 (§5.4 비용 추정 근거)

- 실제 대부분 run은 Runnability 0-1 attempts로 해결되므로 보통 **v3~v5** 범위에서 끝남
- **v7는 극단적 worst case** (Runnability 2회 revise + Evaluator 4회 revise 모두 소진)

### 6.2.2 Sprint 구조의 적용 범위 (v0.8 명시)

**Sprint 구조는 v1 생성 단계(§6.1 Stage 2)에만 적용됨.** v1 완성 이후의 모든 단계 — Runnability pre-check, Evaluator loop — 는 sprint 구조와 무관하게 **전체 코드를 단일 단위로 다룸**.

구체적으로:
- `Executor.fix_runtime_error(files, error)` — 전체 files dict를 받고 raw error에 맞게 수정. sprint 인지 X
- `Executor.revise_for_evaluator(files, feedback)` — 전체 files dict를 받고 evaluator feedback에 맞게 수정. sprint 인지 X

**의도된 단순화 근거**:
- v1 단계는 "처음 만드는" 작업이라 sprint(=PR) 단위로 쪼개는 게 자연스러움
- v1 이후는 "고치는" 작업이라 어느 sprint를 고치는지 사전에 결정하기 어려움 (failure가 여러 sprint에 걸쳐 있을 수 있음)
- Executor가 전체 코드를 보고 알아서 수정 위치 판단하는 것이 더 합리적
- 인터페이스 단순성도 우선 (`revise_*` method가 sprint context 불필요)

**비용 영향**: v1 이후 revise 호출은 input에 전체 files dict 포함 → token 비용은 task가 클수록 비례 증가. 하지만 sprint 인지를 더해도 token 절감되지 않음 (어차피 전체 코드를 봐야 cross-cutting issue 판단 가능).

**모니터링 포인트**: 실제 운영에서 v1 이후 revise가 코드의 일부만 정확히 고치는지 (전체를 임의 재작성하지 않는지) 검증. 실패 시 시스템 프롬프트에 "변경 최소화" 명시 강화.

### 6.2.1 세 loop의 공통 guard 동작

모든 loop에서 마지막 iteration의 동작은 동일:
- 성공 (PASSED / runnable / all_pass): 정상 break, 다음 단계 진행
- 실패 (NEEDS_REVISION / not runnable / some fail): **결과만 metric에 기록**하고 break, 다음 단계 진행

즉 **마지막 iteration에서는 revise 없이 결과만 저장하고 진행**. 이것이 v0.5의 핵심 변경.

### 6.3 Stop Conditions

**Primary (v0.1에서 적용)**:
- **A1**: Evaluator test 모두 통과 → 성공 exit
- **A2**: Max iterations 도달 (Advisor=3, Evaluator=5) → 중단

**Optional (v0.1에서는 off, smoke test 후 결정)**:
- **B1**: 동일 failure set이 2회 연속 (no progress)
- **B2**: 동일 에러 메시지 exact match 2회 연속

**v0.1에서 B1/B2 off 이유**: Early stopping은 level에 따라 iteration 수를 달리 만들어 실험에 bias를 줄 수 있음 (L1은 regression 없이 빠르게 수렴, L2/L3는 early stop 걸려서 iteration 수가 줄어드는 식). v0.1은 단순 max iter만 적용하고, 실제 runs에서 "대부분 stuck에서 iteration 낭비" 패턴이 확인되면 그때 추가 여부 결정.

### 6.4 Regression Handling

- **Metric 기록만, stop signal 아님**
- 각 iteration에서 `regressed = previous_passes - current_passes` 계산
- `metrics['regression_count']` 에 누적
- Regression 빈도 자체가 분석의 finding (블라인드 구조의 failure mode 특성화)
- Regression을 stop signal로 쓰면 L1 vs L2/L3 간 bias 발생 (L2/L3가 더 민감하게 regression 검출)

### 6.5 Non-runnable 코드 처리 (v0.3 개정)

**Primary 처리**: Runnability Pre-Check loop에서 해결
- Syntax error / import error / server startup crash 가 감지되면
- Raw error 메시지를 Executor에 전달 → `Executor.fix_runtime_error(code, error)` 호출
- Max 3 attempts 안에 runnable 상태 도달 시도
- 3회 안에 해결되면 Evaluator 루프으로 진행, 해결 안 되면 실패 상태로 Evaluator 루프 진입

**왜 Advisor가 아닌 별도 loop인가**:
- Advisor는 whitebox static review 전담 (코드 구조, AI slop, 잠재 버그)
- Runtime 검증은 본질적으로 execution이 필요하므로 static review 성격과 분리
- 역할 분리로 논문 서술 및 후속 확장이 깔끔

**왜 Evaluator 루프 안이 아닌가**:
- Evaluator 루프에서 runtime error가 iteration을 소모하면 L1/L2/L3 비교가 오염됨
- 어떤 run은 2/5 iteration을 syntax 수정에, 어떤 run은 0/5 iteration을 → 실험 noise
- 전용 pre-check loop로 분리함으로써 Evaluator iteration은 "실제 동작하는 코드에 대한 피드백 루프" 에만 사용

**Feedback 포맷**:
- Runnability pre-check에서 Executor에게 전달되는 것은 **raw error string 그대로**
- L1/L2/L3 level과 무관 (통제 변수 — 모든 run에서 동일)
- 예:
  ```
  [RUNTIME ERROR] The code failed to start. Error:
  SyntaxError: invalid syntax (main.py, line 23)
  Please fix the code so that the server can start successfully.
  ```

**Runnability Pre-Check 후에도 Evaluator 루프에서 runtime error가 다시 발생**하는 경우:
- 드물지만 가능 (예: 특정 endpoint 호출 시점에 lazy import 실패)
- 기존 정책 유지: Evaluator 루프 안에서 runtime category로 기록
- 이 경우는 "Pre-check에서 startup은 됐지만 실제 요청 처리 중 터짐"
- Metric에 `runtime_failure_in_evaluator_loop` 태그 추가하여 구분

**Metric 영향**:
- 새 metric: `runnability_attempts` (0-3), `runnability_failed` (bool)
- 이 두 metric은 분석 시 "system health" 보조 지표로 사용
- 예: "Tier 3의 task_l에서 Runnability 실패율이 높다 → Executor가 복잡한 구조를 first try에 만드는 것이 어려움" 같은 finding 가능

**왜 Max 3 attempts인가**:
- 대부분의 runtime error는 1-2번의 수정으로 해결됨 (경험적)
- 3번 이상 같은 에러가 반복되면 구조적 문제일 가능성이 높음 → 포기하고 분석 데이터로 남기는 게 정보량 있음
- Pilot에서 "대부분 1-2회에 해결" 또는 "3회로 부족" 패턴이 보이면 조정 가능

### 6.6 State Persistence

- **Fresh server instance per iteration**
- 매 Evaluator iteration 시작 시 새 서버 startup, 종료 시 shutdown
- 이전 iteration의 in-memory state는 discard
- Pytest fixture로 관리 (session/function scope 구현은 TBD)
- 이유:
  - 재현성: 같은 코드가 같은 결과
  - Test 간 오염 방지
  - 실제 개발 워크플로우 반영

### 6.7 (폐기됨, v0.8) — B2 non-blind run 차이점

v0.7까지는 B2 sanity check 용 non-blind 분기를 정의했으나, v0.8에서 B2 매트릭스를 폐기 (§5, §1.3 참고). 모든 run은 blind로 진행.

후속 연구에서 non-blind 비교가 필요해지면 `config.blind: bool` 플래그로 분기 가능 (Orchestrator 코드 베이스는 그 분기를 옵션으로 보존).

---

## 7. Analysis Plan

### 7.1 Track 1 분석 (Task-M, n=15)

1. **Level별 H-PR 곡선**: L1→L2→L3 에 따른 H-PR 변화 (n=5 per level, total 15)
2. **Level별 Overfit Gap 곡선**: 같은 축에서 overfit gap 변화
3. **두 곡선의 shape 비교**: "비대칭" 의 경험적 증거 — 같은 입력 변화에 두 종속변수가 다르게 반응하는가 (Claim 층 c)
4. **Tier-dependence는 본 실험에서 검증 불가**: Task 1개라 tier 간 비교 자체가 없음. Limitations에 명시.

### 7.2 Secondary 분석 (Claim B 분해)

- Task-M의 hidden test를 failure category 별로 분해 (spec_violation / edge_case / security / runtime)
- Cell을 `level × category` 로 쪼개서 어느 category가 level에 민감한지 관찰
- 어느 category에서 비대칭이 두드러지는가

### 7.3 Track 2 분석 (Task-L, n=1)

통계 분석 아닌 **정성 case description**:

- **시스템 동작 여부**: 끝까지 도는가, sprint loop 어디서 멈췄는가, 어느 단계에서 시간/비용을 가장 많이 썼는가
- **산출물 품질**: 최종 코드 LOC, 모듈 구조, FE/BE/DB 각 층의 완성도
- **Hidden test 분포**: passed/failed 분류, failure가 어느 모듈에 집중되는가
- **Failure mode 분류**: 어떤 종류의 실패가 큰 규모에서 두드러졌는가
- **비교 reference**: Track 1의 Task-M × L2 평균 H-PR과 Task-L의 H-PR 비교 (단순 reference, statistical claim 아님)

### 7.4 통계 보고 방식

- Track 1: Bootstrap 95% CI (정규성 가정 없음), n=5 per cell
- Effect size (Cohen's d 또는 paired mean difference)
- n=5의 통계적 한계 정직 보고 — primary claim은 통계 유의성보다 **shape의 질적 서술** 에 무게
- 각 cell의 평균/표준편차/모든 raw 값 reporting (transparent)
- Track 2는 정성 description, 통계 X

### 7.5 Expected Outcome Scenarios (사전 commit, v0.8)

**목적**: 실험 실행 전에 "이런 결과가 나오면 이렇게 해석한다" 를 박아두어 사후 cherry-picking 방지. 팀 alignment 확보. Discussion 작성 시 참조점.

**Dual-track 구조라 Track 1 결과 (M1-M5) × Track 2 결과 (D1-D4) 조합으로 시나리오 정의.**

#### Track 1 (Task-M 측정) Outcome Codes

| 코드 | 관찰 | 해석 | Paper framing |
|---|---|---|---|
| **M1** 완전 비대칭 | H-PR L1<L2<L3, Gap L1→L2 완만 + L2→L3 급증 | 정보량 늘수록 정확성↑, 일정 지점 이후 overfit 가속. L2가 sweet spot | "Asymmetric tradeoff in middle-tier task" |
| **M2** Plateau + overfit | H-PR L1<L2≈L3, Gap 단조 증가 | L2가 정확성 sweet spot, L3 추가 정보는 overfit만 증가 | "Saturation boundary at L2" |
| **M3** 단조 증가 | H-PR 단조 증가, Gap flat | 정보 많이 주는 것이 단조롭게 좋음. overfit 미관찰 | "within-blind feedback density study" |
| **M4** U-curve | H-PR L2 최고, Gap L3 최대 | 사후 관찰로 서술 (사전 commit 아님), descriptive only | "Data shows U-shape" |
| **M5** Null | H-PR flat, Gap flat | level 효과 미관찰. n=5의 power 한계 인정 | "No detectable level effect at n=5" |
| **M6** Floor/Ceiling | H-PR 모두 80%+ 또는 모두 30%- | Task-M scope이 sweet spot이 아니었음 | "Task selection limitation" |

#### Track 2 (Task-L 데모) Outcome Codes

| 코드 | 관찰 | 해석 |
|---|---|---|
| **D1** 강한 데모 | 시스템 끝까지 정상, 최종 산출물 코드 완성, H-PR 60%+ | "큰 규모 풀스택 가능 + 측정 가능 품질" 시연 |
| **D2** 부분 데모 | 시스템 끝까지 정상, H-PR 30-60% | 큰 규모 가능 + failure mode 분석 가치 |
| **D3** 약한 데모 | 시스템 정상, H-PR 0-30% | "scaling failure" case study |
| **D4** 시스템 정지 | Sprint loop 중간 정지, Runnability 반복 실패, 또는 budget cap 도달 | 1회 디버깅 후 재시도, 그래도 실패 시 "current limits of blind multi-agent codegen at scale" 정직 보고 |

#### 조합 시나리오 (대표적인 6가지)

##### Scenario A: M1/M2 + D1 — **이상적 결과**
측정에서 깨끗한 비대칭 + 큰 규모 시연 강함.
- **Paper framing**: "We measure the asymmetric overfit-correctness tradeoff in middle-tier blind multi-agent codegen, and demonstrate the system scales to a full-stack production-shaped task."
- Claim 층 (a)(b)(c)(d)(e) 모두 ✓
- 가장 strong한 결과

##### Scenario B: M1/M2 + D2/D3 — **측정 강함, 데모 정직**
측정은 비대칭 보임, 데모는 한계 시연.
- **Paper framing**: "We characterize the asymmetric tradeoff in middle-tier and observe failure modes when scaling to full-stack."
- Track 1 finding이 main claim, Track 2는 limitations 보강

##### Scenario C: M3/M4 + D1/D2 — **데모 강함, 측정 약함**
큰 규모 가능 + 비대칭 미관찰.
- **Paper framing**: "Building a blind multi-agent system that scales to full-stack: design and observations." within-blind framing.
- Track 2가 main contribution, Track 1은 supporting

##### Scenario D: M5 + D2/D3 — **양쪽 약함, 정직 보고**
측정 null + 데모 부분 성공.
- **Paper framing**: "Code2E system construction: capabilities and observed limitations." 시스템 페이퍼.
- Limitations에 sample size + scale challenges 명시

##### Scenario E: M6 + 어느 D나 — **Task 선정 실수**
Task-M이 sweet spot이 아님.
- **대응**: P1 단계에서 감지되어야 함 (§5.5 decision gate). Week 9 단계에서 감지되면 본 실험 후 Task scope 보강 또는 추가 task 도입 고려 (예산 상황 따라).

##### Scenario F: 어느 M + D4 — **데모 시스템 정지**
- **대응**: 1회 디버깅 후 재실행. 그래도 실패면 D4를 정식 finding으로 보고 ("scaling limit observed at sprint X").
- Track 1 결과는 영향 없음. Paper에는 "Track 1 + Track 2 limit" 으로 보고.

#### Claim 층별 생존 매트릭스

| Scenario | (a) level→pass | (b) level→gap | (c) 비대칭 | (d) 큰 규모 동작 | (e) 측정 가능 품질 | 종합 |
|---|:---:|:---:|:---:|:---:|:---:|---|
| A (M1/M2 + D1) | ✓ | ✓ | ✓ | ✓ | ✓ | 🟢 Ideal |
| B (M1/M2 + D2/D3) | ✓ | ✓ | ✓ | ✓ | △ | 🟢 Strong |
| C (M3/M4 + D1/D2) | ✓ | △ | ✗ | ✓ | ✓/△ | 🟡 Demo-led |
| D (M5 + D2/D3) | ✗ | ✗ | ✗ | ✓ | △ | 🟠 System paper |
| E (M6) | N/A | N/A | N/A | depends | depends | 🟠 Task issue |
| F (* + D4) | depends | depends | depends | ✗ | ✗ | 🟠 Scaling limit |

**핵심**: 모든 시나리오가 publishable한 스토리를 포함. Track 1과 Track 2의 독립성이 robustness의 원천.

#### 추정 확률 (주관적, 사전 기록)

| Scenario | 추정 확률 |
|---|---|
| A (이상적) | ~25% |
| B (측정 강함, 데모 약함) | ~30% |
| C (데모 강함, 측정 약함) | ~25% |
| D (양쪽 약함) | ~10% |
| E (Task 선정 실수) | ~5% (P1으로 감지) |
| F (데모 정지) | ~5% |

**이 확률은 사후 분석에 사용**: 실제 결과가 어느 scenario였는지 대조해서 "사전 예상이 맞았는가" 를 discussion에 기록. 연구 과정의 정직성을 드러내는 장치.

---

## 8. Timeline & Decision Gate

**Current position**: Week 7 마지막 (2026-04-18)
**Total duration**: 12주 단축 학기제
**Remaining**: Week 8 ~ Week 12 (5 weeks)
**Final submission**: Week 12 (5/18-5/24)

### 8.1 Revised Timeline (v0.8: dual-track, 16 runs)

```
Week 7 (4/13-4/19, 현재):
  - 실험 설계 v0.8 확정 (이 문서)
  - Agent 인터페이스 정의 (docs/week07/agent-interface.md)
  - Sprint 기반 아키텍처 설계
  - Orchestrator state machine, Runner/Config 뼈대 구현 (이주영)
  - Executor, Planner stub 구현 (정혁준)
  - Evaluator, Advisor, Feedback formatter stub 구현 (고기호)
  - Task-S prompt + hidden_tests 작성 (고기호) — smoke test 용도
  - Task-M prompt + hidden_tests 작성 (정혁준) — 측정 본체

Week 8 (4/20-4/26):
  - System 통합 완성 (full 4 agents + subprocess + telemetry + budget cap)
  - Sprint 기반 Orchestrator 구현 마무리
  - Task-S로 smoke test (시스템 파이프라인 동작 + 비용 측정)
  - Task-S/M 교차 검증 완료 (cyclic pair, §4.7)
  - Week 8 말: P1 (Task-M × L1 + L3 × 1 = 2 runs) 실행 → 본 실험 진행 결정 게이트

Week 9 (4/27-5/3):
  - ★ P1 결과 분석 + 본 실험 의사결정 ★ (§5.5 표 적용)
  - 결정에 따른 분기:
    ├─ 정상 진행 → Track 1 본 실험 (Task-M × L1/L2/L3 × 5 = 15 runs) 시작
    └─ 비용 초과 / 시스템 문제 → scope 축소 또는 디버깅
  - 중간 분석으로 metric pipeline 검증

Week 10 (5/4-5/10):
  - Track 1 실험 완료 (15 runs)
  - Track 1 분석 + 시각화 (Level 곡선, overfit gap, failure category 분해)
  - Track 2 (Task-L) 도메인 + prompt 확정 (이주영)
  - Task-L hidden test 작성 + canonical 구현

Week 11 (5/11-5/17):
  - ★ Track 2 데모 실행 (Task-L × L2 × 1 run) ★
  - Track 2 정성 분석 (산출물 품질, failure mode, 비교)
  - 두 트랙 종합 + 논문 구조 outline
  - Discussion 초안

Week 12 (5/18-5/24):
  - 논문 작성 + figures 확정
  - 최종 검토 + proofreading
  - 최종 발표 자료 제작
  - 최종 제출 (Week 12 말)
```

### 8.2 비상 체크포인트 (Week 9 초)

P1 직후 다음 4가지를 점검:

- ☐ Smoke test 성공적으로 작동했는가?
- ☐ P1 2 runs 완료 + 비용 + L1/L3 차이 측정되었는가?
- ☐ 시스템이 sprint loop을 끝까지 완주하는가?
- ☐ 비용이 hard cap (per-run $15) 안에 들어오는가?

**기준**:
- 4개 모두 ✓ → Track 1 본 실험 진행
- 1-2개 ✗ → Week 9 초에 집중 처리 후 진행
- **3개 이상 ✗** → **Track 1 scope 축소 또는 보류**:
  - 옵션 a: Repeat 5→3 축소 (Track 1: 9 runs)
  - 옵션 b: Task-M scope 보강 (조건 추가, sweet spot 찾기) 후 P1 재실행
  - 옵션 c: Track 1 폐기 → Track 2 데모만으로 시스템 페이퍼 (최후)

### 8.3 Decision Gate (Week 9, P1 결과 해석)

**사전 commit 규칙** (P1 실행 전에 이 규칙을 박아두어 bias 회피, §5.5 참고):

| P1 관찰 | 해석 | 조치 |
|---|---|---|
| 1 run < $7, L1↔L3 H-PR 차이 10%p+ | sweet spot 적중, 비용 안전 | Track 1 그대로 진행 |
| 1 run $7-15, 차이 10%p+ | 진행 가능, 비용 모니터링 강화 | Track 1 진행, telemetry 적극 모니터 |
| 1 run > $15 | 비용 초과 | repeat 5→3 축소 또는 prompt 최적화 후 재시도 |
| L1↔L3 차이 < 5%p | ceiling/floor 의심 | Task-M scope 보강 또는 Task 재선정 |
| 시스템 미완주 | 시스템 버그 | 디버깅 우선, Track 1 보류 |

**재포지셔닝 시 변경 사항** (Track 1 결과 해석 단계, §7.5 참고):
- Title 조정 (시나리오 A/B/C에 따라)
- Intro motivation 조정
- **데이터, 차트, 분석은 그대로 사용**

### 8.4 Critical Path와 병렬화

**Critical path** (직렬 의존):
Agent 인터페이스 → System 구현 → Task-S/M 작성 → Smoke test → P1 → Decision gate → Track 1 본 실험 → 분석 → Track 2 → 논문

**병렬 가능 작업** (Week 7-8 동시):
- Task 제작 (팀원 2명) ∥ System 구현 (팀원 3명 협력)
- Feedback formatter 구현 ∥ Orchestrator 구현
- Task 교차 검증 ∥ Agent prompt 설계

**역할 분담** (Week 7 확정):
- **이주영**: Orchestrator, Runner, Metric, **비용 telemetry/cap** 구현 + Task-L 제작 (Week 10에)
- **정혁준**: Executor, Planner 구현 + Task-M 제작
- **고기호**: Evaluator, Advisor, Feedback formatter 구현 + Task-S 제작

**교차 검증 페어** (독립 작성 후 비교, Section 4.7):
- Task-S: 고기호 작성 → 정혁준 검토
- Task-M: 정혁준 작성 → 이주영 검토
- Task-L: 이주영 작성 → 고기호 검토 (Week 10)

---

## 9. Open Items (TBD)

v0.8 기준 남은 결정. 본 초안의 blocker는 아니지만 명시된 deadline 전 확정 필요.

| 항목 | 긴급도 | 결정 시점 |
|---|---|---|
| Task-S, Task-M prompt + hidden test 구체 내용 | 🔴 높음 | Week 7 말 |
| Sprint 기반 Orchestrator 구현 세부 (sprint loop + Advisor sub-loop) | 🔴 높음 | Week 7-8 |
| 비용 telemetry / hard cap 구현 (per-run + total) | 🔴 높음 | Week 7-8 |
| Executor prompt 템플릿 (scaffold / revise_for_advisor / fix_runtime_error / revise_for_evaluator) | 🟡 중간 | Week 7-8 구현 중 |
| Planner / Advisor / Evaluator 시스템 프롬프트 | 🟡 중간 | Week 7-8 구현 중 |
| Planner의 sprint 분해 프롬프팅 패턴 (task별 적정 sprint 수 유도) | 🟡 중간 | Week 7-8 |
| `parse_build_sequence` 헬퍼 (Planner 출력에서 sprint list 추출) | 🟡 중간 | Orchestrator 구현 시 |
| AI Slop 운영 정의 (Advisor의 ai_slop category 구체 기준) | 🟢 낮음 | Week 7-8 구현 중 |
| Task-L 구체 도메인 + 스코프 (LOC 목표, sprint 수, 조건 수) | 🟡 중간 | Week 10 (Track 1 분석 후) |
| Playwright sub-schema | 🟢 낮음 | Week 10-11 (Task-L 직전) |
| 최종 figure/table layout | 🟢 낮음 | Week 11 분석 시 |

**v0.7 → v0.8에서 해결된 항목들**:
- 매트릭스 scope: 50 runs → 16 runs (15 측정 + 1 데모)
- B2 sanity check: 폐기, "within-blind" framing 사전 commit
- Sprint 기반 아키텍처: §6.1 신설
- 비용 cap: 통제 변수에 추가 (§3.2.1)
- Task 역할 분리: smoke / 측정 / 데모 (§4)
- Outcome scenario: dual-track 조합으로 재정의 (§7.5)
- Timeline: P1 게이트 도입, 12주 기준 재작성 (§8)

---

## 10. Critical Files (예상 산출물)

이 실험 설계가 실제 실행될 때 생성되어야 하는 파일 구조:

```
code2e-agent/
├── docs/
│   ├── experimental_design.md      # 이 문서 (v0.1 → v1.0)
│   └── week*/                      # 주간 plan + 설계 문서
│
├── tasks/
│   ├── task_s/                     # Smoke test 용
│   │   ├── prompt.txt
│   │   ├── hidden_tests.py
│   │   ├── canonical.py
│   │   └── task_metadata.json
│   ├── task_m/                     # Track 1 측정 본체
│   │   ├── prompt.txt
│   │   ├── hidden_tests.py
│   │   ├── canonical.py
│   │   └── task_metadata.json
│   └── task_l/                     # Track 2 데모 (Week 10에 작성)
│       ├── prompt.txt
│       ├── hidden_tests.py         # pytest + requests + DB + Playwright
│       ├── canonical/              # FE 포함이라 디렉토리
│       │   ├── app.py
│       │   ├── templates/
│       │   └── static/
│       └── task_metadata.json
│
├── src/
│   ├── orchestrator/               # Sprint 기반 state machine + telemetry + budget cap
│   ├── agents/
│   │   ├── planner/
│   │   ├── executor/
│   │   ├── advisor/
│   │   └── evaluator/
│   ├── feedback/
│   │   └── level_formatters.py     # L1, L2, L3 포맷 변환
│   ├── runner/
│   │   ├── run_experiment.py
│   │   └── config.py               # task, level, repeat, budget cap 등
│   └── metrics/
│       ├── hidden_pass_rate.py
│       ├── overfit_gap.py
│       ├── failure_category.py
│       └── cost_telemetry.py       # 비용 추적 + cap 체크 (v0.8 신설)
│
└── results/
    ├── smoke/                      # Task-S × L2 × 1 (시스템 검증)
    │   └── task_s__L2__rep_0/
    ├── pilot/                      # P1: Task-M × L1 + L3 × 1 = 2 runs
    │   ├── task_m__L1__rep_0/
    │   └── task_m__L3__rep_0/
    ├── track1/                     # 15 runs: Task-M × L1/L2/L3 × 5 repeats
    │   └── task_m__level_X__rep_Y/
    └── track2/                     # 1 run: Task-L × L2 × 1 (데모)
        └── task_l__L2__rep_0/
```

각 run 디렉토리 내부 (Orchestrator 작성):
```
results/.../task_X__level_Y__rep_Z/
├── code/                          # v1...vN (각 단계의 코드 스냅샷)
├── agent_calls/*.json              # 모든 agent 호출의 input/output (재현용)
├── metrics.json                    # H-PR, overfit gap, iterations, regression, tokens, cost
├── evaluator_tests.json            # 해당 run의 evaluator-generated test set
└── budget.json                     # 누적 비용, kill 여부
```

---

## 11. Verification

이 실험 설계의 end-to-end 검증 단계:

1. **Task prototype 검증** (Week 7 말)
   - Task-S, Task-M 각각의 canonical 코드와 hidden_tests.py 로 채점
   - 사람이 이상적으로 작성한 구현이 모든 hidden test를 통과해야 함
   - Failure: hidden test가 기계적 번역을 넘어 주관적 해석을 포함하고 있음 → 재작성

2. **Feedback level 포맷터 단위 테스트** (Week 7 말 ~ Week 8)
   - 동일한 test failure에 대해 L1/L2/L3 포맷터가 각각 다른 양의 정보를 출력하는지 확인
   - Executor 프롬프트에 정확히 해당 level의 정보만 들어가는지 확인
   - Failure: level이 의도대로 차별화되지 않음 → 포맷터 수정

3. **Sprint 기반 Orchestrator 단위 테스트** (Week 7-8)
   - Mock Planner가 sprint 3개 출력 → Orchestrator가 sprint마다 scaffold + Advisor sub-loop을 정확히 호출하는지
   - Mock Advisor가 NEEDS_REVISION → revise → PASSED 시퀀스를 정확히 처리하는지
   - 마지막 sprint의 Advisor 마지막 review에서 guard가 동작하는지
   - Failure: state machine 버그 → 디버깅

4. **비용 telemetry + cap 검증** (Week 7-8)
   - Mock agent 응답에 가짜 usage 포함 → Orchestrator가 누적 추적하는지
   - Per-run cap ($15) 도달 시 Orchestrator가 abort하는지
   - Total cap ($350) 도달 시 Runner가 abort하는지
   - Failure: 비용 폭주 위험 → 즉시 수정

5. **Smoke test** (Week 8)
   - Task-S × L2로 시스템 한 번 끝까지 실행
   - 모든 metric 수집 확인 (H-PR, overfit gap, iterations, regression, cost, runnability_attempts, sprint metrics)
   - overfit gap 계산이 합리적 숫자인지 (음수 아님, 과도하지 않음)
   - 1 run 비용이 추정 범위 안인지 ($1-3 예상)
   - Failure: pipeline 어딘가가 끊김 → 디버깅

6. **P1 (Week 8 말)**
   - Task-M × L1 + L3 × 1 = 2 runs 실행
   - 비용 + L1↔L3 H-PR 차이 측정
   - Decision gate 표 적용하여 Track 1 진행 결정 (§5.5, §8.3)
   - Failure: 의사결정 표대로 분기 처리

7. **Track 1 (Week 9-10) 실험 후 cross-validation**
   - 15 runs (Task-M × L1/L2/L3 × 5)의 cell별 평균과 bootstrap CI 산출
   - CI가 너무 넓으면 (예: ±20%p) 패턴 해석 신중
   - Failure: variance가 너무 크면 추가 분석 (within-cell variance 분해)

8. **Track 2 (Week 11) 데모 검증**
   - Task-L × L2 × 1 run 실행
   - 시스템이 끝까지 도는지 (sprint loop 완주, Runnability/Evaluator 정상)
   - Hidden test로 채점되어 H-PR 측정 가능한지
   - Failure: D4 시나리오 발동 (디버깅 + 1회 재시도, 그래도 실패면 정직 보고)

---

## 12. 알려진 한계

이 연구 설계가 아직 답하지 못하는 것:

- **Tier-dependence 검증 불가**: Track 1 측정이 Task-M 단일 task로 제한되어, 기존 Claim C v0.2의 (d) "비대칭이 tier에 의존" 층은 본 실험에서 검증 불가. 후속 연구로 분리.
- **통계적 power 약함**: n=5 per cell의 Track 1은 effect size가 큰 경우만 검출 가능. Cohen's d ~0.8 미만의 약한 효과는 noise에 묻힐 수 있음. 그러나 이는 case study 방법론의 본질적 한계와 정합.
- **Track 2의 N=1**: 데모 1회로는 "이 정도까지 가능" 의 존재 증명만 가능. 일반화 불가. 큰 task에 대한 평균 성능 주장 못 함.
- **블라인드 효과 미검증**: B2 sanity check 폐기로 "non-blind 대비 블라인드의 우위" 자체는 본 실험에서 검증 안 함. "within-blind" framing 사전 commit (§1.3).
- **외부 타당성**: 측정 1 도메인 + 데모 1 도메인에서 관찰된 패턴이 다른 도메인에 일반화되는지는 case study 방법론의 본질적 한계.
- **모델 일반화**: Sonnet 4.6 한 가지에서 본 결과가 다른 모델에 통하는지는 본 실험 scope 외.
- **장기 실행 (long-running) 측면**: Anthropic 글들이 강조한 multi-session/progress-file 측면은 본 실험 scope 외. 후속 연구로 분리.
- **Baseline 다양성**: Claude Code, Cursor 등 외부 비교는 fair comparison의 어려움 때문에 제외.
- **Track 2 (Task-L)의 스택 confound**: BE + DB + FE의 복합 시스템에서 한 부분 실패가 어느 layer 때문인지 분리 어려움. failure mode 분석으로 정성 보고만 가능.

이 한계들은 논문의 Limitations 섹션에 명시적으로 기록.
