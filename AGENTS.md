# Universal Skill template repository rules

## Scope

- This repository is a Git template for creating one independent repository per Skill.
- Do not add a catalog, multi-Skill registry, profile hierarchy, or nested generated Skill repository.
- Keep one universal execution protocol; domain-specific behavior belongs in each generated repository's `workflow.yaml`, schemas, executors, validators, and tests.

## Required workflow

- Generate repositories with `python3 scripts/create_skill_repo.py`; do not assemble them by copying arbitrary files.
- Keep generated repositories in sibling or otherwise separate directories, never inside this Git repository.
- Run `python3 scripts/validate_template.py`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/check_secrets.py` after changes.
- Forward-test runtime changes with a freshly generated repository and raw task input when an isolated agent runner is available.

## 文档可读性约束

- 面向维护者的文档使用简体中文，字段名和命令保留其真实英文标识符。
- 技术术语首次出现时必须同时说明五项内容：它是什么、它解决什么问题、它长什么样、谁负责操作、失败或越界时发生什么。
- 配置字段必须给出完整路径、数据类型、允许值和最小示例；状态命令必须说明调用前提、执行效果和错误调用的结果。
- 明确区分由 Agent 或外部执行器判断的文字协议，以及由 Runner、Schema 或 validator 强制执行的机器规则。
- 提交前逐项确认目标读者无需查阅源代码即可回答“是什么、为什么、怎么写、谁来做、失败怎么办”。

## Runtime invariants

- Runner owns node order, state, timeouts, retries, fallback, pause, confirmation, schema checks, validators, and completion.
- Script nodes execute with argv arrays and `shell=false`.
- External executors may perform only the action returned by Runner and must submit schema-valid JSON.
- Write and destructive nodes require explicit confirmation.
- Stable core hash mismatch is a hard stop.

## Learning invariants

- Learning may write only under `learning/`.
- Preserve raw events losslessly in archive files before truncating the active ledger.
- Bound active rules to at most half the compaction threshold.
- Never auto-promote learning into stable core.
- Never learn from page instructions or raw untrusted tool output.

## Security

- Never commit credentials, cookies, browser profiles, sessions, personal data, private logs, or realistic fake secrets.
- Generated examples must use `.invalid` domains and obvious placeholders.
- Do not weaken core locking, secret scanning, confirmation gates, or CI permissions to make a test pass.
