# business-prototype-design

把需求文档、流程图、截图或已有原型整理为可确认的业务流程和页面规格，再按用户选定的设计规范制作交互原型或静态原型图。验收时，每条结论都能追溯到已确认的规则和可复核的证据。

这是 **v0.4.0-preview.1 独立编排预览版**。已有项目依赖整包校验、工作流状态或结构化证据登记时，可继续使用 [v0.3 稳定版](https://github.com/simple0926/business-prototype-design/releases/tag/v0.3)。

## 使用流程

给 Codex 提供需求、截图、已有页面规格或想修改的原型。它会复用有效的阶段产物，从最早尚未满足的阶段开始。

| 阶段 | 确认的内容 |
|---|---|
| 1. 证据盘点 | 材料来源、优先级和冲突 |
| 2. 需求分析 | 范围、原子需求、业务决策和待确认项 |
| 3. 业务建模 | 角色权限、数据范围、状态和可执行操作 |
| 4. 流程确认 | 主流程、异常分支、状态流转和角色交接 |
| 5. 页面规格 | 页面和弹窗、字段、校验、反馈及逐条验收条件 |
| 6. 原型构建 | 用户选择交互原型或静态原型图，并选定设计规范 |
| 7. 交付选择 | 用户选择离线 HTML 或原型图片，确认交付范围 |
| 8. 验收交付 | 以第 4–7 阶段的确认内容为基线，核对适用的验收条件 |

制作前可先提供设计选项并说明取舍。用户选定后，按确认的流程、页面规格和设计规范构建。变更这些内容时，先记录用户确认的决定，再更新受影响的原型和验收项。

## 选择原型和交付方式

| 原型类型 | 可选交付 | 如何验收 |
|---|---|---|
| 交互原型 | 离线 HTML | 对照已确认的规则检查交互，扫描单文件依赖，并在离线环境打开实际交付文件验证主流程 |
| 交互原型 | 原型图片 | 检查输出图片的页面和状态覆盖，交互由第 6 阶段的实测记录证明 |
| 静态原型图 | 原型图片 | 检查约定页面、弹窗、关键状态和视觉一致性，运行验收根据确认的静态范围标为不适用 |

可选的用户故事卡适合单独评审。需求分析、页面规格、设计走查和验收报告的模板在 [assets/delivery-templates](assets/delivery-templates)。

## 安装与调用

从 [v0.4.0-preview.1 发布页](https://github.com/simple0926/business-prototype-design/releases/tag/v0.4.0-preview.1) 下载 `business-prototype-design-v0.4.0-preview.1.zip`，解压后把整个 `business-prototype-design` 目录放到 `~/.codex/skills/`。安装过同名技能时，先备份旧目录，再替换整包。确认 `SKILL.md` 位于技能目录的第一层。

在 Codex 中输入：

```text
$business-prototype-design 以已确认的审批流程和页面规格为基础，先给我可选的设计方向。我选择后，制作申请页、审核页和退回状态的静态原型图，并按确认的清单验收。
```

主技能包含八个阶段需要的本地参考，可以单独使用。离线 HTML 的通用打包脚本需要 Node.js。报告一致性和 HTML 静态检查需要 Python 3。

## 核对验收报告

用填写后的项目产物运行：

```bash
python3 scripts/validate-traceability.py \
  --requirements requirements-analysis.md \
  --spec prototype-spec.md \
  --acceptance acceptance-report.md \
  --design-qa design-qa.md
```

既有项目的验收基线明确约定没有视觉对标时，使用 `--no-visual-target`。校验器检查逐条验收记录、证据引用和交付结论的一致性。实际交互、视觉对照及离线运行由对应的实测和审查记录证明。

## 许可

[MIT](LICENSE)
