# WhatsApp Web.js 듀얼 백엔드 가이드

MACHO-GPT v3.5-optimal은 Playwright와 whatsapp-web.js를 동시에 지원하여, 실시간(또는 준실시간) WhatsApp 그룹 채팅 수집에 대한 이중화 백엔드를 제공합니다.

## 1. 설치/Installation

1. **Node.js & npm 확인**
   ```bash
   node --version    # >= 14.x
   npm --version
   ```
2. **의존성 설치**
   ```bash
   npm --prefix setup/whatsapp_webjs ci
   ```
3. **최초 QR 인증**
   ```bash
   node setup/whatsapp_webjs/whatsapp_webjs_scraper.js --group "그룹명"
   ```
   터미널에 표시되는 QR 코드를 스캔하면 세션이 `.wwebjs_auth/`에 저장됩니다.

## 2. 사용/Usage

### 2.1 CLI 백엔드 선택
```bash
# 설정 파일(default) 기준 실행
 python run_optimal_scraper.py

# Playwright 고정
 python run_optimal_scraper.py --backend playwright
# whatsapp-web.js 고정 (준실시간 폴링)
python run_optimal_scraper.py --backend webjs --groups "HVDC 물류팀" "MR.CHA 전용"

# 자동 전환 (Playwright 우선, 실패 시 webjs)
 python run_optimal_scraper.py --backend auto --webjs-fallback
 ```

### 2.2 whatsapp-web.js 세부 옵션
```bash
# 미디어(base64) 포함 수집
python run_optimal_scraper.py --backend webjs --webjs-include-media

# 단일 실행 테스트
node setup/whatsapp_webjs/whatsapp_webjs_scraper.js --group "HVDC 물류팀" --limit 100 --include-media
```
스크립트 출력은 JSON이며, Python 브릿지가 자동으로 파싱하여 `data/` 이하 그룹별 파일에 저장합니다.

## 3. 구성/Configuration

`configs/optimal_multi_group_config.yaml`
```yaml
scraper_settings:
  backend: "auto"          # playwright, webjs, auto
  webjs_fallback: true      # Playwright 실패 시 webjs 즉시 전환
  webjs_settings:
    script_dir: "setup/whatsapp_webjs"
    timeout: 300
    auto_install_deps: true
    include_media: false
```
각 그룹 블록의 `max_messages` 값은 webjs 실행 시 `--group-limit` 인자로 전달됩니다.

## 4. 동작/How It Works

1. **Playwright 모드** – 기존 `MultiGroupManager`가 무한 루프로 각 그룹을 스크랩합니다.
2. **whatsapp-web.js 모드** – Python 브릿지가 Node 스크립트를 주기적으로 호출하여 대상 그룹 묶음을 JSON으로 수집합니다.
3. **Auto 모드** – Playwright 초기화 실패 시 즉시 webjs 백엔드로 Failover 합니다. 설정으로 재시도 여부를 제어할 수 있습니다.

## 5. 트러블슈팅/Troubleshooting

| 증상 | 원인 | 해결 |
|------|------|------|
| `Node.js executable not found` | Node 미설치 또는 PATH 미등록 | Node 14+ 설치 후 터미널 재시작 |
| `Initialization timeout reached` | QR 인증 미완료, 네트워크 지연 | QR 재스캔, 또는 `webjs_settings.timeout` 증가 |
| `GROUP_NOT_FOUND` 에러 | 그룹명이 정확하지 않음 | WhatsApp 내 그룹 명칭을 그대로 입력 |
| JSON 파싱 실패 | 오래된 npm 의존성 | `npm --prefix setup/whatsapp_webjs ci` 재실행

## 6. 빠른 점검/Quick Diagnostics

```python
from setup.whatsapp_webjs.whatsapp_webjs_bridge import check_webjs_environment
import asyncio

async def main():
    status = await check_webjs_environment()
    print(status)

asyncio.run(main())
```

출력에 `dependencies_installed: False`가 나타나면 `npm ci`를 다시 수행하십시오.
