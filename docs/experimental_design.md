# Code2E 실험 설계 v0.7 (초안)

> **v0.7 변경**: Scaffolding loop 도입.
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

1-4주차 동안 시스템 아키텍처는 `Master/Code/Test/Final` 4-agent 구조 → `Planner/Executor/Advisor/Evaluator` 오케스트레이션 구조로 한 차례 피벗했습니다. 6주차 말 현 시점에서 시스템 구현을 시작하기 전에 **실험 설계를 확정**해야 하며, 그래야 시스템이 "측정 가능한 형태로" 만들어질 수 있습니다.

이 문서는 그 실험 설계의 현행 초안입니다 (v0.1부터 iterative 수정 진행 중). Claim, 방법론, 변수, 태스크, run matrix, 분석 계획, decision gate를 통합 정리합니다. 향후 세부 결정(태스크 prompt 구체화, 시스템 프롬프트, orchestrator 구현 세부 등)은 모두 이 문서를 기준점으로 진행됩니다.

**핵심 통찰** — Code2E의 claim은 "블라인드가 더 낫다" 같은 평균 성능 비교가 아니라, "피드백 정보 밀도가 어떻게 정확성과 overfit에 작용하는가"라는 mechanism characterization입니다. 따라서 방법론은 traditional benchmark가 아닌 **case study** (Anthropic 두 글과 동일 전통)를 채택합니다.

---

## 1. Research Claim

### 1.1 Primary (Claim C v0.2)

> 블라인드 멀티 에이전트 시스템에서 Executor에게 전달되는 피드백의 정보 밀도는 코드의 실질적 정확성(hidden test pass rate)과 평가자 적합도(Evaluator overfit gap)에 **비대칭적으로** 작용하며, 이 비대칭의 양상은 과제 복잡도(tier)에 따라 **구조적으로 달라진다**.

주장의 누적 구조:
- (a) 피드백 밀도가 pass rate에 영향을 준다
- (b) 피드백 밀도가 overfit gap에 영향을 준다
- (c) 두 지표에 대한 영향이 비대칭적이다 (← 프로젝트의 핵심 bet)
- (d) 비대칭의 양상이 tier에 의존한다 (← bonus)

각 층이 무너져도 바로 아래 층이 정당한 finding으로 남는 robust한 구조.

### 1.2 Secondary (Claim B 분해 분석)

Hidden test를 failure category(spec_violation / runtime / edge_case / security / perf)별로 분해하여, 위 비대칭이 어느 카테고리에서 두드러지는지 관찰. 같은 데이터로 추가 분석 가능하므로 비용 부담 없음.

### 1.3 Fallback

B2 premise validation에서 블라인드 효과가 확인되지 않으면 "within-blind feedback density characterization" 으로 framing 조정. 데이터·차트·통계 분석 그대로 활용. 주요 변경은 title/intro의 수사뿐이며 핵심 finding은 유지.

### 1.4 두 Anthropic 글에 대한 위치

- **글 1 ("단일 vs 멀티 에이전트")**: 멀티 내부에서 "피드백이 어떻게 흐르는가" 가 숨은 축임을 보임
- **글 2 ("QA tuning이 어렵다")**: 그 어려움의 구조를 정량 곡선으로 특성화

---

## 2. Methodology

**Case study framework** — Anthropic harness 논문과 동일한 방법론적 전통

- 3개의 대표 태스크를 tier별로 1개씩 선정
- 각 태스크를 독립 변수(feedback level)를 체계적으로 조작하며 깊이 실행
- Run-level 분석이 가능한 규모(각 cell당 10 runs)
- 통계는 보조 도구, 메인은 mechanism의 질적 서술

**Benchmark가 아닌 이유**: Code2E의 claim은 평균 성능 비교가 아니라 mechanism characterization. Case study가 방법론적으로 정합. Anthropic 두 글이 모두 단일 또는 소수의 야심찬 태스크로 연구를 수행한 precedent가 있음.

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
- 규칙:
  | 조건 | Category |
  |---|---|
  | 기대 HTTP status와 다른 status 반환 | spec_violation |
  | HTTP 5xx 반환 | runtime |
  | 경계값/빈 입력에서 서버 잘못 반응 | edge_case |
  | 미인증/권한 없는 접근이 성공 | security |
  | Timeout / 비정상 지연 | performance |

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
| Max scaffold steps per task | 5 (Planner가 task 복잡도에 맞춰 결정, 상한) |
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

**Build Sequence 작성 가이드라인**:
- Step 수는 task 복잡도에 비례 (권장: Task-S 1 step, Task-M 1-2 steps, Task-L 3-4 steps)
- 상한 5 steps (통제 변수, §3.2.1)
- 각 step은 자연어 한 줄로 무엇을 만들지 명시 (예: "1. SQLite 스키마 + 데이터 모델", "2. 인증 엔드포인트", "3. 이체 트랜잭션 로직", "4. 프론트엔드 (계좌 목록, 이체 폼)")
- Step 순서 = 의존성 순 (DB → API → FE). 후속 step은 선행 step의 산출물에 의존 가능
- Executor의 `scaffold` loop이 이 sequence를 순회하며 step별 1회씩 호출 (§6.1)

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

## 4. Tasks (3 tier-stratified case studies)

각 태스크는 자연어 프로즈 + 명시적 번호 조건의 형태. Hidden test는 조건의 기계적 번역.

**Tier 설계 원칙**: 스택 복잡도로 tier를 정의. 비즈니스 로직 복잡도만이 아니라 Executor가 만들어야 하는 시스템의 아키텍처 층이 tier마다 증가한다.

| Tier | 스택 | 평가 방식 |
|---|---|---|
| Task-S | Backend (in-memory) | requests (HTTP) |
| Task-M | Backend + SQLite | requests (HTTP) + DB 상태 검증 |
| Task-L | Backend + SQLite + Frontend | requests + DB + Playwright (브라우저) |

### 4.1 Task-S (Tier 1, Backend Only) — **단축 URL 서비스**

- **스택**: Python REST API, in-memory 저장
- 단일 리소스 CRUD 수준 + 중복/충돌 처리
- 자연어 프롬프트 + **목표 5개 명시 조건** (±1 융통성)
- 핵심 메커니즘: 같은 long URL은 같은 short code, 코드 충돌 처리, redirect 의미
- 예상 hidden test 수: 10-15개
- 주요 failure categories: spec_violation, edge_case

### 4.2 Task-M (Tier 2, Backend + DB) — **로그인 할일 관리**

- **스택**: Python REST API + SQLite
- 인증 + user isolation + 다중 엔드포인트 + 상태 전이 + 영속 저장
- 자연어 프롬프트 + **목표 7개 명시 조건** (±1 융통성)
- 핵심 메커니즘: 사용자 격리, 토큰 검증, 권한 경계, 완료 상태 변경, DB 스키마 설계
- 예상 hidden test 수: 15-20개
- 주요 failure categories: spec_violation, edge_case, security, runtime

### 4.3 Task-L (Tier 3, Full-Stack) — **잔고 이체 서비스**

- **스택**: Python REST API + SQLite + vanilla HTML/CSS/JS Frontend
- 트랜잭션 + atomicity + rollback + 동시성 + 웹 UI
- 자연어 프롬프트 + **목표 12개 명시 조건** (±1 융통성)
  - Backend 조건 ~9개 (API + DB + 트랜잭션)
  - Frontend 조건 ~3개 (계좌 목록, 이체 폼, 결과 표시)
- 핵심 메커니즘: 부분 실패 시 전체 롤백, 음수 잔고 방지, 동시 이체 처리, 화면에서의 조작 및 결과 확인
- 예상 hidden test 수: 25-30개 (Backend 20-25 + Frontend 5)
- 주요 failure categories: spec_violation, edge_case, security, runtime, performance (concurrency)
- **Frontend hidden test**: Playwright 기반 브라우저 테스트
- **Fallback**: Week 8 smoke test에서 Evaluator의 Playwright test 생성이 불안정하면 FE 조건 제거 후 Backend + DB만으로 진행

**도메인 선택 근거**: 세 도메인이 서로 다른 핵심 어려움을 대표 (리소스 관리 → 사용자 경계 → 트랜잭션). 스택 복잡도가 tier와 함께 증가하여 (in-memory → DB → DB+FE) 실제 서비스 개발의 복잡도 사다리를 반영한다.

**Tier간 평가 메커니즘 차이에 대한 주의**: Task-L의 결과가 Task-S/M과 다를 때, 비즈니스 로직·DB·FE 중 어느 요인 때문인지 분리할 수 없다. 이는 tier를 스택 복잡도로 정의한 데 따르는 confound이며, 논문의 Limitations에 명시한다.

### 4.4 산출물 형식

```
tasks/task_s/
├── prompt.txt          # 자연어 입력 (시스템 공개)
├── hidden_tests.py     # pytest + requests 기반 canonical test (시스템 차단)
├── canonical.py        # 사람이 작성한 이상적 구현 (sanity check용)
└── task_metadata.json  # tier, 조건 수, failure category 분포

tasks/task_m/
├── prompt.txt
├── hidden_tests.py     # pytest + requests + DB 상태 검증
├── canonical.py
└── task_metadata.json

tasks/task_l/
├── prompt.txt
├── hidden_tests.py     # pytest + requests + DB + Playwright
├── canonical/           # FE 포함이므로 디렉토리 (canonical.py 대신)
│   ├── app.py
│   ├── templates/
│   └── static/
└── task_metadata.json
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

**v0.2 scope 조정**: 파란학기제 12주 단축 일정을 반영해 repeat 수를 축소하고 B2를 Task-S에만 국한. 검정력은 d ~0.5 에서 d ~0.6 으로 완화되지만 버퍼 확보 우선.

### 5.1 Primary Experiment (B3 = Code2E blind)

| 축 | 값 | 개수 |
|---|---|---|
| Task | Task-S, Task-M, Task-L | 3 |
| Feedback level | L1, L2, L3 | 3 |
| Repeat | 독립 run | **5** (v0.1 10 → v0.2 5) |

**Primary runs: 3 × 3 × 5 = 45 runs**

### 5.2 B2 Premise Validation (축소)

| 축 | 값 | 개수 |
|---|---|---|
| Task | **Task-S only** (v0.1 3 → v0.2 1) | 1 |
| Condition | non-blind only | 1 |
| Feedback level | L2 only | 1 |
| Repeat | **5** | 5 |

**Additional B2 runs: 1 × 5 = 5 runs**

**B2 축소 근거**: Task-S에서라도 블라인드 효과가 확인되면 premise는 서있다고 볼 수 있음. 3 tasks로 확장하는 것은 후속 작업으로 둠. B2 무결과 시에도 Option 4 fallback으로 "within-blind study" 재포지셔닝 가능.

### 5.3 합계

| 항목 | 수치 |
|---|---|
| 총 runs | **50** (v0.1 120 → v0.2 50) |
| 추정 토큰 비용 (Sonnet) | $25-50 |
| Wall clock (3 parallel) | ~5시간 |

**절감 효과**: 병렬 wall clock 절반 이하, 비용 1/3 이하. 디버깅/재실행/분석 시간 확보.

---

## 6. Single Run Procedure

### 6.1 전체 흐름 pseudocode

```python
# === Run Start ===

# 1. Planner 단계
plan = Planner.structure(prompt_txt)

# 2. Executor 초기 생성 (scaffolding loop, build_sequence 길이만큼 반복)
#    각 step은 이전 step의 누적 결과 위에 추가 작성 (이전 파일 보존)
code = {}
for i, step in enumerate(plan.build_sequence):
    code = Executor.scaffold(plan, code, step, i, len(plan.build_sequence))
# 모든 step 완료 후 code == v1
# scaffold sub-step은 코드 버전 카운트(v1~v9)에 포함 안 됨 — v1 내부 구조

# 3. Advisor 루프 (strict sequential, max 3 reviews, static only)
MAX_ADVISOR_REVIEWS = 3
for i in range(MAX_ADVISOR_REVIEWS):
    review = Advisor.review(code)  # whitebox static review
    if review.verdict == "PASSED":
        break
    if i == MAX_ADVISOR_REVIEWS - 1:
        break  # guard: 마지막 review에서는 revise 하지 않음
    code = Executor.revise_for_advisor(code, review.feedback)
    # i=0 → v2, i=1 → v3
# 최종 review에서도 NEEDS_REVISION이면 그 verdict만 기록하고 다음 단계로

# 4. Runnability Pre-Check (v0.3 신설, max 3 attempts)
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

### 6.2 루프 경계 규칙 (v0.5)

- **세 loop는 strict sequential**: Advisor → Runnability Pre-Check → Evaluator
- 각 loop는 이전 loop의 결과와 무관하게 반드시 실행 (Advisor NEEDS_REVISION, Runnability fail 이어도 다음 loop 진입)
- **세 loop 모두 "마지막 iteration에는 revise 하지 않음" guard 적용**
  - 이유 1: Evaluator loop에서 마지막 revision이 test 없이 만들어지면 overfit gap metric이 오염됨 (마지막 test된 code ≠ 최종 code)
  - 이유 2: 세 loop의 구조 일관성
  - 이유 3: "3회 iteration" = "3회 check, 2회 revise" 로 자연스러운 해석

- **최대 Executor 코드 생성 수 (v0.7)**:
  - v1 (scaffolding loop 누적 결과, `len(build_sequence)` 회 Executor.scaffold 호출)
  - + v2~v3 (Advisor loop: 3 reviews, max **2 revisions**)
  - + v4~v5 (Runnability pre-check: 3 attempts, max **2 revisions**)
  - + v6~v9 (Evaluator loop: 5 tests, max **4 revisions**)
  - = **최대 v9** (scaffold sub-step은 v 카운트에 포함 안 됨; v1을 만드는 내부 구조)

- 실제 대부분의 run은 Advisor에서 바로 PASSED, Runnability 0-1 attempts로 해결되므로 보통 **v5~v7** 범위에서 끝남
- **v9는 극단적 worst case** (Advisor 2회 revise + Runnability 2회 revise + Evaluator 4회 revise 모두 소진)

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

### 6.7 B2 Non-Blind Run 차이점

- 단계 4에서 `feedback = format_feedback_at_level(...)` 호출 시
- **B2 non-blind**: feedback에 Evaluator의 test 코드 자체를 append
- **B3 blind**: 위 append 생략 (feedback format만 전달)
- 코드 베이스는 동일, `config.blind: bool` 플래그로 분기
- 그 외 모든 logic은 동일

---

## 7. Analysis Plan

### 7.1 Primary 분석

1. **Level × Task의 H-PR 곡선**: 각 태스크에서 L1→L2→L3 에 따른 H-PR 변화
2. **Level × Task의 Overfit Gap 곡선**: 같은 축에서 overfit gap 변화
3. **두 곡선의 shape 비교**: "비대칭" 의 경험적 증거 — 같은 입력 변화에 두 종속변수가 다르게 반응하는가
4. **Tier 간 비교**: Tier 1, 2, 3 에서 곡선 shape이 어떻게 달라지는가 → tier-dependence

### 7.2 Secondary 분석 (Claim B)

- Hidden test를 failure category 별로 분해 (spec_violation / runtime / edge_case / security / perf)
- Cell을 `level × tier × category` 로 쪼개서 어느 category가 level에 민감한지 관찰
- 어느 category에서 블라인드가 가장 의미 있는가

### 7.3 B2 Sanity Check 분석

- B3 vs B2 at L2의 overfit gap paired 비교
- 결과 분기:
  - 유의 차이 (B2 > B3) → 블라인드 효과 확인 → Claim C v0.2 확정
  - 무차이 → "within-blind" 재포지셔닝
  - B2 < B3 → 디버깅 (예상 외 결과)

### 7.4 통계 보고 방식

- Bootstrap 95% CI (정규성 가정 없음)
- Effect size (Cohen's d 또는 paired mean difference)
- Primary claim은 통계 유의성보다 **shape의 질적 서술** 에 무게
- 각 cell의 평균/표준편차를 모두 reporting

### 7.5 Expected Outcome Scenarios (사전 commit)

**목적**: 실험 실행 전에 "이런 결과가 나오면 이렇게 해석한다" 를 박아두어 사후 cherry-picking 방지. 팀 alignment 확보. Discussion 작성 시 참조점.

**기본 관찰 차원**:
- H-PR (hidden test pass rate): Level × Task 곡선
- Overfit Gap: Level × Task 곡선
- 두 곡선의 relative shape = "비대칭" 주장의 핵심

#### Scenario A — "완전한 비대칭 확인" (이상적)

**관찰**:
- H-PR: L1 < L2 < L3 단조 증가
- Overfit Gap: L1 → L2 완만 증가, L2 → L3 급격 증가
- Tier가 올라갈수록 L2→L3 구간 gap 증가 폭이 더 큼

**해석**: "피드백 정보량이 늘어날수록 정확성은 꾸준히 오르지만, 일정 지점 이후 overfit이 가속된다. 그 지점은 task 복잡도에 따라 이동한다. L2가 대부분의 상황에서 실용적 sweet spot이다."

**Anthropic 대비 기여**: "QA tuning이 어렵다" 의 어려움이 정확히 이 비대칭 때문임을 경험적으로 보임.

**Paper framing**: "We quantify the asymmetric tradeoff between correctness and evaluator overfit as a function of feedback density, and show the asymmetry strengthens with task complexity."

#### Scenario B — "Plateau + Overfit 증가"

**관찰**:
- H-PR: L1 < L2 ≈ L3 (L2 이후 포화)
- Overfit Gap: L1 < L2 < L3 꾸준히 증가

**해석**: "L2의 정보량이 이미 정확성 향상에 필요한 것을 다 제공한다. L3의 추가 정보는 정확성에는 기여하지 않고 overfit만 가중시킨다. L2가 최적."

**Anthropic 대비 기여**: 자세한 피드백에는 diminishing returns가 있고 그 너머는 overfit 비용만 증가한다는 실용 가이드라인.

**Paper framing**: "Feedback beyond a structured mid-level (L2) adds no accuracy but increases evaluator overfit — a clear saturation boundary for harness design."

#### Scenario C — "단조 증가 (overfit 미발견)"

**관찰**:
- H-PR: L1 < L2 < L3 꾸준히 증가
- Overfit Gap: L1 ≈ L2 ≈ L3 flat

**해석**: "이 setup에서는 정보 많이 주는 것이 단조롭게 좋다. Overfit 현상이 감지되지 않았다. Anthropic의 qualitative 우려는 우리 scale에서는 나타나지 않는다."

**Claim 층 상태**: (a)(b) 유지, (c)(d) 기각

**대응 framing**: "within-blind feedback density study" 로 재포지셔닝. "Overfit은 우리 setup 스케일에서는 observable한 효과가 아니었으며, 더 큰 scale에서 reconsider할 필요가 있다" 를 discussion에 명시.

#### Scenario D — "Tier-dependent flip" (가장 흥미로운 가능성)

**관찰**:
- Task-S: H-PR 단조 증가, overfit 거의 없음
- Task-M: H-PR 증가하다 plateau, overfit 서서히 증가
- Task-L: **H-PR이 L2에서 최고, L3에서 오히려 하락**, overfit이 L3에서 급증

**해석**: "복잡한 task에서는 더 많은 피드백이 코드 품질을 해친다. Executor가 각 실패를 local fix로 대응하다 보면 전체 설계가 엉키고 regression이 누적되기 때문. 피드백 전략은 task 복잡도에 적응해야 한다."

**가장 강력한 이야기**: 단순 "tradeoff 있음" 이 아니라 "tradeoff의 방향이 복잡도에 따라 뒤집힌다" 는 surprise.

**Paper framing**: "Complexity-adaptive feedback strategies: how the optimal feedback granularity inverts as task complexity grows."

#### Scenario E — "U-curve in H-PR"

**관찰**:
- H-PR: L2 최고, L1과 L3 둘 다 낮음
- Overfit Gap: L3에서 가장 큼

**해석**: "피드백 정보량에 U-curve 최적점이 존재한다. L1은 정보 부족으로 수정 못 함, L3는 overfit으로 품질 하락. L2가 sweet spot."

**주의**: "최적점 존재" 는 사전 가정이 아니었음 (Claim v0.2에서 삭제). 이 시나리오가 실제로 나타나면 **사후 관찰** 로 서술하되, claim을 사후에 강화하지 말 것. "Data shows a U-shape at L2" 정도의 descriptive 표현.

#### Scenario F — "No effect of level" (null result)

**관찰**:
- H-PR: flat across L1/L2/L3
- Overfit Gap: flat

**해석**: "이 setup 안에서는 피드백 정보 밀도가 결과에 별 영향이 없다. 더 지배적인 다른 변수가 존재한다 (LLM 능력, task 자체 어려움 등)."

**Claim 층 상태**: (a)(b)(c)(d) 모두 기각

**대응 framing**: Null result로 정직하게 보고. "Code2E's blind multi-agent system shows no feedback-density sensitivity at this scale; dominant variability comes from elsewhere (LLM baseline capability, task-intrinsic complexity)." Within-cell variance 분석과 bootstrap CI를 엄격히 보고하여 "작은 sample 문제" 반박 차단.

**리스크**: 가장 허약한 결과. Reviewer가 "sample size 부족" 으로 공격할 가능성 높음.

#### Scenario G — "시스템 자체가 기능 불능"

**관찰**:
- 대부분의 run이 Runnability pre-check 또는 Evaluator 초반에 실패
- H-PR이 거의 모든 cell에서 0-20%
- Level 간 비교 자체가 불가능

**대응**: Week 9 비상 체크포인트에서 감지 → Option 4 긴급 축소 → 단일 task 케이스 스터디로 재구성. v0.3의 Runnability pre-check이 이 scenario 가능성을 이미 낮춤.

**Fallback paper framing**: "Building a blind multi-agent code generation harness: design decisions and early-stage observations from 3 tasks." 연구 논문에서 시스템 구축 경험 공유 논문으로 포지션 하향.

#### Scenario H — "Secondary 분석의 뜻밖의 발견" (cross-cutting)

Primary가 약하게 나와도 failure category 분해 분석에서 뭔가 나올 가능성. 예:
- "Level은 spec_violation 검출에 영향을 주지만 edge_case에는 무영향"
- "Security failure는 어느 level에서도 개선 없음 (시스템이 security 학습 못 함)"

**중요**: 이런 미시적 발견은 어느 Scenario (A-F) 와도 공존 가능한 secondary finding. Primary가 약할 때의 안전망.

#### Claim 층별 생존 매트릭스

| Scenario | (a) level→pass | (b) level→gap | (c) 비대칭 | (d) tier 의존 | 종합 |
|---|:---:|:---:|:---:|:---:|---|
| A 완전 비대칭 | ✓ | ✓ | ✓ | ✓ | 🟢 Ideal |
| B Plateau + overfit | ✓ | ✓ | ✓ | ? | 🟢 강함 |
| C 단조 증가만 | ✓ | ✗ | ✗ | ? | 🟡 within-blind |
| D Tier flip | ✓ | ✓ | ✓ | ✓ (강) | 🟢 가장 흥미 |
| E U-curve | ✓ | ✓ | ✓ | ? | 🟡 수사 강함 |
| F null | ✗ | ✗ | ✗ | ✗ | 🟠 허약 |
| G 기능 불능 | N/A | N/A | N/A | N/A | 🔴 Option 4 |

**핵심**: G만이 진정한 실패 케이스. A~F는 모두 publishable한 스토리를 포함한다. 이것이 Claim 누적 구조 (a→b→c→d) 설계의 목적이며, 프로젝트의 robustness 근거.

#### 추정 확률 (주관적, 사전 기록)

| Scenario | 추정 확률 |
|---|---|
| A / B / D 중 하나 | ~60% |
| C (단조 증가) | ~20% |
| E (U-curve) | ~10% |
| F (null) | ~8% |
| G (기능 불능) | ~2% (Runnability pre-check 덕에 낮아짐) |

**이 확률은 사후 분석에 사용**: 실제 결과가 어느 scenario였는지 대조해서 "사전 예상이 맞았는가" 를 discussion에 기록. 연구 과정의 정직성을 드러내는 장치.

---

## 8. Timeline & Decision Gate

**Current position**: Week 6 마지막 (2026-04-12)
**Total duration**: 12주 단축 학기제
**Remaining**: Week 7 ~ Week 12 (6 weeks)
**Final submission**: Week 12 (5/18-5/24)

### 8.1 Revised Timeline (Option 2: 5 repeats + minimal B2)

```
Week 6 (현재, 4/6-4/12 끝):
  - 실험 설계 현행본 확정 (이 문서, v0.6까지 iterative 개정)
  - Week 7 작업 분담 준비

Week 7 (4/13-4/19):
  - Task-S prototype 완성 (prompt + hidden_tests + canonical + metadata)
  - 시스템 뼈대 구현 시작 (Orchestrator + agent stubs)
  - Feedback formatter L1/L2/L3 구현 병행
  - Week 7 말: 팀원 2명이 Task-M, Task-L 병행 제작 시작

Week 8 (4/20-4/26):
  - Task-M, Task-L 완성 + 교차 검증 (독립 작성 후 비교)
  - System 전체 구현 완성 (full 4 agents + subprocess communication)
  - B2 분기 config flag 구현
  - Week 8 말: Task-S로 end-to-end smoke test 시작

Week 9 (4/27-5/3):
  - Smoke test 디버깅 마무리 (초반 2-3일)
  - B2 sanity check 실행 (Task-S, L2, 5 runs = 5 runs)
  - ★ DECISION GATE ★ (1-2일, 8.3 참고)
    ├─ 블라인드 효과 ✓ → Claim C v0.2 확정 유지
    └─ 효과 ✗ → "within-blind study" 로 재포지셔닝
  - Week 9 말: Primary 실험 시작 (먼저 Task-S 15 runs 돌리기)
  - ★ 비상 CHECKPOINT ★ (8.2 참고)

Week 10 (5/4-5/10):
  - Primary 실험 주행 (45 runs 중 대부분)
  - 중간 분석으로 metric pipeline 검증
  - 실행 중 발견 버그 fix
  - Task별/level별 데이터 수집 상태 확인

Week 11 (5/11-5/17):
  - Primary 실험 완료 + 필요시 재실행
  - 전체 분석 + 시각화 (곡선, overfit gap, category 분해)
  - 결과 해석 + discussion 초안 시작
  - 논문 구조 outline

Week 12 (5/18-5/24):
  - 논문 작성 + figures 확정
  - 최종 검토 + proofreading
  - 최종 발표 자료 제작
  - 최종 제출 (Week 12 말)
```

### 8.2 비상 체크포인트 (Week 9 말)

Week 9 마지막 시점에 다음 4가지를 점검:

- ☐ Smoke test 성공적으로 작동하는가?
- ☐ B2 sanity check 5 runs 완료되었는가?
- ☐ Decision gate 결정이 내려졌는가?
- ☐ Primary 실험이 시작되었는가 (최소 10+ runs)?

**기준**:
- 4개 모두 ✓ → 계획대로 진행
- 1-2개 ✗ → 다음 주 초에 집중 처리 후 계획 유지
- **3개 이상 ✗** → **Option 4로 긴급 축소**:
  - 2 tasks만 (Task-S, Task-L, Task-M drop)
  - 5 repeats 유지
  - B2 완전 생략 + "within-blind study" framing 사전 commit
  - Primary runs: 2 × 3 × 5 = 30 runs
  - Week 10-11에 Primary만 돌리고 Week 11-12에 분석+글쓰기

### 8.3 Decision Gate (Week 9 중, B2 결과 해석 규칙)

**사전 commit 규칙** (B2 실행 전에 이 규칙을 박아두어야 bias 회피):

Task-S에서 B2(non-blind) vs B3(blind)의 overfit gap 비교:

| 결과 | 해석 | 조치 |
|---|---|---|
| B2 overfit gap > B3 (양적 차이, 방향 맞음) | 블라인드가 overfit 억제에 기여 | Claim C v0.2 확정 유지 |
| B2 ≈ B3 (무차이) | 블라인드의 overfit 억제 효과 미검출 | "within-blind study" 재포지셔닝, 데이터 그대로 활용 |
| B2 < B3 (반대 방향) | 예상 외 결과, 구현 버그 의심 | 디버깅 후 1회 재시도, 그래도 재현되면 재포지셔닝 |

**재포지셔닝 시 변경 사항**:
- Title에서 "Blind" 제거 → "Feedback Information Density in Multi-Agent Code Generation"
- Intro motivation 재작성 (블라인드를 contribution이 아닌 배경으로)
- Related work 섹션에서 A2A/Anthropic 인용 강화
- Discussion 논조 조정 ("within blind systems")
- **데이터, 차트, 분석은 그대로 사용**

### 8.4 Critical Path와 병렬화

**Critical path** (직렬 의존):
Task prototypes → System implementation → Smoke test → B2 → Decision gate → Primary → Analysis → Paper

**병렬 가능 작업** (Week 7-8 동시):
- Task 제작 (팀원 2명) ∥ System 구현 (팀원 1명)
- Feedback formatter 구현 ∥ Orchestrator 구현
- Task 교차 검증 ∥ Advisor/Planner prompt 설계

**역할 분담** (Week 7 확정):
- **이주영**: Orchestrator, Runner, Metric 구현 + Task-L 제작
- **정혁준**: Executor, Planner 구현 + Task-M 제작
- **고기호**: Evaluator, Advisor, Feedback formatter 구현 + Task-S 제작

**교차 검증 페어** (독립 작성 후 비교, Section 4.7):
- Task-S: 고기호 작성 → 정혁준 검토
- Task-M: 정혁준 작성 → 이주영 검토
- Task-L: 이주영 작성 → 고기호 검토

---

## 9. Open Items (TBD)

v0.2 기준 남은 결정. 본 초안의 blocker는 아니지만 명시된 deadline 전 확정 필요.

| 항목 | 긴급도 | 결정 시점 |
|---|---|---|
| Task-S prompt + hidden test 구체 내용 | 🔴 높음 | Week 7 초 |
| Task-M, L 구체 내용 | 🟡 중간 | Week 7 말 ~ Week 8 |
| Orchestrator state machine 구현 세부 | 🟡 중간 | Week 7 구현 중 |
| Executor prompt 템플릿 구체 (initial / revise_for_advisor / **fix_runtime_error** / revise_for_evaluator) | 🟡 중간 | Week 7 구현 중 |
| Planner / Advisor / Evaluator 시스템 프롬프트 | 🟡 중간 | Week 7 구현 중 |
| AI Slop 운영 정의 (Advisor의 ai_slop category 구체 기준) | 🟢 낮음 | Week 7 구현 중 |
| B1/B2 early stopping 추가 여부 | 🟢 낮음 | Week 9 smoke test 후 |
| 최종 figure/table layout | 🟢 낮음 | Week 11 분석 시 |

**v0.1 대비 해결된 항목들** (plan 본문에 반영됨):
- LLM 모델 선택 → Sonnet 4.6 uniform (3.2.1)
- Stop condition 세부 → A1/A2 primary, B1/B2 optional off (6.3)
- Advisor 피드백 포맷 → 3-category structured (3.2.2)
- Planner 출력 구조 → 4-section structured (3.2.3)
- Process isolation → subprocess level (3.2.1)
- Feedback level 정의 (L1-L3) → 3.1.1 ~ 3.1.4
- Task 도메인 → 단축 URL / 로그인 할일 / 잔고 이체 (4.1-4.3)
- Hidden test 형식 → pytest (4.5)
- 교차 검증 프로세스 → 독립 작성 후 비교 (4.7)
- Run procedure 세부 → 6.1-6.7
- Timeline → Section 8 (v0.2 전면 재작성)

---

## 10. Critical Files (예상 산출물)

이 실험 설계가 실제 실행될 때 생성되어야 하는 파일 구조:

```
code2e-agent/
├── docs/
│   ├── experimental_design.md      # 이 문서의 정식 버전 (v0.1 → v1.0)
│   └── architecture-sketch.md      # 기존
│
├── tasks/
│   ├── task_s/
│   │   ├── prompt.txt
│   │   ├── hidden_tests.py
│   │   ├── canonical.py
│   │   └── task_metadata.json
│   ├── task_m/
│   │   ├── prompt.txt
│   │   ├── hidden_tests.py
│   │   ├── canonical.py
│   │   └── task_metadata.json
│   └── task_l/
│       ├── prompt.txt
│       ├── hidden_tests.py
│       ├── canonical.py
│       └── task_metadata.json
│
├── src/
│   ├── orchestrator/               # 결정론적 state machine
│   ├── agents/
│   │   ├── planner/
│   │   ├── executor/
│   │   ├── advisor/
│   │   └── evaluator/
│   ├── feedback/
│   │   └── level_formatters.py     # L1, L2, L3 포맷 변환
│   ├── runner/
│   │   ├── run_experiment.py
│   │   └── config.py               # blind/non-blind flag, level 등
│   └── metrics/
│       ├── hidden_pass_rate.py
│       ├── overfit_gap.py
│       └── failure_category.py
│
└── results/
    ├── primary/                    # 45 runs (3 tasks × 3 levels × 5 repeats)
    │   └── task_X__level_Y__rep_Z/
    └── b2_sanity/                  # 5 runs (Task-S × L2 × 5 repeats, non-blind)
        └── task_s__nonblind__rep_Z/
```

---

## 11. Verification

이 실험 설계의 end-to-end 검증 단계:

1. **Task-S prototype 검증** (Week 7 초)
   - Task-S 한 개를 직접 손으로 만든 canonical 코드와 hidden_tests.py 로 채점
   - 사람이 이상적으로 작성한 구현이 모든 hidden test를 통과해야 함
   - Failure: hidden test가 기계적 번역을 넘어 주관적 해석을 포함하고 있음 → 재작성

2. **Pipeline smoke test** (Week 8 말)
   - Task-S에 대해 B3 시스템을 한 번 끝까지 실행
   - 모든 metric (H-PR, overfit gap, iterations, regression, cost, runnability_attempts) 이 수집되는지 확인
   - 특히 overfit gap 계산이 합리적 숫자가 나오는지 (음수가 아닌지, 과도한 값이 아닌지)
   - Failure: pipeline 어딘가가 끊김 → 디버깅

3. **Feedback level 포맷터 단위 테스트** (Week 7 말 ~ Week 8)
   - 동일한 test failure에 대해 L1/L2/L3 포맷터가 각각 다른 양의 정보를 출력하는지 확인
   - Executor 프롬프트에 정확히 해당 level의 정보만 들어가는지 확인
   - Failure: level이 의도대로 차별화되지 않음 → 포맷터 수정

4. **Evaluator Playwright test 생성 검증** (Week 8 말)
   - Task-L에 대해 Evaluator가 Playwright 기반 test를 안정적으로 생성하는지 확인
   - 생성된 test가 실행 가능하고 의미 있는 검증을 수행하는지 확인
   - Failure: Evaluator가 Playwright test를 생성하지 못함 → Task-L에서 FE 조건 제거, Backend + DB만으로 fallback

5. **B2 sanity check** (Week 9)
   - 실제 B2 실험 결과로 premise validation (Decision Gate, Section 8.3)
   - 결과에 따라 Claim 재포지셔닝 여부 결정
   - Failure: 디버깅 필요 (코드 버그 vs 진짜 negative result 구분)

5. **Primary 실험 후 cross-validation** (Week 11)
   - 3 task × 3 level × **5 repeat** (총 45 runs) 의 곡선이 noise가 아니라 일관된 패턴을 보이는지 확인
   - Bootstrap CI가 너무 넓으면 repeat 수 증가 검토
   - Failure: variance가 너무 큼 → 추가 repeat 또는 Tier 3 단순화 검토

---

## 12. 알려진 한계

이 연구 설계가 아직 답하지 못하는 것:

- **외부 타당성**: 3 태스크에서 관찰된 패턴이 다른 도메인에 일반화되는지는 case study 방법론의 본질적 한계
- **모델 일반화**: 한 가지 LLM에서 본 결과가 다른 모델에 통하는지 (TBD: 모델 선택과 함께 결정)
- **장기 실행 (long-running) 측면**: Anthropic 글들이 강조한 multi-session/progress-file 측면은 본 실험 scope 외. 후속 연구로 분리.
- **Baseline 다양성**: 현재 baseline은 B2 하나뿐. Claude Code, Cursor 등 외부 비교는 fair comparison의 어려움 때문에 제외.
- **Tier간 confound**: Tier가 스택 복잡도(in-memory → DB → DB+FE)로 정의되어, Task-L의 결과 차이가 비즈니스 로직·DB·FE 중 어느 요인에 기인하는지 분리 불가. 단, 이는 실제 서비스의 복잡도 증가 방식을 반영한 의도적 설계.

이 한계들은 논문의 Limitations 섹션에 명시적으로 기록.
