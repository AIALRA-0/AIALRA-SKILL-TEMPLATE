# Workflow 精确参考

## 这份文件能帮你做什么

这份文件用于查询 `workflow.yaml` 的字段、允许值、状态和 Runner 命令；

适合阅读这份文件的人：

- 正在填写 `workflow.yaml` 的维护者；
- 正在实现 executor 或 validator 的开发者；
- 正在核对 Runtime 行为的审计者；

读完以后，你应该能够写出结构合法的工作流，并知道每种状态下一步允许调用什么；

如果你还没有理解整体运行过程，先阅读 [架构入门](architecture.md)；

## 文件格式

文件名固定为 `workflow.yaml`；

当前 Runtime 使用 Python 标准库 JSON 解析器读取它；因此实际文件必须采用兼容 JSON 的 YAML 写法；

实际文件不能包含注释；本文使用 `jsonc` 代码块和同行注释解释字段；

## 顶层分类

顶层只允许三个大分类：

| 分类 | 保存什么 |
|---|---|
| `definition` | 协议版本、Skill 名称和配置状态； |
| `execution` | 运行限制、节点图和最终校验； |
| `learning` | 学习事件的压缩设置； |

具体条目必须进入对应的二级或三级分类；顶层散项和未知分类会被验证器拒绝；

## 顶层完整结构

```jsonc
{
  "definition": { // 工作流身份、协议版本和配置状态；
    "ir_version": 2, // 当前 Workflow IR 版本；只接受整数 2；
    "skill_name": "example-skill", // 必须与 .agents/skills/ 下的目录名一致；
    "configured": true // true 表示可以运行；false 表示安全草稿；
  },
  "execution": { // 单次运行使用的设置；
    "limits": { // 全局资源边界；
      "max_nodes": 16, // 最多成功完成的节点数量；允许 1 到 64；
      "total_timeout_seconds": 1800 // 整次运行的最长秒数；允许 1 到 86400；
    },
    "graph": { // 入口和节点集合；
      "entry_node": "process-input", // 第一个节点的 ID；
      "nodes": [] // 节点数组；实际文件至少包含一个节点；
    },
    "completion": { // 到达完成边后的最终检查；
      "output_schema": "schemas/output.schema.json", // 最终输出 Schema 的安全相对路径；
      "validator": null // 最终 validator 的 argv 数组；不需要时使用 null；
    }
  },
  "learning": { // 受控学习设置；
    "compaction": { // 归档和活跃规则限制；
      "compact_every": 32, // 累计多少条事件后触发压缩；允许 4 到 1000；
      "active_rule_limit": 16 // 活跃规则上限；允许 1 到 500，且不能超过阈值一半；
    }
  }
}
```

## `definition` 分类

### `definition.ir_version`

这个字段表示工作流协议版本；

当前值固定为整数 `2`；不兼容的结构变化需要升级版本；

值错误时，验证器拒绝整个工作流；

### `definition.skill_name`

这个字段是 Skill 的稳定名称；

它必须与 `.agents/skills/` 下唯一 Skill 目录的名称完全一致；

名称不一致时，验证器拒绝工作流；

### `definition.configured`

这个布尔值表示领域工作流是否完成配置；

- `false` 表示安全草稿；Runner 拒绝真实执行；
- `true` 表示领域节点、Schema 和测试已经完成；Runner 可以继续检查其他启动条件；

新生成仓库默认使用 `false`；

## `execution.limits` 分类

### `max_nodes`

这个整数限制一次运行最多完成多少个节点；允许范围为 1 到 64；

节点数组长度不能超过该值；运行期间完成数量达到上限时，Runner 停止；

### `total_timeout_seconds`

这个整数限制整次运行从 `started_at` 开始可以持续多少秒；允许范围为 1 到 86400；

超过总时限时，Runner 停止继续推进；

## `execution.graph` 分类

### `entry_node`

这个字符串指定第一个节点；

它必须等于 `nodes` 数组中某个节点的 `id`；

入口不存在时，验证器拒绝工作流；

### `nodes`

这个数组保存全部节点对象；

数组至少包含一个节点；所有节点都必须从入口沿成功边或回退边到达；

不可达节点和环路会被验证器拒绝；重复执行使用 `max_retries` 表达；

## 一个完整脚本节点

```jsonc
{
  "id": "process-input", // 当前工作流中的唯一节点 ID；
  "input_schema": "schemas/input.schema.json", // 节点输入 Schema；
  "output_schema": "schemas/output.schema.json", // 节点输出 Schema；
  "executor": "script", // 执行器类型；
  "command": [ // Runner 直接启动的 argv 数组；
    "python3",
    "executors/process.py",
    "--input",
    "${input_file}",
    "--output",
    "${output_file}"
  ],
  "side_effect": "none", // 对外部状态的影响类别；
  "requires_confirmation": false, // 执行前是否需要用户确认；
  "timeout_seconds": 60, // 单次尝试的最长秒数；
  "max_retries": 1, // 首次失败后最多重试几次；
  "validator": null, // 额外 validator argv；不需要时使用 null；
  "fallback": null, // 失败后的替代节点；不需要时使用 null；
  "on_success": "__complete__", // 成功后的节点或完成边；
  "stop_conditions": [] // 外部协议停止条件；没有时使用空数组；
}
```

## 一个完整外部节点

```jsonc
{
  "id": "lookup-record", // 当前工作流中的唯一节点 ID；
  "input_schema": "schemas/query.schema.json", // 节点输入 Schema；
  "output_schema": "schemas/records.schema.json", // 节点输出 Schema；
  "executor": "mcp", // 由 Agent 或宿主执行的外部能力；
  "action": { // Runner 返回给 Agent 的动作契约；
    "name": "records.lookup", // 固定动作名称；
    "arguments": { // 固定参数或参数来源；
      "query_from": "node-input"
    }
  },
  "side_effect": "read", // 只读取外部数据；
  "requires_confirmation": false, // 读取节点不强制确认；
  "timeout_seconds": 120, // 等待外部结果的最长秒数；
  "max_retries": 2, // 首次失败后最多重试两次；
  "validator": null, // 不运行额外 validator；
  "fallback": "manual-review", // 重试耗尽后进入替代节点；
  "on_success": "prepare-result", // 成功后进入下一节点；
  "stop_conditions": [ // Agent 必须检查的文字条件；
    "无法访问必需数据源时报告 fallback；",
    "出现身份验证要求时报告 user-required；"
  ]
}
```

示例动作名称和参数仅用于说明结构；具体 Skill 必须替换成真实、经过测试的外部契约；

## 节点字段逐项说明

### `id`

`id` 使用小写 kebab-case 标识节点；例如 `process-input`；

同一工作流中不能重复；

### `input_schema`

该字段指向节点接收数据的 JSON Schema 文件；

Runner 在节点执行前检查输入；路径必须位于当前 Skill 目录内；

### `output_schema`

该字段指向节点产出数据的 JSON Schema 文件；

Runner 在状态转换前检查输出；路径必须位于当前 Skill 目录内；

### `executor`

该字段固定当前节点使用哪一种执行器；运行期间不能替换；

允许值：

| 值 | 谁执行 | 用途 |
|---|---|---|
| `script` | Runner； | 固定、重复和可以计算的操作； |
| `mcp` | Agent 或宿主； | 具有工具名称和结构化参数的外部能力； |
| `browser-dom` | Agent 或宿主； | 通过 DOM 或可访问性结构操作页面； |
| `computer-use` | Agent 或宿主； | 依据屏幕状态操作无法结构化控制的界面； |
| `reasoning` | Agent； | 对无法由固定规则计算的内容进行语义判断； |

验证器拒绝其他值；

### `command`

`command` 只用于 `script` 节点；

它保存 argv 数组；argv 是传给程序的一组命令行参数；数组中的每个字符串都是一个独立参数；

```json
{
  "command": [
    "python3",
    "executors/process.py",
    "--input",
    "${input_file}",
    "--output",
    "${output_file}"
  ]
}
```

Runner 会把 `${input_file}`、`${output_file}` 和 `${skill_dir}` 替换为当前运行的真实路径；

未知占位符会触发错误；空数组、空字符串和控制字符会被拒绝；

### 为什么使用 `shell=false`

Runner 使用 argv 数组直接启动程序，并设置 `shell=false`；

命令不会经过 Bash 或 Zsh；管道符 `|`、重定向符 `>`、通配符 `*` 和命令替换符 `$()` 不会被 Shell 自动解释；

这样可以保持参数边界，减少命令拼接和输入注入风险；

### `action`

`action` 用于所有非 `script` 节点；

它至少包含：

- `name`：非空、单行的动作名称；
- `arguments`：JSON 对象形式的动作参数或参数来源；

Runner 把该对象原样放入外部指令；Agent 或宿主只能执行该动作；

### `side_effect`

该字段表示节点会对工作流之外的数据或系统产生什么影响；

| 值 | 一句话解释 |
|---|---|
| `none` | 节点只处理已经提供的输入，不读取或改变外部数据； |
| `read` | 节点读取外部现有数据，并保持外部状态不变； |
| `write` | 节点创建或更新外部数据，执行前必须取得用户确认； |
| `destructive` | 节点删除、覆盖、撤销或执行其他难以恢复的变更，执行前必须取得用户确认； |

### `requires_confirmation`

这个布尔值表示节点执行前是否需要用户明确同意；

`write` 和 `destructive` 必须使用 `true`；

值为 `true` 时，Runner 先进入 `waiting-confirmation`；

### `timeout_seconds`

这个整数限制单次节点尝试的最长秒数；允许范围为 1 到 3600；

脚本超时或外部等待超时会进入失败处理；

### `max_retries`

这个整数表示首次失败以后最多可以再次执行几次；允许范围为 0 到 10；

值为 `0` 表示不重试；

### `validator`

这个字段保存额外确定性校验程序的 argv 数组；

不需要额外校验时必须声明为 `null`；

validator 返回非零退出码时，节点输出被视为失败；

### `fallback`

这个字段指定失败后的替代节点 ID；

不需要回退时必须声明为 `null`；

它不能使用 `__complete__`；失败结果必须先经过真实节点输出和最终校验；

### `on_success`

这个字段指定节点输出通过检查后进入哪里；

它可以指向另一个节点 ID，也可以使用 `__complete__` 进入最终校验；

### `stop_conditions`

这个数组保存外部执行器必须检查的文字条件；

一个节点可以有多个独立停止原因，因此每个数组元素只保存一个原因；没有附加条件时使用空数组；

Runner 不解析这些文字；Agent 或外部执行器判断条件是否出现，再通过 `fail` 报告；

能够由程序判断的停止规则必须写入 Schema、validator、超时、重试或确认检查；

| 层级 | 保存位置 | 谁检查 |
|---|---|---|
| 外部执行协议 | `stop_conditions`； | Agent 或外部执行器； |
| 机器强制规则 | Schema、validator 和 Runtime 限制； | Runner； |

## `execution.completion` 分类

### `output_schema`

这个字段指向最终输出的 JSON Schema；

到达 `__complete__` 后，Runner 使用它检查当前输出；

### `validator`

这个字段保存最终 validator 的 argv 数组；

不需要额外最终检查时使用 `null`；

最终 Schema 或 validator 失败时，工作流不能进入 `completed`；

## `learning.compaction` 分类

### `compact_every`

这个整数表示积累多少条学习事件后执行压缩；允许范围为 4 到 1000；

默认值为 32；

### `active_rule_limit`

这个整数限制活跃建议规则数量；允许范围为 1 到 500；

它不能超过 `compact_every` 的一半；默认值为 16；

## Runner 状态和命令

Runner 命令只在对应状态下有效；错误状态中的命令会被拒绝；

| 状态 | 当前发生了什么 | 下一条命令 | 命令效果 |
|---|---|---|---|
| `running` | 当前节点具备推进条件，节点尚未完成； | `advance`； | 脚本节点开始执行；外部节点返回动作并进入等待； |
| `waiting-confirmation` | 当前节点正在等待用户明确同意； | `approve`； | 记录确认并恢复为 `running`； |
| `waiting-external` | Runner 已返回外部动作，正在等待结果； | `submit` 或 `fail`； | 提交候选输出或报告失败； |
| `waiting-user` | 当前流程正在等待用户亲自完成必要操作； | `resume`； | 恢复为 `running`； |
| `completed` | 最终输出已经通过全部检查； | 无； | 交付结果并记录学习事件； |
| `failed` | 工作流已经失败并停止； | 无； | 保存错误和轨迹； |

### `start`

用途：使用入口 JSON 创建新状态；

```bash
python3 scripts/runner.py start --input "input.json"
```

成功时返回 `state_id`、当前状态和当前节点指令；

入口数据、工作流、草稿状态或核心锁不合法时返回错误；

### `advance`

用途：推进 `running` 状态中的当前节点；

```bash
python3 scripts/runner.py advance --state-id "真实状态编号"
```

脚本节点由 Runner 执行；外部节点返回结构化动作；需要确认时进入 `waiting-confirmation`；

### `approve`

用途：在用户真实同意后批准当前确认节点；

```bash
python3 scripts/runner.py approve \
  --state-id "真实状态编号" \
  --node-id "真实节点编号"
```

状态或节点不匹配时，Runner 拒绝批准；

### `submit`

用途：把外部动作产生的候选 JSON 交给 Runner 检查；

```bash
python3 scripts/runner.py submit \
  --state-id "真实状态编号" \
  --node-id "真实节点编号" \
  --output "output.json"
```

`submit` 不会直接宣布成功；Runner 仍会检查输出 Schema、validator 和完成条件；

### `fail`

用途：报告外部动作没有产生可接受结果；

```bash
python3 scripts/runner.py fail \
  --state-id "真实状态编号" \
  --node-id "真实节点编号" \
  --kind "retryable" \
  --message "声明的动作没有返回可用结果；"
```

允许的失败类型：

| `kind` | 含义 | Runner 处理 |
|---|---|---|
| `retryable` | 再次执行同一节点可能解决； | 在重试范围内重试，之后回退或失败； |
| `fallback` | 当前动作需要进入预设替代路径； | 进入 `fallback`，不存在时失败； |
| `user-required` | 必须等待用户亲自操作； | 进入 `waiting-user`； |
| `fatal` | 当前错误不允许继续； | 立即进入 `failed`； |

### `resume`

用途：用户完成必要操作后恢复 `waiting-user` 状态；

```bash
python3 scripts/runner.py resume --state-id "真实状态编号"
```

当前状态不是 `waiting-user` 时，Runner 拒绝恢复；

### `status`

用途：读取某次运行保存的完整状态；

```bash
python3 scripts/runner.py status --state-id "真实状态编号"
```

状态编号不存在或格式错误时返回错误；

## 外部节点提交示例

Runner 返回：

```json
{
  "state_id": "example-state-id",
  "status": "waiting-external",
  "node": {
    "id": "lookup-record",
    "executor": "mcp",
    "action": {
      "name": "records.lookup",
      "arguments": {
        "query": "example"
      }
    },
    "output_schema": "schemas/records.schema.json"
  }
}
```

Agent 或宿主只执行 `node.executor` 和 `node.action` 指定的动作；

假设输出 Schema 要求顶层包含 `records` 数组，`output.json` 可以写成：

```json
{
  "records": []
}
```

保存文件后调用 `submit`；Runner 校验成功后进入下一节点或最终验证；

外部动作无法产生合格 JSON 时调用 `fail`；

## 图结构规则

验证器会检查：

- `entry_node` 必须存在；
- 所有节点 ID 必须唯一；
- 所有成功边必须指向节点或 `__complete__`；
- 所有回退边必须指向真实节点；
- 所有节点必须从入口可达；
- 成功边和回退边不能形成环路；
- 节点数量不能超过 `max_nodes`；

任一规则失败时，工作流不能运行；

## 人工审计问题

审核 `workflow.yaml` 时回答：

1. 顶层是否只有三个分类；
2. 入口是否存在；
3. 每个节点是否写清输入、输出、执行器和失败路径；
4. 写入和破坏性节点是否要求确认；
5. 外部文字停止条件是否与机器强制规则分开；
6. 最终输出是否同时受到 Schema 和必要 validator 保护；
7. 所有路径是否可以结束，并且没有环路；

全部问题都能明确回答时，工作流才适合进入测试阶段；
