---
name: "sop-upload"
description: "Upload completed local code changes to the Git remote when a previous task is done, when the user clearly moves to another topic, or when the user asks to commit, push, upload, sync, or close out work. Triggers: sop-upload, '上传', '提交推送', '收尾上传', 'git push', 'commit push', 'sync changes'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-upload

把已完成的本地代码变更收尾到 Git remote。

## 适用前提

前一个任务已经完成、验证过或被用户接受；当前工作区有需要保留的代码、文档或配置变更；用户明确要求上传，或用户明显转向另一个 topic，需要先把上一段工作收口。

## 需要做

- 先检查 `git status`、当前分支、remote 和 diff，区分本次工作产物、用户已有改动、生成物和敏感文件。
- 只 stage 与已完成任务相关的变更；遇到不明来源或不相关改动时保留在工作区，并在结果里说明。
- 提交前确认已有验证结果仍成立；如果没有验证且风险不低，补跑最接近的测试、lint、构建或静态检查。
- 写短而具体的 commit message，表达完成的行为或边界变化，不写泛化流水。
- push 当前分支到对应 remote；push 后报告 branch、remote 和 commit hash。
- push 失败时先判断是凭据、远端落后、冲突、网络还是 hook 问题；可局部修复则修复并重试，根因不清时 transition 到 `diagnose`。
- 如果任务完成需要 TEL 收口，先更新 kanban/context，再把 TEL 变更纳入同一个合理提交。

## 不需要做

- 不上传未完成、未验证且会影响用户使用的工作，除非用户明确要求保存 WIP。
- 不用 `git add .` 代替范围判断。
- 不提交 secrets、机器本地配置、缓存、大型生成物或用户不相关改动。
- 不改写历史、force push、rebase 公共分支或删除远端内容，除非用户明确要求。
- 不把普通代码上传写成 TEL decision。

## TEL 写入

只有上传过程中发现可复用发布/协作约束，或任务完成状态需要更新 kanban/context 时才写入 TEL。
