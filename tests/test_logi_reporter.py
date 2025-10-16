"""
MACHO-GPT v3.4-mini 물류 리포터 테스트 모듈

TDD 방식으로 Multi-Level Header 구조의 Excel 리포트 생성 테스트
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import tempfile
import os


class TestWarehouseMonthlyTransactionStructure(unittest.TestCase):
    """창고_월별_입출고 시트 구조 테스트"""
    
    def setUp(self):
        """테스트 셋업"""
        self.warehouse_cols = [
            'AAA Storage', 'DSV Indoor', 'DSV Outdoor', 
            'DSV Al Markaz', 'DSV MZP', 'Hauler Indoor', 'MOSB'
        ]
        
    def test_warehouse_monthly_structure_should_have_multi_level_headers(self):
        """창고 월별 구조는 Multi-Level Headers를 가져야 함"""
        # Given: 창고 데이터
        from macho_gpt.reports.monthly_transaction_generator import WarehouseMonthlyReporter
        
        # When: 리포터 생성
        reporter = WarehouseMonthlyReporter()
        
        # Then: Multi-Level Headers가 있어야 함
        expected_level_0 = ['입고'] * 7 + ['출고'] * 7
        expected_level_1 = self.warehouse_cols * 2
        
        headers = reporter.get_multi_level_headers()
        
        self.assertEqual(headers['level_0'], expected_level_0)
        self.assertEqual(headers['level_1'], expected_level_1)
        
    def test_classify_location_should_return_correct_warehouse(self):
        """위치 분류 함수는 정확한 창고를 반환해야 함"""
        # Given: 테스트 데이터 행
        from macho_gpt.reports.monthly_transaction_generator import classify_location
        
        test_row = {
            'location': 'DSV Indoor',
            'warehouse': 'DSV_INDOOR_001',
            'site': 'DUBAI'
        }
        
        # When: 위치 분류 실행
        result = classify_location(test_row)
        
        # Then: 정확한 창고 반환
        self.assertEqual(result, 'DSV Indoor')
        
    def test_warehouse_monthly_pivot_should_have_correct_structure(self):
        """창고 월별 피벗 테이블은 올바른 구조를 가져야 함"""
        # Given: 샘플 거래 데이터
        from macho_gpt.reports.monthly_transaction_generator import create_warehouse_monthly_pivot
        
        sample_data = pd.DataFrame({
            'date': ['2024-01-15', '2024-01-20', '2024-02-10'],
            'warehouse': ['DSV Indoor', 'AAA Storage', 'DSV Outdoor'],
            'transaction_type': ['입고', '출고', '입고'],
            'quantity': [100, 50, 75]
        })
        
        # When: 피벗 테이블 생성
        pivot_result = create_warehouse_monthly_pivot(sample_data)
        
        # Then: 올바른 구조를 가져야 함
        self.assertIsInstance(pivot_result, pd.DataFrame)
        self.assertTrue(hasattr(pivot_result.columns, 'levels'))
        self.assertEqual(len(pivot_result.columns.levels), 2)


if __name__ == '__main__':
    unittest.main() 