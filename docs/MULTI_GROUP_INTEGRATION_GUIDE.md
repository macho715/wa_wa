# WhatsApp Multi-Group Integration Guide

**Version:** 1.0.0
**Date:** 2025-01-15
**Author:** MACHO-GPT v3.4-mini Development Team

---

## 📋 개요

HVDC-WHATSAPP 시스템에 멀티 그룹 병렬 스크래핑 기능을 통합한 완전한 가이드입니다.

### 주요 기능

- ✅ **병렬 스크래핑**: 여러 WhatsApp 그룹을 동시에 스크래핑
- ✅ **비동기 처리**: asyncio 기반 고성능 병렬 실행
- ✅ **TDD 검증**: 25개 테스트로 안정성 보장
- ✅ **YAML 설정**: 간편한 그룹 설정 관리
- ✅ **Streamlit 대시보드**: 웹 기반 모니터링 UI
- ✅ **하위 호환성**: 기존 단일 그룹 기능 유지

---

## 🏗️ 시스템 아키텍처

### 디렉토리 구조

```
HVDC-WHATSAPP-main/
├── macho_gpt/
│   ├── async_scraper/              # 멀티 그룹 스크래핑 모듈
│   │   ├── __init__.py
│   │   ├── group_config.py         # 그룹 설정 관리
│   │   ├── async_scraper.py        # 비동기 단일 그룹 스크래퍼
│   │   └── multi_group_manager.py  # 병렬 처리 매니저
│   └── ...
├── configs/
│   └── multi_group_config.yaml     # 멀티 그룹 설정 파일
├── tests/
│   └── test_multi_group_scraper.py # TDD 테스트
├── run_multi_group_scraper.py      # CLI 실행 스크립트
└── simplified_whatsapp_app.py      # Streamlit 대시보드
```

### 핵심 컴포넌트

1. **GroupConfig**: 그룹별 설정 관리 (Pydantic 검증)
2. **AsyncGroupScraper**: Playwright 기반 단일 그룹 스크래퍼
3. **MultiGroupManager**: 병렬 실행 및 태스크 관리
4. **Streamlit Dashboard**: 웹 기반 모니터링 UI

---

## 🚀 빠른 시작

### 1. 필수 요구사항

```bash
# Python 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 2. 설정 파일 생성

`configs/multi_group_config.yaml` 생성:

```yaml
groups:
  - name: "MR.CHA 전용"
    save_file: "data/mr_cha_messages.json"
    scrape_interval: 60
    priority: "HIGH"

  - name: "HVDC Logistics"
    save_file: "data/hvdc_logistics_messages.json"
    scrape_interval: 120
    priority: "MEDIUM"

  - name: "ADNOC Berth Coordination"
    save_file: "data/adnoc_berth_messages.json"
    scrape_interval: 90
    priority: "MEDIUM"

scraper_settings:
  headless: true
  timeout: 45000
  max_parallel_groups: 3

ai_settings:
  enable_ai_summary: true
  confidence_threshold: 0.85
  ai_model: "gpt-4o-mini"
```

### 3. CLI 실행

```bash
# 기본 실행
python run_multi_group_scraper.py --config configs/multi_group_config.yaml

# 제한된 병렬 처리 (리소스 절약)
python run_multi_group_scraper.py --config configs/multi_group_config.yaml --limited-parallel

# Dry-run (설정만 확인)
python run_multi_group_scraper.py --config configs/multi_group_config.yaml --dry-run
```

### 4. Streamlit 대시보드

```bash
# 대시보드 실행
streamlit run simplified_whatsapp_app.py

# 브라우저에서 http://localhost:8501 접속
# "🔄 멀티 그룹" 탭에서 설정 및 상태 확인
```

---

## 📖 상세 가이드

### 설정 파일 상세

#### GroupConfig

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| name | str | ✅ | - | WhatsApp 그룹 채팅방 이름 |
| save_file | str | ✅ | - | 메시지 저장 JSON 파일 경로 |
| scrape_interval | int | ❌ | 60 | 스크래핑 간격 (초, 최소 10) |
| priority | str | ❌ | "MEDIUM" | 우선순위 (HIGH/MEDIUM/LOW) |

#### ScraperSettings

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| headless | bool | ❌ | true | 헤드리스 모드 여부 |
| timeout | int | ❌ | 30000 | Playwright 타임아웃 (ms, 최소 5000) |
| max_parallel_groups | int | ❌ | 5 | 최대 병렬 그룹 수 (1~10) |

#### AIIntegrationSettings

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| enable_ai_summary | bool | ❌ | true | AI 요약 활성화 여부 |
| confidence_threshold | float | ❌ | 0.7 | 신뢰도 임계값 (0.0~1.0) |
| ai_model | str | ❌ | "gpt-4o-mini" | 사용할 AI 모델 |

### 우선순위 시스템

- **HIGH** 🔴: 긴급 그룹, 가장 먼저 처리
- **MEDIUM** 🟡: 일반 그룹, 균형적 처리
- **LOW** 🟢: 낮은 우선순위, 리소스 여유 시 처리

### 병렬 처리 모드

#### 전체 병렬 (Full Parallel)
```bash
python run_multi_group_scraper.py --config configs/multi_group_config.yaml
```
- 모든 그룹을 동시에 실행
- 최대 성능, 높은 리소스 사용

#### 제한된 병렬 (Limited Parallel)
```bash
python run_multi_group_scraper.py --config configs/multi_group_config.yaml --limited-parallel
```
- `max_parallel_groups` 단위로 배치 실행
- 리소스 사용 제한, 안정적 운영

---

## 🧪 테스트

### 테스트 실행

```bash
# 전체 테스트
python -m pytest tests/test_multi_group_scraper.py -v

# 특정 테스트 클래스
python -m pytest tests/test_multi_group_scraper.py::TestGroupConfig -v

# 커버리지 포함
python -m pytest tests/test_multi_group_scraper.py --cov=macho_gpt.async_scraper
```

### 테스트 커버리지

- ✅ 총 26개 테스트
- ✅ GroupConfig 검증 테스트 (4개)
- ✅ ScraperSettings 검증 테스트 (3개)
- ✅ AIIntegrationSettings 검증 테스트 (2개)
- ✅ MultiGroupConfig 로드/검증 테스트 (5개)
- ✅ AsyncGroupScraper 기능 테스트 (4개)
- ✅ MultiGroupManager 병렬 처리 테스트 (5개)
- ✅ 통합 테스트 (2개)

---

## 🔄 마이그레이션 가이드

### 기존 단일 그룹에서 멀티 그룹으로 전환

#### Step 1: 설정 파일 생성

기존 단일 그룹 실행:
```bash
python extract_whatsapp_auto.py --run --room "MR.CHA 전용"
```

멀티 그룹 설정 생성:
```yaml
groups:
  - name: "MR.CHA 전용"           # 기존 그룹
    save_file: "data/mr_cha_messages.json"
    scrape_interval: 60
    priority: "HIGH"

  - name: "New Group 1"            # 추가 그룹
    save_file: "data/new_group1_messages.json"
    scrape_interval: 120
    priority: "MEDIUM"
```

#### Step 2: 멀티 그룹 실행

```bash
python run_multi_group_scraper.py --config configs/multi_group_config.yaml
```

#### Step 3: 데이터 통합

기존 단일 그룹 데이터와 멀티 그룹 데이터는 자동으로 통합됩니다.

### 하위 호환성 보장

- ✅ 기존 `extract_whatsapp_auto.py` 단일 그룹 실행 유지
- ✅ 기존 `auth.json` 인증 방식 유지
- ✅ 기존 대시보드 포트 및 기능 유지
- ✅ 기존 데이터 파일 형식 유지

---

## 📊 모니터링 및 로깅

### 로그 파일

```bash
# 실시간 로그 확인
tail -f logs/multi_group_scraper.log

# 로그 검색
grep "ERROR" logs/multi_group_scraper.log
```

### 로그 레벨

- **INFO**: 일반 동작 정보
- **WARNING**: 경고 (자동 복구 가능)
- **ERROR**: 오류 (수동 개입 필요)

### 상태 확인

```python
# Python에서 상태 확인
from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager

manager = MultiGroupManager(...)
status = manager.get_status()

print(f"실행 중: {status['is_running']}")
print(f"활성 그룹: {status['active_groups']}")
print(f"총 그룹: {status['total_groups']}")
```

---

## 🐛 트러블슈팅

### 문제: Playwright 브라우저 실행 오류

```
Error: Executable doesn't exist at ...
```

**해결:**
```bash
playwright install chromium
```

### 문제: WhatsApp 로그인 실패

```
WARNING: WhatsApp login timeout
```

**해결:**
1. `headless: false`로 설정하여 수동 QR 스캔
2. `auth.json` 세션 파일 확인
3. 타임아웃 증가: `timeout: 60000`

### 문제: 메모리 부족

```
MemoryError: ...
```

**해결:**
1. `--limited-parallel` 옵션 사용
2. `max_parallel_groups` 감소 (예: 3 → 2)
3. `scrape_interval` 증가 (리소스 사용 분산)

### 문제: 설정 검증 실패

```
ValueError: max_parallel_groups는 1~10 사이
```

**해결:**
- 설정 파일의 값 범위 확인
- Pydantic 검증 규칙 준수

---

## 🔒 보안 및 규정 준수

### 데이터 보안

- ✅ 로컬 파일 시스템에만 저장
- ✅ PII/NDA 자동 스크리닝
- ✅ FANR/MOIAT 규정 준수

### 접근 제어

```yaml
# .env 파일로 민감 정보 관리
OPENAI_API_KEY=sk-...
WHATSAPP_SESSION_PATH=auth.json
```

---

## 📈 성능 최적화

### 권장 설정

| 그룹 수 | max_parallel_groups | scrape_interval | 예상 메모리 |
|---------|---------------------|-----------------|-------------|
| 1-3     | 3                   | 60              | ~200MB      |
| 4-6     | 5                   | 90              | ~400MB      |
| 7-10    | 5                   | 120             | ~500MB      |

### 최적화 팁

1. **높은 우선순위 그룹**: `scrape_interval`을 낮게 설정
2. **낮은 우선순위 그룹**: `scrape_interval`을 높게 설정
3. **리소스 제한 환경**: `--limited-parallel` 사용
4. **대용량 그룹**: `timeout` 증가

---

## 🔗 API 참조

### GroupConfig

```python
from macho_gpt.async_scraper.group_config import GroupConfig

config = GroupConfig(
    name="MR.CHA 전용",
    save_file="data/messages.json",
    scrape_interval=60,
    priority="HIGH"
)
```

### AsyncGroupScraper

```python
from macho_gpt.async_scraper.async_scraper import AsyncGroupScraper

scraper = AsyncGroupScraper(
    group_config=config,
    chrome_data_dir="chrome-data",
    headless=True
)

await scraper.run()
```

### MultiGroupManager

```python
from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager

manager = MultiGroupManager(
    group_configs=[config1, config2],
    max_parallel_groups=3
)

results = await manager.run_all_groups()
```

---

## 🛠️ 추가 리소스

- [MACHO-GPT v3.4-mini 메인 README](../README.md)
- [TDD 테스트 문서](test_multi_group_scraper.py)
- [시스템 아키텍처](ARCHITECTURE.md)
- [프로젝트 요약](PROJECT_SUMMARY.md)

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. 로그 파일: `logs/multi_group_scraper.log`
2. 테스트 실행: `python -m pytest tests/test_multi_group_scraper.py -v`
3. 설정 검증: `python run_multi_group_scraper.py --dry-run`

---

**MACHO-GPT v3.4-mini for HVDC PROJECT**
**Samsung C&T Logistics · ADNOC·DSV Partnership**
**Version 1.0.0 | 2025-01-15**

