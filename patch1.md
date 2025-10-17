diff --git a/CHANGELOG.md b/CHANGELOG.md
new file mode 100644
index 0000000000000000000000000000000000000000..1e2c838b0ee016d6b220f0e5423394afe8b23829
--- /dev/null
+++ b/CHANGELOG.md
@@ -0,0 +1,19 @@
+# Changelog
+
+## [Unreleased]
+
+### Added
+- Added whatsapp-web.js bridge with asyncio support and multi-group Node scraper output alignment.
+- Introduced CLI backend selection and failover handling in `run_optimal_scraper.py`.
+
+### Changed
+- Normalized whatsapp-web.js scraper output to structured JSON for easier parsing.
+- Extended configuration dataclasses with webjs backend settings and max message controls.
+
+### Docs
+- Updated README and integration guides for dual backend workflows and npm usage.
+- Documented whatsapp-web.js setup commands and new CLI flags.
+
+### Tests
+- Added unit coverage for whatsapp-web.js bridge success and failure scenarios.
+- Updated multi-group configuration tests for new dataclass fields.
diff --git a/README.md b/README.md
index 29720a122ce8cc4d5d256ee20a93ff44adeed105..c250e22a276f25686ab282d9e3f21a9acf119adf 100644
--- a/README.md
+++ b/README.md
@@ -196,64 +196,68 @@ wa_wa/
 │       └── whatsapp_webjs/             # whatsapp-web.js 통합 (개발 중)
 │
 ├── 📊 **데이터 및 로그**
 │   ├── data/                           # 스크래핑 데이터
 │   │   └── hvdc_whatsapp_extraction_20250725_005855.json
 │   ├── logs/                           # 로그 파일
 │   └── browser_data/                   # 브라우저 세션 데이터
 │
 ├── 📚 **문서화**
 │   └── docs/
 │       ├── OPTIMAL_SYSTEM_FINAL.md
 │       ├── MIGRATION_GUIDE.md
 │       ├── QUICK_START_WORKING_SYSTEM.md
 │       ├── TROUBLESHOOTING.md
 │       └── IMPLEMENTATION_COMPLETE.md
 │
 ├── 🧪 **테스트**
 │   └── tests/                          # 단위 테스트
 │
 └── 📦 **아카이브**
     └── _archive/                       # 백업 및 이전 버전
         ├── deprecated/                 # 사용 중단된 스크립트
         └── success/                    # 성공 데이터
 ```

-## 🔄 whatsapp-web.js 통합 (개발 중)
-
-### 현재 상태
-- Phase 1: 환경 설정 완료 ✅
-- Phase 2: Node.js 스크래퍼 구현 중 🔄
-- Phase 3: Python-Node.js 브릿지 구현 예정
-- Phase 4: 통합 및 설정 예정
-- Phase 5: 문서화 예정
-- Phase 6: 테스트 및 검증 예정
-
-### 예상 기능
-- Playwright 실패 시 whatsapp-web.js로 자동 전환
-- 사용자가 백엔드 선택 가능 (playwright/webjs/auto)
-- Node.js 기반 대안 스크래핑 방법 제공
+## 🔄 whatsapp-web.js 통합
+
+- ✅ Playwright ↔ whatsapp-web.js 듀얼 백엔드 지원
+- ✅ `--backend {playwright,webjs,auto}` CLI 플래그
+- ✅ `--no-webjs-fallback` 옵션으로 전환 제어
+- ✅ Node 스크래퍼 멀티 그룹·ISO 타임스탬프 출력
+- ✅ Python 브릿지에서 자동 환경 검사 및 JSON 파싱
+
+```bash
+# webjs 백엔드 직접 실행
+python run_optimal_scraper.py --backend webjs
+
+# 자동 전환 모드 (Playwright 실패 시 webjs로 재시도)
+python run_optimal_scraper.py --backend auto
+
+# 전환 비활성화
+python run_optimal_scraper.py --backend playwright --no-webjs-fallback
+```

 ## 🛠️ 개발 환경

 ### 필수 요구사항
 - Python 3.8+
 - Node.js 14+ (whatsapp-web.js 통합용)
 - Chrome/Chromium 브라우저
 - Windows 10/11 (테스트 환경)

 ### 권장 환경
 - Python 3.11+
 - Node.js 18+
 - 8GB+ RAM
 - SSD 저장소

 ## 📈 로드맵

 ### v3.5-optimal (현재)
 - ✅ 검증된 성공 시스템 통합
 - ✅ Enhancement 모듈 구현
 - ✅ 개발 도구 및 백업 시스템
 - ✅ 완전한 문서화

 ### v3.6-hybrid (계획)
 - 🔄 whatsapp-web.js 완전 통합
diff --git a/docs/WHATSAPP_WEBJS_INTEGRATION.md b/docs/WHATSAPP_WEBJS_INTEGRATION.md
index 0ab1526c42a58beb4d313ac5a39eee7fbb5117f0..9913436999f1499116c7276dff0ffc9979f6684c 100644
--- a/docs/WHATSAPP_WEBJS_INTEGRATION.md
+++ b/docs/WHATSAPP_WEBJS_INTEGRATION.md
@@ -36,59 +36,62 @@ Tier 4: Setup & Backup (확장)
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
+
+# 쉼표로 복수 그룹 지정
+python run_optimal_scraper.py --backend webjs --groups "HVDC 물류팀" "MR.CHA 전용"
 ```

 #### 3. 자동 전환 (Auto)
 ```bash
 # Playwright 우선, 실패 시 whatsapp-web.js로 전환
 python run_optimal_scraper.py --backend auto

-# 자동 전환 활성화
-python run_optimal_scraper.py --backend auto --webjs-fallback
+# 전환 비활성화 옵션
+python run_optimal_scraper.py --backend auto --no-webjs-fallback
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
@@ -124,51 +127,51 @@ scraper_settings:
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
-npm install
+npm ci
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

diff --git a/macho_gpt/async_scraper/group_config.py b/macho_gpt/async_scraper/group_config.py
index b7207061c5cf7f4a23033c69111bf016f95c0869..19832514e48565e69fd3d6d0dc3f4f020ffd2f64 100644
--- a/macho_gpt/async_scraper/group_config.py
+++ b/macho_gpt/async_scraper/group_config.py
@@ -1,167 +1,244 @@
-"""
-그룹 설정 관리 모듈
-YAML 기반 멀티 그룹 설정 로드 및 검증
-"""
+from __future__ import annotations

 from dataclasses import dataclass, field
-from typing import List, Optional
 from pathlib import Path
+from typing import List
+
 import yaml


+@dataclass
+class WebJSSettings:
+    """whatsapp-web.js 백엔드 설정입니다. (KR)
+    whatsapp-web.js backend settings container. (EN)
+
+    Args:
+        script_dir (str): Node.js 스크립트 디렉터리입니다.
+        timeout (int): 서브프로세스 실행 타임아웃(초)입니다.
+        auto_install_deps (bool): 의존성 자동 설치 여부입니다.
+    """
+
+    script_dir: str = "setup/whatsapp_webjs"
+    timeout: int = 300
+    auto_install_deps: bool = True
+
+    def __post_init__(self) -> None:
+        """설정 값을 검증합니다. (KR)
+        Validate field values. (EN)
+        """
+
+        if self.timeout <= 0:
+            raise ValueError("timeout 값은 0보다 커야 합니다")
+        if not self.script_dir:
+            raise ValueError("script_dir은 비워 둘 수 없습니다")
+
+
 @dataclass
 class GroupConfig:
-    """개별 WhatsApp 그룹 설정"""
+    """개별 WhatsApp 그룹 설정입니다. (KR)
+    Configuration for a single WhatsApp group. (EN)
+
+    Args:
+        name (str): 그룹 이름입니다.
+        save_file (str): 메시지를 저장할 파일 경로입니다.
+        scrape_interval (int): 스크래핑 주기(초)입니다.
+        priority (str): 작업 우선순위입니다.
+        max_messages (int): 그룹당 메시지 수집 상한입니다.
+    """

     name: str
     save_file: str
     scrape_interval: int = 60
     priority: str = "MEDIUM"
+    max_messages: int = 50
+
+    def __post_init__(self) -> None:
+        """설정의 유효성을 검사합니다. (KR)
+        Validate group configuration fields. (EN)
+        """

-    def __post_init__(self):
-        """설정 유효성 검증"""
         if self.scrape_interval < 10:
             raise ValueError(
-                f"scrape_interval은 최소 10초 이상이어야 합니다: {self.scrape_interval}"
+                "scrape_interval은 최소 10초 이상이어야 합니다: "
+                f"{self.scrape_interval}"
             )
-
         if self.priority not in ["HIGH", "MEDIUM", "LOW"]:
             raise ValueError(f"유효하지 않은 priority: {self.priority}")
-
+        if self.max_messages <= 0:
+            raise ValueError("max_messages는 0보다 커야 합니다")
         if not self.name or not self.save_file:
             raise ValueError("name과 save_file은 필수입니다")


 @dataclass
 class ScraperSettings:
-    """스크래퍼 전역 설정"""
+    """스크래퍼 전역 설정입니다. (KR)
+    Global scraper configuration. (EN)
+
+    Args:
+        chrome_data_dir (str): Chrome 사용자 데이터 디렉터리입니다.
+        headless (bool): 헤드리스 모드 사용 여부입니다.
+        timeout (int): Playwright 타임아웃(ms)입니다.
+        max_parallel_groups (int): 병렬 처리 가능한 최대 그룹 수입니다.
+        backend (str): 사용 중인 백엔드 식별자입니다.
+        webjs_fallback (bool): Playwright 실패 시 webjs로 전환 여부입니다.
+        webjs_settings (WebJSSettings): webjs 관련 설정입니다.
+    """

     chrome_data_dir: str = "chrome-data"
     headless: bool = True
     timeout: int = 30000
     max_parallel_groups: int = 5
+    backend: str = "playwright"
+    webjs_fallback: bool = True
+    webjs_settings: WebJSSettings = field(default_factory=WebJSSettings)
+
+    def __post_init__(self) -> None:
+        """설정 값을 검증합니다. (KR)
+        Validate scraper configuration fields. (EN)
+        """

-    def __post_init__(self):
-        """설정 유효성 검증"""
         if self.timeout < 5000:
             raise ValueError(f"timeout은 최소 5000ms 이상이어야 합니다: {self.timeout}")
-
         if self.max_parallel_groups < 1 or self.max_parallel_groups > 10:
             raise ValueError(
-                f"max_parallel_groups는 1~10 사이여야 합니다: {self.max_parallel_groups}"
+                "max_parallel_groups는 1~10 사이여야 합니다: "
+                f"{self.max_parallel_groups}"
+            )
+        if self.backend not in {"playwright", "webjs", "auto"}:
+            raise ValueError(
+                "backend는 playwright, webjs, auto 중 하나여야 합니다: "
+                f"{self.backend}"
             )


 @dataclass
 class AIIntegrationSettings:
-    """AI 통합 설정"""
+    """AI 통합 설정입니다. (KR)
+    AI integration configuration. (EN)
+
+    Args:
+        enabled (bool): AI 통합 활성화 여부입니다.
+        summarize_on_extraction (bool): 메시지 추출 시 요약 여부입니다.
+        confidence_threshold (float): 요약 신뢰도 임계값입니다.
+    """

     enabled: bool = True
     summarize_on_extraction: bool = True
     confidence_threshold: float = 0.90

-    def __post_init__(self):
-        """설정 유효성 검증"""
+    def __post_init__(self) -> None:
+        """설정 값을 검증합니다. (KR)
+        Validate AI integration settings. (EN)
+        """
+
         if not 0.0 <= self.confidence_threshold <= 1.0:
             raise ValueError(
-                f"confidence_threshold는 0.0~1.0 사이여야 합니다: {self.confidence_threshold}"
+                "confidence_threshold는 0.0~1.0 사이여야 합니다: "
+                f"{self.confidence_threshold}"
             )


 @dataclass
 class MultiGroupConfig:
-    """전체 멀티 그룹 설정"""
+    """멀티 그룹 스크래퍼 전체 설정입니다. (KR)
+    Top-level multi-group scraper configuration. (EN)
+
+    Args:
+        whatsapp_groups (List[GroupConfig]): 대상 그룹 설정 목록입니다.
+        scraper_settings (ScraperSettings): 공통 스크래퍼 설정입니다.
+        ai_integration (AIIntegrationSettings): AI 통합 설정입니다.
+    """

     whatsapp_groups: List[GroupConfig] = field(default_factory=list)
     scraper_settings: ScraperSettings = field(default_factory=ScraperSettings)
     ai_integration: AIIntegrationSettings = field(default_factory=AIIntegrationSettings)

     @staticmethod
     def load_from_yaml(config_path: str) -> "MultiGroupConfig":
+        """YAML 설정을 로드합니다. (KR)
+        Load configuration from a YAML file. (EN)
         """
-        YAML 파일에서 멀티 그룹 설정 로드
-
-        Args:
-            config_path: YAML 설정 파일 경로

-        Returns:
-            MultiGroupConfig: 로드된 설정 객체
-
-        Raises:
-            FileNotFoundError: 설정 파일이 없는 경우
-            yaml.YAMLError: YAML 파싱 오류
-            ValueError: 설정 검증 실패
-        """
         config_file = Path(config_path)
-
         if not config_file.exists():
             raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

-        with open(config_file, "r", encoding="utf-8") as f:
-            data = yaml.safe_load(f)
+        with open(config_file, "r", encoding="utf-8") as handle:
+            data = yaml.safe_load(handle)

         if not data:
             raise ValueError(f"빈 설정 파일입니다: {config_path}")

-        # WhatsApp 그룹 파싱
-        groups = []
+        groups: List[GroupConfig] = []
         for group_data in data.get("whatsapp_groups", []):
             group = GroupConfig(
                 name=group_data["name"],
                 save_file=group_data["save_file"],
                 scrape_interval=group_data.get("scrape_interval", 60),
                 priority=group_data.get("priority", "MEDIUM"),
+                max_messages=group_data.get("max_messages", 50),
             )
             groups.append(group)

         if not groups:
             raise ValueError("최소 1개 이상의 WhatsApp 그룹이 필요합니다")

-        # 스크래퍼 설정 파싱
         scraper_data = data.get("scraper_settings", {})
         scraper_settings = ScraperSettings(
             chrome_data_dir=scraper_data.get("chrome_data_dir", "chrome-data"),
             headless=scraper_data.get("headless", True),
             timeout=scraper_data.get("timeout", 30000),
             max_parallel_groups=scraper_data.get("max_parallel_groups", 5),
+            backend=scraper_data.get("backend", "playwright"),
+            webjs_fallback=scraper_data.get("webjs_fallback", True),
+            webjs_settings=WebJSSettings(
+                script_dir=scraper_data.get("webjs_settings", {}).get(
+                    "script_dir", "setup/whatsapp_webjs"
+                ),
+                timeout=scraper_data.get("webjs_settings", {}).get("timeout", 300),
+                auto_install_deps=scraper_data.get("webjs_settings", {}).get(
+                    "auto_install_deps", True
+                ),
+            ),
         )

-        # AI 통합 설정 파싱
         ai_data = data.get("ai_integration", {})
         ai_integration = AIIntegrationSettings(
             enabled=ai_data.get("enabled", True),
             summarize_on_extraction=ai_data.get("summarize_on_extraction", True),
             confidence_threshold=ai_data.get("confidence_threshold", 0.90),
         )

         return MultiGroupConfig(
             whatsapp_groups=groups,
             scraper_settings=scraper_settings,
             ai_integration=ai_integration,
         )

     def validate(self) -> bool:
-        """
-        전체 설정 유효성 검증
+        """설정 전체를 검증합니다. (KR)
+        Validate the entire configuration. (EN)

         Returns:
-            bool: 검증 성공 여부
+            bool: 검증 성공 여부입니다.
         """
-        # 그룹 이름 중복 체크
-        group_names = [g.name for g in self.whatsapp_groups]
+
+        group_names = [group.name for group in self.whatsapp_groups]
         if len(group_names) != len(set(group_names)):
             raise ValueError("중복된 그룹 이름이 있습니다")

-        # 저장 파일 중복 체크
-        save_files = [g.save_file for g in self.whatsapp_groups]
+        save_files = [group.save_file for group in self.whatsapp_groups]
         if len(save_files) != len(set(save_files)):
             raise ValueError("중복된 save_file 경로가 있습니다")

-        # 병렬 처리 수 제한 확인
         if len(self.whatsapp_groups) > self.scraper_settings.max_parallel_groups:
             raise ValueError(
-                f"그룹 수({len(self.whatsapp_groups)})가 "
-                f"max_parallel_groups({self.scraper_settings.max_parallel_groups})를 초과합니다"
+                "그룹 수("
+                f"{len(self.whatsapp_groups)}"
+                ")가 max_parallel_groups("
+                f"{self.scraper_settings.max_parallel_groups}"
+                ")를 초과합니다"
             )

         return True
diff --git a/run_optimal_scraper.py b/run_optimal_scraper.py
index c522ca50817002c76ba135da899642986f679489..42ac08deb25dbb4ab1b0ed24b85d375652dc7b8d 100644
--- a/run_optimal_scraper.py
+++ b/run_optimal_scraper.py
@@ -1,75 +1,87 @@
 #!/usr/bin/env python3
 """
 MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper CLI
 최적 조합: 검증된 성공 시스템 + Enhancement 통합

 Features:
 - Tier 1: 검증된 Core System (2025-07-25 성공 데이터 기반)
 - Tier 2: Enhancement Layer (로딩 안정성 + 스텔스 기능)
 - Tier 3: Development Tools (디버깅, 모니터링)
 - Tier 4: Setup & Backup (인증, 대안 방법)
 """

-import asyncio
-import sys
 import argparse
+import asyncio
+import json
 import logging
+import sys
 from pathlib import Path
-from datetime import datetime
-from typing import Dict, Any, Optional
+from typing import Any, Dict, List, Optional

 # 프로젝트 루트를 Python 경로에 추가
 sys.path.insert(0, str(Path(__file__).parent))

-from macho_gpt.async_scraper.group_config import MultiGroupConfig
-from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager
+from macho_gpt.async_scraper.group_config import (  # noqa: E402
+    GroupConfig,
+    MultiGroupConfig,
+    WebJSSettings,
+)
+from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager  # noqa: E402
+from setup.whatsapp_webjs.whatsapp_webjs_bridge import (  # noqa: E402
+    BridgeResult,
+    WhatsAppWebJSBridge,
+)

 # 로깅 설정
 logging.basicConfig(
     level=logging.INFO,
     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
     handlers=[
         logging.FileHandler("logs/optimal_scraper.log", encoding="utf-8"),
         logging.StreamHandler(),
     ],
 )

 logger = logging.getLogger(__name__)

+BACKEND_PLAYWRIGHT = "playwright"
+BACKEND_WEBJS = "webjs"
+BACKEND_AUTO = "auto"
+

 def print_banner():
     """배너 출력"""
     banner = """
 ================================================================================
-
-         MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper
-
-     Samsung C&T Logistics · HVDC Project · ADNOC·DSV Partnership
-
-                    최적 조합: 성공 시스템 + Enhancement
-
+
+         MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper
+
+     Samsung C&T Logistics · HVDC Project · ADNOC·DSV Partnership
+
+                    최적 조합: 성공 시스템 + Enhancement
+
 ================================================================================
     """
     print(banner)


 def print_usage():
     """사용법 출력"""
     usage = """
 MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper

 기본 사용법:
   python run_optimal_scraper.py

 Enhancement 활성화:
   python run_optimal_scraper.py --enhance-loading
   python run_optimal_scraper.py --enhance-stealth
   python run_optimal_scraper.py --enhance-all

 개발 도구:
   python tools/dom_analyzer.py
   python tools/quick_test.py
   python tools/status_monitor.py

 자세한 내용은 docs/OPTIMAL_SYSTEM_FINAL.md 참조
     """
@@ -95,204 +107,343 @@ async def run_development_tool(tool_name: str):
         else:
             print(f"알 수 없는 도구: {tool_name}")
             print("사용 가능한 도구: dom-analyzer, status-check, quick-test")
     except Exception as e:
         logger.error(f"개발 도구 실행 실패: {e}")


 async def run_setup_tool(setup_name: str):
     """설정 도구 실행"""
     try:
         if setup_name == "manual-auth":
             from setup.manual_auth import main

             await main()
         elif setup_name == "alternative":
             from setup.alternative_methods import main

             await main()
         else:
             print(f"알 수 없는 설정 도구: {setup_name}")
             print("사용 가능한 도구: manual-auth, alternative")
     except Exception as e:
         logger.error(f"설정 도구 실행 실패: {e}")


+def _log_backend_switch(from_backend: str, to_backend: str, reason: str) -> None:
+    """백엔드 전환을 로깅합니다. (KR)
+    Log backend switch details. (EN)
+    """
+
+    logger.warning(
+        "백엔드를 %s에서 %s로 전환합니다: %s", from_backend, to_backend, reason
+    )
+
+
+async def run_playwright_backend(
+    config: MultiGroupConfig, group_configs: List[GroupConfig]
+) -> List[Dict[str, Any]]:
+    """Playwright 백엔드를 실행합니다. (KR)
+    Execute the Playwright backend. (EN)
+    """
+
+    manager = MultiGroupManager(
+        group_configs=group_configs,
+        max_parallel_groups=config.scraper_settings.max_parallel_groups,
+        ai_integration=config.ai_integration.__dict__,
+    )
+    logger.info("Playwright 백엔드로 %d개 그룹을 스크래핑합니다.", len(group_configs))
+    return await manager.run_all_groups()
+
+
+async def run_webjs_backend(
+    group_configs: List[GroupConfig],
+    settings: WebJSSettings,
+    *,
+    max_messages: int,
+) -> List[Dict[str, Any]]:
+    """whatsapp-web.js 백엔드를 실행합니다. (KR)
+    Execute the whatsapp-web.js backend. (EN)
+    """
+
+    bridge = WhatsAppWebJSBridge(settings)
+    results: List[Dict[str, Any]] = []
+    for group_config in group_configs:
+        group_config.max_messages = max_messages
+        bridge_result: BridgeResult = await bridge.scrape_group(
+            group_config, max_messages=max_messages
+        )
+        if bridge_result.success and bridge_result.messages is not None:
+            save_path = Path(group_config.save_file)
+            save_path.parent.mkdir(parents=True, exist_ok=True)
+            with open(save_path, "w", encoding="utf-8") as handle:
+                json.dump(bridge_result.messages, handle, ensure_ascii=False, indent=2)
+            logger.info(
+                "webjs 백엔드가 %s 그룹 메시지 %d건을 저장했습니다.",
+                group_config.name,
+                bridge_result.messages_scraped,
+            )
+        else:
+            logger.error(
+                "webjs 백엔드에서 %s 그룹 스크래핑 실패: %s",
+                group_config.name,
+                bridge_result.error,
+            )
+        results.append(
+            {
+                "group_name": bridge_result.group_name,
+                "success": bridge_result.success,
+                "messages_scraped": bridge_result.messages_scraped,
+                "ai_summary": None,
+                "error": bridge_result.error,
+                "backend": BACKEND_WEBJS,
+            }
+        )
+    return results
+
+
 async def run_optimal_scraper(
     config_file: str,
     enhance_loading: bool = False,
     enhance_stealth: bool = False,
     dev_mode: bool = False,
-    groups: Optional[list] = None,
+    groups: Optional[List[str]] = None,
     max_messages: int = 50,
     timeout: int = 30000,
     headless: bool = True,
-):
-    """최적화된 스크래퍼 실행"""
+    backend: Optional[str] = None,
+    webjs_fallback: Optional[bool] = None,
+) -> List[Dict[str, Any]]:
+    """최적화된 스크래퍼를 실행합니다. (KR)
+    Run the optimal multi-group scraper. (EN)
+    """
+
     try:
         print_banner()
-
-        # 설정 로드
         config = MultiGroupConfig.load_from_yaml(config_file)

-        # Enhancement 설정 적용
         if enhance_loading:
             logger.info("로딩 안정성 개선 활성화")
-            # 로딩 최적화 설정 적용
-
         if enhance_stealth:
             logger.info("스텔스 기능 활성화")
-            # 스텔스 기능 설정 적용
-
         if dev_mode:
             logger.info("개발 모드 활성화")
-            # 디버그 모드 설정 적용

-        # 그룹 필터링
+        selected_groups = config.whatsapp_groups
         if groups:
-            config.whatsapp_groups = [
+            selected_groups = [
                 group for group in config.whatsapp_groups if group.name in groups
             ]
-            logger.info(f"선택된 그룹: {groups}")
+            logger.info("선택된 그룹: %s", groups)
+        if not selected_groups:
+            raise ValueError("스크래핑할 그룹이 없습니다")
+
+        for group_config in selected_groups:
+            group_config.max_messages = max_messages

-        # 스크래퍼 설정 업데이트
-        config.scraper_settings.max_messages = max_messages
         config.scraper_settings.timeout = timeout
         config.scraper_settings.headless = headless
+        config.scraper_settings.max_messages = max_messages

-        # 멀티 그룹 매니저 실행
-        manager = MultiGroupManager(
-            group_configs=config.whatsapp_groups,
-            max_parallel_groups=config.scraper_settings.max_parallel_groups,
-            ai_integration=config.ai_integration.__dict__,
+        configured_backend = backend or config.scraper_settings.backend
+        config.scraper_settings.backend = configured_backend
+        fallback_enabled = (
+            webjs_fallback
+            if webjs_fallback is not None
+            else config.scraper_settings.webjs_fallback
         )

-        logger.info("최적화된 멀티 그룹 스크래핑 시작")
-        results = await manager.run_all_groups()
+        if configured_backend == BACKEND_AUTO:
+            fallback_enabled = True
+            primary_backend = BACKEND_PLAYWRIGHT
+        else:
+            primary_backend = configured_backend

-        # 결과 요약
-        success_count = sum(
-            1 for result in results if result.get("status") == "SUCCESS"
-        )
-        total_count = len(results)
+        results: List[Dict[str, Any]] = []

-        logger.info(f"스크래핑 완료: {success_count}/{total_count} 그룹 성공")
+        if primary_backend == BACKEND_WEBJS:
+            results = await run_webjs_backend(
+                selected_groups,
+                config.scraper_settings.webjs_settings,
+                max_messages=max_messages,
+            )
+        elif primary_backend == BACKEND_PLAYWRIGHT:
+            try:
+                results = await run_playwright_backend(config, selected_groups)
+            except Exception as exc:
+                if fallback_enabled:
+                    _log_backend_switch(BACKEND_PLAYWRIGHT, BACKEND_WEBJS, str(exc))
+                    results = await run_webjs_backend(
+                        selected_groups,
+                        config.scraper_settings.webjs_settings,
+                        max_messages=max_messages,
+                    )
+                else:
+                    raise
+            else:
+                for result in results:
+                    result["backend"] = BACKEND_PLAYWRIGHT
+                if fallback_enabled:
+                    failed_group_names = {
+                        result.get("group_name")
+                        for result in results
+                        if not result.get("success", False)
+                    }
+                    if failed_group_names:
+                        fallback_groups = [
+                            group
+                            for group in selected_groups
+                            if group.name in failed_group_names
+                        ]
+                        _log_backend_switch(
+                            BACKEND_PLAYWRIGHT,
+                            BACKEND_WEBJS,
+                            "Playwright 실패 그룹 감지",
+                        )
+                        fallback_results = await run_webjs_backend(
+                            fallback_groups,
+                            config.scraper_settings.webjs_settings,
+                            max_messages=max_messages,
+                        )
+                        for fallback_result in fallback_results:
+                            for idx, original in enumerate(results):
+                                if original.get("group_name") == fallback_result.get(
+                                    "group_name"
+                                ):
+                                    results[idx] = fallback_result
+                                    break
+                            else:
+                                results.append(fallback_result)
+        else:
+            raise ValueError(f"지원하지 않는 백엔드입니다: {configured_backend}")

+        success_count = sum(1 for result in results if result.get("success", False))
+        logger.info("스크래핑 완료: %d/%d 그룹 성공", success_count, len(results))
         return results

-    except Exception as e:
-        logger.error(f"스크래핑 실행 실패: {e}")
+    except Exception as error:
+        logger.error(f"스크래핑 실행 실패: {error}")
         raise


 def main():
     """메인 함수"""
     parser = argparse.ArgumentParser(
         description="MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper",
         formatter_class=argparse.RawDescriptionHelpFormatter,
         epilog=print_usage(),
     )

     # 기본 옵션
     parser.add_argument(
         "--config",
         default="configs/optimal_multi_group_config.yaml",
         help="설정 파일 경로",
     )

     # Enhancement 옵션
     parser.add_argument(
         "--enhance-loading", action="store_true", help="로딩 안정성 개선 활성화"
     )

     parser.add_argument(
         "--enhance-stealth", action="store_true", help="스텔스 기능 활성화"
     )

     parser.add_argument(
         "--enhance-all", action="store_true", help="모든 Enhancement 활성화"
     )

     # 개발 옵션
     parser.add_argument(
         "--dev-mode", action="store_true", help="개발 모드 (디버깅, 스크린샷 등)"
     )

     parser.add_argument(
         "--tool",
         choices=["dom-analyzer", "status-check", "quick-test"],
         help="개발 도구 실행",
     )

     parser.add_argument(
         "--setup", choices=["manual-auth", "alternative"], help="설정 도구 실행"
     )

     # 백엔드 옵션 (whatsapp-web.js 통합)
     parser.add_argument(
         "--backend",
-        choices=["playwright", "webjs", "auto"],
-        default="playwright",
-        help="스크래핑 백엔드 선택 (기본: playwright)",
+        choices=[BACKEND_PLAYWRIGHT, BACKEND_WEBJS, BACKEND_AUTO],
+        default=None,
+        help="스크래핑 백엔드 선택 (기본: 설정 파일)",
     )

     parser.add_argument(
         "--webjs-fallback",
+        dest="webjs_fallback",
         action="store_true",
         help="Playwright 실패 시 whatsapp-web.js로 자동 전환",
     )
+    parser.add_argument(
+        "--no-webjs-fallback",
+        dest="webjs_fallback",
+        action="store_false",
+        help="Playwright 실패 시에도 webjs로 전환하지 않음",
+    )
+    parser.set_defaults(webjs_fallback=None)

     # 스크래핑 옵션
     parser.add_argument("--groups", nargs="+", help="스크래핑할 그룹 이름들")

     parser.add_argument("--max-messages", type=int, default=50, help="최대 메시지 수")

     parser.add_argument("--timeout", type=int, default=30000, help="타임아웃 (밀리초)")

     parser.add_argument(
         "--no-headless", action="store_true", help="헤드리스 모드 비활성화"
     )

     args = parser.parse_args()

     # Enhancement 설정
     enhance_loading = args.enhance_loading or args.enhance_all
     enhance_stealth = args.enhance_stealth or args.enhance_all

     # 개발 도구 실행
     if args.tool:
         asyncio.run(run_development_tool(args.tool))
         return

     # 설정 도구 실행
     if args.setup:
         asyncio.run(run_setup_tool(args.setup))
         return

     # 스크래퍼 실행
     try:
-        results = asyncio.run(
+        asyncio.run(
             run_optimal_scraper(
                 config_file=args.config,
                 enhance_loading=enhance_loading,
                 enhance_stealth=enhance_stealth,
                 dev_mode=args.dev_mode,
                 groups=args.groups,
                 max_messages=args.max_messages,
                 timeout=args.timeout,
                 headless=not args.no_headless,
+                backend=args.backend,
+                webjs_fallback=args.webjs_fallback,
             )
         )

         print("\n" + "=" * 60)
         print("스크래핑 완료!")
         print("=" * 60)

     except KeyboardInterrupt:
         logger.info("사용자에 의해 중단됨")
     except Exception as e:
         logger.error(f"실행 중 오류 발생: {e}")
         sys.exit(1)


 if __name__ == "__main__":
     main()
diff --git a/setup/whatsapp_webjs/README.md b/setup/whatsapp_webjs/README.md
index 250ec9a1191e057bf8df94f2986a22c777a4a3f6..7414c4ac322e9bb9a8cd53dfd118e37bdfd4402e 100644
--- a/setup/whatsapp_webjs/README.md
+++ b/setup/whatsapp_webjs/README.md
@@ -16,154 +16,163 @@ setup/whatsapp_webjs/
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
-npm install
+npm ci
 ```

 ### 3. 환경 확인 스크립트 실행

 ```bash
 # Node.js 환경 및 의존성 확인
 node check_nodejs.js
 ```

 ### 4. 스크래퍼 테스트

 ```bash
-# 기본 사용법
+# 기본 사용법 (단일 그룹)
 node whatsapp_webjs_scraper.js "그룹이름" 50

-# 예시
-node whatsapp_webjs_scraper.js "HVDC 물류팀" 50
+# 쉼표로 구분된 멀티 그룹
+node whatsapp_webjs_scraper.js "Group A,Group B" 75
+
+# 전체 그룹 스캔 (ALL)
+node whatsapp_webjs_scraper.js "ALL" 50
 ```

 ## 📋 사용법

 ### Node.js 스크래퍼 직접 사용

 ```bash
 # 기본 사용법
-node whatsapp_webjs_scraper.js <group_name> [max_messages] [output_file]
+node whatsapp_webjs_scraper.js <group|group1,group2|ALL> [max_messages]

 # 예시들
 node whatsapp_webjs_scraper.js "HVDC 물류팀" 50
-node whatsapp_webjs_scraper.js "MR.CHA 전용" 100 output.json
+node whatsapp_webjs_scraper.js "HVDC 물류팀,MR.CHA 전용" 100
+node whatsapp_webjs_scraper.js "ALL" 75
 ```

 ### Python 브릿지 사용

 ```python
+from macho_gpt.async_scraper.group_config import GroupConfig
 from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge

-# 브릿지 초기화
 bridge = WhatsAppWebJSBridge()
+group_config = GroupConfig(name="HVDC 물류팀", save_file="data/hvdc.json", max_messages=50)

-# 그룹 스크래핑
-result = await bridge.scrape_group("HVDC 물류팀", max_messages=50)
-print(result)
+result = await bridge.scrape_group(group_config)
+print(result.raw_payload)
 ```

 ### MACHO-GPT 통합 사용

 ```bash
 # whatsapp-web.js 백엔드로 실행
 python run_optimal_scraper.py --backend webjs

 # 자동 전환 모드 (Playwright 실패 시 whatsapp-web.js로 전환)
-python run_optimal_scraper.py --backend auto --webjs-fallback
+python run_optimal_scraper.py --backend auto
+
+# 전환 비활성화
+python run_optimal_scraper.py --backend playwright --no-webjs-fallback

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
-- ✅ 그룹 메시지 수집
-- ✅ JSON 형식 출력
+- ✅ 단일·다중 그룹 메시지 수집
+- ✅ 표준화된 JSON 형식 출력 (stdout 전용)
 - ✅ CLI 인자 처리
 - ✅ 에러 핸들링
 - ✅ 타임아웃 처리
 - ✅ 미디어 정보 수집
+- ✅ ISO 8601 타임스탬프 제공

 ### Python 브릿지 (whatsapp_webjs_bridge.py)

 - ✅ Node.js 환경 자동 확인
 - ✅ 의존성 자동 설치
 - ✅ subprocess를 통한 안전한 실행
 - ✅ JSON 파싱 및 변환
 - ✅ 에러 핸들링 및 로깅
 - ✅ 세션 정리 기능
+- ✅ Playwright 자동 전환을 위한 결과 포맷 정규화

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
diff --git a/setup/whatsapp_webjs/package.json b/setup/whatsapp_webjs/package.json
index a9676453d9d1740184b5ef79b49c48cee127c6ee..22e6961cb81673ec778bb38477cac0ecda7ee309 100644
--- a/setup/whatsapp_webjs/package.json
+++ b/setup/whatsapp_webjs/package.json
@@ -1,30 +1,30 @@
 {
   "name": "whatsapp-webjs-scraper",
   "version": "1.0.0",
   "description": "WhatsApp Web.js scraper for MACHO-GPT v3.5-optimal",
   "main": "whatsapp_webjs_scraper.js",
   "scripts": {
-    "start": "node whatsapp_webjs_scraper.js",
-    "test": "node test_scraper.js",
-    "install-deps": "npm install"
+    "start": "node whatsapp_webjs_scraper.js \"ALL\" 50",
+    "ci": "npm ci",
+    "check": "node check_nodejs.js"
   },
   "dependencies": {
     "whatsapp-web.js": "^1.23.0",
     "qrcode-terminal": "^0.12.0",
     "puppeteer": "^21.0.0"
   },
   "devDependencies": {
     "nodemon": "^3.0.0"
   },
   "engines": {
     "node": ">=14.0.0"
   },
   "keywords": [
     "whatsapp",
     "scraper",
     "macho-gpt",
     "automation"
   ],
   "author": "MACHO-GPT Team",
   "license": "MIT"
 }
diff --git a/setup/whatsapp_webjs/whatsapp_webjs_bridge.py b/setup/whatsapp_webjs/whatsapp_webjs_bridge.py
index 9eb454356ab7646623d0bbc1f85fee1ee1de080f..ddc1cbca59c7cf4c3fcb7e2ad81557bd0c5e46a5 100644
--- a/setup/whatsapp_webjs/whatsapp_webjs_bridge.py
+++ b/setup/whatsapp_webjs/whatsapp_webjs_bridge.py
@@ -1,315 +1,325 @@
-#!/usr/bin/env python3
-"""
-WhatsApp Web.js Python-Node.js 브릿지
-MACHO-GPT v3.5-optimal WhatsApp Web.js 통합
+"""WhatsApp Web.js 브릿지 유틸리티입니다. (KR) WhatsApp Web.js bridge utilities. (EN)

-이 모듈은 Python과 Node.js 간의 브릿지 역할을 하며,
-whatsapp-web.js 스크래퍼를 Python에서 호출할 수 있게 합니다.
+Python 환경에서 whatsapp-web.js Node 스크래퍼를 실행하기 위한 비동기 래퍼를 제공합니다.
 """

-import subprocess
+from __future__ import annotations
+
+import asyncio
 import json
 import logging
-import asyncio
-import shutil
+import subprocess
+from dataclasses import dataclass
 from pathlib import Path
-from typing import Dict, Optional, List, Any
-from datetime import datetime
+from typing import Any, Dict, List, Optional
+
+from macho_gpt.async_scraper.group_config import GroupConfig, WebJSSettings
+
+LOGGER = logging.getLogger(__name__)
+
+
+@dataclass
+class BridgeResult:
+    """브릿지 실행 결과입니다. (KR) Result payload returned by the bridge. (EN)
+
+    Args:
+        group_name (str): 대상 그룹 이름입니다.
+        success (bool): 실행 성공 여부입니다.
+        messages_scraped (int): 수집된 메시지 수입니다.
+        error (Optional[str]): 오류 메시지입니다.
+        raw_payload (Optional[Dict[str, Any]]): 원본 Node 출력입니다.
+    """

-logger = logging.getLogger(__name__)
+    group_name: str
+    success: bool
+    messages_scraped: int
+    error: Optional[str] = None
+    raw_payload: Optional[Dict[str, Any]] = None
+    messages: Optional[List[Dict[str, Any]]] = None


 class WhatsAppWebJSBridge:
-    """WhatsApp Web.js Python-Node.js 브릿지 클래스"""
-
-    def __init__(self, script_dir: str = "setup/whatsapp_webjs"):
-        """
-        브릿지 초기화
-
-        Args:
-            script_dir: Node.js 스크립트 디렉토리 경로
-        """
-        self.script_dir = Path(script_dir)
+    """whatsapp-web.js Python 브릿지입니다. (KR) Python bridge for whatsapp-web.js. (EN)
+
+    Args:
+        settings (WebJSSettings): whatsapp-web.js 설정입니다.
+        node_path (str): Node 실행 파일 경로입니다.
+        npm_path (str): npm 실행 파일 경로입니다.
+    """
+
+    def __init__(
+        self,
+        settings: Optional[WebJSSettings] = None,
+        *,
+        node_path: str = "node",
+        npm_path: str = "npm",
+    ) -> None:
+        self.settings = settings or WebJSSettings()
+        self.node_path = node_path
+        self.npm_path = npm_path
+        self.script_dir = Path(self.settings.script_dir)
         self.node_script = self.script_dir / "whatsapp_webjs_scraper.js"
-        self.package_json = self.script_dir / "package.json"
-        self.node_modules = self.script_dir / "node_modules"
-
-        # 로깅 설정
-        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
-
+        self._environment_ready = False
+
+    async def ensure_environment(self) -> bool:
+        """실행 환경을 준비합니다. (KR) Ensure the execution environment is ready. (EN)"""
+
+        if self._environment_ready:
+            return True
+        if not await self.check_nodejs_available():
+            return False
+        if not await self.check_dependencies_installed():
+            if not self.settings.auto_install_deps:
+                LOGGER.error("npm 의존성이 설치되지 않았습니다.")
+                return False
+            if not await self.install_dependencies():
+                return False
+        self._environment_ready = True
+        return True
+
     async def check_nodejs_available(self) -> bool:
-        """
-        Node.js 환경 확인
-
-        Returns:
-            bool: Node.js 사용 가능 여부
-        """
+        """Node.js 사용 가능 여부를 확인합니다. (KR) Check whether Node.js is available. (EN)"""
+
         try:
-            # Node.js 버전 확인
-            result = subprocess.run(
-                ["node", "--version"],
-                capture_output=True,
-                text=True,
-                timeout=10
+            completed = await asyncio.get_running_loop().run_in_executor(
+                None,
+                lambda: subprocess.run(
+                    [self.node_path, "--version"],
+                    capture_output=True,
+                    text=True,
+                    check=False,
+                    timeout=10,
+                ),
             )
-
-            if result.returncode == 0:
-                version = result.stdout.strip()
-                self.logger.info(f"Node.js 버전: {version}")
-
-                # 버전 파싱 (v14.0.0 형식)
-                major_version = int(version[1:].split('.')[0])
-                if major_version >= 14:
-                    return True
-                else:
-                    self.logger.error(f"Node.js 14.0.0 이상이 필요합니다. 현재: {version}")
-                    return False
-            else:
-                self.logger.error("Node.js가 설치되지 않았습니다.")
-                return False
-
         except FileNotFoundError:
-            self.logger.error("Node.js를 찾을 수 없습니다. PATH에 Node.js가 추가되었는지 확인하세요.")
+            LOGGER.error("Node.js 실행 파일을 찾을 수 없습니다.")
             return False
-        except Exception as e:
-            self.logger.error(f"Node.js 확인 중 오류 발생: {e}")
+        except subprocess.TimeoutExpired:
+            LOGGER.error("Node.js 버전 확인이 시간 초과되었습니다.")
             return False
-
-    async def check_dependencies_installed(self) -> bool:
-        """
-        npm 의존성 설치 확인
-
-        Returns:
-            bool: 의존성 설치 여부
-        """
-        if not self.node_modules.exists():
-            self.logger.warning("node_modules 디렉토리가 없습니다.")
+
+        if completed.returncode != 0:
+            LOGGER.error(
+                "Node.js가 올바르게 설치되지 않았습니다: %s", completed.stderr.strip()
+            )
+            return False
+
+        version_output = completed.stdout.strip()
+        LOGGER.debug("Node.js version output: %s", version_output)
+        try:
+            major_version = int(version_output.lstrip("v").split(".")[0])
+        except (ValueError, IndexError):
+            LOGGER.warning("Node.js 버전 파싱에 실패했습니다: %s", version_output)
+            return True
+        if major_version < 14:
+            LOGGER.error("Node.js 14 이상이 필요합니다. 현재: %s", version_output)
             return False
-
-        # 필수 패키지 확인
-        required_packages = ['whatsapp-web.js', 'qrcode-terminal']
-        missing_packages = []
-
-        for package in required_packages:
-            package_path = self.node_modules / package
-            if not package_path.exists():
-                missing_packages.append(package)
-
-        if missing_packages:
-            self.logger.warning(f"누락된 패키지: {missing_packages}")
+        return True
+
+    async def check_dependencies_installed(self) -> bool:
+        """필수 npm 패키지가 설치되었는지 확인합니다. (KR) Verify npm dependencies are installed. (EN)"""
+
+        node_modules = self.script_dir / "node_modules"
+        if not node_modules.exists():
             return False
-
+        for package_name in ("whatsapp-web.js", "qrcode-terminal"):
+            if not (node_modules / package_name).exists():
+                LOGGER.debug("누락된 패키지 감지: %s", package_name)
+                return False
         return True
-
+
     async def install_dependencies(self) -> bool:
-        """
-        npm 의존성 설치
-
-        Returns:
-            bool: 설치 성공 여부
-        """
+        """npm 의존성을 설치합니다. (KR) Install required npm dependencies. (EN)"""
+
+        LOGGER.info("npm 의존성 설치를 실행합니다.")
         try:
-            self.logger.info("npm 의존성 설치 중...")
-
-            result = subprocess.run(
-                ["npm", "install"],
-                cwd=str(self.script_dir),
-                capture_output=True,
-                text=True,
-                timeout=300  # 5분 타임아웃
+            completed = await asyncio.get_running_loop().run_in_executor(
+                None,
+                lambda: subprocess.run(
+                    [self.npm_path, "ci"],
+                    cwd=str(self.script_dir),
+                    capture_output=True,
+                    text=True,
+                    check=False,
+                    timeout=max(self.settings.timeout, 60),
+                ),
             )
-
-            if result.returncode == 0:
-                self.logger.info("npm 의존성 설치 완료")
-                return True
-            else:
-                self.logger.error(f"npm 설치 실패: {result.stderr}")
-                return False
-
-        except Exception as e:
-            self.logger.error(f"npm 설치 중 오류 발생: {e}")
+        except FileNotFoundError:
+            LOGGER.error("npm 실행 파일을 찾을 수 없습니다.")
             return False
-
-    async def scrape_group(self, group_name: str, max_messages: int = 50, output_file: Optional[str] = None) -> Dict[str, Any]:
-        """
-        그룹 스크래핑 실행
-
+        except subprocess.TimeoutExpired:
+            LOGGER.error("npm ci 명령이 시간 초과되었습니다.")
+            return False
+
+        if completed.returncode != 0:
+            LOGGER.error("npm ci 실패: %s", completed.stderr.strip())
+            return False
+
+        LOGGER.info("npm 의존성이 설치되었습니다.")
+        return True
+
+    async def scrape_group(
+        self,
+        group_config: GroupConfig,
+        *,
+        max_messages: Optional[int] = None,
+    ) -> BridgeResult:
+        """단일 그룹을 스크래핑합니다. (KR) Scrape a single WhatsApp group. (EN)
+
         Args:
-            group_name: 스크래핑할 그룹 이름
-            max_messages: 최대 메시지 수
-            output_file: 출력 파일 경로 (선택적)
-
-        Returns:
-            Dict: 스크래핑 결과
+            group_config (GroupConfig): 대상 그룹 설정입니다.
+            max_messages (Optional[int]): 메시지 수집 상한입니다.
         """
+
+        if not await self.ensure_environment():
+            return BridgeResult(
+                group_name=group_config.name,
+                success=False,
+                messages_scraped=0,
+                error="Node.js 환경이 준비되지 않았습니다.",
+            )
+
+        if not self.node_script.exists():
+            return BridgeResult(
+                group_name=group_config.name,
+                success=False,
+                messages_scraped=0,
+                error=f"Node 스크립트를 찾을 수 없습니다: {self.node_script}",
+            )
+
+        limit = max_messages or group_config.max_messages
+        cmd = [
+            self.node_path,
+            str(self.node_script),
+            group_config.name,
+            str(limit),
+        ]
+
+        LOGGER.info("webjs 스크립트를 실행합니다: %s", " ".join(cmd))
+
         try:
-            # Node.js 환경 확인
-            if not await self.check_nodejs_available():
-                return {
-                    "status": "FAIL",
-                    "error": "Node.js 환경이 설정되지 않았습니다.",
-                    "timestamp": datetime.now().isoformat()
-                }
-
-            # 의존성 확인 및 설치
-            if not await self.check_dependencies_installed():
-                self.logger.info("의존성 설치가 필요합니다. 자동 설치를 시도합니다...")
-                if not await self.install_dependencies():
-                    return {
-                        "status": "FAIL",
-                        "error": "npm 의존성 설치에 실패했습니다.",
-                        "timestamp": datetime.now().isoformat()
-                    }
-
-            # 스크립트 실행
-            cmd = ["node", str(self.node_script), group_name, str(max_messages)]
-            if output_file:
-                cmd.append(output_file)
-
-            self.logger.info(f"Node.js 스크립트 실행: {' '.join(cmd)}")
-
-            result = subprocess.run(
-                cmd,
-                cwd=str(self.script_dir),
-                capture_output=True,
-                text=True,
-                timeout=300  # 5분 타임아웃
+            completed = await asyncio.get_running_loop().run_in_executor(
+                None,
+                lambda: subprocess.run(
+                    cmd,
+                    cwd=str(self.script_dir),
+                    capture_output=True,
+                    text=True,
+                    check=False,
+                    timeout=self.settings.timeout,
+                ),
             )
-
-            if result.returncode == 0:
-                try:
-                    # JSON 파싱
-                    data = json.loads(result.stdout)
-                    data["bridge_info"] = {
-                        "executed_at": datetime.now().isoformat(),
-                        "node_version": await self._get_node_version(),
-                        "script_path": str(self.node_script)
-                    }
-                    return data
-                except json.JSONDecodeError as e:
-                    self.logger.error(f"JSON 파싱 오류: {e}")
-                    return {
-                        "status": "FAIL",
-                        "error": f"JSON 파싱 오류: {e}",
-                        "raw_output": result.stdout,
-                        "timestamp": datetime.now().isoformat()
-                    }
-            else:
-                self.logger.error(f"Node.js 스크립트 실행 실패: {result.stderr}")
-                return {
-                    "status": "FAIL",
-                    "error": result.stderr,
-                    "timestamp": datetime.now().isoformat()
-                }
-
         except subprocess.TimeoutExpired:
-            self.logger.error("Node.js 스크립트 실행 시간 초과")
-            return {
-                "status": "FAIL",
-                "error": "스크립트 실행 시간 초과 (5분)",
-                "timestamp": datetime.now().isoformat()
-            }
-        except Exception as e:
-            self.logger.error(f"스크래핑 중 오류 발생: {e}")
-            return {
-                "status": "FAIL",
-                "error": str(e),
-                "timestamp": datetime.now().isoformat()
-            }
-
-    async def _get_node_version(self) -> str:
-        """Node.js 버전 가져오기"""
-        try:
-            result = subprocess.run(
-                ["node", "--version"],
-                capture_output=True,
-                text=True,
-                timeout=5
+            LOGGER.error("webjs 스크립트가 시간 초과되었습니다.")
+            return BridgeResult(
+                group_name=group_config.name,
+                success=False,
+                messages_scraped=0,
+                error="whatsapp-web.js 실행이 시간 초과되었습니다.",
             )
-            return result.stdout.strip() if result.returncode == 0 else "unknown"
-        except:
-            return "unknown"
-
-    async def get_available_groups(self) -> List[Dict[str, Any]]:
-        """
-        사용 가능한 그룹 목록 가져오기 (미구현)
-
-        Returns:
-            List[Dict]: 그룹 목록
-        """
-        # TODO: Node.js 스크립트를 통해 그룹 목록 가져오기
-        return []
-
-    async def cleanup_session(self) -> bool:
-        """
-        인증 세션 정리
-
-        Returns:
-            bool: 정리 성공 여부
-        """
+
+        stdout = completed.stdout.strip()
+        stderr = completed.stderr.strip()
+        if stderr:
+            LOGGER.debug("webjs stderr: %s", stderr)
+
+        payload: Dict[str, Any]
         try:
-            # .wwebjs_auth 디렉토리 삭제
-            auth_dir = self.script_dir / ".wwebjs_auth"
-            if auth_dir.exists():
-                shutil.rmtree(auth_dir)
-                self.logger.info("인증 세션이 정리되었습니다.")
-                return True
-            return True
-        except Exception as e:
-            self.logger.error(f"세션 정리 중 오류 발생: {e}")
-            return False
+            payload = json.loads(stdout) if stdout else {}
+        except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
+            LOGGER.error("JSON 파싱 실패: %s", exc)
+            return BridgeResult(
+                group_name=group_config.name,
+                success=False,
+                messages_scraped=0,
+                error="whatsapp-web.js 출력 파싱 실패",
+            )

+        status = payload.get("status", "FAIL")
+        if completed.returncode != 0 or status != "SUCCESS":
+            error_message = payload.get("error") or stderr or "알 수 없는 오류"
+            LOGGER.error("webjs 스크립트 실패: %s", error_message)
+            return BridgeResult(
+                group_name=group_config.name,
+                success=False,
+                messages_scraped=0,
+                error=error_message,
+                raw_payload=payload or None,
+            )

-# 편의 함수들
-async def scrape_whatsapp_group(group_name: str, max_messages: int = 50, output_file: Optional[str] = None) -> Dict[str, Any]:
-    """
-    WhatsApp 그룹 스크래핑 편의 함수
-
-    Args:
-        group_name: 그룹 이름
-        max_messages: 최대 메시지 수
-        output_file: 출력 파일 경로
-
-    Returns:
-        Dict: 스크래핑 결과
-    """
-    bridge = WhatsAppWebJSBridge()
-    return await bridge.scrape_group(group_name, max_messages, output_file)
+        groups = payload.get("groups", [])
+        messages: List[Dict[str, Any]] = []
+        for group_entry in groups:
+            if group_entry.get("name") == group_config.name:
+                messages = group_entry.get("messages", [])
+                break
+        else:
+            LOGGER.warning("타깃 그룹이 결과에 없습니다: %s", group_config.name)
+            messages = groups[0].get("messages", []) if groups else []

+        return BridgeResult(
+            group_name=group_config.name,
+            success=True,
+            messages_scraped=len(messages),
+            raw_payload=payload,
+            messages=messages,
+        )

-async def check_webjs_environment() -> Dict[str, Any]:
-    """
-    Web.js 환경 상태 확인
-
-    Returns:
-        Dict: 환경 상태 정보
-    """
-    bridge = WhatsAppWebJSBridge()
-
+    async def scrape_groups(
+        self, group_configs: List[GroupConfig], *, max_messages: Optional[int] = None
+    ) -> List[BridgeResult]:
+        """여러 그룹을 순차로 스크래핑합니다. (KR) Scrape multiple groups sequentially. (EN)"""
+
+        results: List[BridgeResult] = []
+        for group_config in group_configs:
+            result = await self.scrape_group(group_config, max_messages=max_messages)
+            results.append(result)
+        return results
+
+
+async def scrape_whatsapp_group(
+    group_config: GroupConfig,
+    *,
+    max_messages: Optional[int] = None,
+    settings: Optional[WebJSSettings] = None,
+) -> BridgeResult:
+    """헬퍼 함수로 단일 그룹을 스크래핑합니다. (KR) Convenience wrapper to scrape one group. (EN)"""
+
+    bridge = WhatsAppWebJSBridge(settings)
+    return await bridge.scrape_group(group_config, max_messages=max_messages)
+
+
+async def check_webjs_environment(
+    settings: Optional[WebJSSettings] = None,
+) -> Dict[str, Any]:
+    """whatsapp-web.js 실행 환경을 점검합니다. (KR) Inspect the whatsapp-web.js environment. (EN)"""
+
+    bridge = WhatsAppWebJSBridge(settings)
     return {
         "nodejs_available": await bridge.check_nodejs_available(),
         "dependencies_installed": await bridge.check_dependencies_installed(),
         "script_exists": bridge.node_script.exists(),
-        "package_json_exists": bridge.package_json.exists(),
-        "timestamp": datetime.now().isoformat()
+        "package_json_exists": (bridge.script_dir / "package.json").exists(),
     }


-# CLI 테스트용
-if __name__ == "__main__":
-    import sys
-
+if __name__ == "__main__":  # pragma: no cover - manual execution helper
+    import argparse
+
     logging.basicConfig(level=logging.INFO)
-
-    if len(sys.argv) < 2:
-        print("사용법: python whatsapp_webjs_bridge.py <group_name> [max_messages]")
-        sys.exit(1)
-
-    group_name = sys.argv[1]
-    max_messages = int(sys.argv[2]) if len(sys.argv) > 2 else 50
-
-    async def main():
-        result = await scrape_whatsapp_group(group_name, max_messages)
-        print(json.dumps(result, indent=2, ensure_ascii=False))
-
-    asyncio.run(main())
+    parser = argparse.ArgumentParser(description="whatsapp-web.js bridge CLI")
+    parser.add_argument("group", help="스크래핑할 그룹 이름")
+    parser.add_argument("max_messages", nargs="?", type=int, default=50)
+    args = parser.parse_args()
+
+    async def _main() -> None:
+        settings = WebJSSettings()
+        group = GroupConfig(
+            name=args.group,
+            save_file="bridge_cli.json",
+            max_messages=args.max_messages,
+        )
+        result = await scrape_whatsapp_group(group, settings=settings)
+        print(json.dumps(result.raw_payload or {}, ensure_ascii=False, indent=2))
+
+    asyncio.run(_main())
diff --git a/setup/whatsapp_webjs/whatsapp_webjs_scraper.js b/setup/whatsapp_webjs/whatsapp_webjs_scraper.js
index 9ec6b7dc594d31ba10bbf9fcc124938d452265a6..a15b17a0dd2b6401df2a93cd25652575031d0e5f 100644
--- a/setup/whatsapp_webjs/whatsapp_webjs_scraper.js
+++ b/setup/whatsapp_webjs/whatsapp_webjs_scraper.js
@@ -1,186 +1,202 @@
 #!/usr/bin/env node
 /**
- * WhatsApp Web.js 스크래퍼
- * MACHO-GPT v3.5-optimal WhatsApp Web.js 통합
- *
- * 사용법: node whatsapp_webjs_scraper.js <group_name> [max_messages]
- * 예시: node whatsapp_webjs_scraper.js "HVDC 물류팀" 50
+ * whatsapp-web.js 기반 그룹 스크래퍼입니다. (KR) WhatsApp Web.js based group scraper. (EN)
+ *
+ * Usage:
+ *   node whatsapp_webjs_scraper.js "Group Name" [max_messages]
+ *   node whatsapp_webjs_scraper.js "Group A,Group B" 75
+ *   node whatsapp_webjs_scraper.js "ALL" 50
  */

 const { Client, LocalAuth } = require('whatsapp-web.js');
 const qrcode = require('qrcode-terminal');
-const fs = require('fs');
 const path = require('path');

-// CLI 인자 처리
 const args = process.argv.slice(2);
-const groupName = args[0];
-const maxMessages = parseInt(args[1]) || 50;
-const outputFile = args[2] || null;
-
-if (!groupName) {
-    console.error('❌ 사용법: node whatsapp_webjs_scraper.js <group_name> [max_messages] [output_file]');
-    console.error('예시: node whatsapp_webjs_scraper.js "HVDC 물류팀" 50');
-    process.exit(1);
-}
+const groupSpec = args[0];
+const maxMessages = Number.parseInt(args[1] || '50', 10);

-console.log('🚀 MACHO-GPT v3.5-optimal WhatsApp Web.js 스크래퍼 시작');
-console.log(`📋 대상 그룹: ${groupName}`);
-console.log(`📊 최대 메시지 수: ${maxMessages}`);
+const log = (...messages) => console.error(...messages);

-// 클라이언트 설정
-const client = new Client({
-    authStrategy: new LocalAuth({
-        clientId: "macho-gpt-optimal"
+if (!groupSpec) {
+  log('❌ Usage: node whatsapp_webjs_scraper.js "<group|group1,group2|ALL>" [max_messages]');
+  process.exitCode = 1;
+  process.stdout.write(
+    JSON.stringify({
+      status: 'FAIL',
+      error: 'GROUP_SPEC_MISSING',
+      meta: {
+        reason: 'Group specification argument is required.',
+      },
     }),
-    puppeteer: {
-        headless: true,
-        args: [
-            '--no-sandbox',
-            '--disable-setuid-sandbox',
-            '--disable-dev-shm-usage',
-            '--disable-accelerated-2d-canvas',
-            '--no-first-run',
-            '--no-zygote',
-            '--disable-gpu'
-        ]
+  );
+  process.exit();
+}
+
+const normaliseGroupSpec = (spec) => {
+  if (!spec) {
+    return [];
+  }
+  if (spec.trim().toUpperCase() === 'ALL') {
+    return null;
+  }
+  try {
+    if (spec.trim().startsWith('[')) {
+      const parsed = JSON.parse(spec);
+      if (Array.isArray(parsed)) {
+        return parsed.map((value) => String(value).trim()).filter(Boolean);
+      }
     }
+  } catch (error) {
+    log('⚠️  Failed to parse JSON group specification:', error.message);
+  }
+  return spec
+    .split(',')
+    .map((value) => value.trim())
+    .filter(Boolean);
+};
+
+const requestedGroups = normaliseGroupSpec(groupSpec);
+
+const toIsoString = (timestamp) => {
+  if (!timestamp) {
+    return null;
+  }
+  const milliseconds = Number(timestamp) * 1000;
+  return new Date(milliseconds).toISOString();
+};
+
+const emitResult = (payload, exitCode = 0) => {
+  process.stdout.write(JSON.stringify(payload));
+  process.exitCode = exitCode;
+};
+
+const client = new Client({
+  authStrategy: new LocalAuth({ clientId: 'macho-gpt-optimal' }),
+  puppeteer: {
+    headless: true,
+    args: [
+      '--no-sandbox',
+      '--disable-setuid-sandbox',
+      '--disable-dev-shm-usage',
+      '--disable-accelerated-2d-canvas',
+      '--no-first-run',
+      '--no-zygote',
+      '--disable-gpu',
+    ],
+  },
 });

-// QR 코드 이벤트
 client.on('qr', (qr) => {
-    console.log('📱 QR 코드를 스캔하여 WhatsApp에 로그인하세요:');
-    qrcode.generate(qr, { small: true });
-    console.log('⏳ 로그인 대기 중...');
+  log('📱 Scan the QR code to authenticate.');
+  qrcode.generate(qr, { small: true });
 });

-// 인증 상태 이벤트
 client.on('authenticated', () => {
-    console.log('✅ WhatsApp 인증 완료');
-});
-
-// 인증 실패 이벤트
-client.on('auth_failure', (msg) => {
-    console.error('❌ 인증 실패:', msg);
-    process.exit(1);
+  log('✅ Authentication successful.');
 });

-// 연결 끊김 이벤트
-client.on('disconnected', (reason) => {
-    console.log('🔌 연결이 끊어졌습니다:', reason);
+client.on('auth_failure', (message) => {
+  log('❌ Authentication failure:', message);
 });

-// 준비 완료 이벤트
 client.on('ready', async () => {
-    console.log('🎉 WhatsApp Web.js 클라이언트 준비 완료');
-
-    try {
-        // 채팅 목록 가져오기
-        console.log('📋 채팅 목록을 가져오는 중...');
-        const chats = await client.getChats();
-
-        // 대상 그룹 찾기
-        const group = chats.find(chat =>
-            chat.isGroup && chat.name === groupName
-        );
-
-        if (!group) {
-            console.error(`❌ 그룹을 찾을 수 없습니다: ${groupName}`);
-            console.log('📋 사용 가능한 그룹 목록:');
-            const groupChats = chats.filter(chat => chat.isGroup);
-            groupChats.forEach(chat => {
-                console.log(`  - ${chat.name}`);
-            });
-            await client.destroy();
-            process.exit(1);
-        }
-
-        console.log(`✅ 그룹 발견: ${group.name}`);
-        console.log(`👥 참여자 수: ${group.participants.length}`);
-
-        // 메시지 가져오기
-        console.log(`📨 최근 ${maxMessages}개 메시지를 가져오는 중...`);
-        const messages = await group.fetchMessages({ limit: maxMessages });
-
-        console.log(`📊 ${messages.length}개 메시지 수집 완료`);
-
-        // 메시지 데이터 변환
-        const messageData = messages.map(msg => ({
-            id: msg.id.id,
-            body: msg.body || '',
-            timestamp: msg.timestamp,
-            author: msg.author || msg.from,
-            from: msg.from,
-            to: msg.to,
-            type: msg.type,
-            isForwarded: msg.isForwarded,
-            isStarred: msg.isStarred,
-            hasQuotedMsg: msg.hasQuotedMsg,
-            quotedMsgId: msg.quotedMsgId,
-            media: msg.hasMedia ? {
-                mimetype: msg.media.mimetype,
-                filename: msg.media.filename,
-                size: msg.media.filesize
-            } : null
-        }));
-
-        // 결과 데이터 구성
-        const result = {
-            status: 'SUCCESS',
-            timestamp: new Date().toISOString(),
-            group: {
-                name: group.name,
-                id: group.id.id,
-                participants: group.participants.length,
-                isGroup: group.isGroup
-            },
-            messages: messageData,
-            summary: {
-                total_messages: messageData.length,
-                scraped_at: new Date().toISOString(),
-                scraper_version: '3.5-optimal-webjs'
-            }
-        };
-
-        // JSON 출력
-        const jsonOutput = JSON.stringify(result, null, 2);
-
-        if (outputFile) {
-            // 파일로 저장
-            const outputPath = path.resolve(outputFile);
-            fs.writeFileSync(outputPath, jsonOutput, 'utf8');
-            console.log(`💾 결과가 파일에 저장되었습니다: ${outputPath}`);
-        } else {
-            // 콘솔에 출력
-            console.log('📄 결과 데이터:');
-            console.log(jsonOutput);
-        }
-
-        console.log('✅ 스크래핑 완료!');
-
-    } catch (error) {
-        console.error('❌ 스크래핑 중 오류 발생:', error.message);
-        process.exit(1);
-    } finally {
-        // 클라이언트 종료
-        await client.destroy();
-        console.log('🔌 클라이언트 연결 종료');
+  log('🚀 whatsapp-web.js client ready.');
+  const groupsPayload = [];
+
+  try {
+    const chats = await client.getChats();
+    const groupChats = chats.filter((chat) => chat.isGroup);
+
+    const targets =
+      requestedGroups === null
+        ? groupChats
+        : groupChats.filter((chat) => requestedGroups.includes(chat.name));
+
+    if (!targets.length) {
+      emitResult(
+        {
+          status: 'FAIL',
+          error: 'GROUP_NOT_FOUND',
+          meta: {
+            requested: requestedGroups,
+            available_groups: groupChats.map((chat) => chat.name),
+          },
+        },
+        1,
+      );
+      await client.destroy();
+      return;
+    }
+
+    for (const group of targets) {
+      log(`📨 Fetching up to ${maxMessages} messages from ${group.name}`);
+      const messages = await group.fetchMessages({ limit: maxMessages });
+      const serialisedMessages = [];
+
+      for (const message of messages) {
+        serialisedMessages.push({
+          id: message.id.id,
+          body: message.body || '',
+          timestamp_unix: message.timestamp,
+          timestamp_iso: toIsoString(message.timestamp),
+          author: message.author || message.from,
+          from: message.from,
+          to: message.to,
+          type: message.type,
+          has_media: Boolean(message.hasMedia),
+          quoted_msg_id: message.quotedMsgId || null,
+          is_forwarded: Boolean(message.isForwarded),
+          is_starred: Boolean(message.isStarred),
+        });
+      }
+
+      groupsPayload.push({
+        name: group.name,
+        id: group.id._serialized,
+        participants: Array.isArray(group.participants)
+          ? group.participants.length
+          : null,
+        messages: serialisedMessages,
+        summary: {
+          total_messages: serialisedMessages.length,
+          fetched_at: new Date().toISOString(),
+        },
+      });
     }
+
+    emitResult({
+      status: 'SUCCESS',
+      groups: groupsPayload,
+      meta: {
+        backend: 'webjs',
+        scraped_at: new Date().toISOString(),
+        requested_groups: requestedGroups,
+        max_messages: maxMessages,
+        working_directory: path.resolve('.'),
+      },
+    });
+  } catch (error) {
+    log('❌ Error while scraping:', error.message);
+    emitResult(
+      {
+        status: 'FAIL',
+        error: error.message,
+      },
+      1,
+    );
+  } finally {
+    await client.destroy();
+    log('🔌 Client connection closed.');
+  }
 });

-// 에러 처리
-client.on('error', (error) => {
-    console.error('❌ 클라이언트 오류:', error);
-    process.exit(1);
+client.on('disconnected', (reason) => {
+  log('🔌 Client disconnected:', reason);
 });

-// 프로세스 종료 처리
-process.on('SIGINT', async () => {
-    console.log('\n⚠️  사용자에 의해 중단됨');
-    await client.destroy();
-    process.exit(0);
+client.on('error', (error) => {
+  log('❌ Client error:', error.message || error);
 });

-// 클라이언트 초기화
-console.log('🔄 WhatsApp Web.js 클라이언트 초기화 중...');
 client.initialize();
diff --git a/tests/test_multi_group_scraper.py b/tests/test_multi_group_scraper.py
index 7e8b0f97ebe3d45a51eb2fa36790fb141308d355..2f47e1da5810c77a4bf8e25510652569584e67bf 100644
--- a/tests/test_multi_group_scraper.py
+++ b/tests/test_multi_group_scraper.py
@@ -1,96 +1,99 @@
 """
 TDD 테스트: 멀티 그룹 WhatsApp 스크래퍼
 Kent Beck TDD 원칙 준수: Red → Green → Refactor
 """

-import pytest
-import asyncio
-from pathlib import Path
-from unittest.mock import Mock, patch, AsyncMock
 import tempfile
-import yaml
+from pathlib import Path
+from unittest.mock import AsyncMock, Mock, patch
+
+import pytest
+
+from macho_gpt.async_scraper.async_scraper import AsyncGroupScraper

 # 테스트 대상 모듈 import
 from macho_gpt.async_scraper.group_config import (
-    GroupConfig,
-    ScraperSettings,
     AIIntegrationSettings,
+    GroupConfig,
     MultiGroupConfig,
+    ScraperSettings,
 )
-from macho_gpt.async_scraper.async_scraper import AsyncGroupScraper
 from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager


 class TestGroupConfig:
     """GroupConfig 클래스 테스트"""

     def test_should_create_group_config_with_valid_data(self):
         """유효한 데이터로 GroupConfig 생성 테스트"""
         config = GroupConfig(
             name="Test Group",
             save_file="test.json",
             scrape_interval=60,
             priority="HIGH",
+            max_messages=50,
         )

         assert config.name == "Test Group"
         assert config.save_file == "test.json"
         assert config.scrape_interval == 60
         assert config.priority == "HIGH"

     def test_should_raise_error_for_invalid_scrape_interval(self):
         """잘못된 scrape_interval에 대한 오류 테스트"""
         with pytest.raises(ValueError, match="scrape_interval은 최소 10초 이상"):
             GroupConfig(
                 name="Test Group", save_file="test.json", scrape_interval=5  # 10초 미만
             )

     def test_should_raise_error_for_invalid_priority(self):
         """잘못된 priority에 대한 오류 테스트"""
         with pytest.raises(ValueError, match="유효하지 않은 priority"):
             GroupConfig(name="Test Group", save_file="test.json", priority="INVALID")

     def test_should_raise_error_for_empty_name_or_save_file(self):
         """빈 name이나 save_file에 대한 오류 테스트"""
         with pytest.raises(ValueError, match="name과 save_file은 필수입니다"):
             GroupConfig(name="", save_file="test.json")

         with pytest.raises(ValueError, match="name과 save_file은 필수입니다"):
             GroupConfig(name="Test Group", save_file="")


 class TestScraperSettings:
     """ScraperSettings 클래스 테스트"""

     def test_should_create_scraper_settings_with_valid_data(self):
         """유효한 데이터로 ScraperSettings 생성 테스트"""
         settings = ScraperSettings(
             chrome_data_dir="chrome-data",
             headless=True,
             timeout=30000,
             max_parallel_groups=5,
+            backend="playwright",
+            webjs_fallback=True,
         )

         assert settings.chrome_data_dir == "chrome-data"
         assert settings.headless is True
         assert settings.timeout == 30000
         assert settings.max_parallel_groups == 5

     def test_should_raise_error_for_invalid_timeout(self):
         """잘못된 timeout에 대한 오류 테스트"""
         with pytest.raises(ValueError, match="timeout은 최소 5000ms 이상"):
             ScraperSettings(timeout=1000)  # 5000ms 미만

     def test_should_raise_error_for_invalid_max_parallel_groups(self):
         """잘못된 max_parallel_groups에 대한 오류 테스트"""
         with pytest.raises(ValueError, match="max_parallel_groups는 1~10 사이"):
             ScraperSettings(max_parallel_groups=0)  # 1 미만

         with pytest.raises(ValueError, match="max_parallel_groups는 1~10 사이"):
             ScraperSettings(max_parallel_groups=15)  # 10 초과


 class TestAIIntegrationSettings:
     """AIIntegrationSettings 클래스 테스트"""

     def test_should_create_ai_settings_with_valid_data(self):
@@ -168,98 +171,103 @@ ai_integration:
 whatsapp_groups: []
 scraper_settings:
   chrome_data_dir: "chrome-data"
 ai_integration:
   enabled: true
 """

         with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
             f.write(yaml_content)
             temp_path = f.name

         try:
             with pytest.raises(
                 ValueError, match="최소 1개 이상의 WhatsApp 그룹이 필요합니다"
             ):
                 MultiGroupConfig.load_from_yaml(temp_path)
         finally:
             Path(temp_path).unlink()

     def test_should_validate_duplicate_group_names(self):
         """중복된 그룹 이름 검증 테스트"""
         config = MultiGroupConfig()

         # 중복된 그룹 이름 추가
         config.whatsapp_groups = [
-            GroupConfig(name="Test Group", save_file="test1.json"),
-            GroupConfig(name="Test Group", save_file="test2.json"),  # 중복 이름
+            GroupConfig(name="Test Group", save_file="test1.json", max_messages=10),
+            GroupConfig(
+                name="Test Group", save_file="test2.json", max_messages=10
+            ),  # 중복 이름
         ]

         with pytest.raises(ValueError, match="중복된 그룹 이름이 있습니다"):
             config.validate()

     def test_should_validate_duplicate_save_files(self):
         """중복된 save_file 경로 검증 테스트"""
         config = MultiGroupConfig()

         # 중복된 save_file 추가
         config.whatsapp_groups = [
-            GroupConfig(name="Group 1", save_file="test.json"),
-            GroupConfig(name="Group 2", save_file="test.json"),  # 중복 파일
+            GroupConfig(name="Group 1", save_file="test.json", max_messages=10),
+            GroupConfig(
+                name="Group 2", save_file="test.json", max_messages=10
+            ),  # 중복 파일
         ]

         with pytest.raises(ValueError, match="중복된 save_file 경로가 있습니다"):
             config.validate()

     def test_should_validate_max_parallel_groups_limit(self):
         """max_parallel_groups 제한 검증 테스트"""
         config = MultiGroupConfig()

         # 그룹 수가 max_parallel_groups를 초과하는 경우
         config.whatsapp_groups = [
-            GroupConfig(name=f"Group {i}", save_file=f"test{i}.json")
+            GroupConfig(name=f"Group {i}", save_file=f"test{i}.json", max_messages=10)
             for i in range(6)  # 6개 그룹
         ]
         config.scraper_settings.max_parallel_groups = 5  # 최대 5개

         with pytest.raises(
             ValueError, match="그룹 수.*max_parallel_groups.*를 초과합니다"
         ):
             config.validate()


 class TestAsyncGroupScraper:
     """AsyncGroupScraper 클래스 테스트"""

     @pytest.fixture
     def mock_group_config(self):
         """테스트용 GroupConfig 픽스처"""
         return GroupConfig(
             name="Test Group",
             save_file="test.json",
             scrape_interval=60,
             priority="HIGH",
+            max_messages=20,
         )

     def test_should_initialize_async_scraper(self, mock_group_config):
         """AsyncGroupScraper 초기화 테스트"""
         scraper = AsyncGroupScraper(
             group_config=mock_group_config, chrome_data_dir="chrome-data", headless=True
         )

         assert scraper.group_config.name == "Test Group"
         assert scraper.chrome_data_dir == "chrome-data"
         assert scraper.headless is True

     @pytest.mark.asyncio
     async def test_should_initialize_browser_context(self, mock_group_config):
         """브라우저 컨텍스트 초기화 테스트"""
         scraper = AsyncGroupScraper(
             group_config=mock_group_config, chrome_data_dir="chrome-data", headless=True
         )

         with patch("playwright.async_api.async_playwright") as mock_playwright:
             mock_browser = AsyncMock()
             mock_context = AsyncMock()
             mock_page = AsyncMock()

             mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = (
@@ -329,53 +337,53 @@ class TestAsyncGroupScraper:

     @pytest.mark.asyncio
     async def test_should_handle_scraping_errors_gracefully(self, mock_group_config):
         """스크래핑 오류 처리 테스트"""
         scraper = AsyncGroupScraper(
             group_config=mock_group_config, chrome_data_dir="chrome-data", headless=True
         )

         # Mock에서 오류 발생
         mock_page = AsyncMock()
         mock_page.wait_for_selector.side_effect = Exception("Network error")
         scraper.page = mock_page

         # 오류가 발생해도 빈 리스트를 반환해야 함
         messages = await scraper.scrape_messages()
         assert messages == []


 class TestMultiGroupManager:
     """MultiGroupManager 클래스 테스트"""

     @pytest.fixture
     def mock_group_configs(self):
         """테스트용 그룹 설정 리스트 픽스처"""
         return [
-            GroupConfig(name="Group 1", save_file="test1.json"),
-            GroupConfig(name="Group 2", save_file="test2.json"),
-            GroupConfig(name="Group 3", save_file="test3.json"),
+            GroupConfig(name="Group 1", save_file="test1.json", max_messages=15),
+            GroupConfig(name="Group 2", save_file="test2.json", max_messages=15),
+            GroupConfig(name="Group 3", save_file="test3.json", max_messages=15),
         ]

     def test_should_initialize_multi_group_manager(self, mock_group_configs):
         """MultiGroupManager 초기화 테스트"""
         manager = MultiGroupManager(
             group_configs=mock_group_configs, max_parallel_groups=3
         )

         assert len(manager.group_configs) == 3
         assert manager.max_parallel_groups == 3
         assert len(manager.scrapers) == 0  # 아직 스크래퍼 생성 안됨

     @pytest.mark.asyncio
     async def test_should_create_individual_scrapers_per_group(
         self, mock_group_configs
     ):
         """그룹별 개별 스크래퍼 생성 테스트"""
         manager = MultiGroupManager(
             group_configs=mock_group_configs, max_parallel_groups=3
         )

         # start_all_scrapers는 실제로 스크래퍼를 생성하므로 직접 확인
         await manager.start_all_scrapers()

         assert len(manager.scrapers) == 3
diff --git a/tests/test_whatsapp_webjs_bridge.py b/tests/test_whatsapp_webjs_bridge.py
new file mode 100644
index 0000000000000000000000000000000000000000..3ee6a36420647bad508d996a22bec7b6388bdbce
--- /dev/null
+++ b/tests/test_whatsapp_webjs_bridge.py
@@ -0,0 +1,77 @@
+import json
+import subprocess
+from pathlib import Path
+
+import pytest
+
+from macho_gpt.async_scraper.group_config import GroupConfig, WebJSSettings
+from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge
+
+
+@pytest.mark.asyncio
+async def test_scrape_group_success(tmp_path, monkeypatch):
+    script_dir = tmp_path
+    (script_dir / "whatsapp_webjs_scraper.js").write_text(
+        "console.log()", encoding="utf-8"
+    )
+    for package_name in ("whatsapp-web.js", "qrcode-terminal"):
+        (script_dir / "node_modules" / package_name).mkdir(parents=True, exist_ok=True)
+
+    settings = WebJSSettings(script_dir=str(script_dir), timeout=60)
+    bridge = WhatsAppWebJSBridge(settings)
+    group = GroupConfig(name="Demo Group", save_file="demo.json", max_messages=5)
+
+    def fake_run(args, **kwargs):
+        if args[:2] == ["node", "--version"]:
+            return subprocess.CompletedProcess(args, 0, stdout="v18.0.0", stderr="")
+        if args[0] == "node" and args[1].endswith("whatsapp_webjs_scraper.js"):
+            payload = {
+                "status": "SUCCESS",
+                "groups": [
+                    {
+                        "name": "Demo Group",
+                        "messages": [
+                            {"id": "1", "body": "hello", "timestamp_unix": 1},
+                            {"id": "2", "body": "world", "timestamp_unix": 2},
+                        ],
+                    }
+                ],
+            }
+            return subprocess.CompletedProcess(
+                args, 0, stdout=json.dumps(payload), stderr=""
+            )
+        raise AssertionError(f"Unexpected command: {args}")
+
+    monkeypatch.setattr(subprocess, "run", fake_run)
+
+    result = await bridge.scrape_group(group, max_messages=5)
+
+    assert result.success is True
+    assert result.messages_scraped == 2
+    assert result.raw_payload is not None
+
+
+@pytest.mark.asyncio
+async def test_scrape_group_handles_missing_node(monkeypatch, tmp_path):
+    settings = WebJSSettings(script_dir=str(tmp_path))
+    (Path(settings.script_dir) / "whatsapp_webjs_scraper.js").write_text(
+        "console.log()", encoding="utf-8"
+    )
+
+    for package_name in ("whatsapp-web.js", "qrcode-terminal"):
+        (Path(settings.script_dir) / "node_modules" / package_name).mkdir(
+            parents=True, exist_ok=True
+        )
+
+    def missing_node(args, **kwargs):
+        raise FileNotFoundError
+
+    monkeypatch.setattr(subprocess, "run", missing_node)
+
+    bridge = WhatsAppWebJSBridge(settings)
+    group = GroupConfig(name="Demo Group", save_file="demo.json", max_messages=5)
+
+    result = await bridge.scrape_group(group, max_messages=5)
+
+    assert result.success is False
+    assert "환경" in result.error
