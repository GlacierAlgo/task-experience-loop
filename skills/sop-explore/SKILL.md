---
name: "sop-explore"
description: "Map a bounded unknown area until enough understanding exists to choose the next action. Triggers: sop-explore, '调研', '搞清楚', '了解一下', 'explore', '分析一下这个'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-explore

把未知变成足够行动的认知。

## 适用前提

对象、系统、技术、现象或代码区域还不够清楚，且未知范围可以被局部探索收敛。

## 需要做

- 找到对象的职责、边界、入口和关键路径。
- 区分已验证事实、推测和仍缺信息。
- 优先使用本地上下文、TEL、代码和项目文档；只在必要时查官方文档或联网搜索。
- 输出可行动方向，但不替代需要裁决的设计选择。
- 认知足够后 transition 到 `propose`、`review`、`diagnose`、`migrate`、`reduce`、`conform`、`ship` 或 `expand`。

## 不需要做

- 不把探索写成教程。
- 不在探索中做最终设计裁决。
- 不为了完整性无限展开支线。
- 不把远目标展开伪装成局部调研；目标空间不可见时进入 `expand`。
- 不把普通研究发现直接写成 decision。

## TEL 写入

只有产生可复用设计选择、非显然约束或可复用探索方法，并通过 TEL 写入闸门时写入。
