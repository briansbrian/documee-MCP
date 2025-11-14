"""
Enrichment Guide Generator - Main orchestrator for AI content enrichment.

This module orchestrates all enrichment components to generate comprehensive,
evidence-based enrichment guides that enable AI assistants (like Kiro) to
create accurate, educational content. It follows the Feature-to-Lesson Mapping
and Knowledge-to-Course frameworks to ensure systematic, validated content generation.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from src.course.enrichment_models import (
    EnrichmentGuide,
    AntiHallucinationRules,
    EnrichmentInstructions
)
from src.course.feature_mapper import FeatureMapper
from src.course.evidence_collector import EvidenceCollector
from src.course.validation_engine import ValidationEngine
from src.course.teaching_value_assessor import TeachingValueAssessor
from src.course.investigation_engine import InvestigationEngine
from src.course.narrative_builder import NarrativeBuilder
from src.course.code_section_guide_generator import CodeSectionGuideGenerator
from src.course.architecture_extractor import ArchitectureExtractor
from src.course.real_world_context_suggester import RealWorldContextSuggester
from src.course.exercise_from_code_generator import ExerciseFromCodeGenerator
from src.analysis.git_analyzer import GitAnalyzer
from src.analysis.engine import AnalysisEngine
from src.course.models import Lesson
from src.models.analysis_models import FileAnalysis

logger = logging.getLogger(__name__)


class EnrichmentGuideGenerator:
    """
    Main orchestrator for generating comprehensive enrichment guides.
    
    This generator coordinates all enrichment components to create evidence-based
    guides following the Feature-to-Lesson Mapping and Knowledge-to-Course frameworks.
    
    The generation process follows these phases:
    1. Feature Mapping - Connect code to user-facing features
    2. Evidence Collection - Gather code, tests, docs, git history
    3. Validation - Cross-reference all evidence sources
    4. Teaching Value Assessment - Score educational value
    5. Systematic Investigation - Answer what, why, how, when, edge cases, pitfalls
    6. Narrative Structure - Build learning progression
    7. Code Section Guides - Create detailed code explanations
    8. Architecture Context - Extract architectural patterns
    9. Real-World Context - Provide practical examples
    10. Exercise Generation - Create hands-on exercises
    """
    
    def __init__(
        self,
        repo_path: str,
        analysis_engine: AnalysisEngine,
        git_analyzer: Optional[GitAnalyzer] = None
    ):
        """
        Initialize the enrichment guide generator.
        
        Args:
            repo_path: Path to the repository root
            analysis_engine: AnalysisEngine for code analysis
            git_analyzer: Optional GitAnalyzer for git history (created if not provided)
        """
        self.repo_path = Path(repo_path).resolve()
        self.analysis_engine = analysis_engine
        
        # Try to create GitAnalyzer if not provided
        if git_analyzer:
            self.git_analyzer = git_analyzer
        else:
            try:
                self.git_analyzer = GitAnalyzer(str(self.repo_path))
            except (ValueError, Exception) as e:
                logger.warning(f"Could not initialize GitAnalyzer: {e}. Git evidence will be unavailable.")
                self.git_analyzer = None
        
        # Initialize all component generators
        self.feature_mapper = FeatureMapper(str(self.repo_path))
        self.evidence_collector = EvidenceCollector(str(self.repo_path))
        self.validation_engine = ValidationEngine()
        self.teaching_value_assessor = TeachingValueAssessor()
        self.investigation_engine = InvestigationEngine()
        self.narrative_builder = NarrativeBuilder()
        self.code_section_generator = CodeSectionGuideGenerator()
        self.architecture_extractor = ArchitectureExtractor(str(self.repo_path))
        self.real_world_suggester = RealWorldContextSuggester()
        self.exercise_generator = ExerciseFromCodeGenerator()
        
        logger.info(f"Initialized EnrichmentGuideGenerator for: {self.repo_path}")
    
    async def generate_guide(
        self,
        codebase_id: str,
        lesson: Lesson,
        file_analysis: Optional[FileAnalysis] = None
    ) -> EnrichmentGuide:
        """
        Generate a comprehensive enrichment guide for a lesson.
        
        This is the main entry point that orchestrates all enrichment components
        to create a complete, evidence-based guide for AI content enrichment.
        
        Args:
            codebase_id: Identifier for the codebase
            lesson: Lesson object containing file path and metadata
            file_analysis: Optional pre-computed FileAnalysis (will analyze if not provided)
            
        Returns:
            Complete EnrichmentGuide with all components
        """
        logger.info(
            f"Generating enrichment guide for lesson '{lesson.lesson_id}' "
            f"in codebase '{codebase_id}'"
        )
        
        try:
            # Get file analysis if not provided
            if not file_analysis:
                logger.info(f"Analyzing file: {lesson.file_path}")
                file_analysis = await self.analysis_engine.analyze_file(
                    lesson.file_path,
                    use_cache=True
                )
            
            # Phase 1: Feature Mapping
            logger.info("Phase 1: Feature Mapping")
            feature_mapping = self.feature_mapper.identify_feature_from_code(
                lesson,
                file_analysis
            )
            
            # Phase 2: Evidence Collection
            logger.info("Phase 2: Evidence Collection")
            evidence_bundle = await self._collect_evidence(lesson, file_analysis)
            
            # Enrich feature mapping with git/doc evidence
            feature_mapping.business_value = self.feature_mapper.extract_business_value(
                feature_mapping,
                {
                    'git_commits': evidence_bundle.git_commits,
                    'documentation': evidence_bundle.documentation
                }
            )
            
            # Phase 3: Validation
            logger.info("Phase 3: Validation")
            validation_checklist = self._validate_understanding(evidence_bundle)
            
            # Phase 4: Teaching Value Assessment
            logger.info("Phase 4: Teaching Value Assessment")
            teaching_value_assessment = self.teaching_value_assessor.assess_teaching_value(
                feature_mapping,
                evidence_bundle,
                file_analysis
            )
            
            # Phase 5: Systematic Investigation
            logger.info("Phase 5: Systematic Investigation")
            systematic_investigation = self.investigation_engine.investigate(
                feature_mapping,
                evidence_bundle,
                validation_checklist
            )
            
            # Phase 6: Code Section Guides
            logger.info("Phase 6: Code Section Guides")
            code_sections = self._generate_code_section_guides(
                lesson,
                evidence_bundle
            )
            
            # Phase 7: Narrative Structure
            logger.info("Phase 7: Narrative Structure")
            narrative_structure = self.narrative_builder.build_narrative(
                systematic_investigation,
                teaching_value_assessment,
                code_sections,
                lesson_context=self._get_lesson_context(lesson),
                course_outline=None  # Could be passed in if available
            )
            
            # Phase 8: Architecture Context
            logger.info("Phase 8: Architecture Context")
            architecture_context = self._extract_architecture_context(
                file_analysis
            )
            
            # Phase 9: Real-World Context
            logger.info("Phase 9: Real-World Context")
            real_world_context = self.real_world_suggester.generate_context(
                feature_mapping,
                file_analysis.patterns,
                evidence_bundle,
                skill_level="beginner"
            )
            
            # Phase 10: Exercise Generation
            logger.info("Phase 10: Exercise Generation")
            exercise_generation = self.exercise_generator.generate_exercises(
                feature_mapping,
                evidence_bundle
            )
            
            # Phase 11: Anti-Hallucination Rules
            anti_hallucination_rules = self._get_anti_hallucination_rules()
            
            # Phase 12: Enrichment Instructions
            enrichment_instructions = self._get_enrichment_instructions(
                teaching_value_assessment
            )
            
            # Create complete enrichment guide
            enrichment_guide = EnrichmentGuide(
                lesson_id=lesson.lesson_id,
                feature_mapping=feature_mapping,
                evidence_bundle=evidence_bundle,
                validation_checklist=validation_checklist,
                teaching_value_assessment=teaching_value_assessment,
                systematic_investigation=systematic_investigation,
                narrative_structure=narrative_structure,
                code_sections=code_sections,
                architecture_context=architecture_context,
                real_world_context=real_world_context,
                exercise_generation=exercise_generation,
                anti_hallucination_rules=anti_hallucination_rules,
                enrichment_instructions=enrichment_instructions
            )
            
            logger.info(
                f"Successfully generated enrichment guide for lesson '{lesson.lesson_id}': "
                f"teaching_value={teaching_value_assessment.total_score}/14, "
                f"should_teach={teaching_value_assessment.should_teach}, "
                f"{len(code_sections)} code sections, "
                f"{len(evidence_bundle.test_files)} test files, "
                f"{len(evidence_bundle.git_commits)} git commits"
            )
            
            return enrichment_guide
            
        except Exception as e:
            logger.error(
                f"Error generating enrichment guide for lesson '{lesson.lesson_id}': {e}",
                exc_info=True
            )
            raise
    
    async def _collect_evidence(
        self,
        lesson: Lesson,
        file_analysis: FileAnalysis
    ) -> Any:  # Returns EvidenceBundle
        """
        Collect all evidence from multiple sources.
        
        Args:
            lesson: Lesson object
            file_analysis: FileAnalysis object
            
        Returns:
            EvidenceBundle with all collected evidence
        """
        from src.course.enrichment_models import EvidenceBundle
        
        # Collect source code evidence
        source_files = await self.evidence_collector.collect_source_evidence(lesson)
        
        # Collect test evidence
        test_files = await self.evidence_collector.collect_test_evidence(lesson)
        
        # Collect documentation evidence
        documentation = self.evidence_collector.collect_documentation_evidence(
            file_analysis
        )
        
        # Collect dependency evidence
        dependencies = self.evidence_collector.collect_dependency_evidence(
            file_analysis
        )
        
        # Collect git commit evidence
        git_commits = []
        if lesson.file_path and self.git_analyzer:
            try:
                commits = self.git_analyzer.get_relevant_commits([lesson.file_path])
                git_commits = commits
            except Exception as e:
                logger.warning(f"Could not collect git commits: {e}")
                git_commits = []
        
        # Collect dependents (files that import this one)
        # This would require dependency graph analysis
        dependents = []  # Placeholder - would need full dependency graph
        
        return EvidenceBundle(
            source_files=source_files,
            test_files=test_files,
            git_commits=git_commits,
            documentation=documentation,
            dependencies=dependencies,
            dependents=dependents
        )
    
    def _validate_understanding(self, evidence_bundle: Any) -> Any:
        """
        Validate understanding across all evidence sources.
        
        Args:
            evidence_bundle: EvidenceBundle with all evidence
            
        Returns:
            ValidationChecklist with validation results
        """
        from src.course.enrichment_models import ValidationChecklist
        
        # Validate code behavior
        code_behavior = self.validation_engine.validate_code_behavior(
            evidence_bundle.source_files
        )
        
        # Validate test expectations
        expected_behavior = self.validation_engine.validate_test_expectations(
            evidence_bundle.test_files
        )
        
        # Validate documentation alignment
        documentation_alignment = self.validation_engine.validate_documentation_alignment(
            evidence_bundle.documentation
        )
        
        # Validate git context
        git_context = self.validation_engine.validate_git_context(
            evidence_bundle.git_commits
        )
        
        # Cross-reference all sources
        consistency_check = self.validation_engine.cross_reference_sources({
            'code_behavior': code_behavior,
            'test_expectations': expected_behavior,
            'documentation_alignment': documentation_alignment,
            'git_context': git_context
        })
        
        return ValidationChecklist(
            code_behavior=code_behavior,
            expected_behavior=expected_behavior,
            documentation_alignment=documentation_alignment,
            git_context=git_context,
            consistency_check=consistency_check
        )
    
    def _generate_code_section_guides(
        self,
        lesson: Lesson,
        evidence_bundle: Any
    ) -> list:
        """
        Generate guides for each code section in the lesson.
        
        Args:
            lesson: Lesson object
            evidence_bundle: EvidenceBundle with evidence
            
        Returns:
            List of CodeSectionGuide objects
        """
        code_sections = []
        
        # Generate guide for main code example if available
        if lesson.content and hasattr(lesson.content, 'code_example'):
            code_example = lesson.content.code_example
            
            if code_example:
                section_guide = self.code_section_generator.generate_section_guide(
                    code_example,
                    evidence_bundle
                )
                code_sections.append(section_guide)
        
        # If no code examples in lesson, create a generic guide from source files
        if not code_sections and evidence_bundle.source_files:
            # Create a code example from the first source file
            from src.course.models import CodeExample
            
            source_file = evidence_bundle.source_files[0]
            code_example = CodeExample(
                code=source_file.get('code', ''),
                language=source_file.get('language', 'unknown'),
                filename=source_file.get('path', '')
            )
            
            section_guide = self.code_section_generator.generate_section_guide(
                code_example,
                evidence_bundle
            )
            code_sections.append(section_guide)
        
        return code_sections
    
    def _extract_architecture_context(
        self,
        file_analysis: FileAnalysis
    ) -> Any:
        """
        Extract architecture context from file analysis.
        
        Args:
            file_analysis: FileAnalysis object
            
        Returns:
            ArchitectureContext object
        """
        # Create a simple dependency graph from file analysis
        from src.analysis.dependency_analyzer import DependencyGraph, FileNode
        
        # Build a minimal dependency graph for this file
        dependency_graph = DependencyGraph()
        
        # Create node for this file
        node = FileNode(file_path=file_analysis.file_path)
        
        # Add imports as dependencies
        for import_info in file_analysis.symbol_info.imports:
            if not import_info.is_relative:
                node.external_imports.append(import_info.module)
            else:
                node.imports.append(import_info.module)
        
        dependency_graph.nodes[file_analysis.file_path] = node
        
        # Extract architecture context
        return self.architecture_extractor.extract_architecture_context(
            file_analysis,
            dependency_graph
        )
    
    def _get_lesson_context(self, lesson: Lesson) -> Dict[str, Any]:
        """
        Extract lesson context for narrative building.
        
        Args:
            lesson: Lesson object
            
        Returns:
            Dictionary with lesson context
        """
        return {
            'title': lesson.title,
            'lesson_id': lesson.lesson_id,
            'file_path': lesson.file_path,
            'prerequisites': [],  # Could be extracted from lesson metadata
            'related_topics': []  # Could be extracted from lesson metadata
        }
    
    def _get_anti_hallucination_rules(self) -> AntiHallucinationRules:
        """
        Get anti-hallucination rules for AI content generation.
        
        Returns:
            AntiHallucinationRules object with guidelines
        """
        return AntiHallucinationRules(
            always_cite="Never explain code behavior without citing specific evidence from code, tests, or documentation",
            distinguish_fact_inference="Clearly mark inferences and assumptions as such, distinguishing them from verified facts",
            validate_against_tests="Always check test files to verify expected behavior before explaining functionality",
            cross_reference="Verify consistency across multiple evidence sources (code, tests, docs, git) before making claims",
            avoid_assumptions="Don't guess the 'why' behind code - cite git commits or documentation for rationale"
        )
    
    def _get_enrichment_instructions(
        self,
        teaching_value: Any
    ) -> EnrichmentInstructions:
        """
        Get enrichment instructions tailored to the lesson.
        
        Args:
            teaching_value: TeachingValueAssessment object
            
        Returns:
            EnrichmentInstructions object with guidelines
        """
        # Determine focus areas based on teaching value scores
        focus_areas = []
        
        if teaching_value.scores.get('best_practice', 0) >= 2:
            focus_areas.append("Emphasize best practices and why they matter")
        
        if teaching_value.scores.get('reusability', 0) >= 2:
            focus_areas.append("Highlight reusable patterns and where else they apply")
        
        if teaching_value.scores.get('fundamentality', 0) >= 2:
            focus_areas.append("Explain fundamental concepts thoroughly for beginners")
        
        if teaching_value.scores.get('junior_dev', 0) >= 2:
            focus_areas.append("Make content accessible for junior developers")
        
        if teaching_value.scores.get('uniqueness', 0) >= 1:
            focus_areas.append("Explain unique or interesting aspects of the implementation")
        
        # Default focus areas if none identified
        if not focus_areas:
            focus_areas = [
                "Explain the core functionality clearly",
                "Provide practical examples",
                "Connect to real-world use cases"
            ]
        
        # Determine what to avoid based on complexity and audience
        avoid_topics = [
            "Overly academic theory without practical application",
            "Framework-specific implementation details that may change",
            "Advanced optimization techniques for beginner content",
            "Deprecated patterns or outdated practices"
        ]
        
        return EnrichmentInstructions(
            tone="casual",
            depth="detailed",
            focus_areas=focus_areas,
            avoid_topics=avoid_topics,
            evidence_requirements="Cite evidence for every claim - include file paths, line numbers, test names, or commit hashes"
        )


def create_enrichment_guide_generator(
    repo_path: str,
    analysis_engine: AnalysisEngine,
    git_analyzer: Optional[GitAnalyzer] = None
) -> EnrichmentGuideGenerator:
    """
    Factory function to create an EnrichmentGuideGenerator instance.
    
    Args:
        repo_path: Path to repository root
        analysis_engine: AnalysisEngine for code analysis
        git_analyzer: Optional GitAnalyzer for git history
        
    Returns:
        EnrichmentGuideGenerator instance
    """
    return EnrichmentGuideGenerator(repo_path, analysis_engine, git_analyzer)
