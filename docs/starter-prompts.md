# Standard 2.3 Starter Prompts

## Formal Project

```text
请使用 $paper-workflow-orchestrator 完成这个数学建模项目。
赛题和官方附件已放在 problem_files/。
先运行 preflight_check.py 和 workflow_guard.py --status，再按 S0-S8 推进。
所有当前赛题代码写入 paper_output/code/，真实结果、图表、表格、证据和论文写入 paper_output/。
S6 evidence gate 必须使用 official 模式并保持输入哈希新鲜。
S7 使用 Standard 单一正式主线：写作计划、完整章节草稿、逐章审计、必要时排队局部修复、确定性合并、全文统一改写、最终 Markdown 审计。
默认完整竞赛稿，可分多轮完成章节。核对当年赛题的页数限制，每个子问题充分展开推导、计算结果和验证；不要把单次回复当完整论文，也不要凑字凑页。除非我明确要求短稿，否则不改 short-report / smoke-test 或降低验收范围。
不要把 quickstart、legacy 或机械微单元合并稿提升为正式稿。
只有 authoring PASS 后才生成 final_paper.docx，并用 LibreOffice 执行 --render required。
任一门禁失败时继续修复，不要声称已经完成。
```

## Huawei Cup Beginner Guided Project

第一次参加华为杯/研究生数学建模类比赛时，推荐使用 [华为杯新手使用指南](huawei-cup-beginner.md)，并先启用 `beginner-guided` profile。

```text
Codex:       python .agents/skills/paper-workflow-orchestrator/scripts/workflow_profile.py --set beginner-guided
Claude Code: python .claude/skills/paper-workflow-orchestrator/scripts/workflow_profile.py --set beginner-guided
Trae:        python .trae/skills/paper-workflow-orchestrator/scripts/workflow_profile.py --set beginner-guided
```

启用后读取 `paper_output/context/workflow_profile.json`。该 profile 只约束 S1-S5 的执行策略：基线优先、真实基线运行后才能按触发条件升级模型、多个方案比较精度/稳定性/可解释性/实现成本，并提供简短阶段解释；S6-S8 的正式交付门禁保持不变。

## Resume An Interrupted Project

```text
请使用 $paper-workflow-orchestrator 恢复这个项目。
先运行 workflow_guard.py --status，读取 workflow_guard_report.json、workflow_memory.json 和当前文件哈希。
如果项目存在 paper_output/context/workflow_profile.json，也先读取它并继续遵守当前 profile。
从第一个失败阶段继续，不要凭对话记忆重跑已完成阶段，也不要跳过 S6-S8。
```

## Repair A Failing Section

```text
请先读取 writing_plan.json、authoring_state.json、draft_audit.json 和 repair_queue.json。
如果队列策略是 section-rewrite，使用 $paper-formal-writer 重写完整章节。
只有策略明确为 micro-repair 时才使用 $paper-micro-unit-generator，并且只修复队列指定的章节、证据或段落。
修复后重新运行 validate_authoring.py --section <section-id>。
```

## Installation Smoke Test

```text
请运行当前平台 paper-workflow-orchestrator/scripts/quickstart_run.py，只验证安装和基础契约。
确认所有草稿只出现在 paper_output/quickstart/，并确认没有生成 final_paper_source.md、final_paper.docx 或其他正式命名文件。
```

## Platform Script Roots

```text
Codex       -> .agents/skills/
Claude Code -> .claude/skills/
Trae        -> .trae/skills/
```
