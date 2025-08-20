# app/utils/pagination.py
from typing import Optional
from yarl import URL
from typing import Tuple


def build_pagination_link(
    current_url: URL, page: int, size: int, total: int
) -> Optional[str]:
    if page < 1:
        return None
    max_page = (total + size - 1) // size if size > 0 else 1
    if page > max_page:
        return None
    return str(
        current_url.with_query({**current_url.query, "page": page, "size": size})
    )


def parse_pagination(page_raw: str | int | None, size_raw: str | int | None, *, max_size: int = 100, default_page: int = 1, default_size: int = 10) -> Tuple[int, int, int]:
    try:
        page = int(page_raw) if page_raw is not None else default_page
    except ValueError:
        page = default_page
    try:
        size = int(size_raw) if size_raw is not None else default_size
    except ValueError:
        size = default_size

    page = max(page, 1)
    size = max(min(size, max_size), 1)
    skip = (page - 1) * size
    return page, size, skip
