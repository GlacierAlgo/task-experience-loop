---
name: "sop-action"
description: "Shared norm and role-directed router for SOP skills. Treat each skill as a bounded action with automatic context acquisition, explicit applicability, local verification, and TEL memory gates. Not invoked directly by user."
---

# sop-action

所有 SOP skill 都是 action norm，不是 runbook，不是协议模板。

## 写法原则

每个 action 只写普适规则，或带有明确前提的规则：

- 适用前提：什么情况下这个 action 才接管。
- 需要做：这个 action 的义务。
- 不需要做：这个 action 不承担的责任。

不要穷举业务场景，不写固定交接格式，不写详细步骤。

## 上下文补齐

Agent 局部已经具备自治能力。缺信息时按证据距离补齐：

1. 当前消息、对话上下文、TEL loop context。
2. TEL decisions、constraints、patterns。
3. 本地代码、文档、配置、命令、测试、日志。
4. 官方文档或联网搜索；只在信息外部化、时效性或本地证据不足时使用。
5. 问用户；只在业务裁决、约束冲突、破坏性操作、覆盖既有 decision 或无法取得必要信息时使用。

上下文本来就在同一会话和 TEL 中自然保留；不要额外设计上下文传递。

## 确认语义

- **derive**：能从上下文、TEL 或代码推出，就直接推导。
- **verify**：能用命令、测试、浏览器、日志、静态搜索验证，就直接验证。
- **ask**：只有 derive 和 verify 都不足，且该点会改变范围、口径或风险时才问用户。

## Action roles

SOP 是按责任分层的 action 集合，不是互相跳转的平面状态图：

- **Framing**：`propose`、`explore`，负责显影目标空间或局部未知。
- **Readiness gate**：`grill`，负责在已知工作面上闭合执行合同。
- **Lens / assessment**：`layout`、`review`，负责前置一个专门判断面或只读评估。
- **Mutation**：`diagnose`、`conform`、`migrate`、`reduce`、`scaffold`，负责改变范围内状态并验证自身不变量。
- **Release**：`upload`、`ship`，负责把已就绪产物送入 Git remote 或目标运行环境。

默认责任方向是 framing / gate → mutation → release。`layout` 可以在前端 mutation 前提供信息架构判断；`review` 以 findings 结束，不隐含修复。角色表示责任边界，不表示每个任务都要依次执行每层。

## Action routing

- 共享 router 根据用户当前要求、已有合同和最新证据选择 action；单个 skill 不枚举其他 skill 作为下一跳。
- action 的适用前提不成立时，在修改前停止并暴露缺少的事实、边界或裁决，再由 router 重新选择；不要在当前 action 内扩大职责。
- mutation 和 release action 自己完成范围内验证，并对失败做有界分类；修复循环不靠互相 transition 表达。
- action 完成后先结束当前责任。如果用户要求继续，或结果暴露了独立目标，基于最新证据做一次新的 action 选择；不要把它编码成返回边。
- 用户明确要求 commit、push、upload 或同步 Git remote 时，只有 release 前提成立才选择对应 action；部署同理，不把尚未就绪的实现问题夹带进 release。

## TEL

写入 TEL 不是 action 的默认收尾。出现 durable memory 候选时，使用
`tel` skill 判断并执行；decision、pattern、noun、kanban 和 compact
的门槛、格式与命令只由 `tel` skill 定义，其他 action skill 不复制。
