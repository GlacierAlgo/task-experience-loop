---
name: "sop-communicate"
description: "Use GitHub Issues as the communication surface between projects, modules, or machines. Pull relevant issues, write or update issues, and maintain a lightweight artifact that records modular projects, module relationships, responsibilities, and boundary agreements. Triggers: sop-communicate, '沟通', '同步 issue', '拉取 issues', '写 issue', 'GitHub Issues', '跨项目沟通', 'module boundary'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-communicate

用 GitHub Issues 承载跨项目、跨模块和跨机器的沟通。

## 适用前提

任务需要从 GitHub Issues 拉取外部上下文、向另一个项目写入 issue、同步模块边界、请求其他项目配合，或把项目拆分、模块关系和责任边界记录成可追踪 artifact。

## 需要做

- 沟通说明文字中文优先；专业性字词、模块名、接口名、字段名和 GitHub/TEL/agent 等术语可以保留英文。
- 先识别参与沟通的 repo、项目、模块、责任方和当前目标；从 Git remote、TEL、docs 和现有 issues 推导，不足时再问用户。
- 优先读取相关 open issues、已关闭但仍有决策价值的 issues、项目文档和 TEL decisions，避免重复开 issue 或覆盖既有边界。
- 写 issue 前先收束沟通意图：请求对方做什么、为什么需要、依赖哪个模块、完成后如何验证。
- issue 正文保持可执行：背景、模块边界、依赖关系、请求动作、验收口径、相关链接和当前阻塞。
- 如果只是 Mac/Windows 两台本地机器之间的压缩信息点，而不是跨项目正式沟通，transition 到 `sop-handoff`。
- 维护一个轻量沟通 artifact；如果项目已有同类文件则更新它，否则在当前项目中创建最窄的 Markdown artifact。
- artifact 记录模块化项目、模块之间的关联性、分工边界、开放问题和对应 GitHub issue 链接。
- 边界表达必须同时写清 ownership 和 non-ownership：谁拥有语义、生命周期、结果存储、索引/投影、稳定输入输出，谁明确不拥有这些责任。
- 写入或更新 issue 后，回填 issue URL 到 artifact，并在最终结果里列出被读取和被写入的 issue。
- 如果沟通暴露出新的长期边界，按 TEL 闸门判断是否写入 decision，而不是只留在 issue 里。

## Artifact 口径

沟通 artifact 是项目内 Markdown 文件，不是数据库或任务系统。它至少包含：

- `Projects / Modules`：参与的项目和模块。
- `Relationships`：模块之间的依赖、读写关系、调用方向或数据契约。
- `Boundaries`：每个模块负责什么、不负责什么、谁拥有变更；优先用 `Owns`、`Does not own`、`Publishes`、`Consumes` 写成可审计边界。
- `Open Issues`：待沟通问题、GitHub issue 链接和当前状态。
- `Resolved Agreements`：已经确认但尚未值得写成 TEL decision 的工作约定。

机器 handoff 是更轻的 artifact，由 `sop-handoff` 负责；它只写 `Context`、`Boundary`、`Action` 和 `References`，接收方自行决定是否写入本机 obs、TEL 或 kanban。

## 边界范式

跨项目 issue 和 artifact 要偏向这种表达：

- `Octopus` = write-side raw source：只拥有 stable crawled records、raw object、source metadata、stable id、sha256、source_url、payload、checkpoint；不拥有 annotation semantics、task queue、derived result 或 result store。
- `Lighthouse` = read-side derived intelligence：拥有 task lifecycle、parser runs、materials、semantic chunks、context packs、quality、repair、derived result、projection/indexing 和 search。
- `Assembly` = downstream product consumer：只消费 Lighthouse API，不直接读取 Octopus raw workspace，也不拥有 Lighthouse 的 derived semantics。

这种边界比“谁调用谁”更重要；issue 里要把责任方向写到足够让另一个项目不能误接管语义。

## 不需要做

- 不把 GitHub Issues 变成 TEL 的替代品；长期可复用边界仍进入 TEL decisions/patterns。
- 不为模糊想法或内部临时思考开 issue。
- 不把 issue 写成聊天记录；issue 必须能被另一个项目直接消费。
- 不把 `machine-handoffs/` 变成 obs 镜像、聊天备份或长期决策库。
- 不泄露 secrets、私有凭据、客户敏感数据或机器本地不可共享路径。
- 不引入复杂同步协议、锁、数据库或跨项目任务平台。

## TEL 写入

只有沟通确认了长期可复用边界、接口契约、项目分工或跨项目约束时才写入 TEL。普通 issue 同步和一次性协调不写。
