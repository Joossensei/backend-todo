import asyncpg


def record_to_dict(record: asyncpg.Record) -> dict:
    return {k: v for k, v in record.items()}


def records_to_dicts(records: list[asyncpg.Record]) -> list[dict]:
    return [record_to_dict(record) for record in records]
