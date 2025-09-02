import pandas as pd
from typing import Dict, List, Optional, Union, Any
import logging
from pathlib import Path

from mapper import DataMapper
from route import RouteProcessor

class ExportData:
    """
    CSV 파일 처리를 위한 고수준 인터페이스
    """
    
    @staticmethod
    def process_terminal_routes(reference_file: Union[str, Path],
                              input_file: Union[str, Path],
                              output_file: Union[str, Path],
                              config: Dict[str, Any]) -> pd.DataFrame:
        """
        터미널 라우트 처리를 위한 원스톱 함수
        
        Args:
            reference_file: 기준 데이터 파일 (TerminalInfo.csv)
            input_file: 입력 데이터 파일 (Test.csv)
            output_file: 출력 파일 경로
            config: 설정 딕셔너리
        
        Returns:
            처리된 DataFrame
        """
        # 설정값 추출 (기본값 포함)
        key_column = config.get('key_column', 'SVC')
        route_columns = config.get('route_columns', ['Route1', 'Route2'])
        field_mappings = config.get('field_mappings', {
            'Name': 'Name',
            'Wtp': 'Wtp', 
            'Sch': 'Sch'
        })
        max_terminals = config.get('max_terminals', 3)
        output_prefix = config.get('output_prefix', 'T')
        
        try:
            # 데이터 매퍼 초기화
            mapper = DataMapper.from_csv(reference_file, key_column)
            
            # 입력 데이터 로드
            input_df = pd.read_csv(input_file)
            
            # 라우트 프로세서로 처리
            processor = RouteProcessor(mapper)
            result_df = processor.process_routes(
                input_df, route_columns, field_mappings, max_terminals, output_prefix
            )
            
            # 결과 저장
            result_df.to_csv(output_file, index=False)
            print(f"처리 완료! 결과가 '{output_file}' 파일에 저장되었습니다.")
            
            return result_df
            
        except Exception as e:
            logging.error(f"Processing failed: {e}")
            raise