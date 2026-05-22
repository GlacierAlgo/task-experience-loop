---
name: "sop-replicate"
description: "Produce multiple uniform instances from a known template and target list. Use only when there is more than one target or an explicit batch. Triggers: sop-replicate, '批量生成', '按模板生成', '每个都...', 'batch generate', 'for each'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-replicate

模板乘以目标列表。

## 适用前提

已有模板或 schema，且需要为多个目标生成结构一致的实例。

## 需要做

- 明确模板、目标列表、输出位置和校验方式。
- 保持所有实例格式一致。
- 已有 schema 或自动校验时自主批量执行。
- 记录失败目标和失败原因，不让单个失败污染整个批次。
- 模板或 schema 未定时 transition 到 `propose`；目标语义转换时 transition 到 `migrate`；批量目标来自远目标且缺口未显影时 transition 到 `bootstrap`。

## 不需要做

- 不处理单个一次性生成任务。
- 不在已有自动校验时强制用户确认第一个实例。
- 不把批量生成做成语义迁移。
- 不为每个实例创造不同结构。
- 不把缺口场拆成未验证的批量清单。

## TEL 写入

只有批量过程确立可复用 schema、格式约定或生成模式，并通过 TEL 写入闸门时写入。
