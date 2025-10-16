#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini WhatsApp RPA 자동 추출 실행 스크립트
----------------------------------------------------
Samsung C&T Logistics · HVDC Project

기능:
- WhatsApp Web 자동 메시지 추출
- AI 요약 처리
- 데이터 저장 및 관리
- 실시간 상태 모니터링

실행 방법:
python whatsapp_rpa_auto_extract.py --chat "MR.CHA 전용"
python whatsapp_rpa_auto_extract.py --auto
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

# MACHO-GPT 모듈 import
try:
    from macho_gpt.rpa.logi_rpa_whatsapp_241219 import WhatsAppRPAExtractor
    from macho_gpt.core.role_config import RoleConfigManager
except ImportError as e:
    print(f"❌ MACHO-GPT 모듈 import 오류: {e}")
    print("💡 해결 방법: pip install -r requirements.txt")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/whatsapp_rpa.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatsAppRPAAutoExtractor:
    """WhatsApp RPA 자동 추출 관리자"""
    
    def __init__(self):
        self.role_config = RoleConfigManager()
        self.extractor = WhatsAppRPAExtractor(mode="LATTICE")
        
        # 기본 채팅 목록
        self.default_chats = [
            "MR.CHA 전용",
            "HVDC Project",
            "Samsung C&T Team",
            "물류 업무",
            "Emergency Response"
        ]
        
        logger.info("✅ WhatsApp RPA 자동 추출기 초기화 완료")
    
    async def extract_single_chat(self, chat_title: str) -> dict:
        """단일 채팅방 추출"""
        logger.info(f"🔄 단일 채팅방 추출 시작: {chat_title}")
        
        try:
            result = await self.extractor.extract_chat_messages(chat_title)
            
            if result['status'] == 'SUCCESS':
                logger.info(f"✅ 추출 성공: {chat_title}")
                logger.info(f"📊 메시지 수: {result['message_count']}")
                logger.info(f"🎯 신뢰도: {result['confidence']:.2f}")
            else:
                logger.error(f"❌ 추출 실패: {chat_title}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 추출 중 오류 발생: {str(e)}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'chat_title': chat_title,
                'extraction_time': datetime.now().isoformat()
            }
    
    async def extract_all_chats(self) -> list:
        """모든 기본 채팅방 추출"""
        logger.info("🔄 전체 채팅방 자동 추출 시작")
        
        results = []
        for chat_title in self.default_chats:
            logger.info(f"📱 채팅방 처리 중: {chat_title}")
            result = await self.extract_single_chat(chat_title)
            results.append(result)
            
            # 채팅방 간 대기 (서버 부하 방지)
            await asyncio.sleep(5)
        
        # 결과 요약
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        total_count = len(results)
        
        logger.info(f"📊 전체 추출 완료: {success_count}/{total_count} 성공")
        
        return results
    
    def get_status(self) -> dict:
        """현재 상태 확인"""
        return {
            'extractor_status': self.extractor.get_status(),
            'role_config': self.role_config.get_role_description(),
            'default_chats': self.default_chats,
            'timestamp': datetime.now().isoformat()
        }

async def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='MACHO-GPT WhatsApp RPA 자동 추출')
    parser.add_argument('--chat', type=str, help='추출할 채팅방 제목')
    parser.add_argument('--auto', action='store_true', help='모든 기본 채팅방 자동 추출')
    parser.add_argument('--status', action='store_true', help='현재 상태 확인')
    parser.add_argument('--list', action='store_true', help='기본 채팅방 목록 표시')
    
    args = parser.parse_args()
    
    # MACHO-GPT 역할 설정 적용
    role_manager = RoleConfigManager()
    system_prompt = role_manager.get_enhanced_system_prompt(
        "WhatsApp RPA 자동 추출 작업을 수행합니다.",
        mode="LATTICE"
    )
    
    print("🤖 MACHO-GPT v3.4-mini WhatsApp RPA 자동 추출")
    print("=" * 50)
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 모드: LATTICE (OCR 및 자동화)")
    print(f"🏢 프로젝트: Samsung C&T Logistics · HVDC")
    print("=" * 50)
    
    extractor = WhatsAppRPAAutoExtractor()
    
    try:
        if args.status:
            # 상태 확인
            status = extractor.get_status()
            print("\n📊 현재 상태:")
            print(f"  - 추출기 상태: {status['extractor_status']}")
            print(f"  - 역할 설정: {status['role_config']}")
            print(f"  - 기본 채팅방: {len(status['default_chats'])}개")
            
        elif args.list:
            # 기본 채팅방 목록
            print("\n📱 기본 채팅방 목록:")
            for i, chat in enumerate(extractor.default_chats, 1):
                print(f"  {i}. {chat}")
                
        elif args.chat:
            # 단일 채팅방 추출
            print(f"\n🔄 채팅방 추출 시작: {args.chat}")
            result = await extractor.extract_single_chat(args.chat)
            
            if result['status'] == 'SUCCESS':
                print(f"✅ 추출 성공!")
                print(f"📊 메시지 수: {result['message_count']}")
                print(f"🎯 신뢰도: {result['confidence']:.2f}")
                print(f"⏰ 추출 시간: {result['extraction_time']}")
            else:
                print(f"❌ 추출 실패: {result.get('error', 'Unknown error')}")
                
        elif args.auto:
            # 전체 자동 추출
            print("\n🔄 전체 채팅방 자동 추출 시작...")
            results = await extractor.extract_all_chats()
            
            print("\n📊 추출 결과 요약:")
            for result in results:
                status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
                print(f"  {status_icon} {result['chat_title']}: {result['status']}")
                if result['status'] == 'SUCCESS':
                    print(f"     📊 메시지: {result['message_count']}개, 신뢰도: {result['confidence']:.2f}")
                    
        else:
            # 기본 실행 (MR.CHA 전용)
            print("\n🔄 기본 채팅방 추출 시작: MR.CHA 전용")
            result = await extractor.extract_single_chat("MR.CHA 전용")
            
            if result['status'] == 'SUCCESS':
                print(f"✅ 추출 성공!")
                print(f"📊 메시지 수: {result['message_count']}")
                print(f"🎯 신뢰도: {result['confidence']:.2f}")
            else:
                print(f"❌ 추출 실패: {result.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"❌ 실행 중 오류 발생: {str(e)}")
        print(f"❌ 오류 발생: {str(e)}")
        print("💡 해결 방법: 로그 파일을 확인하세요 (logs/whatsapp_rpa.log)")
    
    print("\n🎉 MACHO-GPT WhatsApp RPA 자동 추출 완료")

if __name__ == "__main__":
    asyncio.run(main()) 