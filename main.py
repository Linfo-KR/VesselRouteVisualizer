import pandas as pd
from typing import Dict, List, Optional, Union, Any
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from module.mapper import DataMapper
from module.route import RouteProcessor
from module.export_data import ExportData

def main():
    """Main"""
    
    # 설정 정의
    config = {
        'key_column': 'SVC',
        'route_columns': ['SVC1', 'SVC2'],
        'field_mappings': {
            'Name': 'Name',
            'Wtp': 'Wtp',
            'Sch': 'Sch'
        },
        'max_terminals': 3,
        'output_prefix': 'T'
    }
    
    try:
        # 기존 코드와 동일한 처리
        ROOT_DIR = Path(__file__).parent
        result_df = ExportData.process_terminal_routes(
            proforma=ROOT_DIR / 'data' / 'input' / 'proforma.csv',
            svc=ROOT_DIR / 'data' / 'input' / 'bpa_service_code.csv', 
            output=ROOT_DIR / 'data' / 'output' / 'result.csv',
            config=config
        )
        
        print("\n=== 결과 미리보기 ===")
        print(result_df.head(10))
        
        # 개별 조회 예시
        mapper = DataMapper.from_csv(ROOT_DIR /'data' / 'input' / 'proforma.csv', "SVC")
        single_result = mapper.lookup_values("CKJ,CKJ1", "Name", 1)
        print(f"\n단일 조회 결과: {single_result}")
        
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
    
    
def advanced_examples():
    """다양한 활용 예시"""
    
    # 1. 다른 데이터셋에 적용
    config_custom = {
        'key_column': 'ProductCode',
        'route_columns': ['Category1', 'Category2', 'Category3'],
        'field_mappings': {
            'Price': 'UnitPrice',
            'Stock': 'Inventory',
            'Supplier': 'SupplierName'
        },
        'max_terminals': 2,
        'output_prefix': 'Item'
    }
    
    # 2. 직접 DataMapper 사용
    mapper = DataMapper.from_csv("reference_data.csv", "ID")
    
    # 배치 조회
    keys_list = ["A,B,C", "D,E", "F"]
    batch_results = mapper.batch_lookup(keys_list, ["Name", "Value"], max_positions=2)
    
    # 3. 사용자 정의 처리
    processor = RouteProcessor(mapper)
    input_data = pd.DataFrame({
        'Route1': ['A', 'D'],
        'Route2': ['B,C', 'E'],
        'OtherData': [1, 2]
    })
    
    result = processor.process_routes(
        input_data,
        route_columns=['Route1', 'Route2'],
        field_mappings={'Name': 'FullName', 'Code': 'ID'},
        max_terminals=2
    )