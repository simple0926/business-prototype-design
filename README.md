# business-prototype-design

一个面向业务软件的产品原型设计 Skill：从已有需求、PRD、流程图、截图或旧 HTML 出发，梳理角色、权限、状态和流程，形成页面规格，完成可交互原型，并把需求说明、验收证据和离线单文件 HTML 保持同步。

> 当前版本：`v0.1.0`。目前主要经过作者自己的真实项目验证，欢迎使用脱敏案例反馈问题。

## 解决什么问题

- 需求、流程图和原型经过多轮修改后互相对不上；
- 同一状态在不同角色下含义或操作不一致；
- 只有“能点”的原型，缺少字段限制、权限、异常反馈和验收依据；
- 已有 PRD、流程或旧原型，却被迫每次从头开始；
- 原型修改完成后，没有同步更新需求和交付说明。

它不是一次性的视觉效果图生成器，也不负责开发生产后端。

## 工作方式

Skill 会先识别现有材料成熟度，再选择合适的起点：

- **完整流程**：需求零散、矛盾或尚未确认；
- **快速原型**：业务基线已经确认，可以从页面规格或视觉实现开始；
- **增量修改**：已有原型，根据新反馈分析影响范围并回归验证。

完整流程包含八个阶段：

1. 资料盘点；
2. 需求分析；
3. 业务建模；
4. 流程确认；
5. 页面规格；
6. 视觉与交互实现；
7. 文档同步与打包；
8. 验证与交付。

阶段可以复用，质量门槛不能跳过。执行过程中会在 Codex 对话中用阶段进度板说明当前阶段、阻塞和下一步，不使用虚假的百分比进度。

## 目录结构

```text
business-prototype-design/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── acceptance-and-handoff.md
│   ├── page-specification.md
│   ├── process-and-gates.md
│   ├── product-design-integration.md
│   ├── requirements-analysis.md
│   ├── role-state-and-flow.md
│   └── standalone-html-contract.md
├── scripts/
│   ├── build-standalone.mjs
│   ├── validate-standalone-html.py
│   └── validate-traceability.py
└── assets/
    └── delivery-templates/
```

- `SKILL.md`：入口、模式判断、工作流与完成标准；
- `references/`：按阶段加载的详细规则；
- `scripts/`：单文件构建与交付校验；
- `assets/`：需求、页面规格和验收报告模板；
- `agents/openai.yaml`：Codex 中的展示和调用信息。

## 安装

下载或克隆整个仓库，不要只复制 `SKILL.md`。

个人安装：

```text
$HOME/.agents/skills/business-prototype-design/
```

仅在当前项目中使用：

```text
<项目目录>/.agents/skills/business-prototype-design/
```

确保 `SKILL.md` 直接位于上述目录内。安装后重新启动或刷新 Agent 工具；在 Codex 中可以使用 `$business-prototype-design` 显式调用。

Skill 的基本结构可参考 [OpenAI 官方 Skills 文档](https://developers.openai.com/plugins/build/skills)。

## 使用示例

从需求分析开始：

```text
使用 $business-prototype-design 分析这些 PRD、流程图和截图，先找出会影响实现的冲突，确认后再设计原型。
```

从页面规格开始：

```text
流程已经确认。使用 $business-prototype-design 从页面规格开始，完成可交互原型和单文件交付。
```

修改已有原型：

```text
使用 $business-prototype-design 按这轮反馈增量修改现有 HTML，并同步更新需求说明、流程和验收记录。
```

## Product Design 依赖

本 Skill 负责业务正确性：需求、角色、权限、状态、流程和页面规格。进入视觉与交互实现阶段后，会在可用时调用 Product Design 来确定视觉方向、实现页面并完成设计质量检查。

Product Design 不会随本仓库自动安装：

- 目标 Agent 具备 Product Design 或等价能力时，可以继续完整原型流程；
- 缺少等价能力时，业务分析与页面规格仍可使用，但视觉实现和设计验证会降级；
- 不支持 Agent Skills 的工具需要适配调用方式、文件引用和脚本执行规则。

## 交付物

根据起点和范围，交付物可以包括：

1. 需求分析与决策记录；
2. 角色、权限、状态、操作和流程模型；
3. 页面级原型规格；
4. 可运行的交互原型源码；
5. 原型内嵌需求说明；
6. 设计质量检查记录；
7. 验收报告与需求追溯；
8. 可离线打开的单文件 HTML。

## 已知边界

- 不代替真实业务负责人做最终决策；
- 不保证第一次生成的视觉就是最终稿；
- 复杂业务和跨 Agent 兼容性仍需要更多外部案例验证；
- 自动校验只能证明结构和部分行为正确，不能替代人工业务验收。

## 反馈

欢迎提交 Issue，说明：使用起点、已有材料、真正减少返工的步骤、遗漏或多余的问题，以及开发拿到交付物后仍需要补充的信息。

## License

[MIT](LICENSE)

