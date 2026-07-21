# AIALRA-SKILL-TEMPLATE

一个通用的、可执行的 Agent Skill 仓库模板；它统一每个 Skill 必须遵循的运行协议：

- 图驱动工作流：使用明确的节点和有向边定义执行步骤、先后顺序与状态转换，使每次运行都遵循同一条可检查、可追踪的工作流；
- 结构化输入输出：使用 Schema 约束初始输入、节点输出和最终结果，使 Agent、脚本与外部工具之间通过明确的数据契约协作；
- 确定性执行：将固定、重复、可计算的操作交给参数化脚本执行，并将外部工具调用和语义判断限制在节点声明的范围内；
- 失败回退：为每个节点声明超时、最大重试次数、预定义回退节点、用户等待状态和停止条件，使失败按照受控路径处理；
- 最终验证：在节点执行后校验输出，并在工作流完成前执行最终 Schema 与 Validator 检查，只有通过验证的结果才能交付；
- 受控学习：每次运行后记录一条脱敏、限定范围的经验或教训，定期压缩活跃规则并完整归档原始事件，核心规则只能经过审查、测试和版本变更后更新；
- 独立 Git：每个 Skill 使用独立仓库管理提交历史、版本、测试、发布和回滚，使其能够单独演进并保持可追溯性；

## 核心模型

### Git 仓库

Skill 是围绕一个明确任务领域组织起来的工作流、指令、Schema、脚本、验证器、测试和学习记录；每个 Skill 由本模板生成，并拥有自己的独立 Git 仓库；

采用独立仓库的原因是：

- 变更边界清晰：一个 Skill 的工作流、权限或学习规则发生变化时，不会同时改变其他 Skill；
- 版本独立：每个 Skill 可以按照自身节奏发布版本、创建标签和维护变更记录；
- 测试独立：提交只需要验证当前 Skill 的行为，失败结果和回归范围更容易定位；
- 回滚独立：某个 Skill 出现问题时，可以单独回退到稳定版本，不影响其他 Skill；
- 权限独立：不同 Skill 可以配置不同的维护者、分支保护、外部工具权限和发布策略；
- 历史可追溯：核心规则、实现代码和学习记录保存在同一条版本历史中，能够还原任意版本的完整行为；

一个仓库只包含一个 Skill，可以让触发范围和执行领域保持足够小；Agent 的执行具有概率性；当一个仓库同时承载多个任务领域时，触发判断、工具权限、状态流转和学习规则更容易互相影响；单 Skill 仓库让每次执行只面对一组明确的输入、节点、权限和输出契约；

### Catalog

Catalog 是多个 Skill 的集中注册表，通常保存 Skill 名称、仓库地址、版本、负责人、分类和发现信息；它适合统一浏览、检索、依赖治理和团队级发布管理，也会增加一个共享控制层：Skill 的发现、版本和运行仓库需要共同维护，任何结构变化都可能影响整个集合；

本模板不在单个 Skill 仓库中加入 catalog；当前目标是让每个 Skill 自包含、可独立运行和独立演进；未来需要统一浏览时，可以另建一个轻量外部注册表，仅保存仓库地址、稳定版本和必要的发现信息，不参与 Skill 的具体执行；

### Profile

Profile 是面向某类任务的可复用配置变体，例如研究型、文件生产型或工具操作型 profile；它可以为一组相似 Skill 预设章节、工具策略和操作约定，也会引入额外的继承关系和选择逻辑，使维护者需要同时理解通用模板、profile 和具体 Skill 三层规则；

本模板不设置多 profile；所有 Skill 共享同一套运行协议，具体领域行为直接写入各自的 `workflow.yaml`、Schema、执行器和验证器；这样可以从仓库内容直接确定真实行为，避免通用模板与 profile 之间出现覆盖、冲突或版本漂移；

### Agent

Agent 负责理解用户意图、准备结构化输入、调用当前节点允许的外部工具，以及完成无法脚本化的语义判断；Agent 的输出由模型生成，因此同一请求可能出现不同的推理路径；如果由 Agent 自由决定下一节点，可能产生跳过校验、改变顺序、无限重试、临时选择未声明工具或提前宣布完成等行为，执行结果也难以稳定复现；

### Runner

Runner 是仓库中的确定性状态机程序，对应 `.agents/skills/<skill-name>/scripts/runner.py`；它读取 `workflow.yaml`，为每次运行创建唯一状态，记录当前节点和已完成结果，并根据预先声明的边决定下一步；Runner 负责节点顺序、输入输出校验、超时、重试、回退、用户等待、写操作确认和最终完成条件；

Agent 每次只能处理 Runner 当前返回的节点指令，再把符合 Schema 的结果提交给 Runner；Runner 校验结果后返回下一项允许动作；这个职责边界将概率性的理解与判断限制在节点内部，将流程控制交给可重复执行的程序；

完整运行过程如下：

```mermaid
flowchart TD
    A["用户请求<br/>明确当前任务的目标、约束、输入材料和期望结果"] --> B["输入校验<br/>依据入口 Schema 检查字段、类型、范围和必填内容"]
    B --> C["初始化运行状态<br/>Runner 读取 workflow.yaml，创建状态 ID 并定位入口节点"]
    C --> D["执行当前节点<br/>按照节点声明调用脚本、MCP、浏览器、Computer Use 或推理执行器"]
    D --> E["节点结果校验<br/>使用输出 Schema 和可选 Validator 检查结构、内容与业务约束"]
    E --> F{"节点输出是否通过校验？"}

    F -- "通过，仍有后续节点" --> G["进入下一节点<br/>Runner 按 on_success 边更新状态并继续执行"]
    G --> D
    F -- "通过，工作流完成" --> I["最终验证<br/>使用最终 Schema 和 Final Validator 审查完整交付结果"]
    F -- "失败" --> H{"失败类型与剩余执行预算"}

    H -- "允许重试" --> D
    H -- "执行回退" --> R["切换回退节点<br/>进入 workflow.yaml 预先声明的 fallback 路径"]
    R --> D
    H -- "需要用户操作" --> U["暂停等待用户<br/>等待登录、验证码、确认或补充必要输入"]
    U -- "用户完成后恢复" --> D
    H -- "致命错误或预算耗尽" --> X["停止执行<br/>保存失败状态、错误类型和已完成的节点轨迹"]

    I --> V{"最终结果是否通过验证？"}
    V -- "失败" --> H
    V -- "通过" --> J["交付结果<br/>返回经过验证的最终输出和可追踪的完成状态"]
    J --> K["记录受控学习事件<br/>从本次运行提炼一条脱敏、限定范围的经验或教训"]
    K --> M{"学习事件是否达到压缩阈值？"}
    M -- "未达到" --> N["结束运行<br/>保留当前账本并等待下一次 Skill 调用"]
    M -- "达到" --> L["归档与压缩<br/>完整归档原始事件，并将活跃规则压缩到配置上限"]
    L --> N
```

图中的关键术语：

- `workflow.yaml`：Skill 的工作流定义文件，声明入口节点、节点属性、成功路径、回退路径和全局执行限制；
- Schema：JSON 数据契约，用于限定输入或输出必须包含的字段、类型、取值范围和附加属性；
- Validator：Schema 之外的确定性检查程序，用于验证跨字段关系、业务规则或最终结果质量；
- 状态 ID：一次 Skill 运行的唯一标识，用于保存当前节点、重试次数、确认记录、节点结果和执行轨迹；
- `on_success`：当前节点通过验证后允许进入的下一节点；工作流完成时指向完成状态；
- `fallback`：当前节点重试耗尽或明确要求降级时进入的预定义回退节点；
- 用户等待状态：需要登录、验证码、授权确认或补充输入时使用的暂停状态，用户完成操作后由 Runner 恢复；
- Learning ledger：保存脱敏学习事件的结构化账本；原始事件在压缩前完整归档，活跃规则只保留受限的运行上下文；

## 执行器优先级

执行器优先级用于设计工作流节点；工作流作者应当选择能够可靠完成任务的最高优先级执行器，并把选择结果固定在 `workflow.yaml` 中；Runner 不会在运行时让 Agent 自由切换执行器；

1. **`script`**：适合固定、重复、可计算且能够完全参数化的机械操作，例如格式转换、字段清洗、排序、聚合和确定性文件生成；脚本通过结构化文件接收输入并写出输出，由 Runner 使用参数数组和 `shell=false` 直接执行；脚本结果仍需通过节点输出 Schema 和可选 Validator；
2. **`mcp`**：适合已经提供结构化工具名称、参数和返回值的外部能力，例如数据库查询、服务 API、文件系统连接器或业务系统操作；节点必须声明具体 action 和参数来源，Agent 只负责发起当前允许的调用并提交返回结果；涉及写入或破坏性副作用时仍需经过用户确认；
3. **`browser-dom`**：适合缺少稳定 API 或 MCP、但网页仍能通过 DOM 元素、可访问性树或语义选择器可靠操作的场景；执行应优先读取结构化页面状态、定位明确元素并保留必要证据；页面登录、动态加载和布局变化必须通过超时、停止条件和回退路径处理；
4. **`computer-use`**：适合无法通过 API、MCP 或 DOM 完成，只能依据屏幕视觉状态操作桌面应用或复杂网页的场景；这种执行方式容易受到分辨率、布局、弹窗和焦点变化影响，因此节点必须缩小操作范围并设置严格停止条件；登录、验证码、扫码、双重认证和敏感确认由用户亲自完成；
5. **`reasoning`**：适合无法通过规则或脚本确定的语义判断，例如解释歧义、比较非结构化证据、归纳结论或生成面向用户的说明；推理节点只能在声明的输入、工具、输出 Schema 和停止条件内工作；它不能自行扩大任务范围、改变工作流顺序或绕过最终验证；

## 仓库结构

当前项目包含“模板工厂仓库”和“生成后的单 Skill 仓库”两个层次；模板工厂负责维护生成器、通用运行时和回归测试；`template/` 目录中的素材经过占位符替换后，才会组成一个新的独立 Skill 仓库；

GitHub 的代码块可以稳定显示树形缩进和同行注释，但不支持让代码块内部的单个文件夹独立展开；以下结构保持完全展开，便于搜索文件名、复制路径和逐项审计；

### 模板工厂仓库：AIALRA-SKILL-TEMPLATE

```text
AIALRA-SKILL-TEMPLATE/                                      # 模板工厂仓库根目录；维护生成协议、素材、测试和文档；
├── .git/                                                   # 当前模板工厂自身的 Git 元数据目录；不复制到新 Skill；
├── .github/                                                # 模板工厂在 GitHub 上使用的自动化配置目录；
│   ├── dependabot.yml                                      # 每周检查 GitHub Actions 引用版本，并以 dependencies、security 标签创建更新 PR；
│   └── workflows/                                          # GitHub Actions 工作流目录；
│       └── validate.yml                                    # 在 main 推送和 PR 上生成临时 Skill、运行完整测试、扫描当前文件与全部 Git 历史；
├── docs/                                                   # 模板设计、维护和迁移文档目录；
│   ├── architecture.md                                     # 定义 Workflow IR 字段、Runner 状态转换、外部执行器协议、核心锁和草稿安全边界；
│   ├── learning.md                                         # 定义学习事件格式、脱敏范围、归档顺序、活跃规则上限和人工晋升门槛；
│   ├── maintenance.md                                      # 定义 PATCH、MINOR、MAJOR 判断方式，以及 Draft、Candidate、Stable、Deprecated 生命周期；
│   ├── migration-v0.2.md                                  # 将旧 catalog、profile 和共享 eval 结构逐项映射到独立仓库与 workflow.yaml；
│   └── research-notes.md                                  # 记录规范来源、关键设计依据、链接和最近一次人工复核日期；
├── scripts/                                                # 模板工厂自身的命令行工具目录；
│   ├── check_secrets.py                                    # 逐个读取文本文件，匹配常见令牌和私钥模式，仅报告规则与位置并隐藏实际命中值；
│   ├── create_skill_repo.py                                # 校验名称和描述，渲染全部占位符，冻结核心，验证草稿并初始化独立 Git 仓库；
│   └── validate_template.py                                # 检查必需素材、Python 语法和废弃目录，再试生成仓库并拒绝残留占位符；
├── template/                                               # 创建新 Skill 时复制和渲染的完整仓库素材目录；
│   ├── .agents/                                            # Agent Skill 的发现与运行文件目录；
│   │   └── skills/                                         # Skill 定义集合目录；生成仓库只保留一个 Skill；
│   │       └── __SKILL_NAME__/                             # Skill 名称占位目录；生成时替换为实际名称；
│   │           ├── agents/                                 # Agent 产品界面和调用提示元数据目录；
│   │           │   └── openai.yaml.tmpl                    # 生成 display_name、short_description 和 default_prompt，供兼容的 Agent 产品展示和调用；
│   │           ├── schemas/                                # 默认 JSON 输入输出契约目录；
│   │           │   ├── input.schema.json                   # 只接受 request 字符串的安全草稿入口契约；配置领域工作流时必须具体化；
│   │           │   └── output.schema.json                  # 只允许 not-configured 状态的安全草稿输出契约；防止通用模板伪装成成品；
│   │           ├── scripts/                                # 每个 Skill 自带的确定性运行时脚本目录；
│   │           │   ├── compact.py                          # 先写入内容寻址 JSONL 归档，再合并重复规则、限制活跃数量并安全截断热账本；
│   │           │   ├── freeze_core.py                      # 枚举稳定核心文件并写入 SHA-256 清单；--check 模式只比较且不修改文件；
│   │           │   ├── learn.py                            # 校验终态和核心锁，脱敏一句经验，保证每个 state_id 最多记录一次并触发压缩；
│   │           │   ├── promote.py                          # 检查支持事件数量并生成包含全部未完成审查门槛的提案文件；不写入稳定核心；
│   │           │   ├── runner.py                           # 创建和持久化运行状态，执行脚本节点，发出外部指令并控制校验、重试、回退和完成；
│   │           │   ├── runtime_lib.py                      # 集中实现 JSON 读写、Schema 子集、路径限制、工作流验证、状态文件和核心哈希计算；
│   │           │   └── validate_repo.py                    # 汇总检查名称、SKILL 元数据、UI 元数据、工作流图、学习文件和核心锁一致性；
│   │           ├── SKILL.md.tmpl                           # 生成薄指令文件；声明触发边界、Runner 命令、外部节点提交方式和受控学习要求；
│   │           └── workflow.yaml.tmpl                      # 提供 configured=false 的单节点草稿；领域设计和测试完成前 Runner 拒绝启动；
│   ├── .github/                                            # 新 Skill 仓库的 GitHub 自动化素材目录；
│   │   ├── dependabot.yml                                  # 每周检查生成仓库的 GitHub Actions 引用，创建独立依赖更新 PR；
│   │   └── workflows/                                      # 新 Skill 仓库的 CI 工作流目录；
│   │       └── validate.yml                                # 在 main 推送和 PR 上验证工作流与核心锁、运行测试、扫描文件并检查全部 Git 历史；
│   ├── learning/                                           # 新 Skill 仓库的受控学习数据目录；
│   │   ├── archive/                                        # 完整保存已压缩批次的原始学习事件；
│   │   │   └── .gitkeep                                    # 空占位文件；首个归档批次产生前仍让 archive/ 目录进入初始提交；
│   │   ├── proposals/                                      # 保存待人工审查的核心晋升提案；
│   │   │   └── .gitkeep                                    # 空占位文件；首个晋升提案产生前仍让 proposals/ 目录进入初始提交；
│   │   ├── active-rules.json                               # 初始化规则数组、已处理归档和活跃上限；Runner 只读取其中受限的 advisory 内容；
│   │   └── ledger.jsonl                                    # 以每行一个 JSON 对象保存未压缩原始事件；压缩成功后按批次移入 archive/；
│   ├── scripts/                                            # 新 Skill 仓库的根级验证入口目录；
│   │   ├── check_secrets.py                                # 扫描生成仓库当前文本文件，忽略运行产物，只输出脱敏后的命中位置和规则名；
│   │   └── validate.py                                     # 确认 .agents/skills/ 下只有一个 Skill，再把参数原样交给 validate_repo.py；
│   ├── tests/                                              # 新 Skill 仓库的默认测试目录；
│   │   └── test_runtime.py                                 # 验证草稿图、核心锁、Schema 拒绝未知字段，以及脱敏器移除邮箱、URL 和长编号；
│   ├── .gitignore                                          # 阻止环境文件、私钥、Cookie、会话、.runtime/、虚拟环境和扫描报告进入 Git；
│   ├── .gitleaks.toml                                      # 继承 Gitleaks 内置规则，使 CI 能扫描当前内容和完整历史中的凭据；
│   ├── .pre-commit-config.yaml                             # 注册本地 validate-skill 与 check-sensitive-data 两个提交前钩子；
│   ├── AGENTS.md.tmpl                                      # 写入仓库级长期约束，包括稳定核心、执行顺序、学习边界和必跑检查；
│   ├── CHANGELOG.md.tmpl                                   # 创建 0.1.0 Unreleased 条目，供领域配置和后续发布持续记录；
│   ├── README.md.tmpl                                      # 指导维护者配置草稿、冻结核心、启动 Runner、推进状态和记录学习；
│   ├── SECURITY.md.tmpl                                    # 禁止提交凭据和会话，说明登录归用户完成，并声明核心锁与确认机制的真实边界；
│   └── VERSION                                             # 写入新 Skill 初始版本 0.1.0；冻结核心时该值进入哈希清单；
├── tests/                                                  # 模板工厂的端到端回归测试目录；
│   └── test_template_runtime.py                            # 生成临时仓库并覆盖草稿拒绝、脚本执行、禁止跳步、重试回退、确认、学习压缩和扫描绕过；
├── .editorconfig                                           # 要求 UTF-8、LF、文件末尾换行，并为 Python、JSON、YAML 和 Markdown 统一缩进；
├── .gitignore                                              # 阻止凭据目录、会话、.runtime/、虚拟环境、缓存和本地报告进入模板历史；
├── .gitleaks.toml                                          # 继承 Gitleaks 默认检测规则，供本地或 CI 检查模板完整 Git 历史；
├── .pre-commit-config.yaml                                 # 在提交前调用模板生成验证和按文件敏感信息扫描，失败时阻止提交；
├── AGENTS.md                                               # 向维护 Agent 声明单模板边界、必跑命令、运行不变量、学习不变量和安全禁令；
├── CHANGELOG.md                                            # 按版本记录架构变更；保留 v0.1 catalog 设计与 v0.2 Runtime 重构的历史；
├── CONTRIBUTING.md                                         # 要求每次模板变更说明不变量、补充成功与失败测试、评估 SemVer 并更新变更记录；
├── README.md                                               # 面向人类维护者解释设计原因、Runtime 流程、全部文件职责和新仓库生成方法；
├── SECURITY.md                                             # 记录敏感信息禁令、运行时防线、Gitleaks 层级、核心锁限制和泄漏响应步骤；
└── VERSION                                                 # 记录模板工厂当前版本 0.2.0；用于发布、标签和迁移判断；
```

### 生成后的单 Skill 仓库：my-skill

```text
my-skill/                                                   # 一个可以独立测试、发布和回滚的 Skill 仓库根目录；
├── .git/                                                   # 新 Skill 自己的 Git 元数据和完整版本历史；
├── .agents/                                                # Agent Skill 的发现与运行文件目录；
│   └── skills/                                             # Skill 定义目录；此仓库只包含一个子目录；
│       └── my-skill/                                       # 当前 Skill 的稳定核心目录；
│           ├── agents/                                     # Agent 产品界面和调用提示元数据目录；
│           │   └── openai.yaml                             # 保存显示名称、短描述和默认调用提示；支持该格式的 Agent 产品读取它展示 Skill；
│           ├── schemas/                                    # 节点和最终结果的 JSON 数据契约目录；
│           │   ├── input.schema.json                       # 限定首次 start 接收的数据字段与类型；草稿只收 request，领域配置时必须收窄；
│           │   └── output.schema.json                      # 限定 completed 状态允许交付的数据结构；草稿只允许 not-configured 结果；
│           ├── scripts/                                    # Skill 自带的确定性运行时脚本目录；
│           │   ├── compact.py                              # 达到阈值时先无损写入内容寻址归档，再合并计数、限制活跃规则并清理已归档账本；
│           │   ├── freeze_core.py                          # 将稳定核心文件路径、版本和 SHA-256 写入 .core-lock.json，或只读检查漂移；
│           │   ├── learn.py                                # 只接受完成、失败或用户暂停状态；脱敏一句经验并阻止同一状态重复记账；
│           │   ├── promote.py                              # 将高支持规则写成待审提案，并列出反例、测试、版本、人工批准和重新冻结门槛；
│           │   ├── runner.py                               # 唯一流程控制入口；创建状态、执行 script、暂停外部节点并验证每次提交结果；
│           │   ├── runtime_lib.py                          # 实现原子 JSON 写入、安全相对路径、Schema 子集、图验证、状态存取和核心哈希；
│           │   └── validate_repo.py                        # 一次性汇总检查 Skill 元数据、工作流图、学习文件、活动规则上限和核心锁；
│           ├── SKILL.md                                    # 告诉 Agent 何时触发该 Skill、如何调用 Runner、怎样提交外部结果和记录学习；
│           └── workflow.yaml                               # Skill 的执行事实来源；固定入口节点、执行器、Schema、超时、重试、回退和完成边；
├── .github/                                                # 当前 Skill 的 GitHub 自动化配置目录；
│   ├── dependabot.yml                                      # 每周读取 workflow 中的 Actions 引用并创建依赖升级 PR，不直接修改运行核心；
│   └── workflows/                                          # 当前 Skill 的 CI 工作流目录；
│       └── validate.yml                                    # 在 PR 和 main 推送时检查 configured 状态、核心锁、测试、工作区敏感值和全部提交历史；
├── learning/                                               # 当前 Skill 的受控成长数据目录；
│   ├── archive/                                            # 无损保存已处理批次的完整原始事件；
│   │   └── .gitkeep                                        # 初始空占位；确保 archive/ 在首个达到配置阈值的批次产生前已经受 Git 管理；
│   ├── proposals/                                          # 保存尚未进入稳定核心的晋升提案；
│   │   └── .gitkeep                                        # 初始空占位；确保 proposals/ 在首个晋升建议产生前已经受 Git 管理；
│   ├── active-rules.json                                   # 保存压缩后的有限规则、正负支持计数和已处理归档；Runner 将其作为 advisory 注入；
│   └── ledger.jsonl                                        # 每次运行追加一个脱敏 JSON 事件；达到阈值并成功归档后移除对应热数据；
├── scripts/                                                # 面向维护者和 CI 的根级命令目录；
│   ├── check_secrets.py                                    # 遍历当前文本文件并匹配常见 Token、访问密钥和私钥头；输出始终隐藏实际值；
│   └── validate.py                                         # 校验仓库恰有一个 Skill，并把 --allow-draft 或 --ignore-core-lock 传给内部验证器；
├── tests/                                                  # 当前 Skill 的测试目录；领域测试应继续添加到这里；
│   └── test_runtime.py                                     # 初始验证图结构、锁清单、Schema 拒绝未知字段和学习脱敏；领域作者继续增加成功与失败案例；
├── .core-lock.json                                         # Runner 每次启动和恢复前比较的稳定核心快照；检测未冻结的脚本、Schema 或工作流修改；
├── .gitignore                                              # 排除环境变量文件、密钥、Cookie、会话、.runtime/、虚拟环境、缓存和扫描报告；
├── .gitleaks.toml                                          # 让 Gitleaks 在 CI 中使用内置规则扫描所有提交，同时由当前仓库维护额外配置；
├── .pre-commit-config.yaml                                 # 在开发者提交前先执行完整仓库验证，再对本次文件运行脱敏敏感信息扫描；
├── AGENTS.md                                               # 长期约束 Agent 的节点顺序、核心修改流程、学习写入范围、确认要求和必跑检查；
├── CHANGELOG.md                                            # 按语义版本记录触发边界、输入输出、权限、节点和实现的用户可见变化；
├── README.md                                               # 提供该具体 Skill 的领域说明、配置步骤、启动命令、状态推进和学习操作；
├── SECURITY.md                                             # 声明禁止进入 Git 的数据、登录责任、用户确认要求、核心锁局限和凭据泄漏响应；
└── VERSION                                                 # 当前 Skill 的语义版本；核心冻结时写入清单，发布标签应与它保持一致；
```

### 领域需要时添加的可选目录

```text
.agents/skills/my-skill/                                    # 当前 Skill 的稳定核心目录；
├── executors/                                              # 保存领域专用 script 节点实现；每个脚本应使用结构化输入输出并拥有对应测试；
├── validators/                                             # 保存跨字段、跨节点或业务语义检查程序；退出码决定节点结果是否可接受；
├── references/                                             # 保存推理节点明确引用的稳定知识；只按任务需要加载，避免全部进入上下文；
└── assets/                                                 # 保存交付模板、固定图片或静态资源；不得存放凭据、会话或未经脱敏的用户数据；
```

这些目录不由生成器预先创建；领域工作流确实需要时再添加，并在对应节点、测试和维护文档中声明用途；

## 创建独立 Skill 仓库

```bash
python3 scripts/create_skill_repo.py \
  --name shopping-price-research \
  --output ../shopping-price-research \
  --display-name "Shopping Price Research" \
  --short-description "Compare live prices with verified evidence" \
  --description "Research current product offers with direct evidence. Use when the user asks for live price comparison or link verification. Do not use for purchasing actions or historical-price prediction." \
  --default-prompt 'Use $shopping-price-research to compare current offers for this exact product.'
```

生成器会：

- 优先调用 Codex 内置 `skill-creator` 官方初始化器；
- 创建新的独立 Git 仓库；
- 写入统一 Runner、学习系统、安全策略、测试和 CI；
- 生成核心 SHA-256 锁；
- 让工作流保持 `configured=false`，在领域图和回归测试完成前拒绝运行；

## 固化与成长

稳定核心包括工作流、Schema、脚本、验证器、Skill 指令、安全策略和强制执行文件；`.core-lock.json` 记录它们的哈希；任何未登记变更都会让 Runner 硬停止；

每次执行后只记录一条脱敏、限定 scope 的经验或教训；默认累计 32 条时：

- 原始事件完整移动到 `learning/archive/`，不依赖“已经提交到 Git”才保留；
- 重复规则被确定性合并，保留正负计数和事件哈希；
- 活跃规则最多 16 条，即活跃上下文减半；
- 未进入活跃集合的事件仍在归档和 Git 历史中，不丢失；
- 学习规则只能作为 advisory，不能改变流程、权限或安全边界；

晋升到核心只生成 proposal，不自动修改核心；至少需要 3 个独立支持案例，或一次用户确认的严重安全事件，并完成反例审查、回归测试、版本变更、人工批准和重新冻结；

## 验证模板自身

```bash
python3 scripts/validate_template.py
python3 -m unittest discover -s tests -v
python3 scripts/check_secrets.py
```

详细协议见 [docs/architecture.md](docs/architecture.md)，学习机制见 [docs/learning.md](docs/learning.md)，从 v0.1 迁移见 [docs/migration-v0.2.md](docs/migration-v0.2.md)；
