from math import ceil
from fastapi import Request


def paginate_queryset(
    query,
    page: int,
    page_size: int,
    request: Request,
):
    total = query.count()
    total_pages = ceil(total / page_size) if total else 1

    results = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    def build_url(target_page: int | None):
        if not target_page or target_page < 1 or target_page > total_pages:
            return None
        params = dict(request.query_params)
        params["page"] = target_page
        return str(request.url.include_query_params(**params))

    next_url = build_url(page + 1 if page < total_pages else None)
    previous_url = build_url(page - 1 if page > 1 else None)

    return {
        "count": total,
        "next": next_url,
        "previous": previous_url,
        "results": results,
    }
