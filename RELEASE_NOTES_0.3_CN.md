# `business-prototype-design` 0.3 发布说明

> 发布日期：2026-11-05  
> Skill 版本：`0.3`  
> 最终工件 schema：`0.4`

## 一句话结论

0.3 不再把“文件存在、字段齐全、ID 看起来正确”当成完整证据链：它补上可机器验证的跨文件引用、证据文件身份、状态失效传播和离线依赖闭合，同时明确保留业务语义与真实人工确认的人工责任边界。

## 为什么发布 0.3

0.2 建立了八门状态机、Evidence claim 和五个校验器，但对抗审计发现仍可出现以下假阳性：

- 需求文档充当自己的实现/测试证据；
- Evidence 文件只有占位文本；
- `PAGE-*`、`ACC-*`、manifest/checkpoint Evidence ID 悬空；
- confirmation actor 和时间可任意填写；
- 上游 phase 失效，下游仍保持 confirmed；
- acceptance/design QA 的总结果互相冲突；
- 只含 marker、空脚本和空样式的极小 HTML 通过；
- CSS `@import`、静态 ES import 或构建目录外资产被带入 standalone。

0.3 将这些已经复现、能够可靠表达为契约的问题转成失败测试和机器检查。

## 主要变化

### 1. Evidence 从“路径”升级为“可核对文件”

schema `0.4` 的 Evidence entry 新增：

- `sha256`、`bytes`、`media_type`；
- test evidence 的 `command`、`exit_code`、`test_count`、`result_summary`；
- browser evidence 的可复现 `command`、`exit_code`、`environment`、`target`、`viewport` 和结构化执行轨迹。

Validator 会拒绝目录、缺失文件、digest/大小不一致、占位内容，以及指向、逐字节复制或只改变空白后复制 requirements、acceptance、prototype spec 等契约的自证文件。Test evidence 必须能解析为 TAP、JUnit XML 或结构化 JSON；browser evidence 必须是含步骤、断言、console/network 记录的结构化 JSON。

这只能证明“当前检查的文件就是登记的文件”，不能证明文件里的业务结论一定正确。

### 2. 跨工件引用闭合

- Requirement 的 `PAGE-*` 和 `ACC-*` 必须在 prototype spec 中存在；
- Requirement 的 Source、Decision、Journey 必须分别解析到 Source register、workflow Decision 和 Journey registry；
- manifest unit 的 `EVD-*` 必须格式正确，并可在完整包验收时解析到 Evidence register；
- checkpoint phase evidence 必须解析到 Source、Decision 或 Evidence；
- Journey validator 使用与 Traceability 相同的 Evidence contract，并可核对 Requirement ID。

### 3. 状态机增加 provenance 和失效传播

- confirmed/reused phase 使用 ISO 时间、confirmation provenance 和 `continuation_gate`；
- confirmed Decision 记录 `source_type`、`source_ref`、`confirmed_by`、`confirmed_at`；
- `invalidated_by` 必须解析到 Decision；
- 上游 invalidated 时，下游不能继续保持 confirmed/reused/not_applicable。

本地 validator 只能检查 provenance 记录是否完整；若没有可信聊天/审批事件 API，它无法证明记录中的人工确认真实发生。

### 4. Lite 模式

Lite 仅适用于同时满足以下条件的原型：

- 1 个 actor；
- canonical state 少于 3 个；
- 不涉及权限规则、金额、删除、外部副作用、敏感数据或审批。

任一条件变化就升级为 Full/Fast/Incremental。Lite 可省略不适用的 manifest 和 journey 工件，但最终交付仍需实际行为和证据。

最终包不再只相信 `risk_profile` 的自报计数：Validator 会从标准 Role / Canonical state 表复算 actor/state 数量，并用需求与 prototype spec 的保守风险信号复核审批、权限、金额、删除、外部副作用和敏感数据标志。跨角色、多状态或审批流程不能把 `journey_profile` 伪报为 `none`。

### 5. Manifest 条件化

- `text_only`：记录 `text_source_ids`，不创建空 manifest；
- `image_bearing`：必须使用 manifest；PDF/image 不能自行关闭视觉检查，文件扩展名与常见 magic bytes 也会反查伪报的 `kind`；source 记录 digest 和字节数；unit 绑定注册 Evidence ID。
- `visual_profile: comparison_required`：最终包必须提供 Design QA；`none` 才可省略。

整包 Validator 会把 Source register 反向核对这些 profile：PDF、PNG/JPEG/SVG/WebP、Figma、PPT/Keynote、截图/设计稿类来源不能伪报 `text_only`，`text_source_ids` 必须与文本 Source register 一致，manifest Source ID 也必须来自同一注册表。

### 6. Standalone 安全与完整性

- Builder 使用 realpath confinement，拒绝 `../` 和 symlink 逃逸出构建根目录；
- Builder/validator 用区分代码、字符串、模板字符串和注释的轻量词法扫描拒绝静态 import、`export ... from`、CSS `@import`、动态 import、fetch、worker 等未打包依赖；块注释、行注释和 CSS identifier escape 不能绕过，同时字符串里的示例文本不会被误判；
- `srcset` 不能用首个 data URL 掩盖后续相对或外部候选；
- 五类 BPD 内容改成 paired `START`/`END` section，并要求 section 内有实质内容；
- `--skip-contract-markers` 必须同时给出至少一个显式 `--require`。

### 7. 单一整包验收入口

最终 0.3 包使用 `scripts/validate-package.py`，统一执行 workflow、traceability、standalone、manifest 和 journey 校验，防止只运行某一个较弱的 validator 后误报完成。

## Golden sample

[`examples/golden-sample`](examples/golden-sample) 包含：

- 3 个页面；
- Requester / Reviewer 两个角色；
- new / draft / submitted / approved 四个状态；
- Requirements、prototype spec、workflow checkpoint、Evidence register、Journey、Acceptance 和可运行 standalone；
- 可从样例目录直接运行的 `node verify-sample.mjs`，生成 6 项 TAP 行为结果和结构化 DOM-harness 轨迹；
- 初始审批队列为空、未提交不可审批、空标题拦截、draft → submitted → approved 均由同一份 standalone 脚本执行验证；
- 一次完整 `validate-package.py` 全绿结果。

## 从 0.2 升级

1. 备份旧 Skill 和项目工件。
2. 整体替换 Skill 目录，不要只复制 `SKILL.md`。
3. 对旧项目运行：

```bash
python3 scripts/audit-legacy-project.py <project>
```

4. 将最终交付工件升级为 schema `0.4`：
   - workflow 添加 `skill_version: 0.3`、evidence/journey profile、confirmation provenance、continuation gate；
   - Evidence register 补 digest、大小、媒体类型和 kind-specific metadata；
   - prototype spec 为 `ACC-*` 提供注册位置；
   - standalone marker 改为 paired sections。
5. 运行整包校验并修复全部错误。

旧 schema `0.3` 仍可由部分单项 validator 读取，用于迁移诊断；它不能作为 0.3 最终 passed package。

## 验证命令

```bash
python3 -m unittest discover -s tests -v

cd examples/golden-sample
python3 ../../scripts/validate-package.py \
  --workflow-state prototype-workflow-state.json \
  --requirements requirements-analysis.md \
  --prototype-spec prototype-spec.md \
  --acceptance acceptance-report.md \
  --evidence-register evidence-register.json \
  --journey-coverage journey-coverage.json \
  --standalone prototype-standalone.html \
  --baseline-version B-GOLDEN-001
```

预期：62 项测试通过，golden sample 输出 `package_result=passed`。

## 仍未解决、也不应被夸大的边界

- Hash 与规范化文本摘要证明文件身份并阻止原样/空白改写自证，不证明语义改写后的业务事实正确。
- TAP/JUnit/JSON 解析证明结果文件结构与登记计数一致，不证明任意第三方命令确实被可信执行；需要受信执行器或签名日志才能进一步闭环。
- Provenance 字段证明记录完整，不证明真人确实确认；需要可信外部事件源才能进一步验证。
- Validator 不能替代真实用户研究、服务端权限测试、性能测试、合规审查或生产外部副作用验证。
- Markdown 仍是部分契约输入，复杂转义和非标准表格不如结构化 JSON 稳定。
- Manifest 仍依赖填写的 `total_units`；没有可用 PDF/媒体解析器时，Validator 不会自行证明真实页数。
- 浏览器语义仍需要真实执行与人工/自动断言，不能仅靠静态 HTML 扫描。

