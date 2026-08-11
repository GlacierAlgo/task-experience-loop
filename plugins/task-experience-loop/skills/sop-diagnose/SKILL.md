---
name: "sop-diagnose"
description: "Trace a concrete symptom to root cause, repair it when in scope, and verify the symptom is gone. Triggers: sop-diagnose, '修复报错', 'fix bug', '为什么不工作', '报错', 'debug', '排查故障', 'broken'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../../_shared/resolve.md) and [sop-action](../../_shared/action.md).

# sop-diagnose

具体症状到根因，再到最小修复。

## 适用前提

系统有具体错误、异常行为、性能退化、部署失败或用户可描述的错误症状。

## 需要做

- 找到症状、影响范围和可复现或可观察证据。
- 追到为什么会进入错误状态，而不是只定位哪里报错。
- 在范围内做最小修复，并验证原症状消失。
- 保持既有设计意图，不把有意行为当作 bug 修掉。
- 根因超出 bug 修复边界时 transition 到 `migrate`、`reduce`、`propose` 或 `review`。

## 不需要做

- 不用吞错误、兜底或绕过症状代替根因修复。
- 不借修 bug 顺手重构周边代码。
- 不把无法复现或无法观察的问题猜成确定根因。
- 不把局部症状扩大成远目标推进，除非证据显示目标面本身不清。
- 不把普通 bug 修复过程写成长期设计记忆。
