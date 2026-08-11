---
name: "sop-reduce"
description: "Prove code, files, dependencies, or abstractions are unnecessary and remove them without changing behavior. Triggers: sop-reduce, '清理冗余', '精简', '删除无用', 'remove dead code', '去掉冗余'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../../_shared/resolve.md) and [sop-action](../../_shared/action.md).

# sop-reduce

证明无用，然后删除。

## 适用前提

目标是减少代码、文件、依赖、配置或抽象，且行为应保持不变。

## 需要做

- 明确清理范围、外部消费者和行为不变量。
- 用引用、入口、配置、CLI/API、数据消费者或 TEL 证据证明候选无用。
- 区分 dead、vestigial 和 speculative；无法证明就保留。
- 删除后验证行为不变量。
- 发现需要结构迁移、职责重划或目标面重显影时 transition 到 `migrate` 或 `propose`。

## 不需要做

- 不凭感觉删除。
- 不把 reduce 做成重构。
- 不删除外部消费者仍可能依赖的入口。
- 不把“看起来多余”的远目标缺口当成 dead weight。
- 不把一次清理流水写入 TEL。
