#!/usr/bin/env python3
"""
WhatsApp Web.js Python-Node.js 브릿지
MACHO-GPT v3.5-optimal WhatsApp Web.js 통합

이 모듈은 Python과 Node.js 간의 브릿지 역할을 하며,
whatsapp-web.js 스크래퍼를 Python에서 호출할 수 있게 합니다.
"""

import subprocess
import json
import logging
import asyncio
import shutil
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class WhatsAppWebJSBridge:
    """WhatsApp Web.js Python-Node.js 브릿지 클래스"""
    
    def __init__(self, script_dir: str = "setup/whatsapp_webjs"):
        """
        브릿지 초기화
        
        Args:
            script_dir: Node.js 스크립트 디렉토리 경로
        """
        self.script_dir = Path(script_dir)
        self.node_script = self.script_dir / "whatsapp_webjs_scraper.js"
        self.package_json = self.script_dir / "package.json"
        self.node_modules = self.script_dir / "node_modules"
        
        # 로깅 설정
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def check_nodejs_available(self) -> bool:
        """
        Node.js 환경 확인
        
        Returns:
            bool: Node.js 사용 가능 여부
        """
        try:
            # Node.js 버전 확인
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Node.js 버전: {version}")
                
                # 버전 파싱 (v14.0.0 형식)
                major_version = int(version[1:].split('.')[0])
                if major_version >= 14:
                    return True
                else:
                    self.logger.error(f"Node.js 14.0.0 이상이 필요합니다. 현재: {version}")
                    return False
            else:
                self.logger.error("Node.js가 설치되지 않았습니다.")
                return False
                
        except FileNotFoundError:
            self.logger.error("Node.js를 찾을 수 없습니다. PATH에 Node.js가 추가되었는지 확인하세요.")
            return False
        except Exception as e:
            self.logger.error(f"Node.js 확인 중 오류 발생: {e}")
            return False
    
    async def check_dependencies_installed(self) -> bool:
        """
        npm 의존성 설치 확인
        
        Returns:
            bool: 의존성 설치 여부
        """
        if not self.node_modules.exists():
            self.logger.warning("node_modules 디렉토리가 없습니다.")
            return False
            
        # 필수 패키지 확인
        required_packages = ['whatsapp-web.js', 'qrcode-terminal']
        missing_packages = []
        
        for package in required_packages:
            package_path = self.node_modules / package
            if not package_path.exists():
                missing_packages.append(package)
        
        if missing_packages:
            self.logger.warning(f"누락된 패키지: {missing_packages}")
            return False
            
        return True
    
    async def install_dependencies(self) -> bool:
        """
        npm 의존성 설치
        
        Returns:
            bool: 설치 성공 여부
        """
        try:
            self.logger.info("npm 의존성 설치 중...")
            
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(self.script_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            if result.returncode == 0:
                self.logger.info("npm 의존성 설치 완료")
                return True
            else:
                self.logger.error(f"npm 설치 실패: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"npm 설치 중 오류 발생: {e}")
            return False
    
    async def scrape_group(self, group_name: str, max_messages: int = 50, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        그룹 스크래핑 실행
        
        Args:
            group_name: 스크래핑할 그룹 이름
            max_messages: 최대 메시지 수
            output_file: 출력 파일 경로 (선택적)
            
        Returns:
            Dict: 스크래핑 결과
        """
        try:
            # Node.js 환경 확인
            if not await self.check_nodejs_available():
                return {
                    "status": "FAIL",
                    "error": "Node.js 환경이 설정되지 않았습니다.",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 의존성 확인 및 설치
            if not await self.check_dependencies_installed():
                self.logger.info("의존성 설치가 필요합니다. 자동 설치를 시도합니다...")
                if not await self.install_dependencies():
                    return {
                        "status": "FAIL",
                        "error": "npm 의존성 설치에 실패했습니다.",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # 스크립트 실행
            cmd = ["node", str(self.node_script), group_name, str(max_messages)]
            if output_file:
                cmd.append(output_file)
            
            self.logger.info(f"Node.js 스크립트 실행: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=str(self.script_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            if result.returncode == 0:
                try:
                    # JSON 파싱
                    data = json.loads(result.stdout)
                    data["bridge_info"] = {
                        "executed_at": datetime.now().isoformat(),
                        "node_version": await self._get_node_version(),
                        "script_path": str(self.node_script)
                    }
                    return data
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON 파싱 오류: {e}")
                    return {
                        "status": "FAIL",
                        "error": f"JSON 파싱 오류: {e}",
                        "raw_output": result.stdout,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                self.logger.error(f"Node.js 스크립트 실행 실패: {result.stderr}")
                return {
                    "status": "FAIL",
                    "error": result.stderr,
                    "timestamp": datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("Node.js 스크립트 실행 시간 초과")
            return {
                "status": "FAIL",
                "error": "스크립트 실행 시간 초과 (5분)",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"스크래핑 중 오류 발생: {e}")
            return {
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_node_version(self) -> str:
        """Node.js 버전 가져오기"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    async def get_available_groups(self) -> List[Dict[str, Any]]:
        """
        사용 가능한 그룹 목록 가져오기 (미구현)
        
        Returns:
            List[Dict]: 그룹 목록
        """
        # TODO: Node.js 스크립트를 통해 그룹 목록 가져오기
        return []
    
    async def cleanup_session(self) -> bool:
        """
        인증 세션 정리
        
        Returns:
            bool: 정리 성공 여부
        """
        try:
            # .wwebjs_auth 디렉토리 삭제
            auth_dir = self.script_dir / ".wwebjs_auth"
            if auth_dir.exists():
                shutil.rmtree(auth_dir)
                self.logger.info("인증 세션이 정리되었습니다.")
                return True
            return True
        except Exception as e:
            self.logger.error(f"세션 정리 중 오류 발생: {e}")
            return False


# 편의 함수들
async def scrape_whatsapp_group(group_name: str, max_messages: int = 50, output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    WhatsApp 그룹 스크래핑 편의 함수
    
    Args:
        group_name: 그룹 이름
        max_messages: 최대 메시지 수
        output_file: 출력 파일 경로
        
    Returns:
        Dict: 스크래핑 결과
    """
    bridge = WhatsAppWebJSBridge()
    return await bridge.scrape_group(group_name, max_messages, output_file)


async def check_webjs_environment() -> Dict[str, Any]:
    """
    Web.js 환경 상태 확인
    
    Returns:
        Dict: 환경 상태 정보
    """
    bridge = WhatsAppWebJSBridge()
    
    return {
        "nodejs_available": await bridge.check_nodejs_available(),
        "dependencies_installed": await bridge.check_dependencies_installed(),
        "script_exists": bridge.node_script.exists(),
        "package_json_exists": bridge.package_json.exists(),
        "timestamp": datetime.now().isoformat()
    }


# CLI 테스트용
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("사용법: python whatsapp_webjs_bridge.py <group_name> [max_messages]")
        sys.exit(1)
    
    group_name = sys.argv[1]
    max_messages = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    async def main():
        result = await scrape_whatsapp_group(group_name, max_messages)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(main())
