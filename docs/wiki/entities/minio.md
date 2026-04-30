---
title: MinIO
type: entity
created: 2026-04-29
updated: 2026-04-29
tags: [infra, storage]
related: [[concepts/tech-stack]]
---

# MinIO

- 镜像：`minio/minio:RELEASE.2025-02-28T09-55-16Z`
- API 端口：9000 / 控制台端口：9001
- 默认 Bucket：`max-agent`
- 用途：文件上传、对象存储与静态资源管理
- 数据卷：`./docker-data/minio/data`
- 配置卷：`./infra/minio/config`
