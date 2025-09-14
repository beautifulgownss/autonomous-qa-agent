import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from qa_agent.core.agent import QAAgent

async def test_basic_functionality():
    """Test basic QA agent functionality"""
    
    # Create agent with minimal config
    agent = QAAgent({
        'accessibility': {'enabled': True},
        'performance': {'enabled': False},
        'visual': {'enabled': False},
        'security': {'enabled': False}
    })
    
    # Test on a simple website
    test_url = "https://example.com"
    print(f"Testing QA Agent on: {test_url}")
    
    try:
        report = await agent.analyze_website(test_url)
        
        print(f"\n=== QA Analysis Results ===")
        print(f"URL: {report.url}")
        print(f"Issues Found: {len(report.issues)}")
        print(f"Quality Score: {report.metrics.get('quality_score', 'N/A')}")
        print(f"Execution Time: {report.execution_time_ms:.2f}ms")
        
        if report.issues:
            print(f"\n=== Issues Detected ===")
            for issue in report.issues[:3]:
                print(f"- {issue.title} ({issue.severity.value})")
                print(f"  {issue.description}")
        
        print(f"\nTest completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
