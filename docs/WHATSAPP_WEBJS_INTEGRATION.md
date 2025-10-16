# WhatsApp Web.js 통합 가이드

> **MACHO-GPT v3.5-optimal WhatsApp Web.js 통합**  
> **듀얼 백엔드 지원 - Playwright + whatsapp-web.js**

## 🎯 개요

MACHO-GPT v3.5-optimal은 이제 두 가지 스크래핑 백엔드를 지원합니다:
- **Playwright** (기본): Python 기반, 안정적이고 빠름
- **whatsapp-web.js** (대안): Node.js 기반, 활발한 커뮤니티 지원

## 🏗️ 통합 아키텍처

### 확장된 4-Tier 구조

```
Tier 1: Core System (듀얼 백엔드 지원)
├── run_optimal_scraper.py (통합 CLI)
├── run_multi_group_scraper.py (Playwright 전용)
└── macho_gpt/async_scraper/ (Playwright 엔진)

Tier 2: Enhancement Layer
├── loading_optimizer.py
└── stealth_features.py

Tier 3: Development Tools
├── tools/dom_analyzer.py
├── tools/quick_test.py
└── tools/status_monitor.py

Tier 4: Setup & Backup (확장)
├── setup/manual_auth.py
├── setup/alternative_methods.py
└── setup/whatsapp_webjs/ (신규)
    ├── whatsapp_webjs_bridge.py (Python-Node.js 브릿지)
    ├── whatsapp_webjs_scraper.js (Node.js 스크래퍼)
    ├── package.json
    └── README.md
```

## 🚀 사용법

### 백엔드 선택

#### 1. Playwright (기본)
```bash
# 기본 실행 (Playwright 사용)
python run_optimal_scraper.py

# 명시적으로 Playwright 지정
python run_optimal_scraper.py --backend playwright
```

#### 2. whatsapp-web.js
```bash
# whatsapp-web.js 사용
python run_optimal_scraper.py --backend webjs

# 특정 그룹만 스크래핑
python run_optimal_scraper.py --backend webjs --groups "HVDC 물류팀"
```

#### 3. 자동 전환 (Auto)
```bash
# Playwright 우선, 실패 시 whatsapp-web.js로 전환
python run_optimal_scraper.py --backend auto

# 자동 전환 활성화
python run_optimal_scraper.py --backend auto --webjs-fallback
```

### 설정 파일에서 백엔드 지정

```yaml
# configs/optimal_multi_group_config.yaml
scraper_settings:
  backend: "playwright"  # playwright, webjs, auto
  webjs_fallback: true   # Playwright 실패 시 자동 전환
  webjs_settings:
    script_dir: "setup/whatsapp_webjs"
    timeout: 300
    auto_install_deps: true
```

## 🔄 백엔드 전환 로직

### Auto 모드 동작

1. **Playwright 시도**
   - 기본 백엔드로 Playwright 실행
   - 성공 시 결과 반환
   - 실패 시 다음 단계로

2. **whatsapp-web.js 전환**
   - Node.js 환경 확인
   - 의존성 자동 설치 (필요시)
   - whatsapp-web.js로 재시도
   - 성공 시 결과 반환

3. **최종 실패**
   - 두 백엔드 모두 실패 시 에러 반환
   - 상세한 실패 원인 로깅

### 성공률 추적

```python
# 자동으로 백엔드 성공률 추적
{
    "playwright_success_rate": 0.95,
    "webjs_success_rate": 0.87,
    "auto_mode_recommendation": "playwright"
}
```

## 📊 백엔드 비교

| 특성 | Playwright | whatsapp-web.js |
|------|------------|-----------------|
| **언어** | Python | Node.js |
| **설치 크기** | ~200MB | ~200MB |
| **성능** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **안정성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **커뮤니티** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **업데이트** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **WhatsApp 호환성** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **QR 코드** | 수동 | 자동 |
| **세션 관리** | 수동 | 자동 |
| **디버깅** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🛠️ 설치 및 설정

### 1. Node.js 환경 설정

```bash
# Node.js 설치 (14.0.0 이상)
# Windows: https://nodejs.org/
# macOS: brew install node
# Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# 버전 확인
node --version
npm --version
```

### 2. whatsapp-web.js 의존성 설치

```bash
cd setup/whatsapp_webjs
npm install
```

### 3. 환경 확인

```bash
# Node.js 환경 확인
node check_nodejs.js

# Python 브릿지 테스트
python -c "
from setup.whatsapp_webjs.whatsapp_webjs_bridge import check_webjs_environment
import asyncio
print(asyncio.run(check_webjs_environment()))
"
```

## 🔧 고급 설정

### 환경 변수

```bash
# Puppeteer 설정
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
export PUPPETEER_EXECUTABLE_PATH=/path/to/chrome

# WhatsApp Web.js 설정
export WWEBJS_AUTH_DIR=./.wwebjs_auth
export WWEBJS_DISABLE_SSL=true  # SSL 문제 시
```

### 커스텀 설정

```yaml
# configs/optimal_multi_group_config.yaml
scraper_settings:
  backend: "auto"
  webjs_fallback: true
  webjs_settings:
    script_dir: "setup/whatsapp_webjs"
    timeout: 300
    auto_install_deps: true
    puppeteer_args:
      - "--no-sandbox"
      - "--disable-setuid-sandbox"
      - "--disable-dev-shm-usage"
    auth_strategy: "LocalAuth"
    client_id: "macho-gpt-optimal"
```

## 🧪 테스트 및 검증

### 단위 테스트

```bash
# Node.js 스크래퍼 테스트
cd setup/whatsapp_webjs
node whatsapp_webjs_scraper.js "테스트그룹" 10

# Python 브릿지 테스트
python whatsapp_webjs_bridge.py "테스트그룹" 10
```

### 통합 테스트

```bash
# Playwright 백엔드 테스트
python run_optimal_scraper.py --backend playwright --groups "테스트그룹"

# whatsapp-web.js 백엔드 테스트
python run_optimal_scraper.py --backend webjs --groups "테스트그룹"

# 자동 전환 테스트
python run_optimal_scraper.py --backend auto --groups "테스트그룹"
```

### 성능 벤치마크

```bash
# 성능 비교 테스트
python -c "
import time
import asyncio
from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge

async def benchmark():
    bridge = WhatsAppWebJSBridge()
    
    # whatsapp-web.js 벤치마크
    start = time.time()
    result = await bridge.scrape_group('테스트그룹', 50)
    webjs_time = time.time() - start
    
    print(f'whatsapp-web.js: {webjs_time:.2f}초')
    print(f'상태: {result[\"status\"]}')

asyncio.run(benchmark())
"
```

## 🚨 트러블슈팅

### 일반적인 문제

#### 1. Node.js 환경 문제
```bash
# Node.js 재설치
# Windows: 제어판 > 프로그램 제거 > Node.js 제거 후 재설치
# macOS: brew uninstall node && brew install node
# Ubuntu: sudo apt remove nodejs && curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# PATH 확인
echo $PATH  # macOS/Linux
echo %PATH%  # Windows
```

#### 2. npm 의존성 문제
```bash
# 캐시 정리
npm cache clean --force

# node_modules 재설치
rm -rf node_modules package-lock.json
npm install

# 특정 패키지 재설치
npm uninstall whatsapp-web.js
npm install whatsapp-web.js@latest
```

#### 3. Puppeteer 문제
```bash
# Chrome 설치 확인
google-chrome --version
# 또는
chrome --version

# Puppeteer 재설치
npm uninstall puppeteer
npm install puppeteer@latest
```

#### 4. QR 코드 스캔 실패
```bash
# 인증 세션 정리
rm -rf .wwebjs_auth

# 다시 실행
node whatsapp_webjs_scraper.js "그룹이름" 50
```

### 로그 분석

```bash
# 상세 로그 활성화
DEBUG=* node whatsapp_webjs_scraper.js "그룹이름" 50

# Python 로깅 활성화
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge
# ... 테스트 코드
"
```

## 📈 성능 최적화

### 메모리 사용량 최적화

```javascript
// whatsapp_webjs_scraper.js
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--memory-pressure-off',
            '--max_old_space_size=4096'
        ]
    }
});
```

### 네트워크 최적화

```python
# whatsapp_webjs_bridge.py
result = subprocess.run(
    cmd,
    timeout=300,
    env={
        **os.environ,
        'NODE_OPTIONS': '--max-old-space-size=4096'
    }
)
```

## 🔒 보안 고려사항

### 인증 세션 보안
- `.wwebjs_auth/` 디렉토리는 민감한 정보 포함
- `.gitignore`에 추가 필수
- 공유 환경에서는 정기적 정리

### 네트워크 보안
- VPN 사용 시 WhatsApp Web 접근 제한 가능
- 방화벽에서 WhatsApp 도메인 허용 필요

## 🚀 미래 계획

### v3.6-hybrid (계획)
- [ ] 완전한 듀얼 백엔드 지원
- [ ] 실시간 백엔드 전환
- [ ] 성능 모니터링 대시보드
- [ ] 자동 최적화 추천

### v3.7-enterprise (미래)
- [ ] 클라우드 배포 지원
- [ ] API 서비스 제공
- [ ] 고급 분석 및 리포팅
- [ ] 엔터프라이즈 보안 기능

## 📚 참고 자료

- [whatsapp-web.js 공식 문서](https://wwebjs.dev/)
- [Node.js 공식 문서](https://nodejs.org/docs/)
- [Puppeteer 문서](https://pptr.dev/)
- [Playwright 문서](https://playwright.dev/)
- [MACHO-GPT v3.5-optimal 메인 문서](../README.md)

## 🤝 기여하기

1. **이슈 리포트**: GitHub Issues 사용
2. **기능 요청**: Feature Request 템플릿 사용
3. **코드 기여**: Pull Request 생성
4. **문서 개선**: Documentation 개선 제안

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**MACHO-GPT v3.5-optimal WhatsApp Web.js 통합** - 듀얼 백엔드로 안정성과 유연성을 모두 확보! 🎉
