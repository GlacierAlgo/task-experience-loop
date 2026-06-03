---
name: "sop-action"
description: "Shared norm for SOP skills. Treat each skill as an action norm with automatic context acquisition, objective expansion, lightweight action transition, and TEL memory gates. Not invoked directly by user."
---

# sop-action

所有 SOP skill 都是 action norm，不是 runbook，不是协议模板。

## 写法原则

每个 action 只写普适规则，或带有明确前提的规则：

- 适用前提：什么情况下这个 action 才接管。
- 需要做：这个 action 的义务。
- 不需要做：这个 action 不承担的责任。

不要穷举业务场景，不写固定交接格式，不写详细步骤。

当用户给出的是远目标，而不是一个已经能落到具体动作的局部任务时，先用 `bootstrap` 把目标启动成缺口场，再选择局部 action。

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

## Action transition

action 结束时只判断是否需要进入另一个 action：

- 当前 action 是否完成。
- 是否需要进入另一个 action。
- 如果需要，下一个 action 是什么，为什么。
- 如果不需要，为什么停止。

如果当前 action 发现目标空间仍不可见、缺口无法归属或后续工作面不足以判断，transition 到 `bootstrap`。`bootstrap` 启动远目标并显影工作面，不产出 roadmap、milestone 或固定任务清单。

## Action pointers

SOP 之间允许 pointer to pointer：一个 action 可以只指出下一个更合适的 action，由下一个 action 自己读取上下文并接管，不需要当前 action 展开对方流程。

- 任务完成且用户明显转向新 topic，或需要把当前 repo 变更推到 remote 时，transition 到 `sop-upload`。
- 当前任务产生了另一台 local machine 需要 `git pull` 后看到的压缩信息点时，transition 到 `sop-handoff`。
- 跨项目、跨模块、GitHub Issues 或正式 ownership/boundary 沟通，transition 到 `sop-communicate`。
- pointer 组合只表达接管关系，不表示所有 action 都必须执行；每个 action 仍按自己的适用前提决定是否真正运行。

## TEL 写入闸门

`产出到 TEL` 永远只是候选，不是默认动作。

- Decision：只有能防止 3 个月后的 agent 做错选择或重复争论时才写。
- Pattern：只有“场景 S 下做 A 有复用价值”时才写。
- Kanban：只记录任务级状态，不记录子步骤、活动流水或一次性细节。
- Constraints：只记录全局或跨任务约束；普通观察、临时环境状态、一次性 bug 根因不写。
