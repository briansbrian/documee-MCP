"""
Persistence Manager for Analysis Results.

This module manages long-term storage of analysis results to disk,
enabling incremental analysis and result caching across sessions.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional

from src.models.analysis_models import CodebaseAnalysis, FileAnalysis

logger = logging.getLogger(__name__)


class PersistenceManager:
    """
    Manages disk persistence of analysis results.
    
    Stores analysis results as JSON files in a structured directory:
    .documee/analysis/{codebase_id}/
        - analysis.json (main codebase analysis)
        - file_hashes.json (file hashes for incremental analysis)
        - file_{hash}.json (individual file analyses)
    """
    
    def __init__(self, base_path: str = ".documee/analysis"):
        """
        Initialize the Persistence Manager.
        
        Args:
            base_path: Base directory for storing analysis results
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Persistence Manager initialized with base path: {self.base_path}")
    
    def save_analysis(self, codebase_id: str, analysis: CodebaseAnalysis) -> None:
        """
        Save complete codebase analysis to disk as JSON.
        
        Creates directory structure and saves:
        - Main analysis file with all metadata
        - Individual file analyses for efficient loading
        
        Args:
            codebase_id: Unique identifier for the codebase
            analysis: Complete CodebaseAnalysis object to save
        
        Raises:
            IOError: If unable to write to disk
        """
        try:
            # Create codebase-specific directory
            analysis_dir = self.base_path / codebase_id
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Save main analysis file
            analysis_file = analysis_dir / "analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved analysis for codebase {codebase_id} to {analysis_file}")
            
            # Save individual file analyses for efficient partial loading
            for file_path, file_analysis in analysis.file_analyses.items():
                # Create safe filename from file path hash
                safe_name = hashlib.sha256(file_path.encode()).hexdigest()[:16]
                file_analysis_path = analysis_dir / f"file_{safe_name}.json"
                
                with open(file_analysis_path, 'w', encoding='utf-8') as f:
                    json.dump(file_analysis.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(analysis.file_analyses)} individual file analyses")
            
        except Exception as e:
            logger.error(f"Failed to save analysis for {codebase_id}: {e}")
            raise IOError(f"Failed to save analysis: {e}") from e
    
    def load_analysis(self, codebase_id: str) -> Optional[CodebaseAnalysis]:
        """
        Load complete codebase analysis from disk.
        
        Args:
            codebase_id: Unique identifier for the codebase
        
        Returns:
            CodebaseAnalysis object if found, None otherwise
        """
        try:
            analysis_file = self.base_path / codebase_id / "analysis.json"
            
            if not analysis_file.exists():
                logger.debug(f"No saved analysis found for codebase {codebase_id}")
                return None
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            analysis = CodebaseAnalysis.from_dict(data)
            logger.info(f"Loaded analysis for codebase {codebase_id} from {analysis_file}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to load analysis for {codebase_id}: {e}")
            return None
    
    def get_file_hashes(self, codebase_id: str) -> Dict[str, str]:
        """
        Get stored file hashes for incremental analysis.
        
        File hashes are used to detect which files have changed since
        the last analysis, enabling efficient incremental updates.
        
        Args:
            codebase_id: Unique identifier for the codebase
        
        Returns:
            Dictionary mapping file paths to their SHA-256 hashes
        """
        try:
            hash_file = self.base_path / codebase_id / "file_hashes.json"
            
            if not hash_file.exists():
                logger.debug(f"No file hashes found for codebase {codebase_id}")
                return {}
            
            with open(hash_file, 'r', encoding='utf-8') as f:
                hashes = json.load(f)
            
            logger.debug(f"Loaded {len(hashes)} file hashes for codebase {codebase_id}")
            return hashes
            
        except Exception as e:
            logger.error(f"Failed to load file hashes for {codebase_id}: {e}")
            return {}
    
    def save_file_hashes(self, codebase_id: str, hashes: Dict[str, str]) -> None:
        """
        Save file hashes for incremental analysis.
        
        Stores a mapping of file paths to their SHA-256 hashes,
        enabling detection of changed files in future analyses.
        
        Args:
            codebase_id: Unique identifier for the codebase
            hashes: Dictionary mapping file paths to SHA-256 hashes
        
        Raises:
            IOError: If unable to write to disk
        """
        try:
            # Create codebase-specific directory
            analysis_dir = self.base_path / codebase_id
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file hashes
            hash_file = analysis_dir / "file_hashes.json"
            with open(hash_file, 'w', encoding='utf-8') as f:
                json.dump(hashes, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(hashes)} file hashes for codebase {codebase_id}")
            
        except Exception as e:
            logger.error(f"Failed to save file hashes for {codebase_id}: {e}")
            raise IOError(f"Failed to save file hashes: {e}") from e
    
    def delete_analysis(self, codebase_id: str) -> bool:
        """
        Delete all stored analysis data for a codebase.
        
        Args:
            codebase_id: Unique identifier for the codebase
        
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            analysis_dir = self.base_path / codebase_id
            
            if not analysis_dir.exists():
                logger.debug(f"No analysis directory found for {codebase_id}")
                return False
            
            # Delete all files in the directory
            for file_path in analysis_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
            
            # Delete the directory
            analysis_dir.rmdir()
            
            logger.info(f"Deleted analysis data for codebase {codebase_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete analysis for {codebase_id}: {e}")
            return False
    
    def list_codebases(self) -> list[str]:
        """
        List all codebases with stored analysis data.
        
        Returns:
            List of codebase IDs
        """
        try:
            if not self.base_path.exists():
                return []
            
            codebases = [
                d.name for d in self.base_path.iterdir() 
                if d.is_dir() and (d / "analysis.json").exists()
            ]
            
            logger.debug(f"Found {len(codebases)} codebases with stored analysis")
            return codebases
            
        except Exception as e:
            logger.error(f"Failed to list codebases: {e}")
            return []
