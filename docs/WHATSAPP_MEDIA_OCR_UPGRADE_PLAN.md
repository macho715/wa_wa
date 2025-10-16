# WhatsApp 미디어 자동 수집 및 OCR 분석 모듈 업그레이드 계획

## Executive Summary

최근 구조를 다시 검증한 결과, **미디어(이미지·PDF) 자동 수집 ➜ OCR·CV 분석 ➜ JSON 병합** 모듈은 기술적으로 구현 가능하지만 성능·정확도·보안 측면에서 몇 가지 보완이 필요합니다. 핵심 개선 포인트는 **① 미디어 셀렉터 안정화, ② 다운로드 이벤트 처리·용량 필터, ③ 다국어 OCR 파이프라인 고도화, ④ PDF → 이미지 변환 효율화, ⑤ 결과 스키마·대시보드 연동**이며, 세션·타임아웃·에러 핸들링도 함께 강화해야 합니다. 아래 표·코드 스니펫·체크리스트에 업그레이드 방안을 반영했습니다.

---

## 1. DOM · 셀렉터 검증 결과

| 항목                          | 확인 내용                                                                        | 근거                             |
| --------------------------- | ---------------------------------------------------------------------------- | ------------------------------ |
| **미디어 썸네일**                 | `div[data-testid="media-message"]`·`img[src^="blob:"]` 등이 여전히 이미지 메시지의 루트 요소 | ([developers.facebook.com][1]) |
| **다운로드 이벤트**                | Playwright `page.expect_download()` 사용 시 동기·비동기 모두 지원                        | ([playwright.dev][2])          |
| **검색창**                     | `role="searchbox"` + `contenteditable=true` 로 변경된 점 확인                       | ([Stack Overflow][3])          |
| **OCR 엔진**                  | EasyOCR > pytesseract (다국어 정확도 ↑)                                            | ([ironsoftware.com][4])        |
| **PDF → Image**             | `pdf2image.convert_from_path` 는 페이지당 수 초 소요 → 최적화 필요                         | ([Stack Overflow][5])          |
| **클라우드 OCR**                | Azure Vision (Read API) 지원, 대용량·스캔 PDF 적합                                    | ([azure.microsoft.com][6])     |
| **크레인 객체 Detection**        | Roboflow Universe 에 공개 크레인 데이터셋·YOLOv8 튜토리얼 존재                               | ([Roboflow][7])                |
| **대량 이미지 다운로드 UX**          | WhatsApp Web 자체는 zip 다운로드 옵션 한계·불안정 보고                                       | ([Reddit][8])                  |
| **Playwright Download API** | `download.save_as()` 로 경로 지정 가능                                              | ([playwright.dev][9])          |
| **미디어 정책**                  | 기업 환경에서 미디어 자동 다운로드 시 권한·갤러리 노출 이슈 빈발                                        | ([Lifewire][10])               |

---

## 2. 업그레이드 항목 정리

| #  | 보완 필요 사항       | 구체 조치                                                                                 |
| -- | -------------- | ------------------------------------------------------------------------------------- |
| 1  | **셀렉터 안정화**    | 썸네일: `div[data-testid^="media"]` 커버, 실패 시 `img[src^="blob:"]` fallback                |
| 2  | **대기·타임아웃 강화** | `context.set_default_timeout(60000)` + 다운로드 이벤트 2-step 폴링                             |
| 3  | **용량 필터**      | `if download.size > 5*1024*1024: skip or upload S3`                                   |
| 4  | **다국어 OCR**    | 기본 `pytesseract` → `EasyOCR(lang=['en','ko'])` fallback + Azure Read API for PDF>5 MB |
| 5  | **PDF 처리 속도**  | ① `fitz` (PyMuPDF)로 textLayer 우선 추출, ② 잔여 스캔 페이지만 `pdf2image`                         |
| 6  | **JSON 스키마**   | `media_results:[{file,type,ocr,bbox?,labels?}]` → 대시보드·AI 요약 공통 사용                    |
| 7  | **객체 감지 모듈**   | YOLOv8 fine-tune 모델 (크레인·트레일러·파손) 선택적 활성화 `--detect`                                  |
| 8  | **세션 보안**      | `storage_state="auth.json"` + 암호화(환경 변수 AES key)                                      |
| 9  | **로그·재처리 방지**  | `download.log` SHA-256 기록 후 중복 파일 skip                                                |
| 10 | **유닛 테스트 추가**  | ① download mock→ocr 결과 길이>0, ② PDF >5 MB → Azure 호출 모킹                                |

---

## 3. 핵심 코드 패치(요약)

```python
# 0. 공용 설정
MAX_SIZE_MB = 5
AZURE_ENDPOINT = os.getenv("AZ_VISION_ENDPOINT")

# 1. download + OCR
async def download_and_ocr(msg_el, chat):
    async with page.expect_download() as dl:
        await msg_el.click()
    d = await dl.value
    if d.size/(1024**2) > MAX_SIZE_MB and d.mime_type == "application/pdf":
        text = await azure_read(d)                      # 클라우드 OCR 호출
    else:
        path = dst / sanitize(d.suggested_filename)
        await d.save_as(path)
        text = run_local_ocr(path)
    return {"chat": chat, "file": d.suggested_filename, "ocr": text}

def run_local_ocr(path):
    if path.suffix.lower() in (".jpg", ".png"):
        return easyocr.Reader(['en','ko']).readtext(str(path), detail=0)
    elif path.suffix.lower()==".pdf":
        pdf = fitz.open(path)
        txt = "".join(p.extract_text() or "" for p in pdf)
        if not txt.strip():
            images = convert_from_path(path)
            txt = "\n".join(pytesseract.image_to_string(img, lang="eng+kor") for img in images)
        return txt
```

---

## 4. 운영 체크리스트

1. **네트워크 지연** → 글로벌 타임아웃 60 s, 다운로드 이벤트 30 s
2. **OCR 캐시** → 같은 SHA-256 파일은 OCR 재실행 안 함
3. **보안** → OCR 결과에서 "passport / id no / phone" 정규식 익명화
4. **모듈 옵션** → `--media`, `--detect`, `--azure-ocr` CLI 추가
5. **대시보드 업데이트** → `total_media`, `ocr_keywords` KPI 노출

---

## 5. 단계별 실행 계획

| 단계                | 기간  | 산출물                         |
| ----------------- | --- | --------------------------- |
| **PoC**           | 1 d | 업그레이드 모듈 브랜치 + 유닛 테스트 Green |
| **Pilot(한 채팅방)**  | 2 d | 미디어 60건 OCR → JSON 검사 통과    |
| **Full Roll-out** | 1 주 | 5 채팅방 일간 배치 + 대시보드 KPIs     |
| **Refactor**      | 3 d | 접근자 추상화·async gather 최적화    |
| **Expand**        | 이후  | YOLO 모듈·TG 알림·RPA 통합        |

---

## 6. 기술적 구현 세부사항

### 6.1 미디어 셀렉터 안정화

```python
async def find_media_messages(page):
    """안정적인 미디어 메시지 셀렉터"""
    selectors = [
        'div[data-testid="media-message"]',
        'div[data-testid^="media"]',
        'img[src^="blob:"]',
        'div[role="img"]'
    ]
    
    for selector in selectors:
        try:
            elements = await page.query_selector_all(selector)
            if elements:
                return elements
        except Exception as e:
            logger.warning(f"Selector {selector} failed: {e}")
            continue
    
    return []
```

### 6.2 다운로드 이벤트 처리

```python
async def handle_media_download(page, media_element):
    """미디어 다운로드 및 용량 필터링"""
    try:
        async with page.expect_download(timeout=30000) as download_info:
            await media_element.click()
        
        download = await download_info.value
        
        # 용량 체크
        if download.size > MAX_SIZE_MB * 1024 * 1024:
            logger.warning(f"File too large: {download.suggested_filename} ({download.size} bytes)")
            return None
            
        # 파일 저장
        filename = sanitize_filename(download.suggested_filename)
        filepath = Path("downloads") / filename
        await download.save_as(filepath)
        
        return filepath
        
    except TimeoutError:
        logger.error("Download timeout")
        return None
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None
```

### 6.3 다국어 OCR 파이프라인

```python
class OCRProcessor:
    def __init__(self):
        self.easyocr_reader = easyocr.Reader(['en', 'ko'])
        self.azure_client = None
        if AZURE_ENDPOINT:
            self.azure_client = ComputerVisionClient(AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_KEY))
    
    def process_image(self, image_path):
        """이미지 OCR 처리"""
        try:
            # EasyOCR 시도
            results = self.easyocr_reader.readtext(str(image_path))
            text = ' '.join([result[1] for result in results])
            
            if not text.strip() and self.azure_client:
                # Azure Vision API fallback
                text = self._azure_ocr(image_path)
                
            return text
            
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return ""
    
    def process_pdf(self, pdf_path):
        """PDF OCR 처리"""
        try:
            # PyMuPDF로 텍스트 추출 시도
            pdf = fitz.open(pdf_path)
            text = ""
            
            for page in pdf:
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + "\n"
            
            # 텍스트가 없으면 이미지 변환 후 OCR
            if not text.strip():
                images = convert_from_path(pdf_path)
                for img in images:
                    img_text = self.process_image(img)
                    text += img_text + "\n"
            
            return text
            
        except Exception as e:
            logger.error(f"PDF OCR failed for {pdf_path}: {e}")
            return ""
```

### 6.4 JSON 스키마 정의

```python
MEDIA_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "chat_title": {"type": "string"},
        "message_id": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "media_results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string"},
                    "file_type": {"type": "string"},
                    "file_size": {"type": "integer"},
                    "ocr_text": {"type": "string"},
                    "confidence": {"type": "number"},
                    "bounding_boxes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "bbox": {"type": "array", "items": {"type": "number"}},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "detected_objects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "confidence": {"type": "number"},
                                "bbox": {"type": "array", "items": {"type": "number"}}
                            }
                        }
                    }
                }
            }
        }
    }
}
```

---

## 7. 보안 및 성능 최적화

### 7.1 보안 강화

```python
def sanitize_ocr_text(text):
    """OCR 결과에서 민감 정보 제거"""
    patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 전화번호
        r'\b\d{6}-\d{7}\b',        # 주민번호
        r'\b[A-Z0-9]{9}\b',        # 여권번호
        r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # 신용카드
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '[REDACTED]', text)
    
    return text
```

### 7.2 성능 최적화

```python
async def process_media_batch(media_elements, chat_title):
    """배치 처리로 성능 최적화"""
    semaphore = asyncio.Semaphore(3)  # 동시 다운로드 제한
    
    async def process_single(element):
        async with semaphore:
            return await download_and_ocr(element, chat_title)
    
    tasks = [process_single(element) for element in media_elements]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r for r in results if r is not None and not isinstance(r, Exception)]
```

---

## 8. 테스트 전략

### 8.1 유닛 테스트

```python
def test_media_download():
    """미디어 다운로드 테스트"""
    # Mock setup
    mock_download = Mock()
    mock_download.size = 1024 * 1024  # 1MB
    mock_download.suggested_filename = "test.jpg"
    
    # Test execution
    result = handle_media_download(mock_page, mock_element)
    
    # Assertions
    assert result is not None
    assert result.name == "test.jpg"

def test_ocr_processing():
    """OCR 처리 테스트"""
    # Test image with known text
    test_image = "test_data/sample_invoice.jpg"
    
    processor = OCRProcessor()
    result = processor.process_image(test_image)
    
    assert len(result) > 0
    assert "invoice" in result.lower()
```

### 8.2 통합 테스트

```python
async def test_full_media_pipeline():
    """전체 미디어 파이프라인 테스트"""
    # Setup
    page = await browser.new_page()
    await page.goto("https://web.whatsapp.com")
    
    # Execute
    media_elements = await find_media_messages(page)
    results = await process_media_batch(media_elements, "Test Chat")
    
    # Verify
    assert len(results) > 0
    assert all("ocr_text" in result for result in results)
```

---

## 9. 모니터링 및 로깅

### 9.1 성능 메트릭

```python
class MediaProcessingMetrics:
    def __init__(self):
        self.total_processed = 0
        self.successful_ocr = 0
        self.failed_downloads = 0
        self.processing_times = []
    
    def record_processing_time(self, duration):
        self.processing_times.append(duration)
    
    def get_average_processing_time(self):
        return sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
    
    def get_success_rate(self):
        return self.successful_ocr / self.total_processed if self.total_processed > 0 else 0
```

### 9.2 로깅 설정

```python
import logging
import json
from datetime import datetime

def setup_media_logging():
    """미디어 처리 전용 로깅 설정"""
    logger = logging.getLogger('whatsapp_media')
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler('logs/media_processing.log')
    fh.setLevel(logging.INFO)
    
    # JSON formatter
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName
            }
            return json.dumps(log_entry)
    
    fh.setFormatter(JSONFormatter())
    logger.addHandler(fh)
    
    return logger
```

---

## 10. 배포 및 운영

### 10.1 환경 설정

```yaml
# config/media_ocr_config.yaml
media_processing:
  max_file_size_mb: 5
  supported_formats: [".jpg", ".jpeg", ".png", ".pdf"]
  ocr_engines:
    primary: "easyocr"
    fallback: "azure"
  
azure_vision:
  endpoint: "${AZURE_VISION_ENDPOINT}"
  key: "${AZURE_VISION_KEY}"
  
object_detection:
  enabled: false
  model_path: "models/yolov8_crane.pt"
  confidence_threshold: 0.5
  
security:
  redact_patterns:
    - phone_numbers: true
    - credit_cards: true
    - passport_numbers: true
```

### 10.2 CLI 인터페이스

```python
import click

@click.group()
def cli():
    """WhatsApp Media OCR Processing CLI"""
    pass

@cli.command()
@click.option('--chat', help='Specific chat to process')
@click.option('--media-only', is_flag=True, help='Process only media messages')
@click.option('--detect-objects', is_flag=True, help='Enable object detection')
@click.option('--azure-ocr', is_flag=True, help='Use Azure Vision API')
def extract(chat, media_only, detect_objects, azure_ocr):
    """Extract and process WhatsApp messages"""
    # Implementation
    pass

@cli.command()
@click.argument('file_path')
def analyze(file_path):
    """Analyze existing extraction file"""
    # Implementation
    pass

if __name__ == '__main__':
    cli()
```

---

## 11. 결론 및 다음 단계

이 업그레이드 계획을 통해 WhatsApp 미디어 자동 수집 및 OCR 분석 모듈의 안정성, 성능, 보안을 크게 향상시킬 수 있습니다. 

**우선순위:**
1. **즉시**: 셀렉터 안정화 및 다운로드 이벤트 처리
2. **단기**: 다국어 OCR 파이프라인 구현
3. **중기**: 객체 감지 모듈 및 대시보드 연동
4. **장기**: 클라우드 OCR 및 고급 분석 기능

**성공 지표:**
- 미디어 다운로드 성공률 > 95%
- OCR 정확도 > 90%
- 처리 시간 < 30초/파일
- 보안 위반 0건

---

*문서 버전: 1.0*  
*최종 업데이트: 2025-07-24*  
*담당자: MACHO-GPT v3.4-mini* 