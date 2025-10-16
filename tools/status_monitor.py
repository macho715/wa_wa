#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini WhatsApp RPA 상태 모니터링
------------------------------------------
Samsung C&T Logistics · HVDC Project

기능:
- WhatsApp RPA 추출 진행 상황 모니터링
- 로그 파일 실시간 확인
- 결과 파일 생성 확인
- 시스템 상태 점검
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime

def check_log_files():
    """로그 파일 상태 확인"""
    print("📋 로그 파일 상태 확인")
    print("=" * 40)
    
    log_files = [
        "logs/hvdc_whatsapp_extract.log",
        "logs/whatsapp_rpa.log",
        "logs/whatsapp_rpa_manual.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            print(f"✅ {log_file}")
            print(f"   📊 크기: {size} bytes")
            print(f"   ⏰ 수정시간: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 최근 로그 내용 확인
            if size > 0:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"   📝 최근 로그: {lines[-1].strip()}")
                except Exception as e:
                    print(f"   ❌ 로그 읽기 오류: {str(e)}")
        else:
            print(f"❌ {log_file} - 파일 없음")
        print()

def check_data_files():
    """데이터 파일 상태 확인"""
    print("📊 데이터 파일 상태 확인")
    print("=" * 40)
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data 디렉토리가 없습니다")
        return
    
    # WhatsApp 추출 결과 파일 확인
    extraction_files = list(data_dir.glob("hvdc_whatsapp_extraction_*.json"))
    extraction_files.extend(list(data_dir.glob("whatsapp_extraction_*.json")))
    
    if extraction_files:
        print(f"✅ 추출 결과 파일: {len(extraction_files)}개")
        for file in sorted(extraction_files, key=lambda x: x.stat().st_mtime, reverse=True):
            size = file.stat().st_size
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"   📁 {file.name}")
            print(f"      📊 크기: {size} bytes")
            print(f"      ⏰ 생성시간: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # JSON 파일 내용 미리보기
            if size > 0:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            success_count = sum(1 for item in data if item.get('status') == 'SUCCESS')
                            total_count = len(data)
                            print(f"      📈 성공률: {success_count}/{total_count}")
                            
                            # 채팅방별 결과 요약
                            for item in data:
                                chat_title = item.get('chat_title', 'Unknown')
                                status = item.get('status', 'Unknown')
                                message_count = item.get('message_count', 0)
                                print(f"         - {chat_title}: {status} ({message_count}개 메시지)")
                        else:
                            print(f"      📋 단일 결과: {data.get('status', 'Unknown')}")
                except Exception as e:
                    print(f"      ❌ 파일 읽기 오류: {str(e)}")
            print()
    else:
        print("❌ 추출 결과 파일이 없습니다")
    
    # 기타 데이터 파일 확인
    other_files = [f for f in data_dir.iterdir() if f.is_file() and not f.name.startswith('hvdc_whatsapp_extraction_')]
    if other_files:
        print(f"📁 기타 데이터 파일: {len(other_files)}개")
        for file in other_files:
            size = file.stat().st_size
            print(f"   📄 {file.name} ({size} bytes)")

def check_process_status():
    """프로세스 상태 확인"""
    print("🔄 프로세스 상태 확인")
    print("=" * 40)
    
    try:
        import psutil
        
        # Python 프로세스 확인
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'whatsapp' in cmdline.lower() or 'hvdc' in cmdline.lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline,
                            'memory': proc.info['memory_info'].rss / 1024 / 1024  # MB
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if python_processes:
            print(f"✅ WhatsApp 관련 Python 프로세스: {len(python_processes)}개")
            for proc in python_processes:
                print(f"   🔧 PID: {proc['pid']}")
                print(f"      📝 명령: {proc['cmdline'][:100]}...")
                print(f"      💾 메모리: {proc['memory']:.1f} MB")
        else:
            print("❌ WhatsApp 관련 Python 프로세스가 실행 중이지 않습니다")
        
        # 브라우저 프로세스 확인
        browser_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if any(browser in proc.info['name'].lower() for browser in ['chrome', 'chromium', 'firefox']):
                    browser_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if browser_processes:
            print(f"\n🌐 브라우저 프로세스: {len(browser_processes)}개")
            for proc in browser_processes:
                print(f"   🌐 {proc['name']} (PID: {proc['pid']})")
        else:
            print("\n❌ 브라우저 프로세스가 실행 중이지 않습니다")
            
    except ImportError:
        print("⚠️ psutil 모듈이 설치되지 않았습니다. 프로세스 정보를 확인할 수 없습니다.")
    except Exception as e:
        print(f"❌ 프로세스 확인 중 오류: {str(e)}")

def check_system_status():
    """시스템 전체 상태 확인"""
    print("🤖 MACHO-GPT v3.4-mini WhatsApp RPA 상태 모니터링")
    print("=" * 60)
    print(f"📅 확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 로그 파일 확인
    check_log_files()
    
    # 2. 데이터 파일 확인
    check_data_files()
    
    # 3. 프로세스 상태 확인
    check_process_status()
    
    print("\n" + "=" * 60)
    print("📊 상태 요약")
    print("=" * 60)
    
    # 상태 요약
    log_count = len([f for f in Path("logs").glob("*.log") if f.stat().st_size > 0])
    data_count = len([f for f in Path("data").glob("*.json")])
    
    print(f"📝 활성 로그 파일: {log_count}개")
    print(f"📊 데이터 파일: {data_count}개")
    
    # 권장 사항
    print("\n💡 권장 사항:")
    if log_count == 0:
        print("   - 로그 파일이 없습니다. 추출 프로세스를 시작하세요.")
    if data_count == 0:
        print("   - 추출 결과 파일이 없습니다. WhatsApp RPA를 실행하세요.")
    else:
        print("   - 추출 결과가 있습니다. AI 요약을 실행하세요.")
    
    print("\n🔧 추천 명령어:")
    print("   - python whatsapp_rpa_hvdc_extract.py (추출 실행)")
    print("   - python whatsapp_rpa_auto_extract.py --status (상태 확인)")
    print("   - python run_app.py (대시보드 실행)")

if __name__ == "__main__":
    check_system_status() 