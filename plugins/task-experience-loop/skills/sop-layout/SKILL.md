---
name: "sop-layout"
description: "Front-load information architecture when a frontend task changes page structure or spatial hierarchy. Triggers: sop-layout, 'layout', '布局', '页面结构', '前端骨架'. Auto-invoked for material layout or information-architecture changes, not routine frontend code."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../../_shared/resolve.md) and [sop-action](../../_shared/action.md).

# sop-layout

把用户的判断任务映射成信息层级和空间关系。

## 适用前提

任务会实质改变页面结构、信息架构、视觉层级或主要动作流。纯组件逻辑、文案、样式微调和局部 bug 不触发。

## 需要做

- 找出用户在页面上要快速完成的 1-3 个判断，不把“展示某物”当作判断。
- 把具体信息分成 primary、secondary、tertiary；primary 只保留完成主判断不可缺少的内容。
- 写出进入、操作、反馈、离开的动作流；需要比较的信息必须共屏。
- 让空间占比和位置反映优先级，明确哪些区域锁定、滚动或折叠；组件形态服从数据形态。
- 审计标题和面板 chrome：只保留数据对象或操作状态，删除重复容器身份的标题、边框和装饰。
- 能从现有约束和页面推导时直接执行；只有未决选择会改变结构时才向用户确认。

## 不需要做

- 不输出固定五级模板或为简单任务制造确认步骤。
- 不在信息架构判断里提前写具体 CSS/Tailwind 类名。
- 不替代具体 verb 的执行（scaffold、propose 等）；此 skill 只负责把信息架构前置。
- 不把一次性布局推导写成长文档或 durable memory。

## Action transition

- 信息架构清楚后进入具体执行 action。
- 仍有用户裁决时 transition 到 `grill`；目标边界仍不可见时 transition 到 `propose`。
