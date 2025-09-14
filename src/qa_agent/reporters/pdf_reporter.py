class PDFReporter:
    def __init__(self, config=None):
        self.config = config or {}
    
    async def generate_report(self, report, output_path):
        return output_path / "report.pdf"
