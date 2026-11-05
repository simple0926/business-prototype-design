# business-prototype-design

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

