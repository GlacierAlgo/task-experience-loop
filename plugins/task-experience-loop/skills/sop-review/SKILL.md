---
name: "sop-review"
description: "Read-only assessment of a known object against explicit criteria, ending in evidence-backed findings. Triggers: sop-review, 'review', '审查', '评审', '看看这个有没有问题', 'check this'."
---
> **Shared norms:** Before choosing or running this action, apply [sop-resolve](../../_shared/resolve.md) and [sop-action](../../_shared/action.md).

# sop-review

按标准给出发现，不直接修改。

## 适用前提

用户要判断一个已知 PR、diff、文件、目录、设计、产物或系统状态，已有可用评审标准，且当前不要求直接修。

## 需要做

- 明确评审对象、范围和标准。
- 用用户要求、TEL constraints、decisions、项目约定和证据支撑 findings。
- 区分事实、风险、假设和个人偏好。
- 按用户需要输出 verdict、问题盘点、风险清单或设计评审。
- 以 findings 结束当前只读 action；用户随后要求修改时，由共享 router 把它作为新行动选择。

## 不需要做

- 不直接修代码。
- 不把 reviewer 直觉变成新需求。
- 不把“更安全 / 更灵活 / 更完整”当作无证据要求。
- 不把局部 review 发现扩展成远目标计划，除非证据显示工作面本身未显影。
- 不把 review 发现本身写入 TEL。
