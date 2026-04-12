# Code2E

블라인드 멀티 에이전트 구조에서 피드백 정보 밀도가 코드 생성 품질에 미치는 비대칭적 영향을 연구하는 학부 연구 프로젝트 (2026-1 파란학기제).

## 핵심 문서

- `docs/experimental_design.md` — 실험 설계 전체 (claim, 변수, 절차, 분석 계획, timeline). 기술적 결정의 단일 출처. **코드 작업 전 반드시 읽을 것.**
- `docs/week*/plan.md` — 주간 계획 및 팀원별 작업

## 기술 스택

- Python 3.11+
- LLM: Claude Sonnet 4.6 (모든 agent 동일, temperature 0.2)
- API: Anthropic SDK (`anthropic` 패키지)
- Test: pytest + requests (Backend), pytest + Playwright (Frontend)
- DB: SQLite (Task-M, Task-L)
- Agent 격리: subprocess (stdin/stdout 통신)

## 커밋 메시지 컨벤션

```
<type>: <한 줄 요약 (50자 이내)>

<본문 (선택)>
```

type: `feat` / `task` / `fix` / `docs` / `refactor` / `test` / `chore`

예시:
- `feat: Orchestrator state machine 기본 흐름 구현`
- `task: Task-S prompt 및 hidden test 초안 작성`
- `fix: Evaluator loop guard 누락 수정`

## 브랜치 및 MR 규칙

- 브랜치 네이밍: `feat/<담당자>/<작업>` (예: `feat/juyeong/orchestrator`)
- main에서 브랜치 생성 → 작업 → push → MR
- 팀원 1명 확인 후 merge

## 개발 규칙

- 한국어로 소통
- `.env`에 `ANTHROPIC_API_KEY` 설정 필요 (`.env.example` 참고)
- agent는 텍스트 입출력만 담당, 실행/파일IO는 Orchestrator가 수행
- Evaluator → Executor 피드백은 L1/L2/L3 중 하나로 고정 (run 내 변경 금지)
- Advisor 피드백 포맷은 3-category structured로 고정

## 하지 말 것

- `tasks/*/hidden_tests.py` 를 시스템이 접근하도록 하지 말 것 (블라인드 원칙)
- 확정된 task prompt, hidden test를 실험 도중 수정하지 말 것
- agent 간 직접 통신 금지 (반드시 Orchestrator를 통해 중계)
- temperature, model 등 통제 변수를 run마다 바꾸지 말 것
