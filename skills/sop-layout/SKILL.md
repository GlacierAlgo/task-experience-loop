---
name: "sop-layout"
description: "Front-load information architecture before writing any frontend code. Produces a 5-level reflection chain that maps user judgment to spatial layout. Triggers: sop-layout, 'layout', '布局', '页面结构', '前端骨架'. Auto-invoked: any task producing HTML, JSX, React components, or frontend pages must run this skill before writing code."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../_shared/resolve.md) and [sop-action](../_shared/action.md).

# sop-layout

写前端代码之前，先完成信息架构的反思链，把用户的判断任务映射到空间分配。

## 适用前提

任务会产出 HTML、JSX、React 组件或前端页面。无论是新页面还是对既有页面的布局重构，都必须先跑这条链。

**自动前置**：agent 识别到任务涉及前端页面输出时，自动进入此 skill，不需要用户显式调用。显式调用（`/sop-layout`、`layout`、`布局`）作为 fallback 同样触发。

## 需要做

### 反思链（5 级，全部填完并输出给用户确认后才能写代码）

Agent 必须将填完的链作为结构化输出呈现给用户。用户确认后进入代码阶段。任何一级填不出来，说明对任务理解不足，应先通过上下文补齐或问用户。

---

#### Level 1: 判断锚点

```
{用户在这个页面要快速回答的 1-3 个问题}
```

约束：
- 问题必须是判断句，不是"展示X"。错："展示策略列表"；对："哪些策略值得深看"。
- 超过 3 个 → 页面职责不单一，先拆页面或确认哪个是首屏主任务。
- 问题之间有推进关系（A 的答案触发 B），不是并列。

---

#### Level 2: 信息依赖图

```
primary:   {回答主问题的最小信息集 — 缺任何一个则无法做判断}
secondary: {加深/确认判断的补充信息 — 不看也能做初步判断}
tertiary:  {偶尔查看的参考/诊断/历史 — 多数时候折叠不影响}
```

约束：
- 每级列具体数据单元（如"策略排名表 + 核心 KPI"），不写"相关信息"。
- primary 总量不超过 3-4 个信息单元，超过说明主次没分清。
- 一个信息单元只出现在一级。

---

#### Level 3: 动作流

```
{用户从哪进入} → {做什么操作} → {看到什么反馈} → {带着什么结论离开或进入下一步}
```

约束：
- 必须是动词链，不是名词列表。错："排名、详情、图表"；对："扫排名 → 点选 → 看详情 → 判断是否异常"。
- 每步标注"这步需要看到什么才能做下一步"，直接决定哪些信息必须共屏。
- 两步信息必须同时可见才能比对 → 它们必须在同一视口内。

---

#### Level 4: 空间映射

```
{primary} → 视觉中心 / 最大面积 / 首屏必见
{secondary} → 侧边或紧邻主区 / 首屏可见但面积受限
{tertiary} → 下沉到首屏下方 / 折叠 / tab 切换
布局方向: {跟随动作流 — 动作从左到右则左→右分栏，从上到下则上下切}
```

约束：
- 面积比例反映主次 — primary ≥ 50% 首屏面积。
- 动作流中"必须共屏"的信息不允许分到需要滚动才能看到的区域。
- 明确写出：什么区域内部可滚动（数据列表），什么区域视口锁定（KPI/状态）。
- 数据形态决定组件形态 — 没有时间序列不放折线图，只有分类统计就用柱/表。
- 默认目标视口 1920×1080；基础类直接写桌面端样式，不用 md:/lg: 前缀。移动端用显式 `@media` 或 `sm:` 做降级单列。

---

#### Level 5: Chrome 审计

```
对每一个计划中的标题/header/面板头：
- {标题文本} → 传递的是 [数据对象 | 操作状态 | 容器名]
```

规则：
- 传递数据对象（策略名、run id）→ 保留。
- 传递操作状态（"3/840 selected"、"OK · 6 holdings"）→ 保留。
- 重述容器已表达的身份（区域叫 Inspector 然后标题写 "Inspector"）→ 删除。
- 布局边框/位置已经表达区域身份时，eyebrow 是冗余 → 删除。
- 表格有表头时，不需要面板标题复述内容类型。
- 标题呈现数据对象或操作状态，不命名容器。

---

### 输出格式

Agent 将 5 级链填完后，以结构化 markdown 输出给用户，标题为 `## Layout Reflection`，每级一个小节。用户确认（或调整）后才进入代码阶段。

如果用户说"跳过"或明确表示不需要反思链（如简单的单组件修改不涉及布局），agent 可以跳过。

## 不需要做

- 不写长布局文档，5 级链以精炼为目标。
- 不在链里写具体 CSS/Tailwind 类名 — 那是代码阶段的事。
- 不替代具体 verb 的执行（scaffold、propose 等）；此 skill 只负责把信息架构前置。
- 不对纯组件逻辑修改（如修 bug、改数据处理）强制跑链 — 只有涉及布局/页面结构时触发。
- 不把这条链当作 UI 设计规范文档，它只是一次性的前置推导。

## Action transition

- 链确认后 transition 到具体执行 action（scaffold、propose 或直接编码）。
- 如果填链时发现目标模糊或工作面不清晰，transition 到 `grill` 或 `bootstrap`。
- 任务完成且用户转向新 topic 时 transition 到 `upload`。

## TEL 写入

此 skill 本身通常不写 TEL — 链是一次性产物。只有当反思链的某个决定具有跨任务复用价值（如"我们的所有数据看板都遵循三栏研究流"），且通过 TEL 写入闸门时，才写 decision 或 pattern。
