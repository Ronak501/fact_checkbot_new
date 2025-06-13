from typing import Dict, Any

class SourceValidator:
    def __init__(self):
        self.credible_sources = set()

    def add_credible_source(self, source: str) -> None:
        """Add a source to the list of credible sources."""
        self.credible_sources.add(source)

    def is_credible(self, source: str) -> bool:
        """Check if a source is credible."""
        return source in self.credible_sources

# Example usage
if __name__ == "__main__":
    validator = SourceValidator()
    validator.add_credible_source("Example Source")
    print(validator.is_credible("Example Source"))
