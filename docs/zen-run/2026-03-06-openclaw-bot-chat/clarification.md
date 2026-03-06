# 澄清文档 - OpenCLAW 多 Agent 聊天功能

## 项目概述

构建一个 Web 聊天界面，让多个 OpenCLAW agent 可以在同一个网页中互相聊天和发出指令。

## 核心需求

| 需求 ID | 描述 |
|---------|------|
| REQ-01 | 通过 OpenCLAW Gateway REST API 获取所有 agent |
| REQ-02 | Web 聊天界面，支持多 agent 群聊 |
| REQ-03 | 每个 agent 有鲜明的图标（使用 identity.emoji/avatar） |
| REQ-04 | 支持 @mention 触发特定 agent |
| REQ-05 | 用户作为主持人，可以 @ 任何 agent |
| REQ-06 | 支持 agent 之间互相 @ |
| REQ-07 | 同时显示 agent 回复和执行结果 |

## 技术架构

- **前端**: React + TypeScript + Tailwind CSS
- **后端**: FastAPI (Python)
- **API**: OpenCLAW Gateway REST API
- **实时通信**: WebSocket

## 数据流

1. 前端连接 WebSocket
2. 后端调用 OpenCLAW API 获取 agent 列表
3. 用户发送消息（含 @agent-id）
4. 后端解析消息，转发到 OpenCLAW Gateway
5. Gateway 返回响应，通过 WebSocket 推送到前端

## 待定事项

- OpenCLAW Gateway 的具体 API 端点需实际测试确认
- Agent 图标渲染细节需进一步确认