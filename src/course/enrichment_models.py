"""
Data models for AI content enrichment system.

This module defines comprehensive dataclass models for the enrichment guide system,
following the Feature-to-Lesson Mapping and Knowledge-to-Course frameworks.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


@dataclass
class FeatureMapping:
    """Maps code to user-facing feature (FEATURE-TO-LESSON-MAPPING)."""
    
    feature_name: str
    user_facing_purpose: str  # What users do with this feature
    business_value: str  # Why this feature exists
    entry_points: List[str]  # Where users/code interact with this feature
    feature_flow: List[str]  # Step-by-step user/data flow
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureMapping':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class EvidenceBundle:
    """Collection of evidence for validation (anti-hallucination)."""
    
    source_files: List[Dict[str, Any]]  # {path, lines, code}
    test_files: List[Dict[str, Any]]  # {path, tests, descriptions}
    git_commits: List[Dict[str, Any]]  # {hash, message, date, author}
    documentation: List[Dict[str, Any]]  # {type, content, location}
    dependencies: List[Dict[str, Any]]  # {name, reason, evidence}
    dependents: List[Dict[str, Any]]  # {name, usage, evidence}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvidenceBundle':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class ValidationChecklist:
    """Validation results from multiple sources."""
    
    code_behavior: str  # What code actually does
    expected_behavior: str  # What tests expect
    documentation_alignment: str  # What docs say
    git_context: str  # Why it was built
    consistency_check: bool  # Are all sources consistent?
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationChecklist':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class TeachingValueAssessment:
    """Teaching value scoring (0-14 scale)."""
    
    scores: Dict[str, int]  # reusability, best_practice, fundamentality, uniqueness, junior_dev
    total_score: int  # Sum of all scores
    should_teach: bool  # True if total > 7
    reasoning: str  # Explanation of scores
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeachingValueAssessment':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class SystematicInvestigation:
    """Results of systematic code investigation."""
    
    what_it_does: str  # Factual description (cite code)
    why_it_exists: str  # Business/technical reason (cite commits)
    how_it_works: str  # Implementation details (cite code)
    when_its_used: List[str]  # Usage scenarios (cite call sites)
    edge_cases: List[str]  # Special handling (cite tests)
    common_pitfalls: List[str]  # Known issues (cite evidence)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystematicInvestigation':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class NarrativeStructure:
    """Structure for lesson narrative."""
    
    introduction_points: List[str]  # Context and motivation
    learning_progression: List[str]  # Ordered concepts (simple → complex)
    code_walkthrough_order: List[str]  # Which code to explain when
    conclusion_points: List[str]  # Key takeaways
    next_steps: List[str]  # What to learn next
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeStructure':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class CodeSectionGuide:
    """Evidence-based guide for code section."""
    
    file_path: str
    line_range: Tuple[int, int]
    code_snippet: str
    purpose: str  # What it does (cite tests)
    key_concepts: List[str]  # Concepts demonstrated
    explanation_approach: List[str]  # How to explain (simple → complex)
    related_code: List[Dict[str, str]]  # {path, context, relationship}
    test_evidence: List[Dict[str, str]]  # {test_name, description, file}
    git_evidence: List[Dict[str, str]]  # {commit, message, date}
    common_mistakes: List[str]  # Pitfalls to highlight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert tuple to list for JSON serialization
        data['line_range'] = list(data['line_range'])
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeSectionGuide':
        """Create instance from dictionary."""
        # Convert list back to tuple for line_range
        if isinstance(data.get('line_range'), list):
            data['line_range'] = tuple(data['line_range'])
        return cls(**data)


@dataclass
class ArchitectureContext:
    """Architectural context with evidence."""
    
    component_role: str  # Role in system (cite dependency graph)
    data_flow: str  # How data moves (cite code)
    interaction_diagram: str  # Mermaid diagram
    dependencies: List[Dict[str, str]]  # {name, reason, evidence}
    dependents: List[Dict[str, str]]  # {name, usage, evidence}
    design_patterns: List[Dict[str, str]]  # {pattern, evidence, explanation}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArchitectureContext':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class RealWorldContext:
    """Real-world context and analogies."""
    
    practical_use_cases: List[str]  # Real scenarios
    analogies: List[str]  # Beginner-friendly comparisons
    industry_patterns: List[str]  # Standard approaches
    best_practices: List[str]  # What to emphasize
    anti_patterns: List[str]  # What to avoid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealWorldContext':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class ExerciseGeneration:
    """Exercise generation from codebase."""
    
    hands_on_tasks: List[Dict[str, str]]  # {title, description, difficulty}
    starter_code: str  # Template to complete
    solution_code: str  # Complete solution (from codebase)
    test_cases: List[Dict[str, Any]]  # Validation tests
    progressive_hints: List[str]  # 3-5 hints (general → specific)
    self_assessment: List[str]  # Questions to check understanding
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExerciseGeneration':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class AntiHallucinationRules:
    """Rules to prevent hallucination."""
    
    always_cite: str = "Never explain without citing evidence"
    distinguish_fact_inference: str = "Mark inferences clearly"
    validate_against_tests: str = "Check tests before explaining"
    cross_reference: str = "Verify across multiple files"
    avoid_assumptions: str = "Don't guess the 'why'"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AntiHallucinationRules':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class EnrichmentInstructions:
    """Instructions for AI enrichment."""
    
    tone: str = "casual"  # casual (beginner-friendly)
    depth: str = "detailed"  # detailed (explain thoroughly)
    focus_areas: List[str] = field(default_factory=list)  # What to emphasize
    avoid_topics: List[str] = field(default_factory=list)  # What not to mention
    evidence_requirements: str = "Cite for every claim"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnrichmentInstructions':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class EnrichmentGuide:
    """Complete enrichment guide with evidence."""
    
    lesson_id: str
    feature_mapping: FeatureMapping
    evidence_bundle: EvidenceBundle
    validation_checklist: ValidationChecklist
    teaching_value_assessment: TeachingValueAssessment
    systematic_investigation: SystematicInvestigation
    narrative_structure: NarrativeStructure
    code_sections: List[CodeSectionGuide]
    architecture_context: ArchitectureContext
    real_world_context: RealWorldContext
    exercise_generation: ExerciseGeneration
    anti_hallucination_rules: AntiHallucinationRules
    enrichment_instructions: EnrichmentInstructions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'lesson_id': self.lesson_id,
            'feature_mapping': self.feature_mapping.to_dict(),
            'evidence_bundle': self.evidence_bundle.to_dict(),
            'validation_checklist': self.validation_checklist.to_dict(),
            'teaching_value_assessment': self.teaching_value_assessment.to_dict(),
            'systematic_investigation': self.systematic_investigation.to_dict(),
            'narrative_structure': self.narrative_structure.to_dict(),
            'code_sections': [section.to_dict() for section in self.code_sections],
            'architecture_context': self.architecture_context.to_dict(),
            'real_world_context': self.real_world_context.to_dict(),
            'exercise_generation': self.exercise_generation.to_dict(),
            'anti_hallucination_rules': self.anti_hallucination_rules.to_dict(),
            'enrichment_instructions': self.enrichment_instructions.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnrichmentGuide':
        """Create instance from dictionary."""
        return cls(
            lesson_id=data['lesson_id'],
            feature_mapping=FeatureMapping.from_dict(data['feature_mapping']),
            evidence_bundle=EvidenceBundle.from_dict(data['evidence_bundle']),
            validation_checklist=ValidationChecklist.from_dict(data['validation_checklist']),
            teaching_value_assessment=TeachingValueAssessment.from_dict(data['teaching_value_assessment']),
            systematic_investigation=SystematicInvestigation.from_dict(data['systematic_investigation']),
            narrative_structure=NarrativeStructure.from_dict(data['narrative_structure']),
            code_sections=[CodeSectionGuide.from_dict(section) for section in data['code_sections']],
            architecture_context=ArchitectureContext.from_dict(data['architecture_context']),
            real_world_context=RealWorldContext.from_dict(data['real_world_context']),
            exercise_generation=ExerciseGeneration.from_dict(data['exercise_generation']),
            anti_hallucination_rules=AntiHallucinationRules.from_dict(data['anti_hallucination_rules']),
            enrichment_instructions=EnrichmentInstructions.from_dict(data['enrichment_instructions'])
        )


@dataclass
class EnrichmentStatus:
    """Tracks enrichment progress for lessons."""
    
    lesson_id: str
    status: str  # "pending", "in_progress", "completed"
    enriched_at: Optional[datetime] = None
    enriched_by: str = "kiro"  # "kiro" or user identifier
    version: int = 1  # Increment when re-enriched
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime to ISO format string
        if data['enriched_at']:
            data['enriched_at'] = data['enriched_at'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnrichmentStatus':
        """Create instance from dictionary."""
        # Convert ISO format string back to datetime
        if data.get('enriched_at') and isinstance(data['enriched_at'], str):
            data['enriched_at'] = datetime.fromisoformat(data['enriched_at'])
        return cls(**data)
