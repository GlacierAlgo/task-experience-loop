---
name: "sop-bootstrap"
description: "Bootstrap a distant objective into boundary decisions, module collaboration shape, and a durable gap field without creating a roadmap or fixed plan. Triggers: sop-bootstrap, '启动目标', '启动大目标', '远目标', '大目标', '长期任务', '缺口场', '工作面', '边界设计'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-bootstrap

把远意图启动成可持续工作的边界和缺口场。

## 适用前提

用户给出较远目标或大尺度任务，但具体模块、路径、边界、协作关系、验收内容或下一批工作面无法预先枚举，需要先建立 agent 可持续推进的工作面。

## 需要做

- 建立目标坐标系：用户路径、系统模块、数据流、外部依赖、交互面、部署面和风险面。
- 设计边界，并对边界决策负责：模块为何分开、谁拥有状态、谁暴露能力、谁只消费能力。
- 对 N 个候选模块分别判断内部复杂度、协作复杂度、验证方式和历史选择偏好。
- 前置不确定性：列出会改变边界、接口或协作方式的未知点，并归属到需要验证的工作面。
- 对比当前状态与目标状态，显影已知缺口、未知缺口和需要验证的工作面。
- 用当前上下文、TEL、kanban Done、patterns、decisions、代码和参考案例补齐目标空间。
- 把缺口归属到可执行 action：`explore`、`propose`、`scaffold`、`conform`、`migrate`、`diagnose`、`reduce`、`review`、`ship`。
- 找出最先暴露、最阻塞后续推进的第一批工作面。
- 每轮 action 后根据新证据更新边界和缺口场，而不是维护固定计划。

## 不需要做

- 不写 roadmap、milestone、时间表或固定任务清单。
- 不要求用户预先列出所有模块。
- 不把推测缺口当作已验证事实。
- 不把边界决策推迟到实现阶段再临时决定。
- 不让多个模块管理相似内部复杂度；相似则合并、重划或抽出更清晰边界。
- 不暴露臃肿接口；对外链接和接口必须小巧、精确，并代表业务逻辑分解。
- 不替代具体 action 的局部判断。
- 不把缺口场写成项目愿景、产品介绍或方案文档。
- 不创建文件骨架；需要物理落脚点时 transition 到 `scaffold`。

## TEL 写入

只有目标启动形成可复用启动方法、长期边界、跨任务行动规范或明确后续任务，并通过 TEL 写入闸门时写入。
