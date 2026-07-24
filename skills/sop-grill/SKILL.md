---
name: "sop-grill"
description: "Front-load uncertainty on a task at the design edge, then grill the user in an iterative loop until design context is dense enough to execute. Triggers: sop-grill, grill-me, '盘一盘', 'front-load', '问我', '帮我把不确定性梳理清楚', '前置不确定性', '决策前先想清楚'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-grill

在动手之前，把任务的不确定性前置，通过迭代提问把模糊目标收束成可执行的高密度设计上下文。

## 适用前提

用户给出一个处于设计边缘的局部任务：已有具体行动，但仍有会改变实现形状、且无法从证据推出的用户选择。

目标空间仍不可见或需要先建立边界时，不在这里反复提问，transition 到 `propose`。

## 需要做

前置不确定性、迭代提问、沉淀 durable 选择，三件事：

- 使用 `tel` skill 拉取当前项目的 durable context，避免重问已经裁决的问题。
- 联网核实外部事实：会改变接口或存储形状的 API、依赖、政策、时效性行为，用 web search 先验证再设计。
- 沿四个轴显影不确定性场：边界（谁拥有状态/暴露能力）、外部事实（须核实才能动手的口径）、用户裁决（无法从代码/TEL/测试推出的偏好或不可逆选择）、持久性（哪些结果值得写 TEL，哪些只是任务笔记）。
- 提问必须现场从真实目标 + 已拉到的历史 + web 结果生成，针对具体对象，不用模板问句。
- 小批量提问（一轮 1-3 个可裁决点）→ 用户回答 → 收窄不确定性场 → 生成下一轮 → 直到设计上下文密到可以自治执行。
- 每轮只问真正会改变范围、口径或风险的点；能 derive 或 verify 的不问。
- 窗口关闭前，使用 `tel` skill 判断并记录已经落定的 durable 选择；一次性选择不写。

## 不需要做

- 不用模板问句，不批量抛通用问题。
- 不写长设计文档。
- 上下文已经够密就停止 grill，不为提问而提问。
- 不把一次性任务决策、原始调研笔记或代码里已显然的实现细节写进 TEL。
- 不替代具体 verb 的局部判断；grill 只负责把上下文备足。

## Action transition

- 设计上下文够密后 transition 到 `propose` 或具体 verb 执行。
- 目标空间不可见或缺口无法归属时 transition 到 `propose`。
