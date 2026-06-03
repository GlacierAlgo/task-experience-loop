---
name: "sop-handoff"
description: "Write a compressed machine-to-machine handoff packet when one local machine needs another machine to know a small set of facts after git pull. Can trigger autonomously after exploration, proposal, communication, deployment, or upload work when the receiving machine should initialize local obs/TEL/kanban or act on a boundary. Triggers: sop-handoff, 'handoff', '交接', '给 Windows 看', '给 Mac 看', '跨机器信息点', 'machine handoff'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-handoff

把一台 local machine 需要另一台 machine 知道的信息压缩成 repo 内 handoff packet。

## 适用前提

当前任务产生了另一台机器需要看到的信息，且这些信息不适合直接同步 `obs`、不值得开 GitHub issue、也不需要复杂任务队列。它可以由用户明确要求触发，也可以由 agent 在发现跨机器必要信息时不定期自主触发。

## 需要做

- 先判断是否真的需要 handoff：接收机器需要知道、git pull 后能直接消费、不是完整聊天或 obs 镜像、不是普通 commit diff 自己就能说明的内容。
- 确定方向：`mac-to-windows` 或 `windows-to-mac`；无法从上下文、本机环境或用户指代推出时再问。
- 在 `machine-handoffs/{sender}-to-{receiver}/YYYY-MM-DD-short-topic.md` 写一份短 Markdown。
- packet 只保留 `Context`、`Boundary`、`Action` 和 `References`，控制在接收方能快速吸收的密度。
- 写入前查同方向近期 packet，避免重复写同一事项；需要补充时更新已有 packet 或另写更具体的新 packet。
- 如果接收方需要尽快看到，完成后 transition 到 `sop-upload`，由主流程提交并推送当前 repo。
- 接收方读取 handoff 后，自行初始化或更新本机 obs、TEL decisions、patterns 和 kanban；不要要求发送方直接写接收方本地状态。

## Packet 口径

```markdown
# Short Topic

## Context
- What changed or what the other machine needs to know.

## Boundary
- What this does and does not imply.

## Action
- What the receiving machine should do, if anything.

## References
- Repo paths, commit hashes, issue links, or TEL decision names.
```

## 不需要做

- 不把 `machine-handoffs/` 变成长期知识库、聊天备份、obs 镜像或任务数据库。
- 不写 secrets、token、私有凭据、客户敏感数据、完整本地路径清单或 runtime 状态。
- 不为接收方直接写它的 obs/TEL/kanban；只提供压缩信息点。
- 不为每个普通代码提交写 handoff；commit diff、README 或 issue 已能表达时不写。
- 不把正式跨项目模块沟通塞进 handoff；那种情况 transition 到 `sop-communicate`。
- 不自行 commit/push；需要让对方看到时 transition 到 `sop-upload`。

## TEL 写入

只有 handoff 内容本身形成长期可复用边界、接口契约或跨机器分工原则时才写入 TEL。普通 handoff packet 不写 TEL。
