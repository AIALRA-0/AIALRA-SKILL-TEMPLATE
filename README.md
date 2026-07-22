# AIALRA-SKILL-TEMPLATE

## 这份文件能帮你做什么

这份文件回答两个问题：这个仓库是什么，以及怎样创建第一个 Skill 仓库；

适合阅读这份文件的人：

- 第一次接触本模板的人；
- 准备创建新 Skill 的人；
- 想先看懂整体结构，再决定是否继续的人；

读完以后，你应该能够生成一个安全草稿仓库，并知道下一步该阅读哪份文档；

你现在不需要理解 Runner、Schema、validator 或状态机；这些概念会在后续文档中逐个解释；

## 先用一句话理解这个仓库

这个仓库是一台“Skill 仓库生成器”；

你提供 Skill 的名称、用途和界面文字，生成器会创建一个新的独立 Git 仓库；新仓库已经包含运行框架、测试、安全检查和学习边界；

生成结果默认处于安全草稿状态；完成领域工作流和测试前，它不会执行真实任务；

## Skill 是什么

Skill 是一组围绕明确任务组织起来的指令和资源；

一个 Skill 通常包含：

- 触发说明；
- 执行步骤；
- 输入和输出规则；
- 可重复使用的脚本；
- 结果检查程序；
- 安全边界；
- 测试；

本模板坚持一个仓库只保存一个 Skill；这样可以让版本、权限、测试和回滚保持独立；

## 模板仓库和生成仓库有什么区别

你会接触两种仓库；

| 仓库 | 用途 | 谁来修改 |
|---|---|---|
| 当前模板仓库 | 保存通用生成器和 Runtime； | 模板维护者； |
| 生成后的 Skill 仓库 | 保存某一个具体 Skill； | 该 Skill 的维护者； |

当前仓库的 `template/` 目录保存生成素材；运行生成器后，这些素材会进入新的独立仓库；

生成仓库必须放在当前模板仓库之外；这样可以避免两个 Git 历史互相嵌套；

## 创建第一个 Skill 仓库

### 第一步：准备五项信息

创建前先准备：

1. Skill 名称；
2. 一句完整用途说明；
3. 界面显示名称；
4. 界面短描述；
5. 默认调用提示；

Skill 名称只使用小写字母、数字和连字符；例如 `example-research-skill`；

用途说明需要同时写清适用请求和排除范围；这样可以减少错误触发；

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

命令中的 `../example-research-skill` 表示把新仓库创建在当前仓库旁边；

示例文字需要替换成真实 Skill 信息；名称改变时，`$example-research-skill` 也要改成相同名称；

### 第三步：确认生成成功

成功后，命令会返回新仓库路径和 Skill 名称；

新目录中应当包含：

```text
example-research-skill/
├── .agents/skills/example-research-skill/
├── learning/
├── scripts/
├── tests/
├── AGENTS.md
├── README.md
├── SECURITY.md
└── VERSION
```

生成器还会初始化独立 Git 仓库，并创建第一份核心锁；

## 为什么新仓库暂时不能运行

新仓库的 `workflow.yaml` 包含：

```json
{
  "definition": {
    "configured": false
  }
}
```

`false` 表示领域流程尚未配置完成；Runner 会拒绝启动真实任务；

把它改成 `true` 以前，需要完成：

1. 定义支持范围和排除范围；
2. 定义全部工作流节点；
3. 定义每个节点的输入和输出；
4. 添加成功和失败测试；
5. 完成安全检查；
6. 重新生成核心锁；

生成仓库自己的 `README.md` 会逐步解释这些操作；

## 这个模板会替你守住什么

模板内置以下约束：

- Runner 控制节点顺序和状态转换；
- Schema 检查输入和输出结构；
- validator 执行额外的确定性检查；
- 重试、回退和超时都有限制；
- 写入和破坏性操作需要用户确认；
- 稳定核心由 SHA-256 清单检测漂移；
- 学习内容只能写入 `learning/`；
- 敏感信息扫描会在本地和 CI 中执行；

这些名称暂时看不懂也没有关系；阅读路线会在需要时引导你进入对应解释；

## 这个模板的边界

模板负责生成运行框架和强制检查；

具体 Skill 仍需由维护者定义：

- 真实任务范围；
- 领域工作流；
- 工具和权限；
- 输入输出 Schema；
- 领域测试；
- 结果质量标准；

身份验证、验证码、扫码和双重认证由用户亲自完成；真实凭据和浏览器会话不能写入 Git；

## 接下来应该读什么

根据你的目标选择一份文档；

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

第一次阅读时，建议只打开与你当前目标对应的一份文档；

## 验证模板自身

模板维护者修改当前仓库后，需要运行：

```bash
python3 scripts/validate_template.py
python3 -m unittest discover -s tests -v
python3 scripts/check_secrets.py
```

三条命令的用途、成功输出和失败处理由 [贡献指南](CONTRIBUTING.md) 逐步解释；
