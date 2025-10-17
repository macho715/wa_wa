# WhatsApp Web.js 통합 가이드

> **MACHO-GPT v3.5-optimal WhatsApp Web.js 통합**
> **Tier 4 Setup & Backup - 대안 스크래핑 방법**

## 🎯 개요

이 디렉토리는 MACHO-GPT v3.5-optimal 시스템에 whatsapp-web.js를 통합한 대안 스크래핑 방법을 제공합니다. Playwright 기반 스크래퍼가 실패하거나 사용할 수 없을 때 사용할 수 있는 백업 솔루션입니다.

## 🏗️ 아키텍처

```
setup/whatsapp_webjs/
├── whatsapp_webjs_scraper.js    # Node.js 스크래퍼
├── whatsapp_webjs_bridge.py     # Python-Node.js 브릿지
├── check_nodejs.js              # Node.js 환경 확인
├── package.json                 # npm 의존성
├── package-lock.json            # 의존성 잠금 파일
├── node_modules/                # npm 패키지 (설치 후)
├── .wwebjs_auth/                # 인증 세션 (자동 생성)
└── README.md                    # 이 파일
```

## 🚀 빠른 시작

### 1. Node.js 환경 확인

```bash
# Node.js 버전 확인 (14.0.0 이상 필요)
node --version

# npm 버전 확인
npm --version
```

### 2. 의존성 설치

```bash
# 현재 디렉토리에서 실행
cd setup/whatsapp_webjs
npm install
```

### 3. 환경 확인 스크립트 실행

```bash
# Node.js 환경 및 의존성 확인
node check_nodejs.js
```

### 4. 스크래퍼 테스트

```bash
# 기본 사용법
node whatsapp_webjs_scraper.js "그룹이름" 50

# 예시
node whatsapp_webjs_scraper.js "HVDC 물류팀" 50
```

## 📋 사용법

### Node.js 스크래퍼 직접 사용

```bash
# 기본 사용법
node whatsapp_webjs_scraper.js <group|group1,group2|ALL> [max_messages]

# 예시들
node whatsapp_webjs_scraper.js "HVDC 물류팀" 50
node whatsapp_webjs_scraper.js "HVDC 물류팀,MR.CHA 전용" 100
node whatsapp_webjs_scraper.js "ALL" 75
```

### Python 브릿지 사용

```python
from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge

from macho_gpt.async_scraper.group_config import GroupConfig
from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge

group_config = GroupConfig(name="HVDC 물류팀", save_file="data/hvdc.json", max_messages=50)

result = await bridge.scrape_group(group_config)
print(result.raw_payload)
```

### MACHO-GPT 통합 사용

```bash
# whatsapp-web.js 백엔드로 실행
python run_optimal_scraper.py --backend webjs

# 자동 전환 모드 (Playwright 실패 시 whatsapp-web.js로 전환)
python run_optimal_scraper.py --backend auto

# 전환 비활성화
python run_optimal_scraper.py --backend playwright --no-webjs-fallback

# 특정 그룹만 스크래핑
python run_optimal_scraper.py --backend webjs --groups "HVDC 물류팀" "MR.CHA 전용"
```

## ⚙️ 설정

### package.json 의존성

```json
{
  "dependencies": {
    "whatsapp-web.js": "^1.23.0",
    "qrcode-terminal": "^0.12.0",
    "puppeteer": "^21.0.0"
  }
}
```

### 환경 변수 (선택적)

```bash
# Puppeteer 설정
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
export PUPPETEER_EXECUTABLE_PATH=/path/to/chrome

# WhatsApp Web.js 설정
export WWEBJS_AUTH_DIR=./.wwebjs_auth
```

## 🔧 기능

### Node.js 스크래퍼 (whatsapp_webjs_scraper.js)

- ✅ QR 코드 인증
- ✅ 단일·다중 그룹 메시지 수집
- ✅ 표준화된 JSON 형식 출력 (stdout 전용)
- ✅ CLI 인자 처리
- ✅ 에러 핸들링
- ✅ 타임아웃 처리
- ✅ 미디어 정보 수집
- ✅ ISO 8601 타임스탬프 제공

### Python 브릿지 (whatsapp_webjs_bridge.py)

- ✅ Node.js 환경 자동 확인
- ✅ 의존성 자동 설치
- ✅ subprocess를 통한 안전한 실행
- ✅ JSON 파싱 및 변환
- ✅ 에러 핸들링 및 로깅
- ✅ 세션 정리 기능
- ✅ Playwright 자동 전환을 위한 결과 포맷 정규화

## 📊 Playwright vs whatsapp-web.js 비교

| 기능 | Playwright | whatsapp-web.js |
|------|------------|-----------------|
| **언어** | Python | Node.js |
| **설치 크기** | ~200MB | ~200MB |
| **성능** | 빠름 | 보통 |
| **안정성** | 높음 | 보통 |
| **커뮤니티** | 활발 | 매우 활발 |
| **업데이트** | 정기적 | 매우 빈번 |
| **WhatsApp 호환성** | 수동 관리 | 자동 관리 |
| **QR 코드** | 수동 | 자동 |
| **세션 관리** | 수동 | 자동 |

## 🛠️ 트러블슈팅

### 일반적인 문제

#### 1. Node.js가 설치되지 않음
```bash
# Windows (Chocolatey)
choco install nodejs

# macOS (Homebrew)
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 2. npm 의존성 설치 실패
```bash
# 캐시 정리 후 재설치
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 3. QR 코드 스캔 실패
```bash
# 인증 세션 정리 후 재시도
rm -rf .wwebjs_auth
node whatsapp_webjs_scraper.js "그룹이름" 50
```

#### 4. Puppeteer 오류
```bash
# Chrome 설치 확인
google-chrome --version

# Puppeteer 재설치
npm uninstall puppeteer
npm install puppeteer
```

### 로그 확인

```bash
# 상세 로그와 함께 실행
DEBUG=* node whatsapp_webjs_scraper.js "그룹이름" 50

# Python 브릿지 로그
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from setup.whatsapp_webjs.whatsapp_webjs_bridge import check_webjs_environment
import asyncio
asyncio.run(check_webjs_environment())
"
```

## 🔒 보안 고려사항

### 인증 세션 보안
- `.wwebjs_auth/` 디렉토리는 민감한 인증 정보를 포함합니다
- 이 디렉토리를 `.gitignore`에 추가하세요
- 공유 환경에서는 세션을 정기적으로 정리하세요

### 네트워크 보안
- VPN 사용 시 WhatsApp Web 접근이 제한될 수 있습니다
- 방화벽 설정에서 WhatsApp 도메인을 허용하세요

## 📈 성능 최적화

### 메모리 사용량 최적화
```javascript
// whatsapp_webjs_scraper.js에서
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--memory-pressure-off'
        ]
    }
});
```

### 타임아웃 설정
```python
# whatsapp_webjs_bridge.py에서
result = subprocess.run(
    cmd,
    timeout=300,  # 5분 타임아웃
    # ...
)
```

## 🚀 고급 사용법

### 멀티 그룹 스크래핑
```bash
# 여러 그룹을 순차적으로 스크래핑
for group in "HVDC 물류팀" "MR.CHA 전용" "ADNOC Berth Coordination"; do
    node whatsapp_webjs_scraper.js "$group" 50 "data/${group// /_}.json"
done
```

### Python에서 배치 처리
```python
import asyncio
from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge

async def scrape_multiple_groups():
    bridge = WhatsAppWebJSBridge()
    groups = ["HVDC 물류팀", "MR.CHA 전용", "ADNOC Berth Coordination"]

    for group in groups:
        result = await bridge.scrape_group(group, max_messages=50)
        print(f"{group}: {result['status']}")

asyncio.run(scrape_multiple_groups())
```

## 📚 참고 자료

- [whatsapp-web.js 공식 문서](https://wwebjs.dev/)
- [Node.js 공식 문서](https://nodejs.org/docs/)
- [Puppeteer 문서](https://pptr.dev/)
- [MACHO-GPT v3.5-optimal 메인 문서](../README.md)

## 🤝 기여하기

1. 이슈 리포트: GitHub Issues 사용
2. 기능 요청: Feature Request 템플릿 사용
3. 코드 기여: Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**MACHO-GPT v3.5-optimal WhatsApp Web.js 통합** - 안정적인 백업 스크래핑 솔루션 🎉
