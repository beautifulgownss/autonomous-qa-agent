import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Test basic imports
try:
    from qa_agent.core.agent import QAAgent, QAIssue, IssueType
    print("✅ Core imports working")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test agent creation
try:
    agent = QAAgent()
    print("✅ Agent creation working")
except Exception as e:
    print(f"❌ Agent creation failed: {e}")
    sys.exit(1)

print("Basic setup is working!")
