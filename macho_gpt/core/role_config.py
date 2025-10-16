"""
MACHO-GPT v3.4-mini Role Configuration
------------------------------------------
Samsung C&T Logistics · HVDC Project
파일명: role_config.py

기능:
- 시스템 프롬프트에 역할 정의 자동 주입
- 환경변수 기반 역할 설정 지원
- 일관된 AI 응답 컨텍스트 제공
- 다양한 모드 및 환경 지원

Mode: 모든 모드 지원 (PRIME|ORACLE|ZERO|LATTICE|RHYTHM|COST-GUARD)
Confidence: ≥0.90 required for all operations
"""

from typing import Dict, Any, Optional
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

# 기본 역할 정의
DEFAULT_ROLE_DESCRIPTION = """
🛠️ Samsung C&T Logistics – Middle-East HVDC Mega-Project Copilot (영·한)
• Position: Logistics · Customs · Contract Lead (PMT Tier-1)
• Scope: Import/Export clearance, ADNOC-DSV port ops, storage & inland haulage,
         contract negotiation, cost simulation, regulatory diff-watch, KPI dashboard
• Mission: T+0 decision support, document automation, risk mitigation,
           25% productivity uplift across 10 modules
• Key APIs / Docs: eDAS, UAE Customs, AD Ports, MOEI, FANR, HVDC Mapping System
• Mode: PRIME|ORACLE|ZERO|LATTICE|RHYTHM|COST-GUARD
• Confidence: ≥0.90 required for all operations
• Project: Samsung C&T · ADNOC·DSV Partnership · HVDC Infrastructure
"""

# 환경별 역할 설정
ENVIRONMENT_ROLES = {
    "development": "🧪 [DEV] Samsung C&T Logistics - HVDC Project Developer",
    "staging": "🧪 [STG] Samsung C&T Logistics - HVDC Project Tester", 
    "production": "🛠️ Samsung C&T Logistics – Middle-East HVDC Mega-Project Copilot",
    "demo": "🎯 [DEMO] Samsung C&T Logistics - HVDC Project Showcase"
}

class RoleConfigManager:
    """
    MACHO-GPT v3.4-mini 역할 설정 관리자
    
    Features:
    - 환경변수 기반 역할 설정
    - 동적 프롬프트 생성
    - 모드별 최적화
    - 다국어 지원 (한/영)
    """
    
    def __init__(self, environment: str = "production"):
        """
        역할 설정 관리자 초기화
        
        Args:
            environment: 실행 환경 (development|staging|production|demo)
        """
        self.environment = environment
        self.role_description = self._load_role_description()
        
        logger.info(f"✅ Role Config 초기화 완료 - Environment: {environment}")
    
    def _load_role_description(self) -> str:
        """
        역할 설명 로드 (우선순위: 환경변수 > 환경별 설정 > 기본값)
        
        Returns:
            str: 역할 설명 텍스트
        """
        # 1. 환경변수에서 먼저 확인
        env_role = os.getenv('MACHO_GPT_ROLE_DESCRIPTION')
        if env_role:
            logger.info("🔧 환경변수에서 역할 설정 로드")
            return env_role
        
        # 2. 환경별 설정 확인
        env_specific = ENVIRONMENT_ROLES.get(self.environment)
        if env_specific:
            logger.info(f"🔧 {self.environment} 환경 역할 설정 사용")
            return env_specific
        
        # 3. 기본값 반환
        logger.info("🔧 기본 역할 설정 사용")
        return DEFAULT_ROLE_DESCRIPTION
    
    def get_role_description(self) -> str:
        """
        현재 역할 설명 반환
        
        Returns:
            str: 역할 설명 텍스트
        """
        return self.role_description
    
    def get_enhanced_system_prompt(self, base_prompt: str = "", mode: str = "PRIME") -> str:
        """
        역할 정의가 포함된 향상된 시스템 프롬프트 생성
        
        Args:
            base_prompt: 기본 프롬프트 텍스트
            mode: 현재 동작 모드
            
        Returns:
            str: 향상된 시스템 프롬프트
        """
        # 모드별 추가 지침
        mode_instructions = {
            "PRIME": "기본 모드로 신뢰성 있는 답변을 제공하세요.",
            "ORACLE": "실시간 데이터 기반으로 정확한 분석을 제공하세요.",
            "ZERO": "안전 모드로 기본적인 기능만 사용하세요.",
            "LATTICE": "고급 OCR 및 문서 분석 기능을 활용하세요.",
            "RHYTHM": "실시간 KPI 모니터링 및 알림 기능을 중심으로 하세요.",
            "COST-GUARD": "비용 최적화 및 예산 관리에 집중하세요."
        }
        
        mode_instruction = mode_instructions.get(mode, "표준 프로세스를 따르세요.")
        
        enhanced_prompt = f"""
{self.role_description}

=== CURRENT MODE: {mode} ===
{mode_instruction}

=== TASK CONTEXT ===
{base_prompt}

=== MACHO-GPT v3.4-mini GUIDELINES ===
당신은 MACHO-GPT v3.4-mini입니다. Samsung C&T Logistics의 HVDC 프로젝트를 담당하며, 
상기 역할 정의에 따라 전문적이고 정확한 답변을 제공해야 합니다.

- 항상 신뢰도 ≥0.90을 유지하세요
- 물류/통관/계약 전문 지식을 활용하세요
- 필요시 적절한 /cmd 명령어를 추천하세요
- 한국어와 영어를 적절히 혼용하세요
- HVDC 프로젝트 컨텍스트를 고려하세요
- ADNOC·DSV 파트너십 관계를 염두에 두세요

응답 형식:
1. 핵심 답변 (3-5줄 요약)
2. 상세 설명 (필요시)
3. 추천 명령어 (🔧 **추천 명령어:** 형식)
"""
        
        return enhanced_prompt.strip()
    
    def create_system_message(self, content: str = "", mode: str = "PRIME") -> Dict[str, str]:
        """
        OpenAI 형식의 시스템 메시지 딕셔너리 생성
        
        Args:
            content: 추가 시스템 프롬프트 내용
            mode: 현재 동작 모드
            
        Returns:
            dict: OpenAI 형식의 시스템 메시지
        """
        return {
            "role": "system",
            "content": self.get_enhanced_system_prompt(content, mode)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        역할 설정 상태 정보 반환
        
        Returns:
            dict: 상태 정보
        """
        # 사용 가능한 모드 리스트 (MACHO-GPT v3.4-mini 표준)
        available_modes = ["PRIME", "ORACLE", "ZERO", "LATTICE", "RHYTHM", "COST-GUARD"]
        
        return {
            "environment": self.environment,
            "role_source": "env_var" if os.getenv('MACHO_GPT_ROLE_DESCRIPTION') else "default",
            "role_length": len(self.role_description),
            "available_modes": available_modes,
            "version": "3.4-mini",
            "status": "ready"
        }
    
    def update_role(self, new_role: str) -> bool:
        """
        역할 설정 업데이트
        
        Args:
            new_role: 새로운 역할 설명
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            self.role_description = new_role
            logger.info("✅ 역할 설정 업데이트 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 역할 설정 업데이트 실패: {str(e)}")
            return False

# 전역 인스턴스 생성 (환경 자동 감지)
def get_environment() -> str:
    """현재 환경 자동 감지"""
    env = os.getenv('ENVIRONMENT', os.getenv('ENV', 'production')).lower()
    if env in ENVIRONMENT_ROLES:
        return env
    return 'production'

# 전역 역할 관리자 인스턴스
_role_manager = RoleConfigManager(environment=get_environment())

# 편의 함수들 (하위 호환성)
def get_role_description() -> str:
    """
    역할 설명 반환 (전역 인스턴스)
    
    Returns:
        str: 역할 설명 텍스트
    """
    return _role_manager.get_role_description()

def get_enhanced_system_prompt(base_prompt: str = "", mode: str = "PRIME") -> str:
    """
    향상된 시스템 프롬프트 생성 (전역 인스턴스)
    
    Args:
        base_prompt: 기본 프롬프트 텍스트
        mode: 현재 동작 모드
        
    Returns:
        str: 향상된 시스템 프롬프트
    """
    return _role_manager.get_enhanced_system_prompt(base_prompt, mode)

def create_system_message(content: str = "", mode: str = "PRIME") -> Dict[str, str]:
    """
    시스템 메시지 생성 (전역 인스턴스)
    
    Args:
        content: 추가 시스템 프롬프트 내용
        mode: 현재 동작 모드
        
    Returns:
        dict: OpenAI 형식의 시스템 메시지
    """
    return _role_manager.create_system_message(content, mode)

def get_role_status() -> Dict[str, Any]:
    """
    역할 설정 상태 반환 (전역 인스턴스)
    
    Returns:
        dict: 상태 정보
    """
    return _role_manager.get_status()

# 전역 상수 (하위 호환성)
ROLE_DESCRIPTION = get_role_description()
"""전역 역할 설명 상수"""

# 내보내기
__all__ = [
    "RoleConfigManager",
    "get_role_description", 
    "get_enhanced_system_prompt",
    "create_system_message",
    "get_role_status",
    "ROLE_DESCRIPTION",
    "DEFAULT_ROLE_DESCRIPTION",
    "ENVIRONMENT_ROLES"
] 