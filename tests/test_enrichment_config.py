"""Tests for enrichment configuration."""

import pytest
from src.config.settings import Settings


def test_enrichment_defaults():
    """Test that enrichment configuration loads with correct defaults."""
    settings = Settings()
    
    # Test basic settings
    assert settings.enrichment_skill_level == "beginner"
    assert settings.enrichment_tone == "casual"
    assert settings.enrichment_depth == "detailed"
    
    # Test content options
    content_opts = settings.enrichment_content_options
    assert content_opts["include_analogies"] is True
    assert content_opts["include_diagrams"] is True
    assert content_opts["include_examples"] is True
    assert content_opts["include_exercises"] is True
    assert content_opts["include_best_practices"] is True
    assert content_opts["include_anti_patterns"] is True
    assert content_opts["include_real_world_context"] is True
    assert content_opts["progressive_hints"] is True
    
    # Test evidence requirements
    evidence_reqs = settings.enrichment_evidence_requirements
    assert evidence_reqs["always_cite_sources"] is True
    assert evidence_reqs["validate_against_tests"] is True
    assert evidence_reqs["cross_reference_files"] is True
    assert evidence_reqs["include_git_context"] is True
    
    # Test teaching value settings
    teaching_value = settings.enrichment_teaching_value
    assert teaching_value["min_score_to_teach"] == 7
    assert teaching_value["prioritize_fundamentals"] is True
    assert teaching_value["focus_on_reusability"] is True


def test_enrichment_property_accessors():
    """Test enrichment property accessors."""
    settings = Settings()
    
    assert settings.enrichment_skill_level == "beginner"
    assert settings.enrichment_tone == "casual"
    assert settings.enrichment_depth == "detailed"
    assert settings.enrichment_min_score_to_teach == 7
    assert settings.enrichment_include_analogies is True
    assert settings.enrichment_include_diagrams is True
    assert settings.enrichment_always_cite_sources is True
    assert settings.enrichment_validate_against_tests is True


def test_enrichment_validation():
    """Test that invalid enrichment values are rejected."""
    import tempfile
    import yaml
    
    # Create invalid config
    invalid_config = {
        "ai_enrichment": {
            "skill_level": "invalid_level",
            "tone": "casual",
            "depth": "detailed",
            "content_options": {},
            "evidence_requirements": {},
            "teaching_value": {"min_score_to_teach": 7}
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(invalid_config, f)
        config_path = f.name
    
    try:
        with pytest.raises(ValueError, match="skill_level must be one of"):
            Settings(config_path=config_path)
    finally:
        import os
        os.unlink(config_path)


def test_enrichment_min_score_validation():
    """Test that min_score_to_teach is validated."""
    import tempfile
    import yaml
    
    # Create config with invalid min_score
    invalid_config = {
        "ai_enrichment": {
            "skill_level": "beginner",
            "tone": "casual",
            "depth": "detailed",
            "content_options": {},
            "evidence_requirements": {},
            "teaching_value": {"min_score_to_teach": 20}  # Invalid: > 14
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(invalid_config, f)
        config_path = f.name
    
    try:
        with pytest.raises(ValueError, match="must be between 0 and 14"):
            Settings(config_path=config_path)
    finally:
        import os
        os.unlink(config_path)
