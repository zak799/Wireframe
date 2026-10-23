from datetime import datetime, UTC
from pathlib import Path
from loguru import logger
import sys, json


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "hpack" / "hpack.json"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logger.remove()

logger.add(
    sys.stderr,
    level="DEBUG",
    colorize=True,
    backtrace=True,
    diagnose=False,
    format=(
        "[{time:YYYY-MM-DD HH:mm:ss.SSS}] | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "<level>{message}</level>"
    ),
)


class HPACKError(Exception):
    LEVEL = "CRITICAL"

    def __init__(self, error_msg: str):
        super().__init__(error_msg)
        self.error_msg = error_msg

        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": self.LEVEL,
            "type": type(self).__name__,
            "message": error_msg,
        }

        logger.opt(depth=1).log(self.LEVEL, f"[HPACK] {error_msg}")

        try:
            if LOG_FILE.exists() and LOG_FILE.stat().st_size > 0:
                with LOG_FILE.open("r", encoding="utf-8") as logs:
                    records = json.load(logs)
            else:
                records = []

            if not isinstance(records, list):
                records = [records]

            records.append(record)

            with LOG_FILE.open("w", encoding="utf-8") as logs:
                json.dump(records, logs, indent=4, ensure_ascii=False)
                logs.write("\n")

        except (OSError, json.JSONDecodeError):
            logger.exception("Failed to write HPACK JSON log")


class HPACKDecodeError(HPACKError):
    LEVEL = "CRITICAL"


class HPACKEncodeError(HPACKError):
    LEVEL = "CRITICAL"