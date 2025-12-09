import pandas as pd
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# 현재 스크립트 위치를 기준으로 backend 모듈을 import할 수 있도록 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.database import SessionLocal, engine, Base
from backend.app.models import Port, Service, Rotation

# --- 1. 설정 및 매핑 정의 (이 부분만 수정하면 됩니다!) ---

# 파일 경로
FILE_PATHS = {
    "port_coordinates": "data/coordinate/port_coordinates.csv",
    "proforma": "data/input/proforma.csv",
    "service_codes": "data/input/bpa_service_code.csv"
}

# CSV -> DB 매핑 설정
# Key: DB 모델의 컬럼명
# Value: CSV 파일의 헤더명 (또는 변환 로직에서 사용할 키)
PORT_MAPPING = {
    "name": "port_name",
    "lat": "lat",
    "lon": "lon",
    "code": "locode" # 예: UN/LOCODE가 있다면
}

# --- 2. Extract: 데이터 추출 ---
def load_csv_data(filepath):
    """CSV 파일을 읽어서 DataFrame으로 반환합니다."""
    try:
        df = pd.read_csv(filepath)
        print(f"[Info] Loaded {len(df)} rows from {filepath}")
        return df
    except FileNotFoundError:
        print(f"[Error] File not found: {filepath}")
        return pd.DataFrame()
    except Exception as e:
        print(f"[Error] Failed to load {filepath}: {e}")
        return pd.DataFrame()

# --- 3. Transform: 데이터 변환 및 정제 ---
def transform_ports(coord_df):
    """항구 좌표 데이터를 Port 모델 리스트로 변환합니다."""
    ports = []
    # 데이터가 없는 경우 처리
    if coord_df.empty:
        return []

    # 필요한 컬럼 확인 및 이름 변경 (매핑 적용)
    # 실제 CSV 헤더가 'port', 'lat', 'lon' 이라고 가정하고 로직 작성
    # 실제 데이터에 맞게 유연하게 처리
    
    for _, row in coord_df.iterrows():
        # 데이터 정제 (예: NaN 값 처리)
        port_name = row.get('port') or row.get('port_name')
        
        if pd.isna(port_name):
            continue

        port_data = {
            "name": port_name.strip(),
            "lat": row.get('lat', 0.0),
            "lon": row.get('lon', 0.0),
            "code": row.get('locode', None) # locode 컬럼이 없으면 None
        }
        ports.append(port_data)
    
    return ports

def transform_services_and_rotations(proforma_df, service_code_df, port_map):
    """
    운항 스케줄(Proforma) 데이터를 기반으로 Service와 Rotation 데이터를 생성합니다.
    port_map: {"항구명": port_id} 형태의 딕셔너리
    """
    services = {} # {service_name: Service객체 데이터}
    rotations = [] # Rotation 객체 데이터 리스트

    if proforma_df.empty:
        return [], []

    # proforma.csv 구조: Service, Port, ETB, ETD, ... (가정)
    # 실제로는 'NW1', 'BUSAN', ... 이런 식일 것임.
    
    # 1. 유니크한 서비스 추출
    unique_services = proforma_df['Service'].unique()
    for svc_name in unique_services:
        if pd.isna(svc_name): continue
        services[svc_name] = {
            "name": svc_name,
            "description": f"Service {svc_name}" # 필요시 service_code_df 참조
        }

    # 2. Rotation 생성
    # 각 서비스별로 순서를 매겨야 함
    
    # 먼저 서비스별로 그룹화
    grouped = proforma_df.groupby('Service')
    
    for svc_name, group in grouped:
        # 순서 정렬 (기준이 있다면 sort_values 사용)
        # group = group.sort_values(by='Order') 
        
        for idx, row in enumerate(group.itertuples(), start=1):
            p_name = getattr(row, 'Port', None)
            
            if not p_name: continue
            
            # DB에 있는 항구인지 확인
            port_id = port_map.get(p_name)
            
            # 매핑되지 않는 항구는 건너뛰거나 로그 남김
            if not port_id:
                print(f"[Warning] Port not found in DB: {p_name} (Service: {svc_name})")
                continue

            rotations.append({
                "service_name": svc_name, # 나중에 ID로 변환
                "port_id": port_id,
                "port_order": idx,
                "direction": getattr(row, 'Bound', None), # CSV 컬럼명 확인 필요
                "day": None, # 요일 로직 필요시 추가
                "terminal": getattr(row, 'Terminal', None)
            })
            
    return list(services.values()), rotations

# --- 4. Load: 데이터 적재 ---
def load_to_db(db: Session, ports_data, services_data, rotations_data):
    """변환된 데이터를 DB에 저장합니다."""
    
    # 1. Ports 저장
    print("Loading Ports...")
    # 중복 방지를 위해 기존 데이터 확인 로직이 필요할 수 있음 (Upsert)
    # 여기서는 간단히 새로 넣는 로직 (기존 데이터 삭제 후 넣기는 init_db 참고)
    
    existing_ports = {p.name: p.id for p in db.query(Port).all()}
    new_ports = []
    
    for p_data in ports_data:
        if p_data['name'] not in existing_ports:
            port = Port(**p_data)
            db.add(port)
            new_ports.append(port)
    
    db.commit() # ID 생성을 위해 커밋
    
    # 갱신된 포트 맵핑 (이름 -> ID)
    for p in new_ports:
        existing_ports[p.name] = p.id
        
    print(f"Loaded {len(new_ports)} new ports.")

    # 2. Services 저장
    print("Loading Services...")
    existing_services = {s.name: s.id for s in db.query(Service).all()}
    new_services = []

    for s_data in services_data:
        if s_data['name'] not in existing_services:
            service = Service(**s_data)
            db.add(service)
            new_services.append(service)
    
    db.commit()
    
    for s in new_services:
        existing_services[s.name] = s.id
        
    print(f"Loaded {len(new_services)} new services.")

    # 3. Rotations 저장
    print("Loading Rotations...")
    # Rotation은 싹 지우고 다시 넣거나, 중복 체크가 복잡하므로
    # 여기서는 간단히 추가하는 로직만 작성
    
    for r_data in rotations_data:
        s_id = existing_services.get(r_data['service_name'])
        if s_id:
            # rotation 객체 생성 시 service_name은 제외해야 함
            r_input = r_data.copy()
            del r_input['service_name']
            r_input['service_id'] = s_id
            
            rotation = Rotation(**r_input)
            db.add(rotation)
            
    db.commit()
    print(f"Loaded {len(rotations_data)} rotations.")

def main():
    # DB 테이블 생성 (없으면)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Extract
        coord_df = load_csv_data(FILE_PATHS["port_coordinates"])
        proforma_df = load_csv_data(FILE_PATHS["proforma"])
        service_code_df = load_csv_data(FILE_PATHS["service_codes"])

        # 2. Transform
        ports_data = transform_ports(coord_df)
        
        # 임시로 DB 저장 전, 메모리 상에서 매핑용 딕셔너리 생성 (DB가 비어있을 수 있으므로)
        # 하지만 실제 ID는 DB에 들어가야 생기므로, 로직 순서를 조정
        
        # 먼저 Port부터 DB에 넣어야 ID를 알 수 있음.
        # 따라서 Load 함수 내에서 단계적으로 처리하거나,
        # 여기서 먼저 Port를 넣고 ID 맵을 가져와야 함.
        
        # Load Ports First
        load_to_db(db, ports_data, [], [])
        
        # DB에서 최신 Port ID 맵 가져오기
        port_map = {p.name: p.id for p in db.query(Port).all()}
        
        services_data, rotations_data = transform_services_and_rotations(proforma_df, service_code_df, port_map)

        # 3. Load Remaining
        load_to_db(db, [], services_data, rotations_data)
        
        print("ETL Process Completed Successfully.")
        
    except Exception as e:
        print(f"[Error] ETL Process Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
