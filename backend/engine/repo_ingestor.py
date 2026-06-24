"""
RepoIngestor: clones/reads agent source code and builds an AgentProfile skeleton.
"""
import os
import shutil
import logging
import asyncio
from typing import Optional

from engine.report_schema import AgentProfile

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 500 * 1024  # 500 KB per file
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env", ".env",
    "dist", "build", ".next", ".cache", "coverage", ".pytest_cache", ".tox",
    "htmlcov", ".eggs", "*.egg-info",
}
SKIP_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dll", ".exe", ".bin",
    ".jpg", ".jpeg", ".png", ".gif", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot",
    ".mp4", ".mp3", ".wav",
    ".zip", ".tar", ".gz", ".bz2", ".xz",
    ".lock", ".sum",
}
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java", ".cs", ".rb",
    ".md", ".txt", ".rst", ".yaml", ".yml", ".json", ".toml", ".cfg",
    ".ini", ".env", ".example", ".sh", ".bash", ".dockerfile",
    ".html", ".css", ".xml", ".sql", ".graphql",
}


class RepoIngestor:
    def __init__(self, run_id: str, storage_path: str):
        self.run_id = run_id
        self.storage_path = storage_path

    async def ingest_url(self, repo_url: str) -> str:
        """Clone a repository and return the local path."""
        clone_path = os.path.join(self.storage_path, "repo")
        if os.path.exists(clone_path):
            shutil.rmtree(clone_path)
        os.makedirs(clone_path, exist_ok=True)

        logger.info(f"[{self.run_id}] Cloning {repo_url} to {clone_path}")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._clone_repo, repo_url, clone_path)

        return clone_path

    def _clone_repo(self, repo_url: str, clone_path: str) -> None:
        """Attempt git clone via subprocess, fallback to gitpython."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "clone", "--depth=1", repo_url, clone_path],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                raise RuntimeError(f"git clone failed: {result.stderr.strip()}")
            logger.info(f"[{self.run_id}] git clone succeeded")
            return
        except FileNotFoundError:
            logger.warning(f"[{self.run_id}] git not found, trying gitpython")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Repository clone timed out after 120 seconds")

        # Fallback to gitpython
        try:
            import git
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
            git.Repo.clone_from(repo_url, clone_path, depth=1)
            logger.info(f"[{self.run_id}] gitpython clone succeeded")
        except Exception as e:
            raise RuntimeError(f"Failed to clone repository via gitpython: {e}") from e

    def find_actual_root(self, base_path: str) -> str:
        """
        Handle case where a ZIP extracts to a single top-level directory.
        Returns the effective project root.
        """
        try:
            entries = [e for e in os.listdir(base_path) if not e.startswith(".")]
            if len(entries) == 1:
                candidate = os.path.join(base_path, entries[0])
                if os.path.isdir(candidate):
                    logger.info(f"[{self.run_id}] Detected single-dir extraction root: {candidate}")
                    return candidate
        except Exception:
            pass
        return base_path

    def ingest_directory(self, dir_path: str) -> AgentProfile:
        """Walk a directory and build an AgentProfile with file contents."""
        logger.info(f"[{self.run_id}] Ingesting directory: {dir_path}")

        profile = AgentProfile(
            run_id=self.run_id,
            agent_name="",       # filled by orchestrator
            submission_type="",  # filled by orchestrator
            root_path=dir_path,
        )

        all_files = []
        file_contents = {}
        total_lines = 0

        for root, dirs, files in os.walk(dir_path):
            # Prune directories to skip
            dirs[:] = [
                d for d in dirs
                if d not in SKIP_DIRS
                and not d.startswith(".")
                and not d.endswith(".egg-info")
            ]

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in SKIP_EXTENSIONS:
                    continue

                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, dir_path)

                # Normalise to forward slashes for cross-platform consistency
                rel_path = rel_path.replace("\\", "/")

                # Skip large files
                try:
                    if os.path.getsize(full_path) > MAX_FILE_SIZE:
                        logger.debug(f"[{self.run_id}] Skipping large file: {rel_path}")
                        continue
                except OSError:
                    continue

                all_files.append(rel_path)

                # Only read files that are likely text
                if ext in TEXT_EXTENSIONS or "." not in filename:
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        file_contents[rel_path] = content
                        total_lines += content.count("\n") + 1
                    except Exception as e:
                        logger.debug(f"[{self.run_id}] Could not read {rel_path}: {e}")

        profile.all_files = all_files
        profile.file_count = len(all_files)
        profile.file_contents = file_contents
        profile.total_lines = total_lines

        logger.info(
            f"[{self.run_id}] Ingested {len(all_files)} files, "
            f"{len(file_contents)} readable, {total_lines} total lines"
        )
        return profile
