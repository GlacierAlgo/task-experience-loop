---
name: "sop-propose"
description: "Turn a bounded vague goal into decision-dense context for autonomous execution. Triggers: sop-propose, '出方案', 'proposal', '设计一下方案', '怎么做比较好', '定一下边界'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-propose

把模糊目标收束成可自治执行的设计上下文。

## 适用前提

用户有目标，且目标已经足够近，可以收束 objective、principles、boundaries、completion criteria 或 physical anchor。

## 需要做

- 明确目标、裁决原则、边界、验收标准和物理落脚点。
- 优先用 TEL decisions、constraints、当前 repo 和已有对话消解选项。
- 暴露仍需裁决的选项空间，并只在既有约束无法裁决时问用户。
- 目标过远、工作面不可见或无法枚举主要缺口时 transition 到 `bootstrap`。
- 产出足够后 transition 到具体执行 action。
- 如果方案会影响另一台 local machine 的初始化、分工或操作边界，transition 到 `handoff`；如果用户随后切换 topic 且有 repo 变更，transition 到 `upload`。

## 不需要做

- 不写长方案文档。
- 不重复讨论 TEL 已定 decision。
- 不把 principles 写成无法裁决的空话。
- 不把远目标压扁成虚假的单次方案。
- 不在上下文已经足够时继续停留在 propose。

## TEL 写入

只有产生可复用设计选择、全局约束或明确任务级后续项，并通过 TEL 写入闸门时写入。
