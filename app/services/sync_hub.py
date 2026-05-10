"""
OPC Sync Hub - 同步引擎
并发检查并同步所有项目与GitHub
"""

import os, json, urllib.request, subprocess, zipfile, io, shutil, logging, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger("opc-sync")

@dataclass
class RepoStatus:
    name: str
    path: str
    remote: str = ""
    repo_name: str = ""
    local_date: str = ""
    github_date: str = ""
    dirty_count: int = 0
    untracked_count: int = 0
    status: str = "unknown"     # ok / pulled / pushed / error / skip
    message: str = ""
    last_sync: str = ""
    size_mb: float = 0

@dataclass
class SyncResult:
    timestamp: str = ""
    total: int = 0
    pulled: int = 0
    pushed: int = 0
    ok: int = 0
    skipped: int = 0
    errors: int = 0
    repos: List[RepoStatus] = field(default_factory=list)
    duration_seconds: float = 0

class SyncEngine:
    # 推送历史记录(防止重复推送)
    _push_history: dict = {}

    def __init__(self, config: dict):
        self.config = config
        self.gh = config.get("github", {})
        self.sync_cfg = config.get("sync", {})
        self.token = self.gh.get("token", "")
        self.org = self.gh.get("org", "MoKangMedical")
        self.skip_repos = set(self.gh.get("skip_repos", []))
        self.projects_dir = os.path.expanduser(config.get("projects_dir", "~/Desktop/OPC"))
        self.max_workers = self.sync_cfg.get("max_workers", 8)
        self.api_timeout = self.sync_cfg.get("timeout_api", 10)
        self.clone_timeout = self.sync_cfg.get("timeout_clone", 60)
        self.push_timeout = self.sync_cfg.get("timeout_push", 60)
        self.auto_commit = self.sync_cfg.get("auto_commit", True)
        self.auto_push = self.sync_cfg.get("auto_push", True)

    def api_get(self, url: str) -> Optional[dict]:
        req = urllib.request.Request(url, headers={
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        })
        try:
            with urllib.request.urlopen(req, timeout=self.api_timeout) as resp:
                return json.loads(resp.read())
        except Exception as e:
            logger.debug(f"API error: {url} - {e}")
            return None

    def get_remote_repo_name(self, path: str) -> Optional[str]:
        try:
            r = subprocess.run(["git", "remote", "get-url", "origin"],
                             capture_output=True, text=True, cwd=path, timeout=3)
            if r.returncode == 0 and self.org in r.stdout:
                parts = r.stdout.strip().split(f"{self.org}/")
                if len(parts) >= 2:
                    return parts[1].replace(".git", "")
        except:
            pass
        return None

    def get_local_commit_date(self, path: str) -> Optional[str]:
        try:
            r = subprocess.run(["git", "log", "-1", "--format=%ci"],
                             capture_output=True, text=True, cwd=path, timeout=3)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()[:10]
        except:
            pass
        return None

    def get_github_commit_date(self, repo_name: str) -> Optional[str]:
        data = self.api_get(f"{self.gh['api_base']}/repos/{self.org}/{repo_name}/commits?per_page=1")
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]["commit"]["committer"]["date"][:10]
        return None

    def get_dirty_status(self, path: str) -> tuple:
        try:
            r = subprocess.run(["git", "status", "--porcelain"],
                             capture_output=True, text=True, cwd=path, timeout=3)
            lines = r.stdout.strip().split('\n') if r.stdout.strip() else []
            dirty = sum(1 for l in lines if not l.startswith('??'))
            untracked = sum(1 for l in lines if l.startswith('??'))
            return dirty, untracked
        except:
            return 0, 0

    def get_dir_size_mb(self, path: str) -> float:
        try:
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                dirnames[:] = [d for d in dirnames if d != '.git']
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.isfile(fp):
                        total += os.path.getsize(fp)
            return round(total / 1024 / 1024, 1)
        except:
            return 0

    def download_and_replace(self, repo_name: str, target_dir: str) -> bool:
        url = f"{self.gh['api_base']}/repos/{self.org}/{repo_name}/zipball"
        req = urllib.request.Request(url, headers={
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req, timeout=self.clone_timeout) as resp:
            data = resp.read()

        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            top_dir = names[0].split('/')[0]

            # Save untracked local files
            saved = {}
            r = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                             capture_output=True, text=True, cwd=target_dir, timeout=3)
            max_size = self.sync_cfg.get("max_file_size_mb", 10) * 1024 * 1024
            if r.stdout.strip():
                for f in r.stdout.strip().split('\n')[:50]:
                    src = os.path.join(target_dir, f)
                    if os.path.isfile(src) and os.path.getsize(src) < max_size:
                        with open(src, 'rb') as fh:
                            saved[f] = fh.read()

            # Extract to temp
            temp = target_dir + "_sync_tmp"
            zf.extractall(temp)

            # Remove old content (keep .git)
            for item in os.listdir(target_dir):
                if item == '.git':
                    continue
                p = os.path.join(target_dir, item)
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)

            # Copy new content
            src_dir = os.path.join(temp, top_dir)
            for item in os.listdir(src_dir):
                s = os.path.join(src_dir, item)
                d = os.path.join(target_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            shutil.rmtree(temp)

            # Restore untracked files
            for f, content in saved.items():
                dst = os.path.join(target_dir, f)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, 'wb') as fh:
                    fh.write(content)

            # Git commit
            subprocess.run(["git", "add", "."], capture_output=True, text=True,
                         cwd=target_dir, timeout=5)
            subprocess.run(["git", "commit", "-m", f"Auto-sync from GitHub: {repo_name}"],
                         capture_output=True, text=True, cwd=target_dir, timeout=5)
        return True

    def push_via_api(self, repo_name: str, path: str) -> bool:
        """通过GitHub API推送文件(git push超时时的fallback)"""
        import base64

        # 收集所有文件
        files = []
        for root, dirs, filenames in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'node_modules', '.DS_Store', '.site', 'logs', '.pytest_cache']]
            for f in filenames:
                if f.startswith('.DS_Store') or f.endswith('.pyc') or f.endswith('.pyo'):
                    continue
                full = os.path.join(root, f)
                rel = os.path.relpath(full, path)
                try:
                    sz = os.path.getsize(full)
                    if sz > 10 * 1024 * 1024:  # skip >10MB
                        continue
                    with open(full, 'rb') as fh:
                        files.append((rel, fh.read()))
                except:
                    pass

        if not files:
            return False

        # 创建blobs
        blobs = []
        for fpath, content in files:
            try:
                url = f"{self.gh['api_base']}/repos/{self.org}/{repo_name}/git/blobs"
                data = json.dumps({"content": base64.b64encode(content).decode(), "encoding": "base64"}).encode()
                req = urllib.request.Request(url, data=data, headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read())
                    blobs.append({"path": fpath, "sha": result["sha"], "mode": "100644", "type": "blob"})
            except:
                pass

        if not blobs:
            return False

        # 创建tree
        try:
            url = f"{self.gh['api_base']}/repos/{self.org}/{repo_name}/git/trees"
            data = json.dumps({"tree": blobs}).encode()
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                tree_sha = json.loads(resp.read())["sha"]
        except:
            return False

        # 创建commit
        try:
            url = f"{self.gh['api_base']}/repos/{self.org}/{repo_name}/git/commits"
            data = json.dumps({"message": f"Auto-sync: {repo_name}", "tree": tree_sha}).encode()
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                commit_sha = json.loads(resp.read())["sha"]
        except:
            return False

        # 更新ref
        try:
            url = f"{self.gh['api_base']}/repos/{self.org}/{repo_name}/git/refs/heads/main"
            data = json.dumps({"sha": commit_sha, "force": True}).encode()
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            })
            req.get_method = lambda: 'PATCH'
            urllib.request.urlopen(req, timeout=15)
            return True
        except:
            # 尝试创建ref
            try:
                url = f"{self.gh['api_base']}/repos/{self.org}/{repo_name}/git/refs"
                data = json.dumps({"ref": "refs/heads/main", "sha": commit_sha}).encode()
                req = urllib.request.Request(url, data=data, headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                })
                urllib.request.urlopen(req, timeout=15)
                return True
            except:
                return False

    def push_local(self, path: str, repo_name: str = "") -> bool:
        if self.auto_commit:
            subprocess.run(["git", "add", "."], capture_output=True, text=True,
                         cwd=path, timeout=5)
            subprocess.run(["git", "commit", "-m", "Auto-commit local changes"],
                         capture_output=True, text=True, cwd=path, timeout=5)
        # 先尝试git push
        try:
            r = subprocess.run(
                ["git", "-c", "http.version=HTTP/1.1", "push", "origin", "HEAD:main"],
                capture_output=True, text=True, cwd=path, timeout=self.push_timeout
            )
            if r.returncode == 0:
                return True
        except subprocess.TimeoutExpired:
            logger.info(f"Git push timeout for {repo_name}, trying API...")
        except Exception as e:
            logger.info(f"Git push error for {repo_name}: {e}")

        # git push失败，fallback到API推送
        if repo_name:
            try:
                ok = self.push_via_api(repo_name, path)
                if ok:
                    logger.info(f"API push OK: {repo_name}")
                else:
                    logger.error(f"API push FAIL: {repo_name}")
                return ok
            except Exception as e:
                logger.error(f"API push error: {repo_name} - {e}")
                return False
        return False

    def check_repo(self, item: str) -> RepoStatus:
        target = os.path.join(self.projects_dir, item)
        status = RepoStatus(name=item, path=target, last_sync=datetime.now().isoformat())

        if not os.path.isdir(os.path.join(target, ".git")):
            status.status = "no_git"
            return status

        status.repo_name = self.get_remote_repo_name(target) or ""
        status.local_date = self.get_local_commit_date(target) or ""
        status.dirty_count, status.untracked_count = self.get_dirty_status(target)
        status.size_mb = self.get_dir_size_mb(target)

        if not status.repo_name:
            status.status = "no_remote"
            return status

        gh_date = self.get_github_commit_date(status.repo_name)
        status.github_date = gh_date or ""

        if not gh_date or not status.local_date:
            status.status = "skip"
            status.message = "missing date info"
            return status

        if gh_date > status.local_date:
            # GitHub is newer
            try:
                self.download_and_replace(status.repo_name, target)
                status.status = "pulled"
                status.message = f"{status.local_date} -> {gh_date}"
                logger.info(f"PULL: {item} ({status.local_date} -> {gh_date})")
            except Exception as e:
                status.status = "error"
                status.message = f"pull failed: {str(e)[:50]}"
                logger.error(f"PULL FAIL: {item} - {e}")

        elif status.local_date > gh_date and self.auto_push:
            # 检查是否最近已推送过(防止API推送后重复推送)
            last_push = self._push_history.get(item)
            if last_push and (datetime.now() - last_push).total_seconds() < 7200:
                status.status = "ok"
                status.message = f"recently pushed at {last_push.strftime('%H:%M')}"
            else:
                # Local is newer
                try:
                    if self.push_local(target, status.repo_name):
                        status.status = "pushed"
                        status.message = f"{status.local_date} -> GitHub"
                        self._push_history[item] = datetime.now()
                        logger.info(f"PUSH: {item}")
                    else:
                        status.status = "error"
                        status.message = "push failed"
                        logger.error(f"PUSH FAIL: {item}")
                except Exception as e:
                    status.status = "error"
                    status.message = f"push failed: {str(e)[:50]}"
                    logger.error(f"PUSH FAIL: {item} - {e}")
        else:
            status.status = "ok"

        return status

    def run_sync(self) -> SyncResult:
        start = time.time()
        result = SyncResult(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        items = [d for d in os.listdir(self.projects_dir)
                if os.path.isdir(os.path.join(self.projects_dir, d))
                and not d.startswith('.')]

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.check_repo, item): item for item in items}
            for future in as_completed(futures):
                try:
                    repo_status = future.result()
                    result.repos.append(repo_status)
                    result.total += 1

                    if repo_status.status == "pulled":
                        result.pulled += 1
                    elif repo_status.status == "pushed":
                        result.pushed += 1
                    elif repo_status.status == "ok":
                        result.ok += 1
                    elif repo_status.status in ("skip", "no_git", "no_remote"):
                        result.skipped += 1
                    elif repo_status.status == "error":
                        result.errors += 1
                except Exception as e:
                    result.errors += 1
                    logger.error(f"Thread error: {e}")

        result.duration_seconds = round(time.time() - start, 1)
        result.repos.sort(key=lambda r: r.name)
        return result

    def get_all_repos_status(self) -> List[RepoStatus]:
        """只检查状态，不同步"""
        items = [d for d in os.listdir(self.projects_dir)
                if os.path.isdir(os.path.join(self.projects_dir, d))
                and not d.startswith('.')]

        statuses = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._check_status_only, item): item for item in items}
            for future in as_completed(futures):
                try:
                    statuses.append(future.result())
                except:
                    pass

        return sorted(statuses, key=lambda r: r.name)

    def _check_status_only(self, item: str) -> RepoStatus:
        target = os.path.join(self.projects_dir, item)
        status = RepoStatus(name=item, path=target, last_sync=datetime.now().isoformat())

        if not os.path.isdir(os.path.join(target, ".git")):
            status.status = "no_git"
            return status

        status.repo_name = self.get_remote_repo_name(target) or ""
        status.local_date = self.get_local_commit_date(target) or ""
        status.dirty_count, status.untracked_count = self.get_dirty_status(target)
        status.size_mb = self.get_dir_size_mb(target)

        if not status.repo_name:
            status.status = "no_remote"
            return status

        gh_date = self.get_github_commit_date(status.repo_name)
        status.github_date = gh_date or ""

        if not gh_date or not status.local_date:
            status.status = "skip"
            return status

        if gh_date > status.local_date:
            status.status = "behind"
            status.message = f"GitHub newer: {gh_date}"
        elif status.local_date > gh_date:
            status.status = "ahead"
            status.message = f"Local newer: {status.local_date}"
        else:
            status.status = "synced"

        return status
