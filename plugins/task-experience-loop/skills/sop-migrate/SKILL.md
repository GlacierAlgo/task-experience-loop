---
name: "sop-migrate"
description: "Transform all in-scope instances from pattern A to pattern B while preserving invariants. Triggers: sop-migrate, '迁移', '从...到...', '替换所有', '全量替换', 'migrate'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../../_shared/resolve.md) and [sop-action](../../_shared/action.md).

# sop-migrate

范围内 A 模式到 B 模式的全量转换。

## 适用前提

已有旧模式 A、新模式 B、迁移范围和行为不变量，目标是范围内 A -> B 全覆盖。

## 需要做

- 明确 A 的识别方式、B 的目标契约、迁移范围和排除项。
- 盘点范围内所有 A 实例，标出不能机械处理的例外。
- 保持迁移前后的行为、数据、接口或视觉不变量。
- 用静态搜索、测试、构建、快照或 smoke 覆盖迁移结果。
- A、B、范围或不变量不清时在修改前停止；迁移外缺陷作为独立目标报告，不在当前 action 内夹带修复。

## 不需要做

- 不把参考对齐误扩大成全量迁移。
- 不在 A/B 未定义时猜着迁移。
- 不借迁移删除无关代码。
- 不在目标空间不清时把迁移范围扩大成整体改造。
- 不把每次迁移流水写入 TEL。
