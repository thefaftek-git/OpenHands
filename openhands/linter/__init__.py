"""Linter module for OpenHands.

Part of this Linter module is adapted from Aider (Apache 2.0 License, [original
code](https://github.com/paul-gauthier/aider/blob/main/aider/linter.py)).
- Please see the [original repository](https://github.com/paul-gauthier/aider) for more information.
- The detailed implementation of the linter can be found at: https://github.com/All-Hands-AI/openhands-aci.
"""


# Create a minimal local linter to avoid circular imports
class LintResult:
    def __init__(self, line=0, column=0, message='', file_path=''):
        self.line = line
        self.column = column
        self.message = message
        self.file_path = file_path

    def __repr__(self):
        return f"LintResult(line={self.line}, column={self.column}, message='{self.message}', file_path='{self.file_path}')"


class DefaultLinter:
    """Minimal linter implementation to avoid circular imports."""

    def __init__(self):
        pass

    def lint(self, file_path):
        """Dummy lint method that returns no errors."""
        return []


__all__ = ['DefaultLinter', 'LintResult']
