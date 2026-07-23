# 文件地图

## 这份文件能帮你做什么

这份文件回答两个问题：每个文件有什么用，以及什么时候需要修改它

适合阅读这份文件的人：

- 找不到某项配置位置的人
- 准备修改模板的人
- 准备审计生成结果的人

读完以后，你应该能够根据任务找到正确文件，并避开不相关内容

如果你只想创建第一个 Skill，先阅读根目录 `README.md`

## 先分清两套文件

当前项目包含两套文件

1. 模板工厂文件：保存在当前仓库，用于生成 Skill
2. 生成仓库文件：由 `template/` 中的素材生成，每个 Skill 拥有独立副本

修改模板工厂会影响以后生成的 Skill；已经生成的仓库不会自动同步

## 模板工厂根目录

| 路径 | 谁读取 | 什么时候修改 |
|---|---|---|
| `README.md` | 第一次进入仓库的人 | 创建流程或阅读路线变化时 |
| `AGENTS.md` | 维护当前仓库的 Agent | 仓库级强制规则变化时 |
| `CONTRIBUTING.md` | 模板修改者和审查者 | 修改流程、测试要求或文档标准变化时 |
| `SECURITY.md` | 所有提交者 | 敏感信息、安全边界或泄漏处理变化时 |
| `CHANGELOG.md` | 使用者和发布者 | 每次需要记录版本变化时 |
| `VERSION` | 发布流程和核心清单 | 模板版本升级时 |
| `.editorconfig` | 编辑器和格式化工具 | 通用编码、换行或缩进规则变化时 |
| `.gitignore` | Git | 新的本地产物需要排除时 |
| `.gitleaks.toml` | Gitleaks | 敏感信息扫描规则变化时 |
| `.pre-commit-config.yaml` | pre-commit | 提交前检查流程变化时 |

## `docs/` 文档目录

| 路径 | 这份文档回答什么 |
|---|---|
| `docs/architecture.md` | 一次请求怎样从开始运行到完成 |
| `docs/workflow-reference.md` | `workflow.yaml` 每个字段、状态和命令怎样填写 |
| `docs/file-map.md` | 每个文件有什么用 |
| `docs/learning.md` | 学习事件怎样记录、归档和晋升 |
| `docs/maintenance.md` | 怎样判断版本、发布和弃用 |
| `docs/migration-v0.2.md` | 怎样把 v0.1 旧结构迁移到当前结构 |
| `docs/research-notes.md` | 当前设计依据来自哪里 |

## 模板工厂脚本

| 路径 | 它做什么 | 什么时候运行 |
|---|---|---|
| `scripts/create_skill_repo.py` | 根据参数渲染模板并初始化独立仓库 | 创建新 Skill 仓库时 |
| `scripts/validate_template.py` | 检查模板文件、语法、占位符和临时生成结果 | 每次修改模板后 |
| `scripts/check_secrets.py` | 扫描当前仓库中的敏感信息模式 | 每次提交前 |

## 模板工厂测试

| 路径 | 它验证什么 |
|---|---|
| `tests/test_template_runtime.py` | 生成仓库、草稿拒绝、脚本执行、禁止跳步、重试、回退、确认、学习和敏感信息扫描 |

Runtime 或生成器行为变化时，需要在这里增加成功测试和邻近失败测试

## GitHub 自动化

| 路径 | 它做什么 |
|---|---|
| `.github/workflows/validate.yml` | 在推送和 PR 时运行模板验证、测试、敏感信息扫描和完整历史 Gitleaks |
| `.github/dependabot.yml` | 定期检查 GitHub Actions 依赖更新 |

这些 YAML 文件遵循 GitHub 固定格式；它们的顶层字段不能套入自定义分类

## `template/` 是什么

`template/` 保存新 Skill 仓库的原始素材

文件名中的 `.tmpl` 表示生成时会替换占位符；例如 `__SKILL_NAME__` 会被替换成真实 Skill 名称

不要直接把整个 `template/` 目录当成可运行 Skill；使用生成器创建独立仓库

## 生成仓库的根目录素材

| 模板路径 | 生成后的路径 | 用途 |
|---|---|---|
| `template/README.md.tmpl` | `README.md` | 教维护者配置和运行当前 Skill |
| `template/AGENTS.md.tmpl` | `AGENTS.md` | 约束维护当前 Skill 的 Agent |
| `template/SECURITY.md.tmpl` | `SECURITY.md` | 说明当前 Skill 的安全规则 |
| `template/CHANGELOG.md.tmpl` | `CHANGELOG.md` | 记录当前 Skill 的版本变化 |
| `template/VERSION` | `VERSION` | 保存当前 Skill 版本 |
| `template/.gitignore` | `.gitignore` | 排除凭据、会话、Runtime 状态和缓存 |
| `template/.gitleaks.toml` | `.gitleaks.toml` | 配置 Gitleaks 扫描 |
| `template/.pre-commit-config.yaml` | `.pre-commit-config.yaml` | 配置提交前验证和敏感信息扫描 |

## Skill 目录素材

生成后的核心目录为 `.agents/skills/<skill-name>/`

| 模板路径 | 生成后的文件 | 用途 |
|---|---|---|
| `SKILL.md.tmpl` | `SKILL.md` | 告诉 Agent 何时触发以及怎样调用 Runner |
| `workflow.yaml.tmpl` | `workflow.yaml` | 保存执行节点、顺序、权限、失败路径和最终校验 |
| `agents/openai.yaml.tmpl` | `agents/openai.yaml` | 保存界面显示名称、短描述和默认提示 |
| `schemas/input.schema.json` | `schemas/input.schema.json` | 保存草稿入口 JSON 结构；领域配置时需要替换 |
| `schemas/output.schema.json` | `schemas/output.schema.json` | 保存草稿输出 JSON 结构；领域配置时需要替换 |

## Runtime 脚本素材

这些脚本会进入 `.agents/skills/<skill-name>/scripts/`

| 文件 | 用途 | 谁调用 |
|---|---|---|
| `runner.py` | 创建状态、执行脚本节点、返回外部动作、校验结果并控制状态转换 | Agent、宿主或维护者 |
| `runtime_lib.py` | 提供 JSON、Schema、路径、工作流、状态和核心锁公共函数 | 其他 Runtime 脚本 |
| `validate_repo.py` | 汇总检查 Skill 元数据、工作流、学习文件和核心锁 | 根目录验证入口 |
| `freeze_core.py` | 生成或检查稳定核心 SHA-256 清单 | 维护者 |
| `learn.py` | 记录一条脱敏学习事件 | 完成或用户暂停后 |
| `compact.py` | 归档原始事件并限制活跃规则数量 | `learn.py` 或维护者 |
| `promote.py` | 根据活跃规则生成待人工审查的晋升提案 | 维护者 |

修改这些脚本会改变所有未来生成 Skill 的 Runtime；需要完整成功和失败测试

## 生成仓库的根级脚本

| 模板路径 | 生成后的路径 | 用途 |
|---|---|---|
| `template/scripts/validate.py` | `scripts/validate.py` | 找到唯一 Skill，并调用内部仓库验证器 |
| `template/scripts/check_secrets.py` | `scripts/check_secrets.py` | 扫描生成仓库当前内容 |

## 学习目录素材

| 模板路径 | 生成后的路径 | 用途 |
|---|---|---|
| `template/learning/ledger.jsonl` | `learning/ledger.jsonl` | 保存尚未压缩的原始脱敏事件 |
| `template/learning/active-rules.json` | `learning/active-rules.json` | 保存有限的活跃建议规则 |
| `template/learning/archive/.gitkeep` | `learning/archive/.gitkeep` | 在首个归档出现前保留空目录 |
| `template/learning/proposals/.gitkeep` | `learning/proposals/.gitkeep` | 在首个提案出现前保留空目录 |

Runtime 学习只能修改 `learning/`

## 生成仓库测试和 CI

| 模板路径 | 生成后的路径 | 用途 |
|---|---|---|
| `template/tests/test_runtime.py` | `tests/test_runtime.py` | 检查草稿图、核心锁、Schema 和学习脱敏 |
| `template/.github/workflows/validate.yml` | `.github/workflows/validate.yml` | 在推送和 PR 时验证当前 Skill |
| `template/.github/dependabot.yml` | `.github/dependabot.yml` | 检查 Actions 依赖更新 |

领域 Skill 配置完成前，需要继续增加领域成功、失败和相邻非触发测试

## 按任务找文件

| 你准备做什么 | 先打开哪里 |
|---|---|
| 创建新 Skill 仓库 | 根目录 `README.md` |
| 修改生成命令 | `scripts/create_skill_repo.py` |
| 修改工作流结构 | `workflow.yaml.tmpl`、`runtime_lib.py` 和 Workflow 精确参考 |
| 修改运行状态 | `runner.py`、`runtime_lib.py` 和 Runtime 测试 |
| 修改学习机制 | `learn.py`、`compact.py`、`promote.py` 和 `docs/learning.md` |
| 修改核心锁 | `freeze_core.py`、`runtime_lib.py` 和安全文档 |
| 修改生成仓库说明 | `template/README.md.tmpl` |
| 修改 Agent 执行协议 | `SKILL.md.tmpl` 和 `template/AGENTS.md.tmpl` |
| 修改安全扫描 | 两套 `check_secrets.py`、Gitleaks 配置和 CI |
| 修改模板发布版本 | `VERSION` 和 `CHANGELOG.md` |

## 修改文件前最后确认

回答三个问题：

1. 这个文件由人、Agent 还是程序读取
2. 修改会影响当前模板，还是影响以后生成的 Skill
3. 哪个测试能够证明修改正确，并证明邻近错误会被拒绝

三个问题都能回答时，再开始编辑
