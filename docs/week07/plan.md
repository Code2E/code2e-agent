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
