---
name: "sop-scaffold"
description: "Create the minimal runnable physical anchor for a new project, package, module, or feature area. Triggers: sop-scaffold, '新建项目', '初始化项目', '搭建骨架', '创建骨架', 'create project'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-scaffold

创建最小可运行物理落脚点。

## 适用前提

缺少可工作的文件结构、entry point 或模块骨架，后续 action 没有物理落脚点。

## 需要做

- 明确职责、位置、约束和最小入口。
- 从 TEL 和当前 repo 推导语言、工具链和结构深度。
- 选择能运行的最浅结构。
- 生成有实际内容的文件，避免空 placeholder。
- 目标过远且缺少工作面时 transition 到 `bootstrap`；骨架可运行后 transition 到后续 action。

## 不需要做

- 不在目标、边界或验收不清时强行 scaffold。
- 不把一个单文件内聚脚本升级成项目骨架。
- 不把某个项目的工具链当作全局默认。
- 不用脚手架替代目标展开。
- 不承接远目标启动；远目标先进入 `bootstrap`。
- 不在 scaffold 阶段预设未来复杂层级。

## TEL 写入

Scaffold 本身通常只记录任务状态。只有产生可复用结构决策、工具链约定或新模块边界，并通过 TEL 写入闸门时写入。
