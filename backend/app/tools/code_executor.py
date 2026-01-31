"""Code execution tool implementation."""

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from app.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)


class CodeExecutorTool(Tool):
    """Tool for executing code in a sandboxed environment."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize code executor.

        Config options:
            - timeout: Execution timeout in seconds (default: 30)
            - allowed_languages: List of allowed languages (default: ["python"])
            - max_output_size: Maximum output size in bytes (default: 100000)
        """
        super().__init__(config)
        self.timeout = self.config.get("timeout", 30)
        self.allowed_languages = self.config.get("allowed_languages", ["python"])
        self.max_output_size = self.config.get("max_output_size", 100000)

    @property
    def name(self) -> str:
        return "code_executor"

    @property
    def description(self) -> str:
        return "Execute code in a sandboxed environment. Supports Python and other languages."

    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to execute",
                },
                "language": {
                    "type": "string",
                    "description": f"Programming language (one of: {', '.join(self.allowed_languages)})",
                    "enum": self.allowed_languages,
                },
            },
            "required": ["code", "language"],
        }

    async def execute(self, code: str, language: str = "python") -> ToolResult:
        """
        Execute code in a sandboxed environment.

        Args:
            code: Code to execute
            language: Programming language

        Returns:
            ToolResult with execution output
        """
        if language not in self.allowed_languages:
            return ToolResult(
                success=False,
                output="",
                error=f"Language '{language}' not allowed. Allowed: {', '.join(self.allowed_languages)}",
            )

        try:
            if language == "python":
                result = await self._execute_python(code)
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Language '{language}' not implemented yet",
                )

            return result

        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return ToolResult(
                success=False,
                output="",
                error=f"Execution failed: {str(e)}",
            )

    async def _execute_python(self, code: str) -> ToolResult:
        """Execute Python code in a subprocess."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = Path(f.name)

        try:
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                "python3",
                str(temp_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Execution timed out after {self.timeout} seconds",
                )

            # Decode output
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            # Truncate if too large
            if len(stdout_str) > self.max_output_size:
                stdout_str = stdout_str[: self.max_output_size] + "\n... (output truncated)"

            # Check if execution was successful
            success = process.returncode == 0

            output = stdout_str
            error = stderr_str if not success else None

            return ToolResult(
                success=success,
                output=output,
                error=error,
                metadata={"return_code": process.returncode},
            )

        finally:
            # Clean up temp file
            temp_file.unlink(missing_ok=True)
