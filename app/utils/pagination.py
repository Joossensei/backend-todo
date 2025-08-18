# app/utils/pagination.py
from typing import Optional
from yarl import URL


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
