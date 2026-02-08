import logging
from typing import Any

from langchain_core.callbacks.base import BaseCallbackHandler

log = logging.getLogger(__name__)


class ToolCallLoggingCallbackHandler(BaseCallbackHandler):
    """Logs tool calls via LangChain's callback system."""

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        name = serialized.get("name") or serialized.get("id") or "(tool)"
        run_id = kwargs.get("run_id")
        tool_call_id = kwargs.get("tool_call_id")
        log.info(
            "Tool call start name=%s run_id=%s tool_call_id=%s input_chars=%d",
            name,
            run_id,
            tool_call_id,
            len(input_str) if isinstance(input_str, str) else -1,
        )

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        run_id = kwargs.get("run_id")
        tool_call_id = kwargs.get("tool_call_id")
        output_type = type(output).__name__

        output_chars: int | None
        if isinstance(output, str):
            output_chars = len(output)
        else:
            output_chars = None

        try:
            output_size = len(output)  # type: ignore[arg-type]
        except Exception:
            output_size = None

        log.info(
            "Tool call end run_id=%s tool_call_id=%s output_type=%s output_size=%s output_chars=%s",
            run_id,
            tool_call_id,
            output_type,
            output_size,
            output_chars,
        )

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        run_id = kwargs.get("run_id")
        tool_call_id = kwargs.get("tool_call_id")
        log.exception(
            "Tool call error run_id=%s tool_call_id=%s",
            run_id,
            tool_call_id,
            exc_info=error,
        )
