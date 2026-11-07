# business-prototype-design

[中文](#中文) · [English](#english)

## 中文

`business-prototype-design` 是一个用于业务软件的 AI Skill，把需求文档、截图、流程图、PRD 或旧原型，逐步转换为可追溯的页面规格、可运行交互原型和离线单文件交付物。

**当前公开版本：0.3**

## 0.3 解决了什么

0.2 建立了可恢复的八门状态机和结构化证据骨架；0.3 集中修复审计中发现的“格式通过但引用、文件或离线产物并不真实闭合”：

1. **证据文件可复核：** Evidence 绑定独立文件、SHA-256、字节数、媒体类型和执行摘要；需求/验收文档不能自证。
2. **引用与状态真正相连：** Page、Acceptance、Journey、Decision、Evidence 引用必须解析；上游失效向下游传播；确认记录带来源和 continuation gate。
3. **单文件交付更安全：** Builder 限制资产根目录，拒绝父目录/符号链接逃逸；Validator 拒绝静态 import、CSS `@import` 和 marker-only 空壳。
4. **小任务不再强制重流程：** 新增 Lite 模式和量化升级阈值；纯文本项目不再强制 evidence manifest。

0.3 仍保留八个质量门：

`P1 资料和证据检查` → `P2 需求分析` → `P3 角色、权限和状态` → `P4 业务流程` → `P5 页面详细说明` → `P6 可运行原型` → `P7 同步和离线打包` → `P8 验证与交付`

完整变化请阅读：

- [0.3 大白话更新说明](UPDATE_0.3_CN.md)
- [0.3 发布说明](RELEASE_NOTES_0.3_CN.md)
- [0.2 中文更新说明](UPDATE_HISTORY_CN.md)
- [Changelog](CHANGELOG.md)
- [各阶段后续验证所需材料](VALIDATION_MATERIALS_CN.md)

## 安装

### Codex

```bash
git clone https://github.com/simple0926/business-prototype-design.git
cp -R business-prototype-design ~/.codex/skills/business-prototype-design
```

使用通用 Agent Skills 目录时：

```bash
cp -R business-prototype-design ~/.agents/skills/business-prototype-design
```

如果本地已经安装旧版，请先备份旧目录，再用完整的 0.3 文件夹替换；不要只替换 `SKILL.md`。0.3 的最终工件 schema 为 `0.4`，旧项目先运行 migration audit。

## 使用

在支持 Skills 的 AI 工具中调用：

```text
$business-prototype-design
```

可以向它提供：

- 需求文档、PRD、技术指标或业务规则；
- 截图、流程图、页面草图或视觉参考；
- 已有原型、HTML、源码、测试和验收报告；
- 要修改的局部需求或旧项目。

Skill 会根据规模与材料完整度选择 Lite、Full、Fast 或 Incremental 模式，并从最早尚未满足的质量门开始。

## 验证公开包

```bash
python3 -m unittest discover -s tests -v
```

当前公开版包含 62 项契约测试。它们用于检查状态协议、需求追溯、证据绑定、关键业务旅程、离线文件、路径约束、Lite 阈值、golden sample、整包一致性和旧项目迁移体检。

完整包验收使用：

```bash
python3 scripts/validate-package.py \
  --workflow-state prototype-workflow-state.json \
  --requirements requirements-analysis.md \
  --prototype-spec prototype-spec.md \
  --acceptance acceptance-report.md \
  --evidence-register evidence-register.json \
  --standalone prototype-standalone.html \
  --baseline-version <baseline-version>
```

可执行完整样例见 [`examples/golden-sample`](examples/golden-sample)。

测试通过只能证明它所检查的文件结构、引用关系和证据绑定正确，不能单独证明业务规则、视觉结果、性能或真实外部系统行为正确。

## 目录结构

```text
business-prototype-design/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── RELEASE_NOTES_0.3_CN.md
├── UPDATE_HISTORY_CN.md
├── VALIDATION_MATERIALS_CN.md
├── agents/
├── assets/
├── examples/
├── references/
├── scripts/
└── tests/
```

## 适用边界

这个 Skill 用于需要作为开发参考的业务原型，不是一次性视觉草图生成器，也不代替真实用户研究、服务端权限测试、性能测试和人工业务验收。

## License

[MIT](LICENSE)


---

## English

`business-prototype-design` is an AI skill for business software. It turns requirements documents, screenshots, flowcharts, PRDs, and existing prototypes into traceable page specifications, runnable interactive prototypes, and standalone offline deliverables.

**Current public version: 0.3**

### What 0.3 addresses

Version 0.2 introduced a resumable eight-gate state machine and a structured evidence framework. Version 0.3 addresses audit findings where a document passed format checks while its references, files, or offline deliverables were not actually consistent and complete:

1. **Verifiable evidence files:** Evidence records bind independent files to SHA-256 hashes, byte counts, media types, and execution summaries. Requirements and acceptance documents cannot serve as their own proof.
2. **Connected references and state:** Page, Acceptance, Journey, Decision, and Evidence references must resolve. Invalidated upstream results propagate to downstream stages. Confirmation records retain their sources and continuation gates.
3. **Safer standalone delivery:** The builder confines assets to the configured root and rejects parent-directory and symlink escapes. The validator rejects static imports, CSS `@import`, and empty shells containing only expected markers.
4. **A lighter process for small tasks:** Lite mode and measurable escalation thresholds reduce unnecessary overhead. Text-only projects no longer require an image-evidence manifest.

The eight quality gates remain:

`P1 Materials and evidence review` → `P2 Requirements analysis` → `P3 Roles, permissions, and states` → `P4 Business workflows` → `P5 Detailed page specifications` → `P6 Runnable prototype` → `P7 Synchronization and offline packaging` → `P8 Verification and delivery`

Further reading (the linked detailed documents are currently in Chinese unless otherwise indicated):

- [0.3 plain-language update](UPDATE_0.3_CN.md)
- [0.3 detailed release and migration notes](RELEASE_NOTES_0.3_CN.md)
- [0.2 update history](UPDATE_HISTORY_CN.md)
- [Changelog](CHANGELOG.md)
- [Materials needed for subsequent stage validation](VALIDATION_MATERIALS_CN.md)
- [Bilingual GitHub release notes](https://github.com/simple0926/business-prototype-design/releases)

### Installation

For Codex:

```bash
git clone https://github.com/simple0926/business-prototype-design.git
cp -R business-prototype-design ~/.codex/skills/business-prototype-design
```

For the shared Agent Skills directory:

```bash
cp -R business-prototype-design ~/.agents/skills/business-prototype-design
```

If an older version is installed, back it up first and replace the complete skill directory with version 0.3; do not replace only `SKILL.md`. Version 0.3 uses final-artifact schema `0.4`. Run the migration audit before continuing an older project.

### Usage

Invoke the skill in an AI tool that supports Skills:

```text
$business-prototype-design
```

Provide any relevant materials:

- Requirements documents, PRDs, technical requirements, or business rules.
- Screenshots, flowcharts, page sketches, or visual references.
- Existing prototypes, HTML, source code, tests, or acceptance reports.
- A focused change request or an existing project to continue.

The skill selects Lite, Full, Fast, or Incremental mode according to task size and available materials, starting at the earliest unmet quality gate.

### Validate the public package

```bash
python3 -m unittest discover -s tests -v
```

The current public package contains 62 contract tests covering the state protocol, requirements traceability, evidence binding, critical business journeys, offline files, path constraints, Lite thresholds, the golden sample, package consistency, and migration audits for older projects.

For full-package acceptance:

```bash
python3 scripts/validate-package.py \
  --workflow-state prototype-workflow-state.json \
  --requirements requirements-analysis.md \
  --prototype-spec prototype-spec.md \
  --acceptance acceptance-report.md \
  --evidence-register evidence-register.json \
  --standalone prototype-standalone.html \
  --baseline-version <baseline-version>
```

See [`examples/golden-sample`](examples/golden-sample) for a complete executable example.

Passing these checks establishes only the correctness of the file structures, references, and evidence bindings they inspect. It does not independently establish that business rules, visual results, performance, or real external-system behavior are correct.

### Directory structure

```text
business-prototype-design/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── RELEASE_NOTES_0.3_CN.md
├── UPDATE_HISTORY_CN.md
├── VALIDATION_MATERIALS_CN.md
├── agents/
├── assets/
├── examples/
├── references/
├── scripts/
└── tests/
```

### Scope

This skill is intended for business prototypes that serve as development references. It is not a disposable visual-mockup generator and does not replace real user research, server-side authorization tests, performance testing, or human business acceptance.

### License

[MIT](LICENSE)
