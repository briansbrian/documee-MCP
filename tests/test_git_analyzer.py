"""
Tests for Git analyzer module.
"""

import pytest
import os
from pathlib import Path
from src.analysis.git_analyzer import GitAnalyzer, create_git_analyzer


class TestGitAnalyzer:
    """Test suite for GitAnalyzer class."""
    
    @pytest.fixture
    def repo_path(self):
        """Get the current repository path."""
        # Assuming tests run from repo root
        return Path.cwd()
    
    @pytest.fixture
    def git_analyzer(self, repo_path):
        """Create a GitAnalyzer instance for testing."""
        analyzer = create_git_analyzer(str(repo_path))
        if analyzer is None:
            pytest.skip("Not a Git repository or Git not available")
        return analyzer
    
    def test_create_git_analyzer_valid_repo(self, repo_path):
        """Test creating GitAnalyzer with valid repository."""
        analyzer = create_git_analyzer(str(repo_path))
        assert analyzer is not None
        assert analyzer.repo_path == repo_path
    
    def test_create_git_analyzer_invalid_repo(self, tmp_path):
        """Test creating GitAnalyzer with invalid repository."""
        analyzer = create_git_analyzer(str(tmp_path))
        assert analyzer is None
    
    def test_is_git_repository(self, git_analyzer):
        """Test Git repository detection."""
        assert git_analyzer._is_git_repository() is True
    
    def test_get_relevant_commits_empty_list(self, git_analyzer):
        """Test get_relevant_commits with empty file list."""
        commits = git_analyzer.get_relevant_commits([])
        assert commits == []
    
    def test_get_relevant_commits_valid_file(self, git_analyzer):
        """Test get_relevant_commits with a valid file."""
        # Use README.md as it likely exists and has commits
        commits = git_analyzer.get_relevant_commits(["README.md"], max_commits=5)
        
        # Should return a list (may be empty if file has no history)
        assert isinstance(commits, list)
        
        # If commits exist, verify structure
        if commits:
            commit = commits[0]
            assert "hash" in commit
            assert "author" in commit
            assert "email" in commit
            assert "date" in commit
            assert "message" in commit
            assert "files" in commit
            assert isinstance(commit["files"], list)
    
    def test_get_relevant_commits_nonexistent_file(self, git_analyzer):
        """Test get_relevant_commits with nonexistent file."""
        commits = git_analyzer.get_relevant_commits(
            ["nonexistent_file_12345.txt"],
            max_commits=5
        )
        assert commits == []
    
    def test_get_relevant_commits_multiple_files(self, git_analyzer):
        """Test get_relevant_commits with multiple files."""
        commits = git_analyzer.get_relevant_commits(
            ["README.md", "requirements.txt"],
            max_commits=5
        )
        
        assert isinstance(commits, list)
        # Commits should be sorted by date (newest first)
        if len(commits) > 1:
            dates = [c["date"] for c in commits]
            assert dates == sorted(dates, reverse=True)
    
    def test_get_commit_context_invalid_hash(self, git_analyzer):
        """Test get_commit_context with invalid commit hash."""
        context = git_analyzer.get_commit_context("invalid_hash_12345")
        assert context is None
    
    def test_get_commit_context_valid_hash(self, git_analyzer):
        """Test get_commit_context with valid commit hash."""
        # First get a valid commit
        commits = git_analyzer.get_relevant_commits(["README.md"], max_commits=1)
        
        if not commits:
            pytest.skip("No commits found for README.md")
        
        commit_hash = commits[0]["hash"]
        context = git_analyzer.get_commit_context(commit_hash)
        
        assert context is not None
        assert context["hash"] == commit_hash
        assert "author" in context
        assert "email" in context
        assert "date" in context
        assert "subject" in context
        assert "message" in context
        assert "files" in context
        assert "stats" in context
        assert "insertions" in context["stats"]
        assert "deletions" in context["stats"]
        assert "files_changed" in context["stats"]
    
    def test_find_feature_commits_empty_name(self, git_analyzer):
        """Test find_feature_commits with empty feature name."""
        commits = git_analyzer.find_feature_commits("")
        assert commits == []
    
    def test_find_feature_commits_valid_search(self, git_analyzer):
        """Test find_feature_commits with valid search term."""
        # Search for common terms that might be in commits
        commits = git_analyzer.find_feature_commits("test", max_results=5)
        
        assert isinstance(commits, list)
        
        # If commits found, verify structure
        if commits:
            commit = commits[0]
            assert "hash" in commit
            assert "author" in commit
            assert "message" in commit
            # Verify the search term appears in the message (case-insensitive)
            assert "test" in commit["message"].lower()
    
    def test_find_feature_commits_nonexistent_feature(self, git_analyzer):
        """Test find_feature_commits with nonexistent feature."""
        commits = git_analyzer.find_feature_commits(
            "nonexistent_feature_xyz_12345",
            max_results=5
        )
        assert commits == []
    
    def test_get_file_history_summary_valid_file(self, git_analyzer):
        """Test get_file_history_summary with valid file."""
        summary = git_analyzer.get_file_history_summary("README.md")
        
        # May be None if file has no history
        if summary is not None:
            assert "file_path" in summary
            assert summary["file_path"] == "README.md"
            assert "total_commits" in summary
            assert isinstance(summary["total_commits"], int)
            assert summary["total_commits"] > 0
            assert "contributors" in summary
            assert isinstance(summary["contributors"], list)
            
            if summary["first_commit"]:
                assert "hash" in summary["first_commit"]
                assert "author" in summary["first_commit"]
                assert "date" in summary["first_commit"]
            
            if summary["last_commit"]:
                assert "hash" in summary["last_commit"]
                assert "author" in summary["last_commit"]
                assert "date" in summary["last_commit"]
    
    def test_get_file_history_summary_nonexistent_file(self, git_analyzer):
        """Test get_file_history_summary with nonexistent file."""
        summary = git_analyzer.get_file_history_summary(
            "nonexistent_file_12345.txt"
        )
        assert summary is None
    
    def test_run_git_command_valid(self, git_analyzer):
        """Test _run_git_command with valid command."""
        output = git_analyzer._run_git_command(["--version"])
        assert output is not None
        assert "git version" in output.lower()
    
    def test_run_git_command_invalid(self, git_analyzer):
        """Test _run_git_command with invalid command."""
        output = git_analyzer._run_git_command(["invalid-command-xyz"])
        assert output is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
