from sqlalchemy import func
from sqlalchemy.types import Text


class BM25Text(Text):
    class comparator_factory(Text.Comparator):
        def bm25_match(self, query_text: str, index_name: str = None):
            if index_name:
                bm25_query = func.to_bm25query(query_text, index_name)
                return self.op("<@>")(bm25_query)

            return self.op("<@>")(query_text)
