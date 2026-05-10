"""
OPC Sync Hub - 健康检查器
检查所有仓库的健康状态
"""

import os, subprocess, shutil, logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List
from pathlib import Path

logger = logging.getLogger("opc-health")

@dataclass
class HealthIssue:
    severity: str       # critical / warning / info
    category: str       # git / disk / remote / config
    repo: str
    message: str

@dataclass
class HealthReport:
    timestamp: str = ""
    total_repos: int = 0
    healthy: int = 0
    warnings: int = 0
    critical: int = 0
    disk_usage_gb: float = 0
    disk_free_gb: float = 0
    issues: List[HealthIssue] = field(default_factory=list)

class HealthChecker:
    def __init__(self, config: dict):
        self.config = config
        self.health_cfg = config.get("health", {})
        self.projects_dir = os.path.expanduser(config.get("projects_dir", "~/Desktop/OPC"))
        self.max_repo_size_gb = self.health_cfg.get("max_repo_size_gb", 20)
        self.max_dirty_days = self.health_cfg.get("max_dirty_days", 7)

    def check_disk(self, report: HealthReport):
        """检查磁盘空间"""
        try:
            usage = shutil.disk_usage(self.projects_dir)
            report.disk_usage_gb = round(usage.used / (1024**3), 1)
            report.disk_free_gb = round(usage.free / (1024**3), 1)

            if report.disk_free_gb < 5:
                report.issues.append(HealthIssue(
                    "critical", "disk", "*",
                    f"磁盘空间不足: 仅剩 {report.disk_free_gb}GB"
                ))
            elif report.disk_free_gb < 20:
                report.issues.append(HealthIssue(
                    "warning", "disk", "*",
                    f"磁盘空间偏低: {report.disk_free_gb}GB 可用"
                ))
        except Exception as e:
            logger.error(f"Disk check error: {e}")

    def check_repos(self, report: HealthReport):
        """检查所有仓库健康状态"""
        for item in sorted(os.listdir(self.projects_dir)):
            target = os.path.join(self.projects_dir, item)
            if not os.path.isdir(target) or item.startswith('.'):
                continue

            report.total_repos += 1
            issues_before = len(report.issues)

            # Check .git exists
            if not os.path.isdir(os.path.join(target, ".git")):
                report.issues.append(HealthIssue(
                    "warning", "git", item, "没有.git目录"
                ))
                continue

            # Check repo size
            try:
                size_bytes = sum(
                    os.path.getsize(os.path.join(dp, f))
                    for dp, dn, fn in os.walk(target)
                    for f in fn
                )
                size_gb = size_bytes / (1024**3)
                if size_gb > self.max_repo_size_gb:
                    report.issues.append(HealthIssue(
                        "warning", "disk", item,
                        f"仓库过大: {size_gb:.1f}GB (阈值{self.max_repo_size_gb}GB)"
                    ))
            except:
                pass

            # Check for broken remote
            try:
                r = subprocess.run(["git", "remote", "get-url", "origin"],
                                 capture_output=True, text=True, cwd=target, timeout=3)
                if r.returncode != 0 or not r.stdout.strip():
                    report.issues.append(HealthIssue(
                        "warning", "remote", item, "没有设置remote"
                    ))
            except:
                pass

            # Check for long-standing dirty files
            try:
                r = subprocess.run(["git", "status", "--porcelain"],
                                 capture_output=True, text=True, cwd=target, timeout=3)
                if r.stdout.strip():
                    lines = r.stdout.strip().split('\n')
                    dirty_count = len(lines)
                    if dirty_count > 50:
                        report.issues.append(HealthIssue(
                            "warning", "git", item,
                            f"大量未提交变更: {dirty_count}个文件"
                        ))
            except:
                pass

            # Check for broken submodules
            if os.path.exists(os.path.join(target, ".gitmodules")):
                try:
                    r = subprocess.run(["git", "submodule", "status"],
                                     capture_output=True, text=True, cwd=target, timeout=5)
                    if r.returncode != 0:
                        report.issues.append(HealthIssue(
                            "warning", "git", item, "子模块状态异常"
                        ))
                except:
                    pass

            # Check for lock files (indicates interrupted git operation)
            lock_file = os.path.join(target, ".git", "index.lock")
            if os.path.exists(lock_file):
                report.issues.append(HealthIssue(
                    "critical", "git", item,
                    "存在index.lock文件(上次git操作被中断)"
                ))

            if len(report.issues) == issues_before:
                report.healthy += 1

        # Count by severity
        for issue in report.issues:
            if issue.severity == "critical":
                report.critical += 1
            elif issue.severity == "warning":
                report.warnings += 1

    def run(self) -> HealthReport:
        report = HealthReport(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if self.health_cfg.get("check_disk", True):
            self.check_disk(report)

        if self.health_cfg.get("check_git", True):
            self.check_repos(report)

        logger.info(f"Health check: {report.healthy} healthy, {report.warnings} warnings, {report.critical} critical")
        return report

    def fix_common_issues(self) -> List[str]:
        """自动修复常见问题"""
        fixes = []

        for item in os.listdir(self.projects_dir):
            target = os.path.join(self.projects_dir, item)
            if not os.path.isdir(target):
                continue

            # Fix: remove index.lock
            lock_file = os.path.join(target, ".git", "index.lock")
            if os.path.exists(lock_file):
                os.remove(lock_file)
                fixes.append(f"Removed lock: {item}/.git/index.lock")

            # Fix: ensure .gitignore exists
            gitignore = os.path.join(target, ".gitignore")
            if not os.path.exists(gitignore) and os.path.isdir(os.path.join(target, ".git")):
                with open(gitignore, 'w') as f:
                    f.write(".env\n.env.local\n.env.*.local\n__pycache__/\n*.pyc\n.DS_Store\n.venv/\nnode_modules/\n")
                fixes.append(f"Created .gitignore: {item}")

        return fixes
