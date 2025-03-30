"""
Template loader utility for financial analysis templates.
Provides easy access to specialized analysis templates.
"""

import os
from typing import Dict, Optional
from pathlib import Path

class TemplateLoader:
    """Loads and manages financial analysis templates."""
    
    def __init__(self):
        """Initialize the template loader."""
        self.template_dir = Path(__file__).parent
        self.templates: Dict[str, str] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all available templates."""
        template_files = {
            'balance_sheet': 'balance_sheet_template.md',
            'income_statement': 'income_statement_template.md',
            'cash_flow': 'cash_flow_template.md'
        }
        
        for key, filename in template_files.items():
            path = self.template_dir / filename
            try:
                with open(path, 'r') as f:
                    self.templates[key] = f.read()
            except FileNotFoundError:
                print(f"Warning: Template file {filename} not found")
    
    def get_template(self, template_type: str) -> Optional[str]:
        """
        Get a specific template by type.
        
        Args:
            template_type: Type of template ('balance_sheet', 'income_statement', or 'cash_flow')
            
        Returns:
            Template content if found, None otherwise
        """
        return self.templates.get(template_type)
    
    def get_combined_template(self, template_types: list[str]) -> str:
        """
        Combine multiple templates for comprehensive analysis.
        
        Args:
            template_types: List of template types to combine
            
        Returns:
            Combined template content
        """
        templates = []
        for template_type in template_types:
            if template := self.get_template(template_type):
                templates.append(template)
        
        return "\n\n".join(templates)
    
    def list_available_templates(self) -> list[str]:
        """List all available template types."""
        return list(self.templates.keys())
    
    def get_template_preview(self, template_type: str, max_length: int = 200) -> Optional[str]:
        """
        Get a preview of a template.
        
        Args:
            template_type: Type of template to preview
            max_length: Maximum length of preview
            
        Returns:
            Template preview if found, None otherwise
        """
        if template := self.get_template(template_type):
            preview = template.split('\n')[0:5]
            return '\n'.join(preview) + '...'
        return None

# Example usage:
if __name__ == "__main__":
    loader = TemplateLoader()
    
    # List available templates
    print("Available templates:", loader.list_available_templates())
    
    # Get a specific template
    if balance_sheet_template := loader.get_template('balance_sheet'):
        print("\nBalance Sheet Template Preview:")
        print(loader.get_template_preview('balance_sheet'))
    
    # Combine templates for comprehensive analysis
    comprehensive = loader.get_combined_template(['balance_sheet', 'income_statement', 'cash_flow'])
    print("\nComprehensive Analysis Template Created") 