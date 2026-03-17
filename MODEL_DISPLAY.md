# DevCorp Monitor - 模型显示功能

## 更新内容

已在 DevCorp Monitor 页面 (http://192.168.1.2:5050/) 添加了**模型显示功能**。

### 显示位置

每个渠道卡片的标题下方会显示当前使用的模型，格式如下：

```
🤖 qwen3.5-plus
```

### 功能特点

- **实时显示**: 每 5 秒自动刷新，显示各渠道最新使用的模型
- **多模型支持**: 如果渠道使用了多个模型，会显示所有模型（如：`qwen3.5-plus, kimi-k2.5`）
- **颜色主题**: 模型标签使用青色主题 (#00d9ff)，与整体 UI 风格一致

### 当前配置

| Channel | 模型 |
|---------|------|
| Telegram | bailian/qwen3.5-plus |
| 飞书 (Feishu) | bailian/qwen3.5-plus |
| QQ 机器人 | bailian/qwen3.5-plus |
| Web | bailian/qwen3.5-plus (默认) |

### 修改的文件

- `/home/n100/.openclaw/workspace/openclaw-monitor/server.py`
  - 添加了 `.channel-model` CSS 样式
  - 在 `createChannelCard` 函数中提取模型信息
  - 在渠道卡片标题中显示模型标签

### 重启服务

```bash
# 重启监控服务
pkill -f "openclaw-monitor.*server.py"
cd ~/.openclaw/workspace/openclaw-monitor && python3 server.py &
```

### 数据来源

模型信息来自 OpenClaw 配置文件 `/home/n100/.openclaw/openclaw.json` 中的 `channels.modelByChannel` 配置：

```json
{
  "channels": {
    "modelByChannel": {
      "telegram": { "*": "bailian/qwen3.5-plus" },
      "feishu": { "*": "bailian/qwen3.5-plus" },
      "qqbot": { "*": "bailian/qwen3.5-plus" }
    }
  }
}
```

---

*最后更新：2026-03-17 22:45 (Asia/Shanghai)*
