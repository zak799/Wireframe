"""
HTTP/2 Dynamic Table
To limit the memory requirements on the decoder side, the dynamic
table is constrained in size.
"""

from collections import deque


class DynamicTable:
    ENTRY_OVERHEAD_BYTES: int = 32

    def __init__(self, max_size: bytes = 4096):
        self.current_size: int = 0
        self.max_size: int = max_size
        self._table: deque[tuple[str, str]] = deque()

    @classmethod
    def resize_table(): ...

    def add_header(): ...

    def fetch_header_by_index(): ...

    def evict_old_to_fit(): ...

    def clear_table(): ...

    def __len__(self) -> int:
        return len(self._table)
