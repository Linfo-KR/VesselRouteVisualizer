# PortInfoMapper

## 📖 개요 (Overview)

**PortInfoMapper**는 선사별 서비스 노선(Service Route) 데이터를 기반으로, 각 노선에 해당하는 터미널의 상세 정보(터미널명, 작업 시간, 스케줄 등)를 자동으로 조회하고 매핑하여 하나의 통합된 데이터로 만들어주는 데이터 처리 파이프라인입니다.

CSV 형식의 입력 파일을 받아 처리하며, 설정 파일을 통해 유연하게 데이터 처리 방식을 변경할 수 있습니다.

## ✨ 주요 기능 (Features)

- **CSV 기반 데이터 처리**: `proforma.csv`(기준 정보)와 `bpa_service_code.csv`(입력 정보)를 사용하여 데이터 매핑 수행
- **유연한 라우트 매핑**: 여러 컬럼에 나뉘어 있는 서비스 노선 정보를 조합하여 관련 터미널 정보 조회
- **설정 기반 동작**: `main.py` 내의 `config` 딕셔너리를 통해 키 컬럼, 라우트 컬럼, 필드명 등을 쉽게 변경 가능
- **모듈화된 구조**: 데이터 조회(`mapper`), 핵심 로직(`route`), 실행(`main`) 등 기능별로 모듈이 분리되어 있어 유지보수 및 확장이 용이

## 📂 프로젝트 구조 (Project Structure)

```
PortInfoMapper/
├── data/
│   ├── input/
│   │   ├── proforma.csv       # (기준 정보) 터미널별 상세 정보
│   │   └── bpa_service_code.csv # (입력 정보) 서비스 노선별 코드
│   └── output/
│       └── result.csv         # (출력 결과) 매핑이 완료된 데이터
├── module/
│   ├── main.py              # [실행 진입점] 전체 프로세스 실행
│   ├── export_data.py       # [오케스트레이터] 데이터 처리 흐름 제어
│   ├── route.py             # [핵심 로직] 라우트 정보를 가공하고 매핑
│   ├── mapper.py            # [데이터 조회 엔진] 기준 정보 조회 기능
│   └── normalize_schedule.py  # [유틸리티] 스케줄 문자열 정규화 (현재 미사용)
├── requirements.txt         # 프로젝트 의존성 라이브러리
└── README.md                # 프로젝트 설명 문서
```

## ⚙️ 실행 순서 (Execution Flow)

1.  **`main.py` 실행**: 사용자가 `python module/main.py` 명령으로 스크립트를 실행합니다.
2.  **설정 로드**: `main.py`에서 데이터 처리에 필요한 `config`를 정의합니다.
3.  **`ExportData` 호출**: `main.py`가 `ExportData.process_terminal_routes` 함수를 호출하며 파일 경로와 설정을 전달합니다.
4.  **`DataMapper` 생성**: `ExportData`는 `proforma.csv` 파일을 읽어 기준 정보를 메모리에 적재한 `DataMapper` 객체를 생성합니다.
5.  **`RouteProcessor` 생성**: 생성된 `DataMapper` 객체를 `RouteProcessor`에 주입하여 핵심 로직을 수행할 객체를 생성합니다.
6.  **데이터 처리**: `RouteProcessor`는 `bpa_service_code.csv`의 각 행을 읽어 라우트 코드를 조합하고, `DataMapper`를 통해 최대 `max_terminals` 개수만큼 터미널 정보를 조회합니다.
7.  **결과 생성**: 조회된 터미널 정보(`Name`, `Wtp`, `Sch`)를 원본 데이터에 `T1Name`, `T2Name`... 과 같은 새로운 컬럼으로 추가합니다.
8.  **파일 저장**: `ExportData`는 최종적으로 완성된 데이터프레임을 `result.csv` 파일로 저장하고, `main.py`는 처리 완료 메시지와 함께 결과 미리보기를 출력합니다.

## 🚀 시작하기 (Getting Started)

### 요구사항 (Prerequisites)

- Python 3.8 이상
- `pandas` 라이브러리

### 설치 (Installation)

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 필요한 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

### 실행 (Usage)

`module` 폴더 내의 `main.py` 파일을 직접 실행합니다.

```bash
python module/main.py
```

실행이 완료되면 `data/output/result.csv` 파일에서 최종 결과를 확인할 수 있습니다.

## 🔧 설정 (Configuration)

`module/main.py` 파일 상단의 `config` 딕셔너리에서 주요 동작을 변경할 수 있습니다.

- `key_column`: 기준 정보(`proforma.csv`)에서 키로 사용할 컬럼명 (기본값: `SVC`)
- `route_columns`: 입력 정보(`bpa_service_code.csv`)에서 라우트 정보가 담긴 컬럼 목록 (기본값: `['SVC1', 'SVC2']`)
- `field_mappings`: 출력될 필드명과 기준 정보의 컬럼명을 매핑 (기본값: `{'Name': 'Name', 'Wtp': 'Wtp', 'Sch': 'Sch'}`)
- `max_terminals`: 조회할 최대 터미널 개수 (기본값: `3`)
- `output_prefix`: 결과 컬럼에 붙일 접두사 (기본값: `T`)