import pandas as pd
from typing import Dict, List, Optional, Union, Any
import logging
from pathlib import Path

class DataMapper:
    """
    범용 데이터 매핑 클래스
    기준 데이터를 바탕으로 다른 데이터의 필드를 조회하고 매핑하는 기능 제공
    """
    
    def __init__(self, reference_df: pd.DataFrame, key_column: str):
        """
        Args:
            reference_df: 기준이 되는 DataFrame (조회 대상 데이터)
            key_column: 조회 키로 사용할 컬럼명
        """
        self.reference_df = reference_df.copy()
        self.key_column = key_column
        self._validate_reference_data()
        
        # 성능 최적화를 위한 인덱스 생성
        if key_column in self.reference_df.columns:
            self.reference_df.set_index(key_column, inplace=True)
    
    def _validate_reference_data(self):
        """기준 데이터 유효성 검사"""
        if self.reference_df.empty:
            raise ValueError("Reference DataFrame is empty")
        
        if self.key_column not in self.reference_df.columns:
            raise ValueError(f"Key column '{self.key_column}' not found in reference data")
    
    @classmethod
    def from_csv(cls, file_path: Union[str, Path], key_column: str, **kwargs) -> 'DataMapper':
        """
        CSV 파일에서 DataMapper 인스턴스 생성
        
        Args:
            file_path: CSV 파일 경로
            key_column: 조회 키로 사용할 컬럼명
            **kwargs: pd.read_csv에 전달할 추가 인수
        """
        try:
            df = pd.read_csv(file_path, **kwargs)
            return cls(df, key_column)
        except Exception as e:
            raise ValueError(f"Failed to load CSV file '{file_path}': {e}")
    
    def lookup_values(self, 
                     keys: Union[str, List[str]], 
                     target_column: str,
                     position: int = 1,
                     separator: str = ",") -> str:
        """
        키(들)에 해당하는 값 조회
        
        Args:
            keys: 조회할 키 또는 키들의 문자열 (구분자로 분리된)
            target_column: 조회할 대상 컬럼명
            position: 결과에서 가져올 위치 (1-based index)
            separator: 키 구분자 (기본값: ",")
        
        Returns:
            조회된 값 (문자열)
        """
        if not keys or target_column not in self.reference_df.columns:
            return ""
        
        # 키 리스트 정규화
        if isinstance(keys, str):
            key_list = [key.strip() for key in keys.split(separator) if key.strip()]
        else:
            key_list = [str(key).strip() for key in keys if str(key).strip()]
        
        if not key_list:
            return ""
        
        try:
            # 인덱스를 사용한 빠른 조회
            matching_values = []
            for key in key_list:
                if key in self.reference_df.index:
                    value = self.reference_df.loc[key, target_column]
                    if pd.notna(value):
                        matching_values.append(str(value))
            
            # 중복 제거 및 순서 유지
            unique_values = list(dict.fromkeys(matching_values))
            
            # 지정된 위치의 값 반환
            if 1 <= position <= len(unique_values):
                return unique_values[position - 1]
            
        except Exception as e:
            logging.warning(f"Error during lookup: {e}")
        
        return ""
    
    def batch_lookup(self, 
                    keys_list: List[Union[str, List[str]]], 
                    target_columns: List[str],
                    max_positions: int = 3,
                    separator: str = ",") -> pd.DataFrame:
        """
        여러 키셋에 대한 일괄 조회
        
        Args:
            keys_list: 조회할 키들의 리스트
            target_columns: 조회할 대상 컬럼들
            max_positions: 최대 조회 위치 수
            separator: 키 구분자
        
        Returns:
            조회 결과 DataFrame
        """
        results = []
        
        for keys in keys_list:
            row_result = {}
            
            for col in target_columns:
                for pos in range(1, max_positions + 1):
                    value = self.lookup_values(keys, col, pos, separator)
                    column_name = f"T{pos}{col}" if pos > 1 or len(target_columns) > 1 else col
                    row_result[column_name] = value
                    
                    # 값이 없으면 더 이상 위치 검사하지 않음
                    if not value:
                        break
            
            results.append(row_result)
        
        return pd.DataFrame(results)