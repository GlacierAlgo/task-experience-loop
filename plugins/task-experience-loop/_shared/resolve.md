---
name: "sop-resolve"
description: "Shared norm for SOP skills. Resolve user pointers to concrete anchors before choosing or running an action. Not invoked directly by user."
---

# sop-resolve

所有 SOP skill 在判断动作边界前，先静默做指代消解。

## 核心职责

用户的词经常是 pointer。Agent 要找的是用户此刻指向的具体对象，不是通用定义。

## 解引用顺序

1. 当前用户消息和最近对话上下文。
2. TEL loop context、constraints、decisions、patterns。
3. 当前仓库代码、文档、配置、命令输出。
4. 项目级说明，例如 `AGENTS.md`。
5. 通用知识或外部资料。

最近上下文可以补充 TEL，但不能静默覆盖 active decision 或 hard constraint。发生冲突时，把冲突作为需要裁决的 context，而不是直接猜。

## 消解范围

- 项目名 -> 当前 workspace、repo、服务或数据目录。
- 概念名 -> 本项目中的具体 contract、模块、口径或实践。
- 缩写 -> 当前项目使用的全称和边界。
- 上文指代 -> 最近讨论中的具体对象。
- 用户自造词 -> 用户心智模型中的含义。

## 粒度

解到足够行动即可：

| pointer | 解到 | 不需要 |
| --- | --- | --- |
| "那个 API" | 具体 endpoint / 函数 / route | 全量接口文档 |
| "像上次一样" | 上次可复用做法 + 约束 | 完整历史回顾 |
| "配置驱动" | 当前项目中新增实体的扩展方式 | 设计模式教程 |
| "这个问题" | 症状、对象、复现入口 | 全项目扫描 |

## 问用户的条件

只有 scope 链走完仍无法确定对象，或当前消息与 TEL hard constraint 冲突时，才简短问一次。问题限制在 1-3 个可裁决点。

## 输出方式

通常不向用户展示消解过程。若后续 action 依赖高风险 anchor，在工作说明或结果中顺带写出 anchor 来源，便于发现偏差。
