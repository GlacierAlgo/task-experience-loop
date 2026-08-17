---
name: "sop-grill"
description: "Front-load uncertainty at a design edge: surface boundary, external-fact, user-ruling, and persistence unknowns; resolve them into an executable contract covering deliverable, scope, default assumptions, and completion criteria; then conditionally preserve durable choices in TEL. Use before implementation when that contract is materially under-specified. Triggers: sop-grill, grill-me, '盘一盘', 'front-load', '问我', '帮我把不确定性梳理清楚', '前置不确定性', '决策前先想清楚'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../../_shared/resolve.md) and [sop-action](../../_shared/action.md).

# sop-grill

在动手之前，先显影不确定性从哪里来、该如何消解，再把结果闭合成可执行合同。合同不充分时不进入代码修改；窗口关闭前检查是否产生了值得长期保留的选择，但不要求每次 grill 都写 TEL。

## 适用前提

用户给出一个处于设计边缘的局部任务：已有具体行动，但仍有会改变实现形状、且无法从证据推出的用户选择；或 agent 即将实现，却无法准确复述交付物、范围、默认假设、完成标准中的至少一项。

目标空间仍不可见或需要先建立边界时，不在这里反复提问，transition 到 `propose`。

## 需要做

显影不确定性、闭合执行合同、按需沉淀 durable 选择，三件事。两组轴是正交关系：第一组负责发现和路由未知，第二组负责证明任务已经可以执行；不要互相替代，也不要强行一一映射。

### 1. 显影不确定性场

- 使用 `tel` skill 拉取当前项目的 durable context，避免重问已经裁决的问题。
- 沿四个发现轴检查载重未知：
  1. **边界**：谁拥有状态、暴露能力、承担副作用与验证责任；优先从 TEL、架构和代码推导，所有权仍是业务选择时再问。
  2. **外部事实**：哪些 API、依赖、政策、数据口径或时效行为必须核实才能设计；查权威来源，不让用户替 agent 做可验证的事实搜索。
  3. **用户裁决**：哪些偏好、不可逆选择或取舍无法从上下文、代码、TEL 和测试推出；只问这些真正需要用户决定的点。
  4. **持久性**：哪些结果可能约束未来任务，哪些只服务当前执行；先标记候选，不在选择尚未稳定时提前写 TEL。
- 按 derive → verify → ask 消解未知。提问必须从真实目标、历史和证据现场生成，每轮只问 1-3 个会改变范围、口径或风险的点。

### 2. 闭合执行合同

- 把已消解的信息投影到四个闭合轴：
  1. **交付物**：产出什么，以及它的文件、接口、行为或呈现形态。
  2. **范围**：允许和禁止修改的文件、模块、数据、接口与外部副作用。
  3. **默认假设**：需求未写明处按什么现有约束或最小解释推进。
  4. **完成标准**：哪些可观察证据代表通过，哪些结果代表未通过。
- 每个闭合轴出现缺口时，追溯到一个或多个发现轴，选择 derive、verify 或 ask；不要把八个轴展开成八道固定问题。
- transition 到实现 action 前，用四条简短、可见的复述分别声明交付物、范围、默认假设和完成标准。用户纠正任一载重项时，定位被推翻的发现轴，原合同失效，继续 grill。
- 任一闭合轴仍有会改变实现形状、范围或验收的未知项时，禁止写代码或修改目标产物；四轴充分且无冲突时，不另设确认仪式，直接进入执行。

### 3. Maybe memorize

- 窗口关闭前做一次轻量 memory-candidate audit：本轮没有形成新选择、约束、拒绝理由或接口合同时，直接结束，不制造 TEL 记录。
- 出现候选时，使用 `tel` skill 执行 durable gate、查重、归类和写入治理。已有记录已经覆盖时只复用；只有通过 gate 的新增、合并或 supersede 才修改 TEL。
- memory audit 能从对话和证据完成时不再询问用户；只有记忆内容或覆盖关系仍存在会改变长期含义的歧义时，才继续 grill。

## 不需要做

- 不用模板问句，不批量抛通用问题。
- 不把两组轴扩写成长设计文档、八问清单或固定问卷。
- 上下文已经够密就停止 grill，不为提问而提问。
- 不要求用户重复确认已经能够 derive 或 verify 的执行合同。
- 不把“用户回答了问题”视为必须记忆，也不为了让 grill 看起来有产出而强行落盘。
- 不在窗口关闭时回扫整段会话凑候选；只判断本轮 grill 实际形成的 durable 结果。
- 不把一次性任务决策、原始调研笔记或代码里已显然的实现细节写进 TEL。
- 不替代具体 verb 的局部判断；grill 只负责把上下文备足。

## Action transition

- 四轴执行合同充分并完成可见复述后，transition 到 `propose` 或具体 verb 执行。
- 任一载重项仍不充分时留在 grill，不进入实现。
- 目标空间不可见或缺口无法归属时 transition 到 `propose`。
