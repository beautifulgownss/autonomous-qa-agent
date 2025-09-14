class PerformanceDetector:
    def __init__(self, config=None):
        self.config = config or {}
    
    def is_enabled(self):
        return False
    
    async def detect_issues(self, page_data):
        return []
