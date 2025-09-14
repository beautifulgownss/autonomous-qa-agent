import asyncio
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import logging
from pathlib import Path

class IssueType(Enum):
    BUG = "bug"
    ACCESSIBILITY = "accessibility" 
    PERFORMANCE = "performance"
    SECURITY = "security"
    UX = "user_experience"
    VISUAL = "visual_regression"

class IssueSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class QAIssue:
    """Represents a detected QA issue"""
    id: str
    type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    element_selector: Optional[str] = None
    screenshot_path: Optional[str] = None
    steps_to_reproduce: List[str] = field(default_factory=list)
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QAReport:
    """Complete QA analysis report"""
    url: str
    timestamp: float
    issues: List[QAIssue]
    summary: Dict[str, Any]
    metrics: Dict[str, float]
    recommendations: List[str]
    execution_time_ms: float

class QAAgent:
    """Autonomous QA Agent that analyzes websites for issues"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.detectors = []
        self.analyzers = []
        self.reporters = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._setup_logging()
        self._load_detectors()
        self._load_analyzers()
        self._load_reporters()
    
    def _setup_logging(self):
        """Configure logging for the agent"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_detectors(self):
        """Load all available issue detectors"""
        from ..detectors.accessibility_detector import AccessibilityDetector
        from ..detectors.performance_detector import PerformanceDetector
        from ..detectors.visual_detector import VisualDetector
        from ..detectors.security_detector import SecurityDetector
        
        self.detectors = [
            AccessibilityDetector(self.config.get('accessibility', {})),
            PerformanceDetector(self.config.get('performance', {})),
            VisualDetector(self.config.get('visual', {})),
            SecurityDetector(self.config.get('security', {}))
        ]
    
    def _load_analyzers(self):
        """Load content analyzers"""
        from ..analyzers.content_analyzer import ContentAnalyzer
        from ..analyzers.layout_analyzer import LayoutAnalyzer
        from ..analyzers.interaction_analyzer import InteractionAnalyzer
        
        self.analyzers = [
            ContentAnalyzer(self.config.get('content', {})),
            LayoutAnalyzer(self.config.get('layout', {})),
            InteractionAnalyzer(self.config.get('interaction', {}))
        ]
    
    def _load_reporters(self):
        """Load report generators"""
        from ..reporters.html_reporter import HTMLReporter
        from ..reporters.json_reporter import JSONReporter
        from ..reporters.pdf_reporter import PDFReporter
        
        self.reporters = [
            HTMLReporter(self.config.get('html_report', {})),
            JSONReporter(self.config.get('json_report', {})),
            PDFReporter(self.config.get('pdf_report', {}))
        ]
    
    async def analyze_website(self, url: str, options: Optional[Dict[str, Any]] = None) -> QAReport:
        """Main entry point: analyze a website and return comprehensive QA report"""
        start_time = time.time()
        options = options or {}
        
        self.logger.info(f"Starting QA analysis for: {url}")
        
        try:
            # Phase 1: Web scraping and data collection
            page_data = await self._collect_page_data(url, options)
            
            # Phase 2: Run all detectors in parallel
            all_issues = await self._run_detectors(page_data)
            
            # Phase 3: Analyze content and interactions
            analysis_results = await self._run_analyzers(page_data)
            
            # Phase 4: Generate recommendations
            recommendations = await self._generate_recommendations(all_issues, analysis_results)
            
            # Phase 5: Create comprehensive report
            execution_time = (time.time() - start_time) * 1000
            
            report = QAReport(
                url=url,
                timestamp=time.time(),
                issues=all_issues,
                summary=self._create_summary(all_issues),
                metrics=self._calculate_metrics(all_issues, analysis_results),
                recommendations=recommendations,
                execution_time_ms=execution_time
            )
            
            self.logger.info(f"Analysis complete. Found {len(all_issues)} issues in {execution_time:.2f}ms")
            return report
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {url}: {str(e)}")
            raise
    
    async def _collect_page_data(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Collect all necessary data from the webpage"""
        from .web_scraper import WebScraper
        
        scraper = WebScraper(self.config.get('scraper', {}))
        
        # Collect comprehensive page data
        page_data = await scraper.scrape_page(url, {
            'take_screenshots': True,
            'analyze_accessibility': True,
            'measure_performance': True,
            'extract_forms': True,
            'map_user_flows': True,
            **options
        })
        
        return page_data
    
    async def _run_detectors(self, page_data: Dict[str, Any]) -> List[QAIssue]:
        """Run all issue detectors in parallel"""
        tasks = []
        
        for detector in self.detectors:
            if detector.is_enabled():
                task = asyncio.create_task(detector.detect_issues(page_data))
                tasks.append(task)
        
        # Wait for all detectors to complete
        detector_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten all issues and handle exceptions
        all_issues = []
        for i, result in enumerate(detector_results):
            if isinstance(result, Exception):
                self.logger.error(f"Detector {self.detectors[i].__class__.__name__} failed: {result}")
            else:
                all_issues.extend(result)
        
        return all_issues
    
    async def _run_analyzers(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run content and interaction analyzers"""
        tasks = []
        
        for analyzer in self.analyzers:
            task = asyncio.create_task(analyzer.analyze(page_data))
            tasks.append(task)
        
        analyzer_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all analysis results
        combined_results = {}
        for i, result in enumerate(analyzer_results):
            if isinstance(result, Exception):
                self.logger.error(f"Analyzer {self.analyzers[i].__class__.__name__} failed: {result}")
            else:
                analyzer_name = self.analyzers[i].__class__.__name__.lower()
                combined_results[analyzer_name] = result
        
        return combined_results
    
    async def _generate_recommendations(self, issues: List[QAIssue], analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on detected issues"""
        from .recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine(self.config.get('recommendations', {}))
        return await engine.generate_recommendations(issues, analysis)
    
    def _create_summary(self, issues: List[QAIssue]) -> Dict[str, Any]:
        """Create summary statistics for the report"""
        summary = {
            'total_issues': len(issues),
            'by_severity': {},
            'by_type': {},
            'critical_issues': []
        }
        
        for issue in issues:
            # Count by severity
            severity = issue.severity.value
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Count by type
            issue_type = issue.type.value
            summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1
            
            # Collect critical issues
            if issue.severity == IssueSeverity.CRITICAL:
                summary['critical_issues'].append({
                    'title': issue.title,
                    'type': issue.type.value
                })
        
        return summary
    
    def _calculate_metrics(self, issues: List[QAIssue], analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics and scores"""
        total_issues = len(issues)
        critical_issues = len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
        high_issues = len([i for i in issues if i.severity == IssueSeverity.HIGH])
        
        # Quality score (0-100, higher is better)
        quality_score = max(0, 100 - (critical_issues * 25 + high_issues * 10 + total_issues * 2))
        
        metrics = {
            'quality_score': quality_score,
            'accessibility_score': self._calculate_accessibility_score(issues),
            'performance_score': analysis.get('performance', {}).get('score', 100),
            'security_score': self._calculate_security_score(issues),
            'ux_score': self._calculate_ux_score(issues)
        }
        
        return metrics
    
    def _calculate_accessibility_score(self, issues: List[QAIssue]) -> float:
        """Calculate accessibility compliance score"""
        accessibility_issues = [i for i in issues if i.type == IssueType.ACCESSIBILITY]
        if not accessibility_issues:
            return 100.0
        
        penalty = sum(
            25 if issue.severity == IssueSeverity.CRITICAL else
            15 if issue.severity == IssueSeverity.HIGH else
            5 if issue.severity == IssueSeverity.MEDIUM else 1
            for issue in accessibility_issues
        )
        
        return max(0, 100 - penalty)
    
    def _calculate_security_score(self, issues: List[QAIssue]) -> float:
        """Calculate security assessment score"""
        security_issues = [i for i in issues if i.type == IssueType.SECURITY]
        if not security_issues:
            return 100.0
        
        penalty = sum(
            40 if issue.severity == IssueSeverity.CRITICAL else
            25 if issue.severity == IssueSeverity.HIGH else
            10 if issue.severity == IssueSeverity.MEDIUM else 2
            for issue in security_issues
        )
        
        return max(0, 100 - penalty)
    
    def _calculate_ux_score(self, issues: List[QAIssue]) -> float:
        """Calculate user experience score"""
        ux_issues = [i for i in issues if i.type == IssueType.UX]
        if not ux_issues:
            return 100.0
        
        penalty = sum(
            20 if issue.severity == IssueSeverity.CRITICAL else
            12 if issue.severity == IssueSeverity.HIGH else
            6 if issue.severity == IssueSeverity.MEDIUM else 2
            for issue in ux_issues
        )
        
        return max(0, 100 - penalty)
