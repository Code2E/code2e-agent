# Week 7 (4/13 - 4/19)

## 목표

- Agent 인터페이스 계약 확정 (Orchestrator ↔ Agent 통신 규약)
- Task-S prototype 완성 (prompt + hidden_tests + canonical)
- 시스템 뼈대 구현 시작 (Orchestrator + Executor/Planner + Evaluator/Advisor stub)

## 팀원별 작업

### 이주영

| 작업                                                     | 산출물                                                 | 상태 |
| -------------------------------------------------------- | ------------------------------------------------------ | ---- |
| Agent 인터페이스 정의 (stdin/stdout 포맷, 입출력 스키마) | `docs/week07/agent-interface.md`                       | ⬜   |
| Orchestrator state machine 구현                          | `src/orchestrator/`                                    | ⬜   |
| Runner / Config 뼈대                                     | `src/runner/run_experiment.py`, `src/runner/config.py` | ⬜   |
| Task-L 제작 착수                                         | `tasks/task_l/prompt.txt`                              | ⬜   |

### 고기호

| 작업                                   | 산출물                             | 상태 |
| -------------------------------------- | ---------------------------------- | ---- |
| Task-S prompt 작성                     | `tasks/task_s/prompt.txt`          | ⬜   |
| Task-S hidden test 작성                | `tasks/task_s/hidden_tests.py`     | ⬜   |
| Task-S canonical 구현 + test 통과 검증 | `tasks/task_s/canonical.py`        | ⬜   |
| Task-S metadata                        | `tasks/task_s/task_metadata.json`  | ⬜   |
| Evaluator stub 구현                    | `src/agents/evaluator/`            | ⬜   |
| Advisor stub 구현                      | `src/agents/advisor/`              | ⬜   |
| Feedback formatter L1/L2/L3 구현       | `src/feedback/level_formatters.py` | ⬜   |

### 정혁준

| 작업                                                                                          | 산출물                    | 상태 |
| --------------------------------------------------------------------------------------------- | ------------------------- | ---- |
| Executor 구현 (scaffold, revise_for_advisor, fix_runtime_error, revise_for_evaluator)         | `src/agents/executor/`    | ⬜   |
| Planner 구현 (5-section 구조화 출력, [Build Sequence] 포함)                                   | `src/agents/planner/`     | ⬜   |
| Task-M 제작 착수                                                                              | `tasks/task_m/prompt.txt` | ⬜   |

## 의존 관계

- 이주영의 인터페이스 정의 (월-화) → 고기호/정혁준 agent 구현 시작
- Task-S prototype (고기호) → Week 8 smoke test 입력 (critical path)

## 회고 (주말 작성)

- 완료:
- 이월:
- 피드백:

## 고기호 한것
### Task-S
- tasks/task_s/
	- prompt.txt, canonical.py, hidden_tests.py
	- task_s의 hidden test에서 어떤 실험을 정확히 하는지 없어, 이에 대해서는 클로드와 같이 작업해 prompt.txt 정의 후 hidden_test.py구현 -> canonical.py도 저 hidden_tests에 맞게 구현
- 목적
	- 단축 URL 서비스
	- 목표 5개 명시조건
	- 핵심 메커니즘: 같은 long URL은 같은 short code
	- 코드 충돌 처리
	- redirect 의미
- 구조(각각 C1, C2, C3, C4, C5로 구분)
	- C1,C2,C3,C5 -> spec_violation
	- C4 -> edge_case
	1. `POST /shorten` — JSON body `{"url": "<원본 URL>"}` 를 받아 201 응답과 `{"code": "<단축코드>"}` 를 반환한다.
	2. 같은 URL을 여러 번 단축 요청하면 항상 동일한 코드를 반환한다.
	3. `GET /{code}` — 해당 코드에 대응하는 원본 URL로 302 리디렉션한다.
	4. `POST /shorten` 에서 URL이 비어 있거나 유효하지 않으면 (http/https 미시작) 400을 반환한다.
	5. `GET /{code}` 에서 존재하지 않는 코드를 요청하면 404를 반환한다.
### level_formatters
- 레벨 반환 형식 정의 L1, L2, L3
- experimental_design에 맞게 정의함
### evaluator, advisor stub 