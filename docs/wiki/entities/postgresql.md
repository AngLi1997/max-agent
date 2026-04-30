---
title: PostgreSQL
type: entity
created: 2026-04-29
updated: 2026-04-29
tags: [infra, database]
related: [[concepts/data-model]], [[concepts/tech-stack]]
---

# PostgreSQL

- 镜像：`pgvector/pgvector:pg17`（内置 pgvector 扩展）
- 端口：5432
- 默认库：`max_agent`
- 用途：核心业务数据持久化 + 向量检索
- 数据卷：`./docker-data/postgres`
- 初始化脚本：`./infra/postgres/init/`
