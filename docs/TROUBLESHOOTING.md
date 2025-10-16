# 🔧 MACHO-GPT v3.5-optimal 문제 해결 가이드

## 개요

MACHO-GPT v3.5-optimal 시스템 사용 중 발생할 수 있는 문제들과 해결 방법을 정리한 가이드입니다.

## 🚨 긴급 문제 해결

### 1. 시스템이 시작되지 않음

#### 증상
```bash
python run_optimal_scraper.py
# 아무 반응 없음 또는 오류 메시지
```

#### 해결 방법
```bash
# 1. Python 버전 확인
python --version  # 3.8+ 필요

# 2. 의존성 재설치
pip install -r requirements.txt --force-reinstall

# 3. 가상환경 사용
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 브라우저가 열리지 않음

#### 증상
- 브라우저 창이 나타나지 않음
- Chrome 관련 오류 메시지

#### 해결 방법
```bash
# 1. Chrome 설치 확인
google-chrome --version  # Linux
# 또는
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version  # Windows

# 2. Chrome 데이터 디렉토리 초기화
rm -rf chrome-data/
mkdir chrome-data

# 3. 헤드리스 모드 비활성화
python run_optimal_scraper.py --no-headless
```

### 3. QR 코드가 나타나지 않음

#### 증상
- WhatsApp Web 페이지는 로드되지만 QR 코드가 보이지 않음
- "QR 코드를 스캔하세요" 메시지만 표시

#### 해결 방법
```bash
# 1. 페이지 로딩 대기
# 30초 정도 기다린 후 새로고침

# 2. 로딩 안정성 개선 활성화
python run_optimal_scraper.py --enhance-loading

# 3. 수동 인증 도구 사용
python setup/manual_auth.py
```

## 🔍 스크래핑 문제

### 1. 그룹을 찾을 수 없음

#### 증상
```
WARNING: Group not found: HVDC 물류팀
ERROR: Failed to locate group
```

#### 해결 방법
```bash
# 1. DOM 분석으로 그룹 확인
python tools/dom_analyzer.py

# 2. 그룹 검색 기능 사용
python run_optimal_scraper.py --search-groups

# 3. 그룹 이름 정확성 확인
# 설정 파일에서 그룹 이름이 정확한지 확인
```

### 2. 메시지 추출 실패

#### 증상
```
WARNING: Failed to extract message
ERROR: No messages found
```

#### 해결 방법
```bash
# 1. 로딩 안정성 개선 활성화
python run_optimal_scraper.py --enhance-loading

# 2. 디버그 모드로 실행
python run_optimal_scraper.py --debug

# 3. 타임아웃 증가
python run_optimal_scraper.py --timeout 60000
```

### 3. 메시지가 비어있음

#### 증상
- 스크래핑은 성공하지만 메시지 내용이 비어있음
- JSON 파일에 빈 배열만 저장됨

#### 해결 방법
```bash
# 1. 메시지 로딩 대기 시간 증가
python run_optimal_scraper.py --message-wait 5000

# 2. 스크롤 기능 활성화
python run_optimal_scraper.py --enable-scroll

# 3. 최대 메시지 수 증가
python run_optimal_scraper.py --max-messages 100
```

## 🌐 네트워크 문제

### 1. 연결 시간 초과

#### 증상
```
ERROR: Timeout waiting for page load
ERROR: Network connection failed
```

#### 해결 방법
```bash
# 1. 타임아웃 증가
python run_optimal_scraper.py --timeout 120000

# 2. 재시도 횟수 증가
python run_optimal_scraper.py --retry-count 5

# 3. 네트워크 상태 확인
python tools/status_monitor.py --check-network
```

### 2. WhatsApp Web 로딩 실패

#### 증상
- WhatsApp Web 페이지가 로드되지 않음
- "사이트에 연결할 수 없음" 오류

#### 해결 방법
```bash
# 1. 인터넷 연결 확인
ping web.whatsapp.com

# 2. 프록시 설정 확인
python run_optimal_scraper.py --no-proxy

# 3. User-Agent 변경
python run_optimal_scraper.py --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

## 🔒 인증 문제

### 1. 로그인 실패

#### 증상
- QR 코드를 스캔했지만 로그인되지 않음
- "로그인에 실패했습니다" 메시지

#### 해결 방법
```bash
# 1. 수동 인증 도구 사용
python setup/manual_auth.py

# 2. 대안 방법 시도
python setup/alternative_methods.py

# 3. 세션 데이터 초기화
rm -rf chrome-data/
python run_optimal_scraper.py
```

### 2. 세션 만료

#### 증상
- 중간에 "세션이 만료되었습니다" 메시지
- 스크래핑이 중단됨

#### 해결 방법
```bash
# 1. 자동 재로그인 활성화
python run_optimal_scraper.py --auto-relogin

# 2. 세션 유지 시간 증가
python run_optimal_scraper.py --session-timeout 3600

# 3. 주기적 재인증
python run_optimal_scraper.py --periodic-auth
```

## 🛡️ 탐지 및 차단 문제

### 1. 봇 탐지됨

#### 증상
- "의심스러운 활동이 감지되었습니다" 메시지
- CAPTCHA 요구
- 계정 일시 정지

#### 해결 방법
```bash
# 1. 스텔스 기능 활성화
python run_optimal_scraper.py --enhance-stealth

# 2. 인간 행동 시뮬레이션
python run_optimal_scraper.py --simulate-human

# 3. 요청 간격 증가
python run_optimal_scraper.py --request-interval 5000
```

### 2. IP 차단

#### 증상
- "접근이 차단되었습니다" 메시지
- 모든 요청이 실패

#### 해결 방법
```bash
# 1. VPN 사용
# 2. 프록시 서버 사용
python run_optimal_scraper.py --proxy "http://proxy-server:port"

# 3. User-Agent 로테이션
python run_optimal_scraper.py --rotate-user-agent
```

## 💾 데이터 문제

### 1. 데이터 저장 실패

#### 증상
```
ERROR: Failed to save data
ERROR: Permission denied
```

#### 해결 방법
```bash
# 1. 디렉토리 권한 확인
chmod 755 data/
chmod 755 logs/

# 2. 디스크 공간 확인
df -h  # Linux/Mac
# 또는
dir  # Windows

# 3. 백업 디렉토리 사용
python run_optimal_scraper.py --backup-dir /tmp/backup/
```

### 2. JSON 파일 손상

#### 증상
- JSON 파일이 읽을 수 없음
- 파싱 오류 발생

#### 해결 방법
```bash
# 1. 손상된 파일 백업
mv data/messages_*.json data/corrupted/

# 2. 새로 스크래핑
python run_optimal_scraper.py --force-refresh

# 3. 데이터 검증
python -c "
import json
import glob
for file in glob.glob('data/messages_*.json'):
    try:
        with open(file, 'r') as f:
            json.load(f)
        print(f'OK: {file}')
    except:
        print(f'ERROR: {file}')
"
```

## 🔧 성능 문제

### 1. 메모리 사용량 과다

#### 증상
- 시스템이 느려짐
- 메모리 부족 오류

#### 해결 방법
```bash
# 1. 최대 메시지 수 제한
python run_optimal_scraper.py --max-messages 30

# 2. 병렬 처리 수 제한
python run_optimal_scraper.py --max-parallel 2

# 3. 메모리 모니터링
python tools/status_monitor.py --monitor-memory
```

### 2. CPU 사용량 과다

#### 증상
- CPU 사용률이 100%에 가까움
- 시스템이 응답하지 않음

#### 해결 방법
```bash
# 1. 요청 간격 증가
python run_optimal_scraper.py --request-interval 3000

# 2. 스크롤 기능 비활성화
python run_optimal_scraper.py --no-scroll

# 3. Enhancement 비활성화
python run_optimal_scraper.py --no-enhancements
```

## 📊 로그 분석

### 로그 파일 위치
```bash
# 로그 파일 확인
ls -la logs/

# 최신 로그 확인
tail -f logs/optimal_scraper_*.log

# 오류 로그만 확인
grep "ERROR" logs/optimal_scraper_*.log
```

### 일반적인 로그 패턴

#### 성공적인 실행
```
INFO: Starting optimal scraper
INFO: Browser launched successfully
INFO: WhatsApp Web loaded
INFO: QR code displayed
INFO: Login successful
INFO: Group found: HVDC 물류팀
INFO: Messages extracted: 25
INFO: Data saved successfully
```

#### 오류가 있는 실행
```
ERROR: Failed to launch browser
WARNING: Group not found: HVDC 물류팀
ERROR: Timeout waiting for page load
WARNING: Failed to extract message
```

## 🆘 고급 문제 해결

### 1. 시스템 진단
```bash
# 전체 시스템 상태 확인
python tools/status_monitor.py --full-diagnosis

# 네트워크 연결 테스트
python tools/status_monitor.py --test-network

# 브라우저 호환성 테스트
python tools/status_monitor.py --test-browser
```

### 2. 설정 검증
```bash
# 설정 파일 검증
python run_optimal_scraper.py --validate-config

# 기본 설정으로 테스트
python run_optimal_scraper.py --use-default-config
```

### 3. 완전 초기화
```bash
# 모든 데이터 초기화
rm -rf chrome-data/ data/ logs/
mkdir chrome-data data logs

# 기본 설정으로 시작
python run_optimal_scraper.py --use-default-config
```

## 📞 지원 요청

### 문제 보고 시 포함할 정보
1. **오류 메시지**: 정확한 오류 메시지 복사
2. **로그 파일**: `logs/optimal_scraper_*.log` 파일
3. **시스템 정보**: OS, Python 버전, Chrome 버전
4. **재현 단계**: 문제를 재현하는 정확한 단계
5. **설정 파일**: 사용 중인 설정 파일 내용

### 로그 수집
```bash
# 로그 파일 압축
tar -czf logs_backup.tar.gz logs/

# 시스템 정보 수집
python tools/status_monitor.py --collect-info > system_info.txt
```

---

**💡 팁**: 대부분의 문제는 로딩 안정성 개선(`--enhance-loading`)을 활성화하거나 타임아웃을 증가시키는 것으로 해결됩니다. 문제가 지속되면 디버그 모드(`--debug`)로 실행하여 상세한 정보를 확인하세요.
