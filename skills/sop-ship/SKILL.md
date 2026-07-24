---
name: "sop-ship"
description: "Move a locally ready artifact into its target runtime and verify it is reachable. Triggers: sop-ship, '部署', '上线', '推到服务器', 'deploy', 'ship it'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-ship

把本地就绪产物发布到目标运行环境。

## 适用前提

产物本地已经足够就绪，任务是发布、部署、同步或启动到目标环境并验证。

## 需要做

- 明确产物、目标运行环境、发布方式和验证入口。
- 从 TEL、项目脚本、docs、env 和现有部署记录推导发布方式。
- 发布前识别本地未就绪、未提交关键变更、权限或凭据风险。
- 发布后验证用户关心入口可达或 artifact 已发布。
- 本地未就绪或运行失败时 transition 到 `diagnose`；部署方式、目标边界或工作面未定时 transition 到 `propose`。

## 不需要做

- 不把部署方式固定为某个工具或平台。
- 不在本地明显未就绪时强行发布。
- 不修改服务器配置，除非任务明确要求或已有约束支持。
- 不把发布动作升级成长期路线图。
- 不把普通部署流水写成 decision。
