# PortInfoMapper

## 📖 개요 (Overview)

**PortInfoMapper**는 선사별 서비스 노선(Service Route) 데이터를 기반으로, 각 노선에 해당하는 터미널의 상세 정보(터미널명, 작업 시간, 스케줄 등)를 자동으로 조회하고 매핑하여 하나의 통합된 데이터로 만들어주는 데이터 처리 파이프라인입니다.

또한, 처리된 데이터를 기반으로 **정기 노선도 PPT 보고서를 자동으로 생성**하는 기능을 포함하고 있습니다.

## ✨ 주요 기능 (Features)

- **CSV 기반 데이터 처리**: `proforma.csv`(기준 정보)와 `bpa_service_code.csv`(입력 정보)를 사용하여 데이터 매핑 수행
- **유연한 라우트 매핑**: 여러 컬럼에 나뉘어 있는 서비스 노선 정보를 조합하여 관련 터미널 정보 조회
- **운항 스케줄 정규화**: `Wed13 ~ Thu10`, `Sat/Sun`, `TBD` 등 다양한 형식의 스케줄 문자열을 `요일 HH ~ 요일 HH` 형태의 표준 형식으로 자동 변환
- **PPT 자동 생성**: 최종 데이터를 기반으로, 사전 정의된 레이아웃에 따라 각 항로별 정보를 담은 PPT 슬라이드를 자동으로 생성
- **항만 좌표 크롤링**: `shipxplorer.com`에서 전 세계 항만의 위도, 경도 좌표를 자동으로 수집
- **설정 기반 동작**: `config` 파일 및 `main.py` 설정을 통해 키 컬럼, 필드명, PPT 스타일 등을 쉽게 변경 가능
- **모듈화된 구조**: 데이터 처리 및 PPT 생성을 기능별 모듈로 분리하여 유지보수 및 확장이 용이

## 📂 프로젝트 구조 (Project Structure)

```
PortInfoMapper/
├── config/
│   └── ppt_config.json      # PPT 레이아웃 및 스타일 설정
├── data/
│   ├── input/               # 원본 데이터
│   ├── output/              # 데이터 처리 결과
│   └── test/                # 테스트용 데이터 및 템플릿
├── module/
│   ├── automate_ppt.py      # [PPT 생성] PPT 자동화 클래스
│   ├── coordinate_crawler.py  # [유틸리티] 항만 좌표 정보 크롤링
│   ├── export_data.py       # [오케스트레이터] 데이터 처리 흐름 제어
│   ├── route.py             # [핵심 로직] 라우트 정보를 가공하고 매핑
│   ├── mapper.py            # [데이터 조회 엔진] 기준 정보 조회 기능
│   └── normalize_schedule.py  # [유틸리티] 스케줄 문자열 정규화
├── main.py                  # [실행 진입점] 전체 프로세스 실행
├── requirements.txt         # 프로젝트 의존성 라이브러리
└── README.md                # 프로젝트 설명 문서
```

## ⚙️ 실행 순서 (Execution Flow)

1.  **`main.py` 실행**: 사용자가 `python main.py` 명령으로 스크립트를 실행합니다.
2.  **데이터 처리**: `ExportData` 모듈이 `proforma.csv`와 `bpa_service_code.csv`를 처리하여 `result.csv`를 생성합니다. (기존과 동일)
3.  **PPT 자동화 실행**: `main.py`가 `run_ppt_automation` 함수를 호출합니다.
4.  **PPT 설정 로드**: `automate_ppt.py` 모듈이 `config/ppt_config.json` 파일을 읽어 PPT 레이아웃과 스타일 설정을 로드합니다.
5.  **데이터 로드**: PPT 생성에 필요한 데이터(`data/test/proforma_test.csv`)를 로드합니다.
6.  **슬라이드 생성**: `PptAutomator`가 데이터의 각 행을 순회하며, JSON 설정에 정의된 위치, 크기, 폰트, 색상에 맞춰 항로별 슬라이드를 생성합니다.
7.  **PPT 파일 저장**: 모든 슬라이드 생성이 완료되면, JSON 설정에 명시된 경로와 파일명으로 최종 PPT 파일을 저장합니다.

## 🚀 시작하기 (Getting Started)

### 요구사항 (Prerequisites)

- Python 3.8 이상
- `pandas`, `python-pptx` 라이브러리

### 설치 (Installation)

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 필요한 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

### 실행 (Usage)

#### 전체 파이프라인 실행

프로젝트 루트 디렉토리에서 `main.py` 파일을 직접 실행하여 전체 데이터 처리 및 PPT 생성 파이프라인을 실행합니다.

```bash
python main.py
```

실행이 완료되면 `data/output/result.csv` 파일과 `BPA_정기노선도_자동화_v3.pptx` 파일에서 최종 결과를 확인할 수 있습니다.

#### 항만 좌표 수집

`module/coordinate_crawler.py` 파일을 직접 실행하여 항만 좌표 정보를 크롤링하고 `data/coordinate/port_coordinates.csv` 파일로 저장할 수 있습니다.

```bash
python module/coordinate_crawler.py
```

## 🔧 설정 (Configuration)

### 데이터 처리 설정

`main.py` 파일 상단의 `config` 딕셔너리에서 데이터 처리 관련 동작을 변경할 수 있습니다.

- `key_column`, `route_columns`, `field_mappings`, `max_terminals`, `output_prefix` 등

### PPT 레이아웃 설정

`config/ppt_config.json` 파일에서 PPT의 시각적 요소를 상세하게 설정할 수 있습니다.

- `file_paths`: 입력 데이터 및 출력 PPT 파일 경로
- `slide_dimensions`: 슬라이드 전체 크기
- `colors`: 사용할 색상 정의 (RGB 배열)
- `elements`: 각 도형/표의 위치(`pos`), 크기(`size`), 폰트, 색상 등 상세 스타일 정의

