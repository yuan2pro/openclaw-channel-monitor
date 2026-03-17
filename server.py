#!/usr/bin/env python3
"""
OpenClaw Pipeline Monitor - Channel-based task view
"""

import json
import os
import subprocess
import time
import glob
import re
from datetime import datetime
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENCLAW_DIR = os.path.expanduser("~/.openclaw")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Channel Monitor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #eee;
            min-height: 100vh;
        }
        
        .header {
            position: sticky;
            top: 0;
            background: linear-gradient(180deg, #0a0a0f 0%, rgba(10,10,15,0.98) 100%);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #00d9ff, #00ff88);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .logo-text {
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header-stats {
            display: flex;
            gap: 24px;
        }
        
        .stat {
            text-align: center;
            padding: 4px 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
        }
        
        .stat-value {
            font-size: 20px;
            font-weight: 700;
            color: #00d9ff;
        }
        
        .stat-label {
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
        }
        
        .container {
            padding: 16px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .channels-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
        }
        
        .channel-card {
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
            overflow: hidden;
            position: relative;
        }
        
        .channel-card.has-active {
            border-color: transparent;
        }
        
        .channel-card.has-active::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 12px;
            padding: 1px;
            background: linear-gradient(90deg, 
                rgba(0, 217, 255, 0.5), 
                rgba(0, 255, 136, 0.5), 
                rgba(0, 217, 255, 0.5)
            );
            background-size: 200% 100%;
            animation: channelGlow 3s linear infinite;
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
        }
        
        @keyframes channelGlow {
            0% { background-position: 0% 0; }
            100% { background-position: 200% 0; }
        }
        
        .channel-header {
            padding: 14px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .channel-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .channel-icon {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .channel-title {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .channel-name {
            font-size: 14px;
            font-weight: 600;
        }
        
        .channel-role {
            font-size: 11px;
            color: #00ff88;
            font-weight: 500;
        }
        
        .channel-role-desc {
            font-size: 10px;
            color: #555;
            padding: 6px 14px;
            background: rgba(255,255,255,0.02);
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }
        
        .channel-workload {
            padding: 8px 14px;
            background: rgba(255,255,255,0.01);
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }
        
        .workload-bar {
            height: 4px;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            border-radius: 2px;
            transition: width 0.5s ease;
            min-width: 2px;
        }
        
        .workload-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 6px;
        }
        
        .workload-percent {
            font-size: 11px;
            color: #00ff88;
            font-weight: 600;
        }
        
        .workload-tokens {
            font-size: 10px;
            color: #666;
        }
        
        .channel-count {
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 10px;
            background: rgba(255,255,255,0.08);
            color: #888;
        }
        
        .channel-count.active {
            background: rgba(255, 200, 0, 0.15);
            color: #ffc800;
        }
        
        .channel-model {
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 6px;
            background: rgba(0, 217, 255, 0.1);
            color: #00d9ff;
            font-weight: 500;
            margin-top: 4px;
            display: inline-block;
        }
        
        /* Channel colors */
        .channel-telegram .channel-icon { background: rgba(0, 136, 204, 0.15); }
        .channel-telegram .channel-name { color: #0088cc; }
        
        .channel-feishu .channel-icon { background: rgba(0, 200, 167, 0.15); }
        .channel-feishu .channel-name { color: #00c8a7; }
        
        .channel-qqbot .channel-icon { background: rgba(18, 183, 245, 0.15); }
        .channel-qqbot .channel-name { color: #12b7f5; }
        
        .channel-webchat .channel-icon { background: rgba(100, 150, 255, 0.15); }
        .channel-webchat .channel-name { color: #6496ff; }
        
        .channel-local .channel-icon { background: rgba(150, 150, 150, 0.15); }
        .channel-local .channel-name { color: #999; }
        
        .channel-content {
            padding: 12px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .task-item {
            background: rgba(255,255,255,0.02);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            border: 1px solid rgba(255,255,255,0.05);
            position: relative;
            overflow: hidden;
        }
        
        .task-item:last-child {
            margin-bottom: 0;
        }
        
        .task-item.active {
            background: rgba(0, 255, 136, 0.03);
        }
        
        /* 正在执行的任务 - 跑马灯边框效果 */
        .task-item.processing {
            border: none;
            background: rgba(0, 217, 255, 0.08);
            position: relative;
        }
        
        .task-item.processing::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 8px;
            padding: 2px;
            background: linear-gradient(90deg, 
                #00d9ff, #00ff88, #00d9ff, #00ff88, #00d9ff
            );
            background-size: 300% 100%;
            animation: borderRun 1s linear infinite;
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
        }
        
        /* 进度条跑马灯 */
        .task-item.processing .task-progress-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, 
                transparent 0%, #00d9ff 30%, #00ff88 50%, #00d9ff 70%, transparent 100%
            );
            background-size: 200% 100%;
            animation: progressRun 1.5s linear infinite;
            border-radius: 0 0 8px 8px;
        }
        
        @keyframes borderRun {
            0% { background-position: 0% 50%; }
            100% { background-position: 300% 50%; }
        }
        
        @keyframes progressRun {
            0% { background-position: 100% 0; }
            100% { background-position: -100% 0; }
        }
        
        /* 已完成的任务 - 静态，不亮灯 */
        .task-item.completed {
            border: 1px solid rgba(255,255,255,0.03);
            background: rgba(255,255,255,0.01);
            opacity: 0.5;
        }
        
        .task-indicator {
            font-size: 11px;
            margin-right: 4px;
        }
        
        .task-indicator.processing {
            animation: spin 1s linear infinite;
            display: inline-block;
        }
        
        .task-indicator.done {
            color: #00ff88;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* 已完成的任务 - 静态显示 */
        .task-item.completed {
            border: 1px solid rgba(100, 200, 100, 0.2);
            background: rgba(100, 200, 100, 0.02);
        }
        
        .task-item.completed .task-title::before {
            content: '✅ ';
        }
        
        /* 空闲任务 */
        .task-item.idle {
            opacity: 0.7;
        }
        
        .task-title {
            font-size: 13px;
            font-weight: 500;
            color: #fff;
        }
        
        .task-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }
        
        .task-sender {
            font-size: 10px;
            color: #00d9ff;
        }
        
        .task-time {
            font-size: 10px;
            color: #555;
        }
        
        .empty-state {
            text-align: center;
            padding: 20px;
            color: #444;
            font-size: 12px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #444;
        }
        
        .status-dot.online {
            background: #00ff88;
            box-shadow: 0 0 8px rgba(0, 255, 136, 0.5);
        }
        
        .status-dot.busy {
            background: #ffc800;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .refresh-btn {
            background: rgba(0, 217, 255, 0.1);
            border: 1px solid rgba(0, 217, 255, 0.2);
            color: #00d9ff;
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .refresh-btn:hover {
            background: rgba(0, 217, 255, 0.15);
        }
        
        ::-webkit-scrollbar {
            width: 4px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.02);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
        }
        
        .last-update {
            font-size: 11px;
            color: #444;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <div class="logo-icon">🏢</div>
            <div class="logo-text">DevCorp Monitor</div>
        </div>
        <div class="header-stats">
            <div class="stat">
                <div class="stat-value" id="active-channels">-</div>
                <div class="stat-label">工作角色</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="total-tasks">-</div>
                <div class="stat-label">进行任务</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="total-tokens">-</div>
                <div class="stat-label">Tokens</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="last-update">更新: <span id="last-update">-</span></span>
            <button class="refresh-btn" onclick="loadData()">🔄 刷新</button>
        </div>
    </div>
    
    <div class="container">
        <div class="channels-grid" id="channels-grid">
            <!-- 动态填充 -->
        </div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        
        const CHANNEL_CONFIG = {
            'telegram': { 
                name: 'Telegram', 
                icon: '📱', 
                color: '#0088cc',
                role: '💻 技术主管',
                roleDesc: '架构设计 · 代码审查 · 技术决策'
            },
            'feishu': { 
                name: '飞书', 
                icon: '🪽', 
                color: '#00c8a7',
                role: '🎯 产品经理',
                roleDesc: '需求分析 · 产品规划 · 用户故事'
            },
            'qqbot': { 
                name: 'QQ', 
                icon: '💬', 
                color: '#12b7f5',
                role: '🎨 设计师',
                roleDesc: '界面设计 · 用户体验 · 原型制作'
            },
            'webchat': { 
                name: 'Web', 
                icon: '🌐', 
                color: '#6496ff',
                role: '👨‍💻 工程师',
                roleDesc: '编码实现 · 功能开发 · Bug修复'
            }
        };
        
        function formatTokens(tokens) {
            if (!tokens) return '0';
            if (tokens >= 1000000) return (tokens / 1000000).toFixed(1) + 'M';
            if (tokens >= 1000) return (tokens / 1000).toFixed(1) + 'K';
            return tokens.toString();
        }
        
        function timeAgo(timestamp) {
            if (!timestamp) return '-';
            const seconds = Math.floor((Date.now() - timestamp) / 1000);
            if (seconds < 60) return '刚刚';
            if (seconds < 3600) return Math.floor(seconds / 60) + '分钟前';
            if (seconds < 86400) return Math.floor(seconds / 3600) + '小时前';
            return Math.floor(seconds / 86400) + '天前';
        }
        
        function createTaskItem(task, index) {
            const sender = task.sender || '';
            const status = task.status || 'idle';
            const isActive = task.isActive || false;
            const progress = task.taskProgress || 0;
            
            // 只有当前正在执行的任务才亮灯
            let statusClass = 'idle';
            if (status === 'working' && isActive) {
                statusClass = 'processing';
            } else if (task.title) {
                statusClass = 'completed';
            }
            
            // 简化工作内容显示
            let workContent = task.title || '未命名';
            
            // 截断过长的内容
            if (workContent.length > 20) {
                workContent = workContent.substring(0, 20) + '...';
            }
            
            // 进度条（仅在处理中时显示）
            const progressBar = statusClass === 'processing' 
                ? `<div class="task-progress-bar"></div>`
                : '';
            
            // 状态指示器
            const indicator = statusClass === 'processing' 
                ? '<span class="task-indicator processing">🔄</span>'
                : '<span class="task-indicator done">✓</span>';
            
            return `
                <div class="task-item ${statusClass}">
                    <div class="task-row">
                        <span class="task-title">${indicator} ${workContent}</span>
                        <span class="task-time">${timeAgo(task.updatedAt)}</span>
                    </div>
                    ${progressBar}
                </div>
            `;
        }
        
        function createChannelCard(channelKey, tasks) {
            const config = CHANNEL_CONFIG[channelKey] || { name: channelKey, icon: '📡', color: '#888', role: '未知角色', roleDesc: '' };
            const activeCount = tasks.filter(t => t.status === 'working' || t.isActive).length;
            const totalCount = tasks.length;
            const totalTokens = tasks.reduce((sum, t) => sum + (t.tokens || 0), 0);
            
            // Get unique models for this channel
            const models = [...new Set(tasks.map(t => t.model || 'unknown').filter(Boolean))];
            const modelDisplay = models.length > 0 ? models.join(', ') : '未知';
            
            const statusDot = activeCount > 0 
                ? '<div class="status-dot busy"></div>'
                : (totalCount > 0 ? '<div class="status-dot online"></div>' : '<div class="status-dot"></div>');
            
            const countClass = activeCount > 0 ? 'active' : '';
            const cardClass = activeCount > 0 ? 'has-active' : '';
            
            // Get workload percentage from global variable
            const workloadPercent = (window.channelWorkload && window.channelWorkload[channelKey]) || 0;
            
            let content = '';
            if (tasks.length > 0) {
                // 按活跃状态排序，然后按更新时间排序
                const sortedTasks = [...tasks].sort((a, b) => {
                    // 正在执行的任务排前面
                    if (a.status === 'working' && b.status !== 'working') return -1;
                    if (b.status === 'working' && a.status !== 'working') return 1;
                    // 然后按活跃状态
                    if (a.isActive && !b.isActive) return -1;
                    if (!a.isActive && b.isActive) return 1;
                    // 最后按更新时间
                    return (b.updatedAt || 0) - (a.updatedAt || 0);
                });
                // 显示更多任务（最多 10 个），确保已完成的任务也能看到
                content = sortedTasks.slice(0, 10).map(createTaskItem).join('');
            } else {
                content = '<div class="empty-state">💤 空闲等待任务...</div>';
            }
            
            return `
                <div class="channel-card ${cardClass}">
                    <div class="channel-header">
                        <div class="channel-info">
                            ${statusDot}
                            <div class="channel-icon">${config.icon}</div>
                            <div class="channel-title">
                                <span class="channel-name">${config.name}</span>
                                <span class="channel-role">${config.role}</span>
                                <span class="channel-model">🤖 ${modelDisplay}</span>
                            </div>
                        </div>
                        <span class="channel-count ${countClass}">${activeCount > 0 ? activeCount + ' 处理中' : (totalCount > 0 ? totalCount + ' 任务' : '空闲')}</span>
                    </div>
                    <div class="channel-role-desc">${config.roleDesc}</div>
                    <div class="channel-workload">
                        <div class="workload-bar" style="width: ${workloadPercent}%"></div>
                        <div class="workload-info">
                            <span class="workload-percent">${workloadPercent}% 工作量</span>
                            <span class="workload-tokens">📊 ${formatTokens(totalTokens)}</span>
                        </div>
                    </div>
                    <div class="channel-content">
                        ${content}
                    </div>
                </div>
            `;
        }
        
        async function loadData() {
            try {
                const res = await fetch(API_BASE + '/api/channels');
                const data = await res.json();
                
                // Update header stats
                document.getElementById('active-channels').textContent = data.activeChannels || 0;
                document.getElementById('total-tasks').textContent = data.totalTasks || 0;
                document.getElementById('total-tokens').textContent = formatTokens(data.totalTokens || 0);
                
                // Calculate workload percentage for each channel
                const totalTokens = data.totalTokens || 1; // Avoid division by zero
                const channelWorkload = {};
                for (const [key, tasks] of Object.entries(data.channels || {})) {
                    const channelTokens = tasks.reduce((sum, t) => sum + (t.tokens || 0), 0);
                    channelWorkload[key] = Math.round((channelTokens / totalTokens) * 100);
                }
                
                // Make it globally available
                window.channelWorkload = channelWorkload;
                
                // Render channels
                const grid = document.getElementById('channels-grid');
                const channelOrder = ['telegram', 'feishu', 'qqbot', 'webchat'];
                
                let html = '';
                for (const channelKey of channelOrder) {
                    const tasks = data.channels[channelKey] || [];
                    html += createChannelCard(channelKey, tasks);
                }
                
                // Add any other channels not in the default order
                for (const [key, tasks] of Object.entries(data.channels || {})) {
                    if (!channelOrder.includes(key)) {
                        html += createChannelCard(key, tasks);
                    }
                }
                
                grid.innerHTML = html;
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString('zh-CN');
                
            } catch (error) {
                console.error('Failed to load data:', error);
            }
        }
        
        // Initial load
        loadData();
        
        // Auto refresh every 5 seconds
        setInterval(loadData, 5000);
    </script>
</body>
</html>
"""


def parse_session_file(filepath):
    """Parse a session JSONL file to extract metadata"""
    info = {
        'sessionId': os.path.basename(filepath).replace('.jsonl', ''),
        'transcriptPath': filepath,
        'model': 'unknown',
        'channel': 'webchat',
        'title': '',
        'sender': '',
        'tokens': 0,
        'updatedAt': 0,
        'lastAction': '',
        'status': 'idle',
        'isActive': False,
        'currentTask': '',  # 当前正在执行的任务
        'taskProgress': 0   # 任务进度
    }
    
    try:
        stat = os.stat(filepath)
        info['updatedAt'] = int(stat.st_mtime * 1000)
        
        # Check if active in last 2 minutes (更短的时间窗口)
        age_seconds = (time.time() * 1000 - info['updatedAt']) / 1000
        info['isActive'] = age_seconds < 120  # 2 minutes
        info['status'] = 'working' if info['isActive'] else 'idle'
        
        last_user_msg = ''
        last_tool = ''
        tool_count = 0  # 工具调用次数
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # 从后往前读取，找到最近的工具调用
            for line in reversed(lines):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    
                    # Get model info
                    if data.get('type') == 'model_change':
                        info['model'] = data.get('modelId', 'unknown')
                    elif data.get('type') == 'custom' and data.get('customType') == 'model-snapshot':
                        info['model'] = data.get('data', {}).get('modelId', info['model'])
                    
                    # Get message info
                    if data.get('type') == 'message':
                        msg = data.get('message', {})
                        if msg.get('role') == 'assistant':
                            content = msg.get('content', [])
                            if isinstance(content, list):
                                for item in content:
                                    if item.get('type') == 'toolCall':
                                        tool_name = item.get('name', '')
                                        if tool_name and not last_tool:
                                            last_tool = tool_name
                                            tool_count += 1
                            
                            usage = msg.get('usage', {})
                            if usage.get('totalTokens'):
                                info['tokens'] += usage['totalTokens']
                        
                        elif msg.get('role') == 'user':
                            content = msg.get('content', [])
                            if isinstance(content, list) and len(content) > 0:
                                text = content[0].get('text', '')
                                
                                # Detect channel - 优先从 System 消息前缀检测（最可靠）
                                # 格式 1: System: [2026-03-17 22:03:29 GMT+8] Feishu[default] DM | ...
                                # 格式 2: System: [...] QQ[...] 或 Telegram[...]
                                if text.startswith('System:') or '[GMT' in text:
                                    if 'Feishu[' in text:
                                        info['channel'] = 'feishu'
                                    elif 'Telegram[' in text or 'telegram:direct' in text.lower():
                                        info['channel'] = 'telegram'
                                    elif 'QQ[' in text or 'qqbot:direct' in text.lower() or 'qqbot:c2c' in text.lower():
                                        info['channel'] = 'qqbot'
                                    elif 'openclaw-control-ui' in text or 'openclaw-tui' in text:
                                        info['channel'] = 'webchat'
                                # QQ 特殊格式：ROBOT1.0_USO9tjr4（消息 ID 包含 QQ 特征）
                                elif 'ROBOT1.0_' in text or 'qqbot:c2c' in text.lower():
                                    info['channel'] = 'qqbot'
                                # Fallback: 从消息内容检测
                                elif 'Feishu' in text or '飞书' in text:
                                    info['channel'] = 'feishu'
                                elif 'QQ' in text or 'qqbot' in text.lower():
                                    info['channel'] = 'qqbot'
                                elif 'Telegram' in text or 'telegram' in text or 'telegram:direct' in text.lower():
                                    info['channel'] = 'telegram'
                                elif 'webchat' in text.lower() or 'openclaw-tui' in text:
                                    info['channel'] = 'webchat'
                                
                                # Extract sender
                                if '"label"' in text or '"name"' in text:
                                    label_match = re.search(r'"label"\s*:\s*"([^"]+)"', text)
                                    if label_match:
                                        label = label_match.group(1)
                                        label_clean = re.sub(r'\s*\([^)]{10,}\)', '', label).strip()
                                        if label_clean and not label_clean.startswith('ou_') and not label_clean.startswith('A836') and len(label_clean) < 30:
                                            info['sender'] = label_clean
                                    
                                    if not info['sender']:
                                        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', text)
                                        if name_match:
                                            name = name_match.group(1)
                                            if name and not name.startswith('ou_') and not name.startswith('A836') and len(name) < 30:
                                                info['sender'] = name
                                
                                # Extract user message
                                if not text.startswith('A new session') and not text.startswith('Read HEARTBEAT') and not text.startswith('System:') and not text.startswith('Conversation info') and not text.startswith('Sender (untrusted metadata)'):
                                    clean = text
                                    clean = re.sub(r'```json\s*.*?```', '', clean, flags=re.DOTALL)
                                    clean = re.sub(r'Conversation info.*?```', '', clean, flags=re.DOTALL)
                                    clean = re.sub(r'Sender \(untrusted metadata\).*?```', '', clean, flags=re.DOTALL)
                                    clean = re.sub(r'\[.*?GMT\+8\]', '', clean)
                                    clean = re.sub(r'你正在通过.*?【.*?】', '', clean, flags=re.DOTALL)
                                    clean = re.sub(r'System:.*', '', clean)
                                    clean = ' '.join(clean.split()).strip()
                                    if clean and len(clean) > 2 and not last_user_msg:
                                        last_user_msg = clean
                    
                except:
                    continue
        
        # Extract current task details
        current_task_detail = ''
        last_tool_name = ''
        
        # 从后往前读取，找到最近的工具调用及其参数
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for line in reversed(lines[-100:]):  # 只看最后100行
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if data.get('type') == 'message':
                        msg = data.get('message', {})
                        if msg.get('role') == 'assistant':
                            content = msg.get('content', [])
                            if isinstance(content, list):
                                for item in reversed(content):
                                    if item.get('type') == 'toolCall':
                                        tool_name = item.get('name', '')
                                        args = item.get('arguments', {})
                                        
                                        if not last_tool_name:
                                            last_tool_name = tool_name
                                        
                                        # 构建详细任务描述
                                        if tool_name == 'read':
                                            path = args.get('path', args.get('file_path', ''))
                                            if path:
                                                filename = path.split('/')[-1] if '/' in str(path) else str(path)
                                                current_task_detail = f"读取: {filename}"
                                        
                                        elif tool_name == 'write':
                                            path = args.get('file_path', args.get('path', ''))
                                            content_preview = args.get('content', '')[:20] if args.get('content') else ''
                                            if path:
                                                filename = path.split('/')[-1] if '/' in str(path) else str(path)
                                                current_task_detail = f"保存: {filename}"
                                        
                                        elif tool_name == 'edit':
                                            path = args.get('file_path', args.get('path', ''))
                                            if path:
                                                filename = path.split('/')[-1] if '/' in str(path) else str(path)
                                                current_task_detail = f"编辑: {filename}"
                                        
                                        elif tool_name == 'exec':
                                            cmd = str(args.get('command', ''))[:25]
                                            if cmd:
                                                current_task_detail = f"执行: {cmd}"
                                        
                                        elif tool_name == 'web_search':
                                            q = str(args.get('query', ''))[:18]
                                            if q:
                                                current_task_detail = f"搜索: {q}"
                                        
                                        elif tool_name == 'web_fetch':
                                            url = str(args.get('url', ''))[:20]
                                            if url:
                                                current_task_detail = f"获取: {url}"
                                        
                                        elif tool_name == 'browser':
                                            action = args.get('action', '操作')
                                            current_task_detail = f"浏览器: {action}"
                                        
                                        elif tool_name == 'message':
                                            action = args.get('action', '')
                                            target = args.get('target', args.get('channel', ''))
                                            if target:
                                                current_task_detail = f"消息→{str(target)[:15]}"
                                            elif action:
                                                current_task_detail = f"消息: {action}"
                                        
                                        elif tool_name == 'qveris_discover':
                                            q = str(args.get('query', ''))[:15]
                                            current_task_detail = f"发现API: {q}" if q else "发现API"
                                        
                                        elif tool_name == 'qveris_call':
                                            tool_id = str(args.get('tool_id', ''))[:20]
                                            current_task_detail = f"调用: {tool_id}" if tool_id else "调用API"
                                        
                                        elif tool_name == 'sessions_list':
                                            current_task_detail = "查看会话列表"
                                        
                                        elif tool_name == 'sessions_send':
                                            msg_preview = str(args.get('message', ''))[:15]
                                            current_task_detail = f"发送: {msg_preview}" if msg_preview else "发送消息"
                                        
                                        elif tool_name == 'sessions_spawn':
                                            task = str(args.get('task', ''))[:15]
                                            current_task_detail = f"启动代理: {task}" if task else "启动代理"
                                        
                                        elif tool_name == 'memory_search':
                                            q = str(args.get('query', ''))[:12]
                                            current_task_detail = f"搜索记忆: {q}" if q else "搜索记忆"
                                        
                                        elif tool_name == 'gateway':
                                            action = args.get('action', '')
                                            current_task_detail = f"网关: {action}" if action else "网关配置"
                                        
                                        elif tool_name == 'process':
                                            action = args.get('action', '')
                                            current_task_detail = f"进程: {action}" if action else "管理进程"
                                        
                                        elif tool_name == 'subagents':
                                            action = args.get('action', '')
                                            current_task_detail = f"代理: {action}" if action else "管理代理"
                                        
                                        elif tool_name:
                                            # 默认显示工具名
                                            tool_names = {
                                                'qveris_inspect': '检查API',
                                                'qveris_execute': '执行查询',
                                                'tts': '语音合成',
                                                'switch_model': '切换模型',
                                                'session_status': '查看状态',
                                                'sessions_history': '获取历史',
                                                'memory_get': '读取记忆',
                                                'cron': '定时任务',
                                                'feishu_im_user_message': '飞书消息',
                                                'feishu_calendar_event': '飞书日程',
                                                'feishu_task_task': '飞书任务'
                                            }
                                            if not current_task_detail:
                                                current_task_detail = tool_names.get(tool_name, tool_name)
                                        
                                        if current_task_detail:
                                            break
                    if current_task_detail:
                        break
                except:
                    continue
        
        # Set title with detail
        if current_task_detail:
            info['title'] = current_task_detail
            info['currentTask'] = current_task_detail
        elif last_user_msg:
            info['title'] = last_user_msg[:50]
        else:
            info['title'] = "会话"
        
        if last_tool and info['isActive']:
            info['status'] = 'working'
            info['lastAction'] = last_tool
            
    except:
        pass
    
    return info


def get_channels_data():
    """Get data grouped by channel"""
    sessions = []
    agents_dir = os.path.join(OPENCLAW_DIR, "agents")
    
    # Load sessions.json to get deliveryContext channel (反映消息实际来源)
    sessions_meta = {}
    sessions_json_path = os.path.join(agents_dir, "main", "sessions", "sessions.json")
    if os.path.exists(sessions_json_path):
        try:
            with open(sessions_json_path, 'r') as f:
                sessions_data = json.load(f)
                for session_key, session_info in sessions_data.items():
                    session_id = session_info.get('sessionId', '')
                    # 使用 deliveryContext.channel 判断渠道（反映实际消息来源）
                    dc_channel = session_info.get('deliveryContext', {}).get('channel', '')
                    if dc_channel in ['telegram', 'feishu', 'qqbot', 'webchat']:
                        sessions_meta[session_id] = dc_channel
        except:
            pass
    
    for agent_path in glob.glob(os.path.join(agents_dir, "*")):
        sessions_dir = os.path.join(agent_path, "sessions")
        if os.path.isdir(sessions_dir):
            for session_file in glob.glob(os.path.join(sessions_dir, "*.jsonl")):
                session_info = parse_session_file(session_file)
                # 使用 deliveryContext.channel 覆盖（更准确，反映实际消息来源）
                session_id = session_info.get('sessionId', '')
                if session_id in sessions_meta:
                    session_info['channel'] = sessions_meta[session_id]
                sessions.append(session_info)
    
    # Group by channel
    channels = {}
    for session in sessions:
        channel = session.get('channel', 'webchat')
        if channel not in channels:
            channels[channel] = []
        channels[channel].append(session)
    
    # Add running processes as "local" channel - 已禁用，只显示AI角色
    # try:
    #     result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
    #     if result.returncode == 0:
    #         local_tasks = []
    #         for line in result.stdout.split('\n'):
    #             if ('openclaw' in line.lower() or 'python' in line.lower()) and 'server.py' not in line:
    #                 parts = line.split()
    #                 if len(parts) >= 11:
    #                     cmd = ' '.join(parts[10:15])
    #                     proc_name = cmd.split()[0] if cmd.split() else cmd
    #                     if '/' in proc_name:
    #                         proc_name = proc_name.split('/')[-1]
    #                     local_tasks.append({
    #                         'channel': 'local',
    #                         'title': f'🔄 {proc_name}',
    #                         'sender': '系统进程',
    #                         'model': 'system',
    #                         'status': 'working',
    #                         'lastAction': cmd[:35],
    #                         'isActive': True,
    #                         'updatedAt': int(time.time() * 1000)
    #                     })
    #         if local_tasks:
    #             channels['local'] = local_tasks
    # except:
    #     pass
    
    # Sort each channel's tasks by activity
    for channel in channels:
        channels[channel].sort(key=lambda x: (x.get('isActive', False), x.get('updatedAt', 0)), reverse=True)
    
    # Calculate totals
    total_tasks = sum(len(tasks) for tasks in channels.values())
    total_tokens = sum(t.get('tokens', 0) for tasks in channels.values() for t in tasks)
    active_channels = sum(1 for tasks in channels.values() if any(t.get('isActive') or t.get('status') == 'working' for t in tasks))
    
    return {
        'channels': channels,
        'totalTasks': total_tasks,
        'totalTokens': total_tokens,
        'activeChannels': active_channels
    }


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/channels')
def api_channels():
    return jsonify(get_channels_data())


@app.route('/api/sessions')
def api_sessions():
    channels_data = get_channels_data()
    all_sessions = []
    for tasks in channels_data['channels'].values():
        all_sessions.extend(tasks)
    return jsonify({
        "count": len(all_sessions),
        "sessions": all_sessions[:50],
        "totalTokens": channels_data['totalTokens']
    })


@app.route('/api/pipeline')
def api_pipeline():
    channels_data = get_channels_data()
    all_tasks = []
    for tasks in channels_data['channels'].values():
        all_tasks.extend(tasks)
    
    now = time.time() * 1000
    return {
        "processing": [t for t in all_tasks if t.get('status') == 'working' or t.get('isActive')][:10],
        "input": [t for t in all_tasks if not t.get('isActive') and (now - t.get('updatedAt', 0)) < 1800000][:10],
        "done": [t for t in all_tasks if not t.get('isActive')][:10],
        "queue": [],
        "output": []
    }


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    print("🚀 Starting OpenClaw Channel Monitor...")
    print("📍 Dashboard: http://localhost:5050")
    print("Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True)