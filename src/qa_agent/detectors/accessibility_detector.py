import uuid
from typing import List, Dict, Any
from ..core.agent import QAIssue, IssueType, IssueSeverity

class AccessibilityDetector:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    async def detect_issues(self, page_data: Dict[str, Any]) -> List[QAIssue]:
        """Detect accessibility issues in the page"""
        issues = []
        
        if 'accessibility' not in page_data:
            return issues
        
        accessibility_data = page_data['accessibility']
        
        # Process detected accessibility issues
        for issue_data in accessibility_data.get('issues', []):
            issue = self._create_accessibility_issue(issue_data, page_data['url'])
            if issue:
                issues.append(issue)
        
        return issues
    
    def _create_accessibility_issue(self, issue_data: Dict[str, Any], url: str) -> QAIssue:
        """Convert raw accessibility issue to QAIssue"""
        
        issue_type = issue_data['type']
        element = issue_data['element']
        
        severity_map = {
            'missing_alt_text': IssueSeverity.HIGH,
            'keyboard_accessibility': IssueSeverity.CRITICAL,
            'color_contrast': IssueSeverity.MEDIUM,
            'heading_structure': IssueSeverity.MEDIUM
        }
        
        return QAIssue(
            id=str(uuid.uuid4()),
            type=IssueType.ACCESSIBILITY,
            severity=severity_map.get(issue_type, IssueSeverity.MEDIUM),
            title=self._get_issue_title(issue_type),
            description=issue_data['message'],
            element_selector=element.get('selector'),
            steps_to_reproduce=[
                f"Navigate to {url}",
                f"Locate element: {element.get('tagName', 'unknown')}",
                "Check accessibility compliance"
            ],
            expected_behavior=self._get_expected_behavior(issue_type),
            actual_behavior=issue_data['message'],
            confidence=0.9,
            metadata={
                'wcag_guideline': self._get_wcag_guideline(issue_type),
                'element_details': element
            }
        )
    
    def _get_issue_title(self, issue_type: str) -> str:
        titles = {
            'missing_alt_text': 'Image Missing Alt Text',
            'keyboard_accessibility': 'Element Not Keyboard Accessible',
            'color_contrast': 'Insufficient Color Contrast',
            'heading_structure': 'Improper Heading Structure'
        }
        return titles.get(issue_type, 'Accessibility Issue')
    
    def _get_expected_behavior(self, issue_type: str) -> str:
        behaviors = {
            'missing_alt_text': 'All images should have descriptive alt text',
            'keyboard_accessibility': 'All interactive elements should be keyboard accessible',
            'color_contrast': 'Text should have sufficient contrast ratio (4.5:1 minimum)',
            'heading_structure': 'Headings should follow proper hierarchical structure'
        }
        return behaviors.get(issue_type, 'Element should be accessible')
    
    def _get_wcag_guideline(self, issue_type: str) -> str:
        guidelines = {
            'missing_alt_text': 'WCAG 2.1 - 1.1.1 Non-text Content',
            'keyboard_accessibility': 'WCAG 2.1 - 2.1.1 Keyboard',
            'color_contrast': 'WCAG 2.1 - 1.4.3 Contrast (Minimum)',
            'heading_structure': 'WCAG 2.1 - 1.3.1 Info and Relationships'
        }
        return guidelines.get(issue_type, 'WCAG 2.1')
