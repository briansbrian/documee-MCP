"""
Git Analyzer for evidence collection.

This module provides Git repository analysis capabilities for extracting
commit history, context, and feature-related information to support
evidence-based content enrichment.
"""

import logging
import subprocess
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class GitAnalyzer:
    """
    Analyzes Git repository for evidence collection.
    
    Provides methods to extract commit history, search for feature-related
    commits, and gather contextual information about code changes.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize Git analyzer.
        
        Args:
            repo_path: Path to the Git repository root
            
        Raises:
            ValueError: If repo_path is not a valid Git repository
        """
        self.repo_path = Path(repo_path).resolve()
        
        if not self._is_git_repository():
            raise ValueError(f"Not a valid Git repository: {repo_path}")
        
        logger.info(f"Initialized GitAnalyzer for repository: {self.repo_path}")
    
    def _is_git_repository(self) -> bool:
        """
        Check if the path is a valid Git repository.
        
        Returns:
            True if valid Git repository, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"Git repository check failed: {e}")
            return False
    
    def _run_git_command(
        self,
        args: List[str],
        timeout: int = 30
    ) -> Optional[str]:
        """
        Run a git command and return output.
        
        Args:
            args: Git command arguments (without 'git' prefix)
            timeout: Command timeout in seconds
            
        Returns:
            Command output as string, or None if command failed
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning(
                    f"Git command failed: git {' '.join(args)}\n"
                    f"Error: {result.stderr}"
                )
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: git {' '.join(args)}")
            return None
        except FileNotFoundError:
            logger.error("Git executable not found. Is Git installed?")
            return None
        except Exception as e:
            logger.error(f"Error running git command: {e}")
            return None
    
    def get_relevant_commits(
        self,
        file_paths: List[str],
        max_commits: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find commits that modified the specified files.
        
        Args:
            file_paths: List of file paths relative to repository root
            max_commits: Maximum number of commits to return per file
            
        Returns:
            List of commit dictionaries with keys:
                - hash: Commit hash
                - author: Author name
                - email: Author email
                - date: Commit date (ISO format)
                - message: Commit message
                - files: List of files modified in this commit
        """
        if not file_paths:
            logger.warning("No file paths provided to get_relevant_commits")
            return []
        
        commits_dict = {}
        
        for file_path in file_paths:
            # Normalize path to be relative to repo root
            try:
                rel_path = Path(file_path).as_posix()
            except Exception as e:
                logger.warning(f"Invalid file path {file_path}: {e}")
                continue
            
            # Get commit log for this file
            # Format: hash|author|email|date|subject
            output = self._run_git_command([
                "log",
                f"-{max_commits}",
                "--format=%H|%an|%ae|%aI|%s",
                "--follow",  # Follow file renames
                "--",
                rel_path
            ])
            
            if not output:
                continue
            
            for line in output.split('\n'):
                if not line.strip():
                    continue
                
                try:
                    parts = line.split('|', 4)
                    if len(parts) != 5:
                        continue
                    
                    commit_hash, author, email, date, subject = parts
                    
                    # Get full commit message
                    full_message = self._run_git_command([
                        "log",
                        "-1",
                        "--format=%B",
                        commit_hash
                    ])
                    
                    # Get files modified in this commit
                    files_output = self._run_git_command([
                        "diff-tree",
                        "--no-commit-id",
                        "--name-only",
                        "-r",
                        commit_hash
                    ])
                    
                    files = files_output.split('\n') if files_output else []
                    
                    # Store commit (avoid duplicates)
                    if commit_hash not in commits_dict:
                        commits_dict[commit_hash] = {
                            "hash": commit_hash,
                            "author": author,
                            "email": email,
                            "date": date,
                            "subject": subject,
                            "message": full_message or subject,
                            "files": files
                        }
                    
                except Exception as e:
                    logger.warning(f"Error parsing commit line: {line}, error: {e}")
                    continue
        
        # Convert to list and sort by date (newest first)
        commits = list(commits_dict.values())
        commits.sort(key=lambda x: x["date"], reverse=True)
        
        logger.info(
            f"Found {len(commits)} relevant commits for "
            f"{len(file_paths)} file(s)"
        )
        
        return commits
    
    def get_commit_context(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """
        Extract detailed context for a specific commit.
        
        Args:
            commit_hash: Git commit hash (full or abbreviated)
            
        Returns:
            Dictionary with commit details:
                - hash: Full commit hash
                - author: Author name
                - email: Author email
                - date: Commit date (ISO format)
                - subject: Commit subject line
                - message: Full commit message
                - files: List of files modified
                - stats: Diff statistics (insertions, deletions)
                - diff: Full diff output (optional, can be large)
        """
        if not commit_hash:
            logger.warning("Empty commit hash provided")
            return None
        
        # Get commit details
        # Format: hash|author|email|date|subject
        output = self._run_git_command([
            "log",
            "-1",
            "--format=%H|%an|%ae|%aI|%s",
            commit_hash
        ])
        
        if not output:
            logger.warning(f"Commit not found: {commit_hash}")
            return None
        
        try:
            parts = output.split('|', 4)
            if len(parts) != 5:
                return None
            
            full_hash, author, email, date, subject = parts
            
            # Get full commit message
            full_message = self._run_git_command([
                "log",
                "-1",
                "--format=%B",
                commit_hash
            ])
            
            # Get files modified
            files_output = self._run_git_command([
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                commit_hash
            ])
            files = files_output.split('\n') if files_output else []
            
            # Get diff statistics
            stats_output = self._run_git_command([
                "show",
                "--stat",
                "--format=",
                commit_hash
            ])
            
            # Parse stats (last line usually has summary)
            insertions = 0
            deletions = 0
            if stats_output:
                lines = stats_output.strip().split('\n')
                if lines:
                    # Look for pattern like "5 files changed, 123 insertions(+), 45 deletions(-)"
                    summary_line = lines[-1]
                    if 'insertion' in summary_line:
                        try:
                            parts = summary_line.split(',')
                            for part in parts:
                                if 'insertion' in part:
                                    insertions = int(part.strip().split()[0])
                                elif 'deletion' in part:
                                    deletions = int(part.strip().split()[0])
                        except (ValueError, IndexError):
                            pass
            
            commit_context = {
                "hash": full_hash,
                "author": author,
                "email": email,
                "date": date,
                "subject": subject,
                "message": full_message or subject,
                "files": files,
                "stats": {
                    "insertions": insertions,
                    "deletions": deletions,
                    "files_changed": len(files)
                }
            }
            
            logger.debug(f"Retrieved context for commit {full_hash[:8]}")
            return commit_context
            
        except Exception as e:
            logger.error(f"Error extracting commit context: {e}")
            return None
    
    def find_feature_commits(
        self,
        feature_name: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search commit messages for mentions of a feature.
        
        Args:
            feature_name: Feature name or keyword to search for
            max_results: Maximum number of commits to return
            
        Returns:
            List of commit dictionaries matching the search criteria
        """
        if not feature_name:
            logger.warning("Empty feature name provided")
            return []
        
        # Search commit messages using git log --grep
        # Format: hash|author|email|date|subject
        output = self._run_git_command([
            "log",
            f"-{max_results}",
            "--format=%H|%an|%ae|%aI|%s",
            "--grep", feature_name,
            "--regexp-ignore-case",  # Case-insensitive search
            "--all"  # Search all branches
        ])
        
        if not output:
            logger.info(f"No commits found for feature: {feature_name}")
            return []
        
        commits = []
        
        for line in output.split('\n'):
            if not line.strip():
                continue
            
            try:
                parts = line.split('|', 4)
                if len(parts) != 5:
                    continue
                
                commit_hash, author, email, date, subject = parts
                
                # Get full commit message
                full_message = self._run_git_command([
                    "log",
                    "-1",
                    "--format=%B",
                    commit_hash
                ])
                
                # Get files modified
                files_output = self._run_git_command([
                    "diff-tree",
                    "--no-commit-id",
                    "--name-only",
                    "-r",
                    commit_hash
                ])
                files = files_output.split('\n') if files_output else []
                
                commits.append({
                    "hash": commit_hash,
                    "author": author,
                    "email": email,
                    "date": date,
                    "subject": subject,
                    "message": full_message or subject,
                    "files": files
                })
                
            except Exception as e:
                logger.warning(f"Error parsing commit line: {line}, error: {e}")
                continue
        
        logger.info(
            f"Found {len(commits)} commits mentioning feature: {feature_name}"
        )
        
        return commits
    
    def get_file_history_summary(
        self,
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a file's Git history.
        
        Args:
            file_path: Path to file relative to repository root
            
        Returns:
            Dictionary with file history summary:
                - total_commits: Total number of commits affecting this file
                - first_commit: First commit that introduced the file
                - last_commit: Most recent commit affecting the file
                - contributors: List of unique contributors
                - creation_date: Date file was first added
                - last_modified: Date of last modification
        """
        try:
            rel_path = Path(file_path).as_posix()
        except Exception as e:
            logger.warning(f"Invalid file path {file_path}: {e}")
            return None
        
        # Get total commit count
        count_output = self._run_git_command([
            "log",
            "--oneline",
            "--follow",
            "--",
            rel_path
        ])
        
        if not count_output:
            logger.info(f"No Git history found for file: {file_path}")
            return None
        
        total_commits = len(count_output.split('\n'))
        
        # Get first commit (oldest)
        first_output = self._run_git_command([
            "log",
            "--format=%H|%an|%aI|%s",
            "--follow",
            "--diff-filter=A",  # Added
            "--",
            rel_path
        ])
        
        first_commit = None
        creation_date = None
        if first_output:
            lines = first_output.strip().split('\n')
            if lines:
                parts = lines[-1].split('|', 3)  # Get last line (oldest)
                if len(parts) >= 3:
                    first_commit = {
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "subject": parts[3] if len(parts) > 3 else ""
                    }
                    creation_date = parts[2]
        
        # Get last commit (newest)
        last_output = self._run_git_command([
            "log",
            "-1",
            "--format=%H|%an|%aI|%s",
            "--follow",
            "--",
            rel_path
        ])
        
        last_commit = None
        last_modified = None
        if last_output:
            parts = last_output.split('|', 3)
            if len(parts) >= 3:
                last_commit = {
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "subject": parts[3] if len(parts) > 3 else ""
                }
                last_modified = parts[2]
        
        # Get unique contributors
        contributors_output = self._run_git_command([
            "log",
            "--format=%an|%ae",
            "--follow",
            "--",
            rel_path
        ])
        
        contributors = []
        if contributors_output:
            seen = set()
            for line in contributors_output.split('\n'):
                if '|' in line:
                    name, email = line.split('|', 1)
                    if email not in seen:
                        seen.add(email)
                        contributors.append({"name": name, "email": email})
        
        summary = {
            "file_path": file_path,
            "total_commits": total_commits,
            "first_commit": first_commit,
            "last_commit": last_commit,
            "contributors": contributors,
            "creation_date": creation_date,
            "last_modified": last_modified
        }
        
        logger.debug(
            f"File history summary for {file_path}: "
            f"{total_commits} commits, {len(contributors)} contributors"
        )
        
        return summary


def create_git_analyzer(repo_path: str) -> Optional[GitAnalyzer]:
    """
    Factory function to create a GitAnalyzer instance.
    
    Args:
        repo_path: Path to Git repository
        
    Returns:
        GitAnalyzer instance, or None if not a valid repository
    """
    try:
        return GitAnalyzer(repo_path)
    except ValueError as e:
        logger.info(f"Cannot create GitAnalyzer: {e}")
        return None
