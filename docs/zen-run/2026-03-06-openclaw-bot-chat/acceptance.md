# 验收标准 - OpenCLAW 多 Agent 聊天功能

## 功能标准

### 后端模块
- [ ] 后端服务可以启动并监听端口
- [ ] GET /api/agents 返回 OpenCLAW Gateway 中的 agent 列表
- [ ] POST /api/chat 接收消息并转发到对应的 agent
- [ ] WebSocket 连接正常建立
- [ ] Agent 响应通过 WebSocket 推送到前端

### 前端模块
- [ ] 前端页面正常加载
- [ ] 显示 agent 列表（头像、名称、emoji）
- [ ] 可以发送消息
- [ ] @mention 正确解析
- [ ] 实时显示 agent 回复
- [ ] 显示 agent 执行结果

### 集成
- [ ] 前后端联调正常
- [ ] WebSocket 实时通信正常
- [ ] 消息可以触发 agent 响应

## 测试标准

- 新增测试总数 ≥ 24 条
- 每个公开函数 ≥ 3 条测试
- 覆盖正常路径、错误路径、边界情况

## 质量门控

- 所有单元测试通过
- 前端构建成功
- 后端服务启动无错误

## 循环退出承诺

<promise>ZEN_RUN_COMPLETE</promise>