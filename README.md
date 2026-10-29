# business-prototype-design

`business-prototype-design` 是一个用于业务软件的 AI Skill，把需求文档、截图、流程图、PRD 或旧原型，逐步转换为可追溯的页面规格、可运行交互原型和离线单文件交付物。

**当前公开版本：0.2**

## 0.2 解决了什么

0.1 搭起了“从需求到原型”的基本流程；0.2 没有继续增加阶段，而是重点解决三个执行问题：

1. **任务能接着做：** 任务中断、更换会话或需求变化后，可以从正确的阶段继续。
2. **需求能查清去向：** 每条需求都能回到原始材料，并查到它影响的角色、状态、流程、页面或后台结果。
3. **完成结论能拿出证据：** 测试文件存在不等于需求已经被验证；每个“通过”都要绑定对应需求、业务场景、检查断言和可重现证据。

0.2 固定为八个质量门：

`P1 资料和证据检查` → `P2 需求分析` → `P3 角色、权限和状态` → `P4 业务流程` → `P5 页面详细说明` → `P6 可运行原型` → `P7 同步和离线打包` → `P8 验证与交付`

完整变化请阅读：

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

如果本地已经安装过 0.1，请先备份旧目录，再用完整的 0.2 文件夹替换；不要只替换 `SKILL.md`。

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

Skill 会根据材料完整度选择 Full、Fast 或 Incremental 模式，并从最早尚未满足的质量门开始。

## 验证公开包

```bash
python3 tests/test_contracts.py
```

当前公开版包含 30 项契约测试。它们用于检查状态协议、需求追溯、证据绑定、关键业务旅程、离线文件和旧项目迁移体检。

测试通过只能证明它所检查的文件结构、引用关系和证据绑定正确，不能单独证明业务规则、视觉结果、性能或真实外部系统行为正确。

## 目录结构

```text
business-prototype-design/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── UPDATE_HISTORY_CN.md
├── VALIDATION_MATERIALS_CN.md
├── agents/
├── assets/
├── references/
├── scripts/
└── tests/
```

## 适用边界

这个 Skill 用于需要作为开发参考的业务原型，不是一次性视觉草图生成器，也不代替真实用户研究、服务端权限测试、性能测试和人工业务验收。

## License

[MIT](LICENSE)

