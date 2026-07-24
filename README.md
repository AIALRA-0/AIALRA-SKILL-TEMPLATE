# AIALRA-SKILL-TEMPLATE

## 这份文件能帮你做什么

这份文件回答两个问题：这个仓库是什么，以及怎样创建第一个 Skill 仓库

适合阅读这份文件的人：

- 第一次接触本模板的人
- 准备创建新 Skill 的人
- 想先看懂整体结构，再决定是否继续的人

读完以后，你应该能够生成一个安全草稿仓库，并知道下一步该阅读哪份文档

你现在不需要理解 Runner、Schema、validator 或状态机；这些概念会在后续文档中逐个解释

## 先用一句话理解这个仓库

这个仓库是一台“Skill 仓库生成器”

你提供 Skill 的名称、用途和界面文字，生成器会创建一个新的独立 Git 仓库；新仓库已经包含运行框架、测试、安全检查和学习边界

生成结果默认处于安全草稿状态；完成领域工作流和测试前，它不会执行真实任务

## Skill 是什么

Skill 是一组围绕明确任务组织起来的指令和资源

一个 Skill 通常包含：

- 触发说明
- 执行步骤
- 输入和输出规则
- 可重复使用的脚本
- 结果检查程序
- 安全边界
- 测试

本模板坚持一个仓库只保存一个 Skill；这样可以让版本、权限、测试和回滚保持独立

## 模板仓库和生成仓库有什么区别

你会接触两种仓库

| 仓库 | 用途 | 谁来修改 |
|---|---|---|
| 当前模板仓库 | 保存通用生成器和 Runtime | 模板维护者 |
| 生成后的 Skill 仓库 | 保存某一个具体 Skill | 该 Skill 的维护者 |

当前仓库的 `template/` 目录保存生成素材；运行生成器后，这些素材会进入新的独立仓库

这句话的准确含义是：生成后的 Skill 仓库与 `template/` 目录经过处理后的结构相同，不会与整个模板仓库相同

生成器会依次完成以下处理：

1. 把 `template/` 里面的文件复制到新仓库根目录 —— 新仓库以 `template/` 的内容为基础
2. 把 `__SKILL_NAME__` 等占位符替换成真实信息 —— 通用素材因此变成当前 Skill 的文件
3. 删除文件名末尾的 `.tmpl` —— 例如 `README.md.tmpl` 会变成 `README.md`
4. 创建 `.core-lock.json` —— 新仓库从第一次生成开始就能检测稳定核心漂移
5. 初始化新的 `.git/` —— 新 Skill 因此拥有独立提交、版本、远端和回滚历史

下面是几项实际映射：

| 模板工厂中的来源 | 生成仓库中的结果 | 是否进入新仓库 |
|---|---|---|
| `template/README.md.tmpl` | `README.md` | 进入 |
| `template/.agents/skills/__SKILL_NAME__/SKILL.md.tmpl` | `.agents/skills/<真实名称>/SKILL.md` | 进入 |
| `template/.agents/skills/__SKILL_NAME__/workflow.yaml.tmpl` | `.agents/skills/<真实名称>/workflow.yaml` | 进入 |
| 根目录 `scripts/create_skill_repo.py` | 没有对应文件 | 不进入，它只负责生成仓库 |
| 根目录 `docs/` | 没有对应目录 | 不进入，它只解释模板工厂 |
| 根目录 `tests/test_template_runtime.py` | 没有对应文件 | 不进入，它只测试模板工厂 |

因此可以把当前仓库理解成两层：

- 模板工厂层 —— 根目录的生成器、说明和模板测试
- Skill 成品层 —— `template/` 经过替换后形成的独立仓库

### 为什么生成仓库不能放在模板仓库里面

模板仓库和生成仓库都会拥有自己的 `.git/`

错误结构长这样：

```text
AIALRA-SKILL-TEMPLATE/       # 外层模板仓库
└── example-skill/           # 错误放入外层仓库内部的生成仓库
    └── .git/                # 内层 Skill 仓库自己的 Git 历史
```

这种结构叫嵌套 Git 仓库，会出现以下表现：

- 在外层运行 `git status` 时，看不到内层每个文件的普通变化 —— 外层 Git 会把内层仓库视为另一个边界
- 在外层运行 `git add` 时，可能看到 `adding embedded git repository` 警告 —— Git 可能只记录一个指向内层提交的 gitlink
- 其他人只克隆外层仓库时，可能拿不到内层仓库的实际文件 —— 内层内容没有按照正常文件进入外层历史
- Agent 或脚本可能找到错误的仓库根目录 —— 提交、标签、核心锁和远端操作可能落到错误仓库
- 删除、移动或回滚外层目录时，内层尚未推送的提交可能一起丢失 —— 两套生命周期会互相干扰

正确结构让两个仓库成为同级目录：

```text
工作目录/
├── AIALRA-SKILL-TEMPLATE/   # 模板工厂仓库
└── example-skill/           # 生成后的独立 Skill 仓库
```

## 创建第一个 Skill 仓库

### 第一步：准备五项信息

创建前需要确定以下五项信息：

1. Skill 名称 —— 这是程序使用的稳定标识，只能包含小写字母、数字和单个连字符，长度为 1 到 64 个字符，例如 `example-research-skill`
2. 完整用途说明 —— 这是 Codex 判断何时触发 Skill 的主要依据，长度为 40 到 1024 个字符，必须同时写明适用请求和不适用边界
3. 界面显示名称 —— 这是人在 Codex 界面中看到的名称，可以使用空格和自然语言，例如 `Example Research Skill`
4. 界面短描述 —— 这是界面中帮助人快速理解 Skill 的简短说明，长度为 25 到 64 个字符
5. 默认调用提示 —— 这是界面提供的示例请求，必须明确包含 `$Skill名称`，让 Codex 知道用户希望调用哪个 Skill

这五项信息可以先在与 Codex 的对话中讨论，由 Codex 整理成候选文本并交给你确认

确认后，它们作为生成命令的参数传入，不需要先手工写入模板文件

生成器会把它们写入以下位置：

| 信息 | 主要写入位置 | 生成后有什么用 |
|---|---|---|
| Skill 名称 | Skill 目录名、`SKILL.md`、`workflow.yaml` 和界面元数据 | 让目录、触发名称和工作流身份保持一致 |
| 完整用途说明 | `SKILL.md` 顶部的 `description` | 让 Codex 判断什么时候使用和什么时候不使用 |
| 界面显示名称 | `agents/openai.yaml` 和文档标题 | 让人看到清晰名称 |
| 界面短描述 | `agents/openai.yaml` | 让 Skill 列表能够快速说明用途 |
| 默认调用提示 | `agents/openai.yaml` | 为用户提供一条可以直接修改和使用的示例请求 |

### 线上仓库位置怎样处理

这五项信息不包含 GitHub 仓库地址

`--output` 只决定本地目录位置，生成器只会在本地执行 `git init -b main`

生成器不会自动创建 GitHub 仓库、预留线上名称、设置 `origin` 或推送内容

线上仓库按照以下顺序处理：

1. 确定 Skill 名称 —— 建议本地目录名与线上仓库名保持一致
2. 需要提前占用名称时，在 GitHub 创建一个空仓库 —— 不要同时生成 README、许可证或 `.gitignore`
3. 在模板仓库旁边生成本地 Skill 仓库 —— `--output` 使用同级目录
4. 完成人工审计和本地验证 —— 未通过以前不推送正式版本
5. 把空仓库 URL 设置为生成仓库的 `origin` —— 远端地址保存在本地 `.git/config`
6. 提交并推送经过验证的内容 —— 线上仓库从第一个合格提交开始保存历史

GitHub token、密码和其他认证信息由 Git 或已授权工具管理，不能写入生成命令、README、Skill 文件或远端 URL

### 第二步：运行生成命令

在当前仓库根目录运行：

```bash
python3 scripts/create_skill_repo.py \
  --name example-research-skill \
  --output ../example-research-skill \
  --display-name "Example Research Skill" \
  --short-description "Research a defined topic with checked evidence" \
  --description "Research a defined topic with checked evidence. Use when the user requests evidence-based research. Do not use for purchasing, account changes, or unrelated tasks." \
  --default-prompt 'Use $example-research-skill to research this topic.'
```

命令每一部分的含义如下：

| 命令部分 | 是什么 | 有什么用 |
|---|---|---|
| `python3` | Python 解释器 | 负责运行生成程序 |
| `scripts/create_skill_repo.py` | 当前模板仓库的生成器 | 读取参数并创建完整 Skill 仓库 |
| `\` | Shell 的续行符 | 表示下一行仍属于同一条命令，不能在它后面添加其他文字 |
| `--name` | Skill 稳定名称 | 决定 Skill 目录名、触发名称和工作流身份 |
| `--output` | 本地输出路径 | 决定新仓库创建在哪里，`../` 表示当前模板仓库的上一级目录 |
| `--display-name` | 界面显示名称 | 写入界面元数据和生成文档标题 |
| `--short-description` | 界面短描述 | 写入界面元数据，帮助用户快速识别用途 |
| `--description` | 完整触发说明 | 写入 `SKILL.md`，用于判断适用请求和排除范围 |
| `--default-prompt` | 默认调用提示 | 写入界面元数据，并通过 `$example-research-skill` 明确引用当前 Skill |
| 引号 | 参数边界 | 让包含空格和 `$` 的整段文字作为一个参数传给生成器 |

示例文字都需要替换成真实 Skill 信息

名称改变时，`--name`、`--output` 和默认提示中的 `$example-research-skill` 必须一起修改

生成器还有一个可选的 `--portable` 参数，它只在隔离测试或无法使用官方初始化器时使用，正常创建正式 Skill 时不添加

### 第三步：确认生成成功

成功后，命令会返回类似下面的结果：

```json
{
  "created": true,
  "repository": "/本地绝对路径/example-research-skill",
  "skill": "example-research-skill",
  "initializer": "official initializer: /初始化器路径"
}
```

`created=true` 表示生成、草稿验证、核心锁创建和本地 Git 初始化已经全部完成

`repository` 表示新仓库的本地绝对路径

`skill` 表示生成器最终采用的稳定名称

`initializer` 表示本次使用官方初始化器还是隔离测试使用的 portable 初始化器

参数不合法、输出目录已经存在、草稿验证失败或 Git 初始化失败时，命令返回 `ERROR` 并停止

生成器先在临时目录工作，失败时会清理临时内容，不会覆盖已经存在的目标目录

新目录中应当包含以下主要内容，`#` 后面的文字是本页解释，不属于真实文件名：

```text
example-research-skill/                         # 新 Skill 的独立仓库根目录
├── .git/                                       # 当前 Skill 自己的提交、分支和远端配置
├── .agents/skills/example-research-skill/      # Codex 能够发现和运行的 Skill 主目录
│   ├── agents/openai.yaml                      # Skill 在 Codex 界面中的显示信息
│   ├── schemas/                                # 入口和结果必须遵守的 JSON 数据结构
│   ├── scripts/                                # Runner、验证、学习和核心锁程序
│   ├── SKILL.md                                # 触发说明与 Agent 运行协议
│   └── workflow.yaml                           # 节点、顺序、执行器和失败路径
├── .github/                                    # GitHub Actions 与依赖更新配置
├── learning/                                   # 脱敏事件、活跃规则、归档和晋升提案
├── scripts/                                    # 仓库级验证和敏感信息扫描入口
├── tests/                                      # Runtime 基础测试和未来的领域测试
├── .core-lock.json                             # 稳定核心文件的 SHA-256 摘要清单
├── .gitleaks.toml                              # Gitleaks 敏感信息扫描配置
├── .gitignore                                  # 禁止 Git 跟踪的本地和运行时文件
├── .pre-commit-config.yaml                     # 提交前可以运行的自动检查
├── AGENTS.md                                   # 约束仓库内 Agent 的维护和运行行为
├── CHANGELOG.md                                # 记录每个 Skill 版本的用户可见变化
├── README.md                                   # 教维护者配置、运行和审计当前 Skill
├── SECURITY.md                                 # 说明凭据、确认和事故处理边界
└── VERSION                                     # 当前 Skill 的独立版本号
```

生成器还会初始化独立 Git 仓库，并创建第一份核心锁

## 为什么新仓库暂时不能运行

新仓库的 `workflow.yaml` 包含：

```json
{
  "definition": {
    "configured": false
  }
}
```

`false` 表示领域流程尚未配置完成；Runner 会拒绝启动真实任务

把它改成 `true` 以前，需要完成：

1. 定义支持范围和排除范围 —— 在 `SKILL.md` 中明确哪些请求应当触发，哪些相邻请求不能触发
2. 定义全部工作流节点 —— 用真实领域步骤替换 `workflow.yaml` 中唯一的通用草稿节点
3. 定义每个节点的输入和输出 —— 为入口、节点结果和最终结果编写可由 Runner 检查的 Schema
4. 选择执行器并声明权限 —— 为每个节点固定 `script`、`mcp`、`browser-dom`、`computer-use` 或 `reasoning`，同时声明副作用和确认要求
5. 添加成功和失败测试 —— 证明合法请求能够完成，并证明错误输入、越权操作和相邻非触发请求会被拒绝
6. 完成安全检查 —— 确认仓库没有凭据和个人信息，所有外部写入都有用户确认
7. 设置 `definition.configured=true` —— 只在领域流程和测试已经完成后解除安全草稿状态
8. 更新版本并重新生成核心锁 —— 保存本次稳定行为的版本记录和 SHA-256 摘要

生成仓库自己的 `README.md` 会逐步解释这些操作

## 这个模板会替你守住什么

模板内置以下约束：

- Runner 控制节点顺序和状态转换 —— Agent 只能推进当前节点，不能跳过步骤或自行宣布完成
- Schema 检查输入和输出结构 —— 缺少字段、类型错误和额外字段会在进入下一节点前被拒绝
- validator 执行额外的确定性检查 —— Schema 无法表达的跨字段关系和结果规则由程序继续检查
- 重试、回退和超时都有限制 —— 失败不能无限循环，工作流只能按照预先声明的路径继续
- 写入和破坏性操作需要用户确认 —— Runner 会在改变外部状态前暂停，用户明确同意后才能继续
- 稳定核心由 SHA-256 清单检测漂移 —— 工作流、Schema 或 Runtime 出现未登记变化时会硬停止
- 学习内容只能写入 `learning/` —— 运行经验只能形成建议，不能自动修改稳定工作流和权限
- 敏感信息扫描会在本地和 CI 中执行 —— 当前文件和完整 Git 历史都会检查疑似凭据与私钥

这些名称暂时看不懂也没有关系；阅读路线会在需要时引导你进入对应解释

## 这个模板的边界

模板负责生成运行框架和强制检查

具体 Skill 仍需由维护者定义：

- 真实任务范围
- 领域工作流
- 工具和权限
- 输入输出 Schema
- 领域测试
- 结果质量标准

身份验证、验证码、扫码和双重认证由用户亲自完成；真实凭据和浏览器会话不能写入 Git

## 接下来应该读什么

根据你的目标选择一份文档

| 你的目标 | 下一份文档 |
|---|---|
| 想看懂一次请求怎样运行 | [架构入门](docs/architecture.md) |
| 准备填写 `workflow.yaml` | [Workflow 精确参考](docs/workflow-reference.md) |
| 想知道每个文件有什么用 | [文件地图](docs/file-map.md) |
| 想理解 Skill 怎样积累经验 | [受控学习](docs/learning.md) |
| 准备升级版本或发布 | [版本与维护](docs/maintenance.md) |
| 准备修改当前模板 | [贡献指南](CONTRIBUTING.md) |
| 准备处理权限和敏感信息 | [安全策略](SECURITY.md) |
| 正在迁移旧版 v0.1 | [迁移指南](docs/migration-v0.2.md) |
| 想审查设计依据 | [研究依据](docs/research-notes.md) |

第一次阅读时，建议只打开与你当前目标对应的一份文档

## 验证模板自身

模板维护者修改当前仓库后，需要运行：

```bash
python3 scripts/validate_template.py
python3 -m unittest discover -s tests -v
python3 scripts/check_secrets.py
```

三条命令的用途、成功输出和失败处理由 [贡献指南](CONTRIBUTING.md) 逐步解释
