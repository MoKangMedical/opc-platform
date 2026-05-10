"""
OPC Sync Hub - 报告生成器
生成HTML/JSON/Text格式的同步和健康报告
"""

import os, json, logging
from datetime import datetime
from typing import List
from pathlib import Path

logger = logging.getLogger("opc-report")

class ReportGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.reports_dir = os.path.expanduser(
            os.path.join(config.get("projects_dir", "~/Desktop/OPC"), "opc-sync-hub", "reports")
        )
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_sync_html(self, sync_result, health_report=None) -> str:
        """生成HTML格式同步报告"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Status counts
        status_counts = {}
        for r in sync_result.repos:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1

        # Build repo rows
        rows = []
        for r in sync_result.repos:
            status_class = {
                'ok': 'success', 'synced': 'success', 'pulled': 'info',
                'pushed': 'primary', 'behind': 'warning', 'ahead': 'warning',
                'error': 'danger', 'skip': 'secondary', 'no_git': 'secondary',
                'no_remote': 'secondary'
            }.get(r.status, 'secondary')

            status_label = {
                'ok': 'OK', 'synced': '已同步', 'pulled': '已拉取',
                'pushed': '已推送', 'behind': 'GitHub更新', 'ahead': '本地更新',
                'error': '错误', 'skip': '跳过', 'no_git': '无Git',
                'no_remote': '无Remote'
            }.get(r.status, r.status)

            rows.append(f"""
            <tr>
                <td><a href="https://github.com/MoKangMedical/{r.repo_name}" target="_blank">{r.name}</a></td>
                <td><span class="badge bg-{status_class}">{status_label}</span></td>
                <td>{r.local_date}</td>
                <td>{r.github_date}</td>
                <td>{r.dirty_count}/{r.untracked_count}</td>
                <td>{r.size_mb}MB</td>
                <td class="text-muted small">{r.message}</td>
            </tr>""")

        # Health section
        health_html = ""
        if health_report:
            health_badge = "success" if health_report.critical == 0 else "danger"
            issues_html = ""
            for issue in health_report.issues[:20]:
                icon = {"critical": "bi-exclamation-triangle-fill text-danger",
                        "warning": "bi-exclamation-circle-fill text-warning",
                        "info": "bi-info-circle-fill text-info"}.get(issue.severity, "bi-info-circle")
                issues_html += f'<tr><td><i class="{icon}"></i></td><td>{issue.category}</td><td>{issue.repo}</td><td>{issue.message}</td></tr>'

            health_html = f"""
            <div class="card mb-4">
                <div class="card-header"><i class="bi bi-heart-pulse"></i> 健康检查</div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col"><h4>{health_report.healthy}</h4><small class="text-muted">健康</small></div>
                        <div class="col"><h4 class="text-warning">{health_report.warnings}</h4><small class="text-muted">警告</small></div>
                        <div class="col"><h4 class="text-danger">{health_report.critical}</h4><small class="text-muted">严重</small></div>
                        <div class="col"><h4>{health_report.disk_free_gb}GB</h4><small class="text-muted">磁盘可用</small></div>
                    </div>
                    {'<table class="table table-sm mt-3"><tbody>' + issues_html + '</tbody></table>' if issues_html else '<p class="text-success mt-3">所有检查通过</p>'}
                </div>
            </div>"""

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OPC Sync Hub - {now}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body {{ background: #0d1117; color: #c9d1d9; }}
        .card {{ background: #161b22; border: #30363d; }}
        .table {{ color: #c9d1d9; }}
        .table td, .table th {{ border-color: #21262d; vertical-align: middle; }}
        .badge {{ font-weight: 500; }}
        .stat-card {{ background: #161b22; border-radius: 8px; padding: 20px; text-align: center; }}
        .stat-card h2 {{ margin: 0; font-size: 2rem; }}
        .stat-card small {{ color: #8b949e; }}
        .header {{ background: linear-gradient(135deg, #1a1f35 0%, #0d1117 100%); padding: 30px 0; border-bottom: 1px solid #30363d; }}
        a {{ color: #58a6ff; text-decoration: none; }}
        .text-muted {{ color: #8b949e !important; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1><i class="bi bi-arrow-left-right"></i> OPC Sync Hub</h1>
            <p class="text-muted mb-0">MoKangMedical 项目同步中心 | 最后更新: {now}</p>
        </div>
    </div>

    <div class="container py-4">
        <div class="row mb-4">
            <div class="col-md-2"><div class="stat-card"><h2>{sync_result.total}</h2><small>总项目</small></div></div>
            <div class="col-md-2"><div class="stat-card"><h2 class="text-success">{sync_result.ok}</h2><small>同步OK</small></div></div>
            <div class="col-md-2"><div class="stat-card"><h2 class="text-info">{sync_result.pulled}</h2><small>已拉取</small></div></div>
            <div class="col-md-2"><div class="stat-card"><h2 class="text-primary">{sync_result.pushed}</h2><small>已推送</small></div></div>
            <div class="col-md-2"><div class="stat-card"><h2 class="text-warning">{sync_result.skipped}</h2><small>跳过</small></div></div>
            <div class="col-md-2"><div class="stat-card"><h2 class="text-danger">{sync_result.errors}</h2><small>错误</small></div></div>
        </div>

        {health_html}

        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-folder2-open"></i> 项目列表</span>
                <span class="badge bg-secondary">{sync_result.total} 个仓库 | {sync_result.duration_seconds}s</span>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead><tr>
                            <th>项目名称</th><th>状态</th><th>本地日期</th>
                            <th>GitHub日期</th><th>变更</th><th>大小</th><th>备注</th>
                        </tr></thead>
                        <tbody>{''.join(rows)}</tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <script>setTimeout(()=>location.reload(), 300000);</script>
</body>
</html>"""
        return html

    def save_report(self, html: str, filename: str = None) -> str:
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path = os.path.join(self.reports_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

        # Also save as latest
        latest = os.path.join(self.reports_dir, "latest.html")
        with open(latest, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"Report saved: {path}")
        return path

    def generate_json(self, sync_result) -> str:
        data = {
            "timestamp": sync_result.timestamp,
            "summary": {
                "total": sync_result.total,
                "pulled": sync_result.pulled,
                "pushed": sync_result.pushed,
                "ok": sync_result.ok,
                "skipped": sync_result.skipped,
                "errors": sync_result.errors,
                "duration_seconds": sync_result.duration_seconds
            },
            "repos": [
                {
                    "name": r.name,
                    "status": r.status,
                    "local_date": r.local_date,
                    "github_date": r.github_date,
                    "dirty": r.dirty_count,
                    "size_mb": r.size_mb,
                    "message": r.message
                }
                for r in sync_result.repos
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
