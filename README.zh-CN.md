*让 AI Agent 记住我们为什么这么做，也记住哪些办法真的管用。*

# Task Experience Loop（TEL）

[English](README.md) | 简体中文

Task Experience Loop（TEL）是给经常和 Codex、Claude Code 一起做长期项目的人准备的。它把任务、重要决定和真正有用的做法记在本地 Markdown 文件里。换一个会话后，Agent 仍然知道之前做过哪些取舍，不用每次都从头解释。

TEL 不会把每段对话都存下来，也不负责调度 Agent。它只记三类东西：还没做完的事、以后仍要遵守的决定，以及已经证明好用的办法。

## 为什么需要 TEL

一个项目做久了，最容易丢的往往不是代码，而是代码背后的来龙去脉：

- 为什么当时选择了 A，而不是同样可行的 B；
- 哪些约束跨任务、跨会话仍然成立；
- 遇到类似问题时，哪种办法以前试过而且有效；
- 当前项目正在推进什么，而不是所有项目混在一张任务板上；
- 经验积累后，哪些内容已经重复、过时或互相冲突。

TEL 把这些内容放在你自己的本地目录里，再根据当前 Git 项目挑出相关部分交给 Agent。这样既能接上以前的工作，也不必每次塞给它一大包历史记录。

## TEL 能帮你做什么

- **分开管理每个项目的任务**：每个项目只有 `Backlog` 和 `Active`，而且一次只推进一个 Active 任务。
- **把重要决定写清楚**：当时有哪些选择、为什么这样选，以及什么时候需要重新考虑。
- **记住真正好用的办法**：下次遇到类似情况，可以直接复用。
- **只给 Agent 当前需要的上下文**：`tel context` 会按当前仓库和任务生成 `loop-context.md`。
- **记住你自己的叫法**：机器名、项目代号和个人术语不用反复解释。
- **定期整理，但不擅自删除**：`tel compact` 只提出建议，改动原始记录前仍然要经过用户同意。
- **提供一组常用工作 skills**：探索、排错、评审、出方案、迁移和交付都有对应入口。

## 先跑起来

当前版本面向 macOS / Linux，需要 Python 3.12 或更高版本。

```bash
git clone https://github.com/GlacierAlgo/task-experience-loop.git
cd task-experience-loop

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .

export TEL_DIR="$HOME/.tel"
mkdir -p "$TEL_DIR"
```

当前代码里的默认数据路径还是开发者本机路径，所以其他用户现在需要明确设置 `TEL_DIR`。TEL 的数据都会放在这里，不需要数据库，也不会依赖外部服务。

安装 Codex 与 Claude Code skills：

```bash
./install.sh
```

安装脚本会把仓库中的 skills 软链接到 `~/.codex/skills/` 和 `~/.claude/skills/`。这种方式适合本地试用和开发：仓库里的 skill 一改，两边会立刻生效。

安装后不会自动在每次会话开始时读取 TEL。你可以显式调用 `$tel`，也可以在自己的 `AGENTS.md` 中加入 session-start 规则。

## 花一分钟试一下

在任意 Git 项目中运行：

```bash
tel task start "让搜索结果可解释"
tel context --stdout
tel task
```

完成后：

```bash
tel task done
```

TEL 会从最近的 Git 根目录推导项目名。非 Git 工作区可以设置 `TEL_PROJECT`：

```bash
TEL_PROJECT=my-project tel context --stdout
```

常用命令：

```bash
tel task add "下一项工作"       # 加入当前项目 Backlog
tel task start "当前工作"      # 开始任务；每个项目最多一个 Active
tel task done                   # 完成并从实时任务板移除
tel noun add dgx "DGX 执行机"  # 记录用户自己的全局名词
tel search architecture         # 搜索决策
tel compact                     # 生成经验池整理建议
```

## 文件放在哪里

`TEL_DIR` 中的主要内容：

```text
TEL_DIR/
├── kanban.md              # 所有项目尚未完成的承诺
├── constraints.md         # 跨项目约束
├── nouns.md               # 用户自己的全局名词
├── decisions/             # 决策记录
├── patterns/              # 可复用模式
├── summaries/             # 生成的索引、项目摘要和整理建议
├── archive/               # 已被替代的决策
└── loop-context.md        # 当前项目的生成上下文
```

项目专属决策会在 frontmatter 中用 `projects: [project-id]` 写明归属。TEL 不会因为正文里偶然提到某个项目名，就擅自把这条决定算到那个项目头上。

任务板只保存尚未完成的承诺：

```text
absent --add--> Backlog
absent/Backlog --start--> Active
Backlog/Active --done--> absent
```

做完的事情交给 Git、项目产物或会话记录保存，不再一直堆在任务板里。

## Skills

仓库目前包含 `tel` 协议 skill，以及 12 个行动型 SOP skills：

- 理解与设计：`sop-explore`、`sop-grill`、`sop-propose`、`sop-layout`
- 检查与修复：`sop-review`、`sop-diagnose`、`sop-conform`
- 结构变更：`sop-migrate`、`sop-reduce`、`sop-scaffold`
- 交付：`sop-ship`、`sop-upload`

这些 skills 不是一套必须逐条照做的流程。它们更像工作边界：告诉 Agent 什么时候该继续查、什么时候可以动手，以及什么情况必须回来问你。

## 它适合谁

TEL 比较适合：

- 单人或小团队长期使用编码 Agent；
- 同时维护多个仓库，又需要共享少量全局经验；
- 希望经验以 Markdown 保存在自己机器上；
- 希望重要决定能被检查、更新，也能在过时后删掉。

TEL 不试图成为：

- 聊天记录归档器或全量活动日志；
- 向量数据库或通用知识库；
- 多 Agent 调度器；
- 自动替用户决定哪些历史记录必须永久保留的黑盒记忆系统。

## 现在做到哪一步

TEL 目前是 `0.1.0`，已经可以在本地使用。CLI、分项目任务板、决策和模式索引、上下文生成、全局名词以及 `compact` 都已经能跑。

标准 Codex Plugin 还在准备中。正式 release 之前，更适合先在个人环境里试用，并把 `TEL_DIR` 放在一个会定期备份的本地目录中。
