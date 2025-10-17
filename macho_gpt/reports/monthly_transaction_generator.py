"""물류 월별 리포트 생성기. Logistics monthly report generator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


WAREHOUSE_COLUMNS: List[str] = [
    "AAA Storage",
    "DSV Indoor",
    "DSV Outdoor",
    "DSV Al Markaz",
    "DSV MZP",
    "Hauler Indoor",
    "MOSB",
]


@dataclass
class WarehouseMonthlyReporter:
    """창고 월별 리포터. Warehouse monthly reporter."""

    inbound_label: str = "입고"
    outbound_label: str = "출고"

    def get_multi_level_headers(self) -> Dict[str, List[str]]:
        """멀티레벨 헤더 반환. Provide multi-level column headers."""

        level_0 = [self.inbound_label] * len(WAREHOUSE_COLUMNS) + [
            self.outbound_label
        ] * len(WAREHOUSE_COLUMNS)
        level_1 = WAREHOUSE_COLUMNS * 2
        return {"level_0": level_0, "level_1": level_1}


def classify_location(row: Dict[str, str]) -> str:
    """위치 기반 창고 분류. Classify warehouse by location fields."""

    location = row.get("location") or ""
    warehouse = row.get("warehouse") or ""
    if location in WAREHOUSE_COLUMNS:
        return location
    for candidate in WAREHOUSE_COLUMNS:
        if candidate.replace(" ", "_").lower() in warehouse.lower():
            return candidate
    return location or warehouse or "Unknown"


def create_warehouse_monthly_pivot(dataframe: pd.DataFrame) -> pd.DataFrame:
    """월별 창고 피벗 생성. Create monthly pivot table for warehouses."""

    if dataframe.empty:
        multi_columns = pd.MultiIndex.from_product(
            [["입고", "출고"], WAREHOUSE_COLUMNS], names=["구분", "창고"]
        )
        return pd.DataFrame(columns=multi_columns)

    data = dataframe.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["month"] = data["date"].dt.to_period("M").astype(str)
    pivot = pd.pivot_table(
        data,
        index="month",
        columns=["transaction_type", "warehouse"],
        values="quantity",
        aggfunc="sum",
        fill_value=0,
    )
    pivot = pivot.reindex(columns=pd.MultiIndex.from_product([["입고", "출고"], WAREHOUSE_COLUMNS]), fill_value=0)
    pivot.sort_index(axis=1, level=[0, 1], inplace=True)
    return pivot
