#!/usr/bin/env python3
"""
OPC Sync Hub - 主入口
CLI + 定时任务 + Web服务

用法:
  python main.py sync       # 立即同步一次
  python main.py status     # 查看状态
  python main.py health     # 健康检查
  python main.py fix        # 自动修复
  python main.py report     # 生成报告
  python main.py web        # 启动Web仪表盘
  python main.py daemon     # 守护进程(定时同步+Web)
  python main.py cron       # 单次同步(cron调用)
"""

import os, sys, yaml, json, logging, time, signal
from datetime import datetime
from pathlib import Path
from threading import Thread

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from sync_engine import SyncEngine, SyncResult
from health_checker import HealthChecker
from report_generator import ReportGenerator

def load_config():
    config_path = BASE_DIR / "config" / "settings.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

def setup_logging(config):
    log_dir = BASE_DIR / config.get("logging", {}).get("dir", "logs")
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, config.get("logging", {}).get("level", "INFO")),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "opc-sync.log"),
            logging.StreamHandler()
        ]
    )

def cmd_sync(config):
    """立即同步"""
    engine = SyncEngine(config)
    health = HealthChecker(config)
    reporter = ReportGenerator(config)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始同步...")
    result = engine.run_sync()
    health_report = health.run()

    # Generate report
    html = reporter.generate_sync_html(result, health_report)
    reporter.save_report(html)

    # Print summary
    print(f"\n同步完成 ({result.duration_seconds}s)")
    print(f"  总计: {result.total}")
    print(f"  拉取: {result.pulled}")
    print(f"  推送: {result.pushed}")
    print(f"  OK: {result.ok}")
    print(f"  跳过: {result.skipped}")
    print(f"  错误: {result.errors}")

    if result.errors > 0:
        print("\n错误详情:")
        for r in result.repos:
            if r.status == "error":
                print(f"  {r.name}: {r.message}")

    # Print health
    if health_report.critical > 0 or health_report.warnings > 0:
        print(f"\n健康告警: {health_report.critical} 严重, {health_report.warnings} 警告")
        for issue in health_report.issues[:5]:
            print(f"  [{issue.severity}] {issue.repo}: {issue.message}")

    return result

def cmd_status(config):
    """查看状态"""
    engine = SyncEngine(config)
    repos = engine.get_all_repos_status()

    print(f"\nOPC 项目状态 ({len(repos)} 个仓库)")
    print("=" * 80)

    status_groups = {}
    for r in repos:
        status_groups.setdefault(r.status, []).append(r)

    for status, label in [
        ("synced", "已同步"), ("ok", "OK"), ("behind", "GitHub更新"),
        ("ahead", "本地更新"), ("error", "错误"), ("skip", "跳过"),
        ("no_remote", "无Remote"), ("no_git", "无Git")
    ]:
        group = status_groups.get(status, [])
        if group:
            print(f"\n{label} ({len(group)}):")
            for r in group:
                extra = f" ({r.message})" if r.message else ""
                print(f"  {r.name:45s} local:{r.local_date:10s} gh:{r.github_date:10s}{extra}")

def cmd_health(config):
    """健康检查"""
    checker = HealthChecker(config)
    report = checker.run()

    print(f"\n健康检查报告 ({report.timestamp})")
    print("=" * 60)
    print(f"  总仓库: {report.total_repos}")
    print(f"  健康: {report.healthy}")
    print(f"  警告: {report.warnings}")
    print(f"  严重: {report.critical}")
    print(f"  磁盘可用: {report.disk_free_gb}GB")

    if report.issues:
        print("\n问题列表:")
        for issue in report.issues:
            icon = {"critical": "!!!", "warning": "!", "info": "?"}.get(issue.severity, " ")
            print(f"  [{icon}] {issue.repo}: {issue.message}")
    else:
        print("\n所有检查通过!")

def cmd_fix(config):
    """自动修复"""
    checker = HealthChecker(config)
    fixes = checker.fix_common_issues()

    if fixes:
        print(f"已修复 {len(fixes)} 个问题:")
        for f in fixes:
            print(f"  {f}")
    else:
        print("没有需要修复的问题")

def cmd_report(config):
    """生成报告"""
    engine = SyncEngine(config)
    health = HealthChecker(config)
    reporter = ReportGenerator(config)

    print("生成同步报告...")
    result = engine.run_sync()
    health_report = health.run()

    html = reporter.generate_sync_html(result, health_report)
    path = reporter.save_report(html)

    # Also save JSON
    json_data = reporter.generate_json(result)
    json_path = path.replace('.html', '.json')
    with open(json_path, 'w') as f:
        f.write(json_data)

    print(f"报告已保存:")
    print(f"  HTML: {path}")
    print(f"  JSON: {json_path}")

def cmd_web(config):
    """启动Web仪表盘"""
    import uvicorn
    web_cfg = config.get("web", {})
    host = web_cfg.get("host", "0.0.0.0")
    port = web_cfg.get("port", 9200)
    print(f"启动 Web 仪表盘: http://{host}:{port}")

    # Import and run server
    from server import app
    uvicorn.run(app, host=host, port=port, log_level="info")

def cmd_daemon(config):
    """守护进程: 定时同步 + Web服务"""
    import uvicorn
    from server import app

    interval = config.get("sync", {}).get("interval_minutes", 30) * 60
    web_cfg = config.get("web", {})
    port = web_cfg.get("port", 9200)

    def sync_loop():
        while True:
            try:
                cmd_sync(config)
            except Exception as e:
                logging.error(f"Sync error: {e}")
            time.sleep(interval)

    # Start sync thread
    t = Thread(target=sync_loop, daemon=True)
    t.start()

    print(f"守护进程启动:")
    print(f"  同步间隔: {interval//60} 分钟")
    print(f"  Web仪表盘: http://0.0.0.0:{port}")
    print(f"  按 Ctrl+C 停止")

    # Start web server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

def cmd_cron(config):
    """单次同步(cron调用)"""
    engine = SyncEngine(config)
    result = engine.run_sync()

    # Save minimal log
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sync_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, 'a') as f:
        f.write(f"[{result.timestamp}] total:{result.total} pull:{result.pulled} push:{result.pushed} err:{result.errors} ({result.duration_seconds}s)\n")

    # Print for cron output
    if result.pulled > 0 or result.pushed > 0 or result.errors > 0:
        print(f"[{result.timestamp}] pull:{result.pulled} push:{result.pushed} err:{result.errors}")

def main():
    config = load_config()
    setup_logging(config)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    commands = {
        "sync": cmd_sync,
        "status": cmd_status,
        "health": cmd_health,
        "fix": cmd_fix,
        "report": cmd_report,
        "web": cmd_web,
        "daemon": cmd_daemon,
        "cron": cmd_cron,
    }

    if cmd in commands:
        commands[cmd](config)
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
