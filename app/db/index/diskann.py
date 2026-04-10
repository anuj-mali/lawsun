from typing import Literal, Optional, Union

from sqlalchemy import Index
from sqlalchemy.sql.schema import Column


class DiskANNIndex(Index):
    DISTANCE_OPS = {
        "cosine": "vector_cosine_ops",
        "l2": "vector_l2_ops",
        "ip": "vector_ip_ops",
    }

    def __init__(
        self,
        name: str,
        column: Union[Column, str],
        distance: Literal["cosine", "l2", "ip"] = "cosine",
        labels_column: Optional[Union[Column, str]] = None,
        storage_layout: Optional[str] = None,
        num_neighbors: Optional[int] = None,
        search_list_size: Optional[int] = None,
        max_alpha: Optional[float] = None,
        num_dimensions: Optional[int] = None,
        num_bits_per_dimension: Optional[int] = None,
        **kwargs,
    ):
        if distance not in self.DISTANCE_OPS:
            raise ValueError(
                f"distance must be one of: {list(self.DISTANCE_OPS.keys())}"
            )

        self.distance = distance

        col_name = column.name if isinstance(column, Column) else column

        columns = [column]
        if labels_column is not None:
            columns.append(labels_column)

        diskann_with = {
            "storage_layout": storage_layout,
            "num_neighbors": num_neighbors,
            "search_list_size": search_list_size,
            "max_alpha": max_alpha,
            "num_dimensions": num_dimensions,
            "num_bits_per_dimension": num_bits_per_dimension,
        }
        diskann_with = {k: v for k, v in diskann_with.items() if v is not None}

        super().__init__(
            name,
            *columns,
            postgresql_using="diskann",
            postgresql_ops={col_name: self.DISTANCE_OPS[distance]},
            postgresql_with=diskann_with,
            **kwargs,
        )

    def __repr__(self) -> str:
        has_labels = len(self.columns) > 1
        return (
            f"DiskANNIndex({self.name!r}, distance={self.distance!r}, "
            f"labels={'yes' if has_labels else 'no'})"
        )
