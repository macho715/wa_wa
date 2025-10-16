"""
MACHO-GPT v3.4-mini Workflow Management
HVDC Project - Samsung C&T Logistics Integration
대화방 간 업무 연결 및 워크플로우 관리
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class ChatRoomType(Enum):
    TEAM = "team"          # 팀 대화방
    PROJECT = "project"    # 프로젝트 대화방
    TASK = "task"         # 태스크 대화방
    MEETING = "meeting"   # 미팅 대화방
    SUPPORT = "support"   # 지원 대화방

@dataclass
class BusinessTask:
    """비즈니스 태스크 클래스"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: str
    created_by: str
    chat_room_id: str
    due_date: Optional[str] = None
    dependencies: List[str] = None
    tags: List[str] = None
    progress: float = 0.0
    confidence: float = 0.85
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

@dataclass
class ChatRoom:
    """대화방 클래스 확장"""
    id: str
    name: str
    type: ChatRoomType
    members: List[str]
    active: bool = True
    created_by: str = "system"
    description: str = ""
    tags: List[str] = None
    parent_room_id: Optional[str] = None
    child_room_ids: List[str] = None
    connected_tasks: List[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    last_activity: str = None
    confidence: float = 0.90
    auto_archive_days: int = 30
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.child_room_ids is None:
            self.child_room_ids = []
        if self.connected_tasks is None:
            self.connected_tasks = []
        if self.last_activity is None:
            self.last_activity = datetime.now().isoformat()

class WorkflowManager:
    """MACHO-GPT 워크플로우 관리자"""
    
    def __init__(self, data_file: str = "data/workflow_data.json"):
        self.data_file = data_file
        self.chat_rooms: Dict[str, ChatRoom] = {}
        self.tasks: Dict[str, BusinessTask] = {}
        
        # 데이터 폴더가 없으면 생성
        data_dir = Path(data_file).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_data()
    
    def get_enum_value(self, enum_obj):
        """Safely get enum value whether it's a string or enum object"""
        if isinstance(enum_obj, str):
            return enum_obj
        return enum_obj.value if hasattr(enum_obj, 'value') else str(enum_obj)
        
    def load_data(self):
        """데이터 파일에서 워크플로우 데이터 로드"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 대화방 데이터 로드
                for room_data in data.get('chat_rooms', []):
                    room_data['type'] = ChatRoomType(room_data['type'])
                    room_data['priority'] = TaskPriority(room_data['priority'])
                    room = ChatRoom(**room_data)
                    self.chat_rooms[room.id] = room
                
                # 태스크 데이터 로드
                for task_data in data.get('tasks', []):
                    task_data['status'] = TaskStatus(task_data['status'])
                    task_data['priority'] = TaskPriority(task_data['priority'])
                    task = BusinessTask(**task_data)
                    self.tasks[task.id] = task
                    
        except FileNotFoundError:
            logger.info("워크플로우 데이터 파일이 없습니다. 기본 데이터를 생성합니다.")
            self._create_default_data()
        except Exception as e:
            logger.error(f"데이터 로드 오류: {str(e)}")
            self._create_default_data()
    
    def save_data(self):
        """워크플로우 데이터를 파일에 저장"""
        try:
            data = {
                'chat_rooms': [asdict(room) for room in self.chat_rooms.values()],
                'tasks': [asdict(task) for task in self.tasks.values()],
                'metadata': {
                    'version': '3.4-mini',
                    'last_updated': datetime.now().isoformat(),
                    'total_rooms': len(self.chat_rooms),
                    'total_tasks': len(self.tasks)
                }
            }
            
            # Enum을 문자열로 변환
            for room_data in data['chat_rooms']:
                room_data['type'] = self.get_enum_value(room_data['type'])
                room_data['priority'] = self.get_enum_value(room_data['priority'])
            
            for task_data in data['tasks']:
                task_data['status'] = self.get_enum_value(task_data['status'])
                task_data['priority'] = self.get_enum_value(task_data['priority'])
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"데이터 저장 오류: {str(e)}")
    
    def _create_default_data(self):
        """기본 대화방 및 태스크 데이터 생성"""
        # 기본 대화방 생성
        default_rooms = [
            {
                'name': '마케팅팀',
                'type': ChatRoomType.TEAM,
                'members': ['김민수', '이영희', '박철수'],
                'description': '마케팅 전략 및 캠페인 기획',
                'tags': ['marketing', 'campaign', 'strategy']
            },
            {
                'name': '개발팀',
                'type': ChatRoomType.TEAM,
                'members': ['정수민', '한지우', '최동혁'],
                'description': '시스템 개발 및 기술 지원',
                'tags': ['development', 'tech', 'system'],
                'priority': TaskPriority.HIGH
            },
            {
                'name': '디자인팀',
                'type': ChatRoomType.TEAM,
                'members': ['김디자', '이시안', '박UI'],
                'description': 'UI/UX 디자인 및 브랜딩',
                'tags': ['design', 'ui', 'branding']
            },
            {
                'name': '영업팀',
                'type': ChatRoomType.TEAM,
                'members': ['정영업', '한세일', '최고객'],
                'description': '고객 관리 및 영업 활동',
                'tags': ['sales', 'customer', 'business'],
                'priority': TaskPriority.URGENT
            },
            {
                'name': '경영진',
                'type': ChatRoomType.MEETING,
                'members': ['최대표', '김이사', '박부장'],
                'description': '경영 의사결정 및 전략 수립',
                'tags': ['management', 'strategy', 'decision'],
                'priority': TaskPriority.CRITICAL
            },
            {
                'name': 'HVDC 프로젝트',
                'type': ChatRoomType.PROJECT,
                'members': ['프로젝트매니저', '기술리더', '품질관리자'],
                'description': 'Samsung C&T HVDC 프로젝트 전용',
                'tags': ['hvdc', 'samsung', 'project', 'logistics']
            }
        ]
        
        for room_config in default_rooms:
            self.create_chat_room(**room_config)
        
        # 기본 태스크 생성
        self._create_sample_tasks()
        
        self.save_data()
    
    def _create_sample_tasks(self):
        """샘플 태스크 생성"""
        marketing_room_id = None
        dev_room_id = None
        
        for room_id, room in self.chat_rooms.items():
            if room.name == '마케팅팀':
                marketing_room_id = room_id
            elif room.name == '개발팀':
                dev_room_id = room_id
        
        if marketing_room_id:
            self.create_task(
                title="신규 캠페인 기획",
                description="Q1 신규 제품 런칭을 위한 마케팅 캠페인 기획 및 실행",
                chat_room_id=marketing_room_id,
                assignee="김민수",
                priority=TaskPriority.HIGH,
                due_date=(datetime.now() + timedelta(days=14)).isoformat(),
                tags=["campaign", "launch", "q1"]
            )
        
        if dev_room_id:
            self.create_task(
                title="시스템 성능 최적화",
                description="대시보드 응답 시간 개선 및 데이터베이스 쿼리 최적화",
                chat_room_id=dev_room_id,
                assignee="정수민",
                priority=TaskPriority.MEDIUM,
                due_date=(datetime.now() + timedelta(days=7)).isoformat(),
                tags=["optimization", "performance", "database"]
            )
    
    def create_chat_room(self, name: str, type: ChatRoomType, members: List[str], 
                        description: str = "", tags: List[str] = None, 
                        priority: TaskPriority = TaskPriority.MEDIUM,
                        parent_room_id: Optional[str] = None) -> str:
        """새 대화방 생성"""
        room_id = str(uuid.uuid4())
        
        room = ChatRoom(
            id=room_id,
            name=name,
            type=type,
            members=members,
            description=description,
            tags=tags or [],
            priority=priority,
            parent_room_id=parent_room_id
        )
        
        # 부모 대화방이 있는 경우 연결
        if parent_room_id and parent_room_id in self.chat_rooms:
            self.chat_rooms[parent_room_id].child_room_ids.append(room_id)
        
        self.chat_rooms[room_id] = room
        self.save_data()
        
        logger.info(f"새 대화방 생성: {name} (ID: {room_id})")
        return room_id
    
    def create_task(self, title: str, description: str, chat_room_id: str,
                   assignee: str, priority: TaskPriority = TaskPriority.MEDIUM,
                   due_date: Optional[str] = None, tags: List[str] = None,
                   dependencies: List[str] = None) -> str:
        """새 태스크 생성"""
        task_id = str(uuid.uuid4())
        
        task = BusinessTask(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            assignee=assignee,
            created_by="system",
            chat_room_id=chat_room_id,
            due_date=due_date,
            tags=tags or [],
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        
        # 대화방에 태스크 연결
        if chat_room_id in self.chat_rooms:
            self.chat_rooms[chat_room_id].connected_tasks.append(task_id)
        
        self.save_data()
        
        logger.info(f"새 태스크 생성: {title} (ID: {task_id})")
        return task_id
    
    def connect_rooms(self, parent_room_id: str, child_room_id: str) -> bool:
        """대화방 간 연결 설정"""
        if parent_room_id not in self.chat_rooms or child_room_id not in self.chat_rooms:
            return False
        
        parent_room = self.chat_rooms[parent_room_id]
        child_room = self.chat_rooms[child_room_id]
        
        # 양방향 연결 설정
        if child_room_id not in parent_room.child_room_ids:
            parent_room.child_room_ids.append(child_room_id)
        
        child_room.parent_room_id = parent_room_id
        
        self.save_data()
        logger.info(f"대화방 연결: {parent_room.name} -> {child_room.name}")
        return True
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """워크플로우 전체 요약 정보"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        urgent_tasks = len([t for t in self.tasks.values() if t.priority in [TaskPriority.URGENT, TaskPriority.CRITICAL]])
        
        # 대화방 타입별 통계
        room_stats = {}
        for room_type in ChatRoomType:
            room_stats[room_type.value] = len([r for r in self.chat_rooms.values() if r.type == room_type])
        
        return {
            "total_rooms": len(self.chat_rooms),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "urgent_tasks": urgent_tasks,
            "room_stats": room_stats,
            "confidence": self._calculate_workflow_confidence(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_workflow_confidence(self) -> float:
        """워크플로우 전체 신뢰도 계산"""
        if not self.tasks:
            return 0.85  # 기본 신뢰도
        
        total_confidence = 0
        for task in self.tasks.values():
            # 태스크 상태에 따른 가중치
            status_weight = {
                TaskStatus.COMPLETED: 1.0,
                TaskStatus.IN_PROGRESS: 0.8,
                TaskStatus.PENDING: 0.6,
                TaskStatus.BLOCKED: 0.3,
                TaskStatus.CANCELLED: 0.1
            }
            
            task_confidence = task.confidence * status_weight.get(task.status, 0.5)
            total_confidence += task_confidence
        
        avg_confidence = total_confidence / len(self.tasks)
        return min(avg_confidence, 1.0)
    
    def get_connected_workflow(self, room_id: str) -> Dict[str, Any]:
        """특정 대화방과 연결된 워크플로우 정보"""
        if room_id not in self.chat_rooms:
            return {}
        
        room = self.chat_rooms[room_id]
        
        # 연결된 태스크들
        connected_tasks = [self.tasks[task_id] for task_id in room.connected_tasks if task_id in self.tasks]
        
        # 하위 대화방들
        child_rooms = [self.chat_rooms[child_id] for child_id in room.child_room_ids if child_id in self.chat_rooms]
        
        # 상위 대화방
        parent_room = self.chat_rooms.get(room.parent_room_id) if room.parent_room_id else None
        
        return {
            "room": asdict(room),
            "connected_tasks": [asdict(task) for task in connected_tasks],
            "child_rooms": [asdict(child) for child in child_rooms],
            "parent_room": asdict(parent_room) if parent_room else None,
            "workflow_health": self._calculate_room_health(room_id)
        }
    
    def _calculate_room_health(self, room_id: str) -> Dict[str, Any]:
        """대화방 워크플로우 건강도 계산"""
        if room_id not in self.chat_rooms:
            return {}
        
        room = self.chat_rooms[room_id]
        tasks = [self.tasks[task_id] for task_id in room.connected_tasks if task_id in self.tasks]
        
        if not tasks:
            return {
                "status": "healthy",
                "confidence": 0.85,
                "issues": [],
                "recommendations": ["태스크를 생성하여 업무를 관리해보세요."]
            }
        
        issues = []
        recommendations = []
        
        # 지연된 태스크 확인
        overdue_tasks = []
        for task in tasks:
            if task.due_date and task.status != TaskStatus.COMPLETED:
                due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                if due_date < datetime.now():
                    overdue_tasks.append(task.title)
        
        if overdue_tasks:
            issues.append(f"지연된 태스크: {len(overdue_tasks)}개")
            recommendations.append("지연된 태스크의 우선순위를 재검토하세요.")
        
        # 블록된 태스크 확인
        blocked_tasks = [t for t in tasks if t.status == TaskStatus.BLOCKED]
        if blocked_tasks:
            issues.append(f"블록된 태스크: {len(blocked_tasks)}개")
            recommendations.append("블록된 태스크의 장애물을 해결하세요.")
        
        # 건강도 계산
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        health_score = completed_tasks / total_tasks if total_tasks > 0 else 0.85
        
        status = "healthy"
        if len(issues) > 2:
            status = "critical"
        elif len(issues) > 0:
            status = "warning"
        
        return {
            "status": status,
            "confidence": health_score,
            "completion_rate": health_score,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overdue_tasks": len(overdue_tasks),
            "blocked_tasks": len(blocked_tasks),
            "issues": issues,
            "recommendations": recommendations
        }
    
    def update_task_status(self, task_id: str, status: TaskStatus, progress: float = None) -> bool:
        """태스크 상태 업데이트"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = status
        task.updated_at = datetime.now().isoformat()
        
        if progress is not None:
            task.progress = min(max(progress, 0.0), 100.0)
        
        # 완료된 태스크의 경우 진행률을 100%로 설정
        if status == TaskStatus.COMPLETED:
            task.progress = 100.0
        
        self.save_data()
        logger.info(f"태스크 상태 업데이트: {task.title} -> {status.value}")
        return True
    
    def get_team_workload(self) -> Dict[str, Any]:
        """팀별 업무량 분석"""
        team_workload = {}
        
        for room in self.chat_rooms.values():
            if room.type == ChatRoomType.TEAM:
                tasks = [self.tasks[task_id] for task_id in room.connected_tasks if task_id in self.tasks]
                
                member_tasks = {}
                for member in room.members:
                    member_tasks[member] = len([t for t in tasks if t.assignee == member])
                
                team_workload[room.name] = {
                    "total_tasks": len(tasks),
                    "member_tasks": member_tasks,
                    "avg_tasks_per_member": len(tasks) / len(room.members) if room.members else 0,
                    "priority_distribution": self._get_priority_distribution(tasks)
                }
        
        return team_workload
    
    def _get_priority_distribution(self, tasks: List[BusinessTask]) -> Dict[str, int]:
        """태스크 우선순위 분포"""
        distribution = {priority.value: 0 for priority in TaskPriority}
        
        for task in tasks:
            distribution[task.priority.value] += 1
        
        return distribution
    
    def generate_workflow_triggers(self) -> List[str]:
        """워크플로우 기반 자동 트리거 생성"""
        triggers = []
        
        # 워크플로우 신뢰도 확인
        confidence = self._calculate_workflow_confidence()
        if confidence < 0.90:
            triggers.append("/switch_mode ZERO")
            triggers.append("/workflow_optimization urgent")
        
        # 지연된 태스크 확인
        overdue_count = 0
        for task in self.tasks.values():
            if task.due_date and task.status != TaskStatus.COMPLETED:
                due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                if due_date < datetime.now():
                    overdue_count += 1
        
        if overdue_count > 3:
            triggers.append("/urgent_processor task_management")
            triggers.append("/alert_system overdue_tasks")
        
        # 크리티컬 태스크 확인
        critical_tasks = [t for t in self.tasks.values() if t.priority == TaskPriority.CRITICAL]
        if len(critical_tasks) > 2:
            triggers.append("/escalate_priority critical_review")
        
        # 팀 업무량 불균형 확인
        workload = self.get_team_workload()
        for team_name, team_data in workload.items():
            if team_data["avg_tasks_per_member"] > 10:
                triggers.append(f"/workload_balancer {team_name}")
        
        return triggers

# 전역 워크플로우 매니저 인스턴스
workflow_manager = WorkflowManager() 