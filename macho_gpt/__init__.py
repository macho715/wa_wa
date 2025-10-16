"""
MACHO-GPT v3.4-mini 모듈 초기화
Samsung C&T Logistics · HVDC Project Integration
"""

import logging

logger = logging.getLogger(__name__)

# 버전 정보
__version__ = "3.4-mini"
__project__ = "HVDC_SAMSUNG_CT_ADNOC_DSV"

# Optional modules (graceful degradation)
try:
    from .core.logi_workflow_241219 import workflow_manager, ChatRoomType, TaskPriority, TaskStatus
    WORKFLOW_AVAILABLE = True
    logger.info("✅ Workflow module loaded")
except ImportError as e:
    WORKFLOW_AVAILABLE = False
    logger.warning(f"⚠️  Workflow module not available: {e}")

try:
    from .core.logi_ai_summarizer_241219 import LogiAISummarizer
    AI_SUMMARIZER_AVAILABLE = True
    logger.info("✅ AI Summarizer module loaded")
except ImportError as e:
    AI_SUMMARIZER_AVAILABLE = False
    logger.warning(f"⚠️  AI Summarizer module not available: {e}")

try:
    from .rpa.logi_rpa_whatsapp_241219 import WhatsAppRPAExtractor
    RPA_AVAILABLE = True
    logger.info("✅ RPA module loaded")
except ImportError as e:
    RPA_AVAILABLE = False
    logger.warning(f"⚠️  RPA module not available: {e}")

__all__ = []
    
if WORKFLOW_AVAILABLE:
    __all__.extend(["workflow_manager", "ChatRoomType", "TaskPriority", "TaskStatus"])

if AI_SUMMARIZER_AVAILABLE:
    __all__.append("LogiAISummarizer")

if RPA_AVAILABLE:
    __all__.append("WhatsAppRPAExtractor")

# 시스템 상태
SYSTEM_STATUS = {
    "version": __version__,
    "project": __project__,
    "workflow_available": WORKFLOW_AVAILABLE,
    "ai_summarizer_available": AI_SUMMARIZER_AVAILABLE,
    "rpa_available": RPA_AVAILABLE
}

def get_system_status():
    """시스템 상태 반환"""
    return SYSTEM_STATUS 