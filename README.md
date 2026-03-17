# OpenClaw Channel Monitor

🏢 **DevCorp Monitor** - OpenClaw 多渠道任务监控仪表盘

实时监控 OpenClaw 各渠道（飞书、QQ、Telegram、Web）的任务执行状态、模型使用情况和 Token 消耗。

![Dashboard](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ 功能特性

- 📊 **多渠道监控** - 同时监控飞书、QQ、Telegram、Web 等渠道的任务
- 🤖 **模型显示** - 实时显示每个渠道使用的 AI 模型
- ⚡ **实时更新** - 每 5 秒自动刷新任务状态
- 🎨 **精美 UI** - 深色主题，动态效果，任务状态一目了然
- 📈 **工作量统计** - 按渠道统计 Token 消耗和工作量百分比

## 🚀 快速开始

### 前置要求

- Python 3.8+
- OpenClaw 已安装并运行
- Flask, Flask-CORS

### 安装依赖

```bash
pip install flask flask-cors
```

### 启动服务

```bash
# 方式 1: 直接启动
python3 server.py

# 方式 2: 使用启动脚本
./start.sh

# 方式 3: Docker 部署
docker-compose up -d
```

### 访问仪表盘

打开浏览器访问：http://localhost:5050

## 📁 项目结构

```
openclaw-monitor/
├── server.py              # 主服务程序
├── README.md              # 项目说明
├── docker-compose.yml     # Docker 编排
├── Dockerfile             # Docker 镜像
├── install-service.sh     # 安装 systemd 服务
├── openclaw-monitor.service  # systemd 服务配置
└── start.sh               # 启动脚本
```

## 🔧 配置说明

服务会自动从 OpenClaw 的数据目录读取会话信息：
- 会话文件：`~/.openclaw/agents/main/sessions/*.jsonl`
- 会话元数据：`~/.openclaw/agents/main/sessions/sessions.json`

无需额外配置，启动即可使用。

## 📊 API 接口

| 接口 | 说明 |
|------|------|
| `GET /` | 仪表盘页面 |
| `GET /api/channels` | 各渠道任务数据 |
| `GET /api/sessions` | 所有会话列表 |
| `GET /health` | 健康检查 |

### API 响应示例

```json
{
  "channels": {
    "feishu": [
      {
        "sessionId": "xxx",
        "title": "执行：cat ~/.openclaw/openclaw.",
        "model": "qwen3.5-plus",
        "status": "idle",
        "isActive": false,
        "tokens": 1234,
        "updatedAt": 1773759782725
      }
    ],
    "qqbot": [...],
    "telegram": [...],
    "webchat": [...]
  },
  "totalTasks": 8,
  "totalTokens": 9060341,
  "activeChannels": 2
}
```

## 🛠️ 部署为系统服务

```bash
# 安装 systemd 服务
sudo ./install-service.sh

# 启动服务
sudo systemctl start openclaw-monitor

# 开机自启
sudo systemctl enable openclaw-monitor

# 查看状态
sudo systemctl status openclaw-monitor
```

## 📝 更新日志

### 2026-03-18
- ✅ 修复渠道识别错误（QQ/飞书消息混淆问题）
- ✅ 添加模型显示功能
- ✅ 优化任务排序逻辑（活跃任务优先）
- ✅ 增加任务显示数量（最多 10 个/渠道）

### 2026-03-17
- ✅ 初始版本发布
- ✅ 支持多渠道监控
- ✅ 实时任务状态更新

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**Made with ❤️ for OpenClaw Community**
