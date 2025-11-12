"""Template Engine - Renders content using Jinja2 templates."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, DictLoader, TemplateError, TemplateSyntaxError
from .config import CourseConfig


class TemplateEngine:
    """Renders course content using Jinja2 templates."""
    
    def __init__(self, config: CourseConfig):
        """Initialize the template engine.
        
        Args:
            config: Course generation configuration
        """
        self.config = config
        self.env = self._create_environment()
    
    def _create_environment(self) -> Environment:
        """Create and configure the Jinja2 environment.
        
        Returns:
            Configured Jinja2 Environment
        """
        # Determine template directory
        if self.config.template_dir and os.path.exists(self.config.template_dir):
            # Use custom template directory
            loader = FileSystemLoader(self.config.template_dir)
        else:
            # Use default templates directory
            default_template_dir = Path(__file__).parent / "templates"
            if default_template_dir.exists():
                loader = FileSystemLoader(str(default_template_dir))
            else:
                # Fallback to empty DictLoader if no templates directory exists
                loader = DictLoader({})
        
        # Create environment with configuration
        env = Environment(
            loader=loader,
            autoescape=False,  # We're generating markdown, not HTML
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Add custom filters
        env.filters['slugify'] = self._slugify
        env.filters['format_duration'] = self._format_duration
        
        return env
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug.
        
        Args:
            text: Text to slugify
            
        Returns:
            Slugified text
        """
        return text.lower().replace(' ', '-').replace('_', '-')
    
    def _format_duration(self, minutes: int) -> str:
        """Format duration in minutes to human-readable format.
        
        Args:
            minutes: Duration in minutes
            
        Returns:
            Formatted duration string
        """
        if minutes < 60:
            return f"{minutes} minutes"
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minutes"
    
    def validate_template(self, template_name: str) -> bool:
        """Validate that a template exists and has valid syntax.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            True if template is valid
            
        Raises:
            TemplateError: If template is invalid or doesn't exist
        """
        try:
            # Try to get the template - this will raise if it doesn't exist or has syntax errors
            self.env.get_template(template_name)
            return True
        except TemplateSyntaxError as e:
            raise TemplateError(f"Template '{template_name}' has syntax error at line {e.lineno}: {e.message}")
        except Exception as e:
            raise TemplateError(f"Template '{template_name}' validation failed: {str(e)}")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Template variables
            
        Returns:
            Rendered template content
            
        Raises:
            TemplateError: If template rendering fails
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateSyntaxError as e:
            raise TemplateError(f"Template '{template_name}' has syntax error at line {e.lineno}: {e.message}")
        except Exception as e:
            raise TemplateError(f"Failed to render template '{template_name}': {str(e)}")
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Render a template from a string.
        
        Args:
            template_string: Template content as string
            context: Template variables
            
        Returns:
            Rendered template content
            
        Raises:
            TemplateError: If template rendering fails
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**context)
        except TemplateSyntaxError as e:
            raise TemplateError(f"Template string has syntax error at line {e.lineno}: {e.message}")
        except Exception as e:
            raise TemplateError(f"Failed to render template string: {str(e)}")
    
    def list_templates(self) -> list[str]:
        """List all available templates.
        
        Returns:
            List of template names
        """
        return self.env.list_templates()
    
    def add_template(self, name: str, content: str) -> None:
        """Add a template dynamically to the environment.
        
        Args:
            name: Template name
            content: Template content
        """
        # Create a new DictLoader with the new template
        if isinstance(self.env.loader, DictLoader):
            self.env.loader.mapping[name] = content
        else:
            # If using FileSystemLoader, we can't add templates dynamically
            # This would require switching to a ChoiceLoader
            raise NotImplementedError("Cannot add templates dynamically when using FileSystemLoader")
    
    def render_lesson(self, lesson: Any) -> str:
        """Render a lesson using the lesson template.
        
        Args:
            lesson: Lesson object to render
            
        Returns:
            Rendered lesson content
        """
        return self.render_template("lesson.md.j2", {"lesson": lesson})
    
    def render_exercise(self, exercise: Any) -> str:
        """Render an exercise using the exercise template.
        
        Args:
            exercise: Exercise object to render
            
        Returns:
            Rendered exercise content
        """
        return self.render_template("exercise.md.j2", {"exercise": exercise})
    
    def render_module(self, module: Any) -> str:
        """Render a module using the module template.
        
        Args:
            module: Module object to render
            
        Returns:
            Rendered module content
        """
        return self.render_template("module.md.j2", {"module": module})
    
    def render_index(self, course: Any) -> str:
        """Render the course index using the index template.
        
        Args:
            course: CourseOutline object to render
            
        Returns:
            Rendered index content
        """
        return self.render_template("index.md.j2", {"course": course})
