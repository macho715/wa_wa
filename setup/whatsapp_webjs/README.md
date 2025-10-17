# whatsapp-web.js 백업 스크레이퍼 가이드

이 디렉터리는 MACHO-GPT의 whatsapp-web.js 백엔드 구성 요소를 포함합니다. Playwright 백엔드가 실패했을 때 즉시 전환할 수 있도록 Node.js 기반 스크래핑을 제공합니다.

## 1. 설치/Installation

```bash
node --version   # 14 이상 확인
npm --version
npm ci           # 프로젝트 루트에서 실행 시 package-lock 기반 설치
npm --prefix setup/whatsapp_webjs ci
```

## 2. 사용/Usage

### 2.1 단일 실행 테스트
```bash
node setup/whatsapp_webjs/whatsapp_webjs_scraper.js --group "HVDC 물류팀" --limit 100
node setup/whatsapp_webjs/whatsapp_webjs_scraper.js --group "HVDC 물류팀" --include-media
```
출력은 JSON이며, stdout에는 데이터가, stderr에는 로그가 출력됩니다.

### 2.2 Python 브릿지 사용
```python
import asyncio
from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge

async def main():
    bridge = WhatsAppWebJSBridge(timeout=300)
    result = await bridge.scrape_group("HVDC 물류팀", limit=50, include_media=False)
    print(result["group"]["summary"])

asyncio.run(main())
```

### 2.3 통합 실행
```bash
# whatsapp-web.js 백엔드로 실행
python run_optimal_scraper.py --backend webjs

# 자동 전환 모드 (Playwright 실패 시 whatsapp-web.js로 전환)
python run_optimal_scraper.py --backend auto --webjs-fallback

# 특정 그룹만 스크래핑
 python run_optimal_scraper.py --backend webjs --groups "HVDC 물류팀" "MR.CHA 전용"
python run_optimal_scraper.py --backend auto --webjs-fallback --webjs-include-media
```

## 3. 구성/Configuration Highlights

- `package.json` – `npm run ci` 또는 `npm --prefix setup/whatsapp_webjs ci` 사용 권장
- `whatsapp_webjs_scraper.js`
  - `--group/-groups` : 하나 이상의 그룹 지정
  - `--group-limit`   : `그룹명=메시지수` 형태, 개별 limit 지정
  - `--include-media` : base64 미디어 포함
  - `--timeout`       : 초기화 제한 시간(초)
- `whatsapp_webjs_bridge.py`
  - Node/npm 가용성 체크
  - 필요 시 `npm ci` 자동 실행 (`auto_install_deps`)
  - `scrape_groups`, `scrape_group` API 제공

## 4. 세션 정리/Session Cleanup

```bash
rm -rf setup/whatsapp_webjs/.wwebjs_auth
```

또는 Python에서:
```python
asyncio.run(WhatsAppWebJSBridge().cleanup_session())
```

## 5. 자주 묻는 질문/FAQ

| 질문 | 답변 |
|------|------|
| QR 코드가 계속 뜨나요? | 처음 1회 인증 후 `.wwebjs_auth/` 폴더가 유지되도록 하세요. |
| 미디어가 너무 커요 | `--webjs-include-media` 옵션을 끄거나, Node 스크립트 실행 시 `--group-limit` 값을 줄이세요. |
| Playwright → webjs 전환이 안 돼요 | `--backend auto --webjs-fallback` 조합을 사용하고, `check_webjs_environment()` 상태를 확인하세요. |

## 6. 진단/Diagnostics

```python
from setup.whatsapp_webjs.whatsapp_webjs_bridge import check_webjs_environment
import asyncio

async def diagnostics():
    print(await check_webjs_environment())

asyncio.run(diagnostics())
```

이 값이 `dependencies_installed: False`이면 `npm --prefix setup/whatsapp_webjs ci`를 다시 실행하십시오.
