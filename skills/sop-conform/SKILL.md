---
name: "sop-conform"
description: "Align current state with a concrete reference or standard. Triggers: sop-conform, '对齐到', '参考这个', '做成这样', '像...一样', 'match this', 'align to'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-conform

当前状态对齐一个明确参考。

## 适用前提

用户给出参考、标准、截图、样本、接口契约或另一个实现，并要求当前状态与其一致。

## 需要做

- 解清参考真正要求继承的属性，而不是复制所有表面细节。
- 明确当前状态、对齐范围、可接受差异和验证方式。
- 消除范围内的可见或可测差距，并验证关键行为不回归。
- 发现参考本身有问题时指出问题，不盲从参考。
- 完成后判断是否需要 transition 到 `review`、`migrate`、`diagnose`、`propose` 或 `expand`。

## 不需要做

- 不做像素级复制，除非用户明确要求。
- 不把局部参考对齐扩大成全量迁移。
- 不替用户重新设计目标原则。
- 不在目标空间不清时猜测参考之外的工作面。
- 不为了对齐引入无关功能或重构。

## TEL 写入

只在形成可复用视觉标准、接口契约或跨任务对齐方法，并通过 TEL 写入闸门时写入。
