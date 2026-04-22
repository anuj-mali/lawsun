from typing import Optional, Union

from sqlalchemy import Index
from sqlalchemy.sql.schema import Column


class BM25Index(Index):
    def __init__(
        self,
        name: str,
        column: Union[Column, str],
        text_config: str,
        k1: Optional[float] = None,
        b: Optional[float] = None,
        **kwargs,
    ):
        bm25_with = {
            "text_config": text_config,
            "k1": k1,
            "b": b,
        }
        bm25_with = {k: v for k, v in bm25_with.items() if v is not None}

        super().__init__(
            name,
            column,
            postgresql_using="bm25",
            postgresql_with=bm25_with,
            **kwargs,
        )

    def __repr__(self) -> str:
        text_config = self.dialect_kwargs.get("postgresql_with", {}).get("text_config")
        return f"BM25Index({self.name!r}, text_config={text_config!r})"
