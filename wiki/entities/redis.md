---
title: Redis
type: entity
created: 2026-04-29
updated: 2026-04-29
tags: [infra, cache]
related: [[concepts/tech-stack]]
---

# Redis

- 镜像：`redis:7.4-alpine`
- 端口：6379
- 用途：缓存、会话态辅助存储、令牌状态管理
- 配置文件：`./infra/redis/redis.conf`
- 数据卷：`./docker-data/redis`
