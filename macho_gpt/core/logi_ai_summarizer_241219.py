"""
MACHO-GPT v3.4-mini AI Summarizer for WhatsApp Messages
HVDC Project - Samsung C&T Logistics
"""

import json
import yaml
import logging
from datetime import datetime
from typing import Dict, List, Optional
import openai
from pathlib import Path

class LogiAISummarizer:
    """AI-powered WhatsApp message summarizer for HVDC project"""
    
    def __init__(self, config_path: str = "configs/openai_config.yaml"):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self._setup_openai()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load OpenAI configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            return {}
            
    def _setup_openai(self):
        """Setup OpenAI client"""
        try:
            api_key = self.config.get('openai', {}).get('api_key')
            if api_key:
                openai.api_key = api_key
                self.logger.info("OpenAI API configured successfully")
            else:
                self.logger.error("OpenAI API key not found in config")
        except Exception as e:
            self.logger.error(f"Failed to setup OpenAI: {e}")
            
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def analyze_chat_messages(self, messages: List[str], chat_title: str) -> Dict:
        """Analyze WhatsApp chat messages using AI"""
        try:
            # Prepare messages for analysis
            message_text = "\n".join(messages[:50])  # Limit to first 50 messages
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(chat_title, message_text)
            
            # Get AI analysis
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model=self.config.get('openai', {}).get('model', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": "You are a logistics expert analyzing WhatsApp messages for HVDC project."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get('openai', {}).get('max_tokens', 2000),
                temperature=self.config.get('openai', {}).get('temperature', 0.3)
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            analysis = self._parse_analysis_response(analysis_text)
            
            return {
                "chat_title": chat_title,
                "message_count": len(messages),
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.95
            }
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {chat_title}: {e}")
            return {
                "chat_title": chat_title,
                "message_count": len(messages),
                "analysis": {"error": str(e)},
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.0
            }
            
    def _create_analysis_prompt(self, chat_title: str, messages: str) -> str:
        """Create analysis prompt for AI"""
        return f"""
다음은 HVDC 프로젝트의 WhatsApp 채팅방 "{chat_title}" 메시지들입니다.
이 메시지들을 분석하여 다음 항목들을 한국어로 요약해주세요:

1. 주요 주제 및 내용 요약
2. 중요한 일정이나 마감일
3. 진행 중인 작업 현황
4. 문제점이나 이슈
5. 필요한 조치사항
6. 핵심 키워드 (5-10개)
7. 전체적인 톤 (긍정/부정/중립)

메시지 내용:
{messages}

분석 결과를 JSON 형식으로 제공해주세요:
{{
    "summary": "주요 내용 요약",
    "schedule": "중요 일정",
    "progress": "진행 현황", 
    "issues": "문제점",
    "actions": "조치사항",
    "keywords": ["키워드1", "키워드2"],
    "sentiment": "긍정/부정/중립"
}}
"""
        
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse AI analysis response"""
        try:
            # Try to extract JSON from response
            if "{" in response_text and "}" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Fallback to text analysis
                return {
                    "summary": response_text,
                    "schedule": "일정 정보 없음",
                    "progress": "진행 현황 정보 없음",
                    "issues": "문제점 정보 없음", 
                    "actions": "조치사항 정보 없음",
                    "keywords": [],
                    "sentiment": "중립"
                }
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON response, using text fallback")
            return {
                "summary": response_text,
                "schedule": "일정 정보 없음",
                "progress": "진행 현황 정보 없음", 
                "issues": "문제점 정보 없음",
                "actions": "조치사항 정보 없음",
                "keywords": [],
                "sentiment": "중립"
            }
            
    def analyze_extraction_file(self, file_path: str) -> Dict:
        """Analyze WhatsApp extraction file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            results = []
            total_messages = 0
            
            for chat_data in data:
                if chat_data.get('status') == 'SUCCESS' and chat_data.get('messages'):
                    messages = chat_data['messages']
                    chat_title = chat_data['chat_title']
                    
                    self.logger.info(f"Analyzing {chat_title} ({len(messages)} messages)")
                    analysis = self.analyze_chat_messages(messages, chat_title)
                    results.append(analysis)
                    total_messages += len(messages)
                    
            # Create summary report
            summary_report = {
                "total_chats_analyzed": len(results),
                "total_messages": total_messages,
                "analysis_timestamp": datetime.now().isoformat(),
                "chat_analyses": results,
                "overall_summary": self._create_overall_summary(results)
            }
            
            return summary_report
            
        except Exception as e:
            self.logger.error(f"Failed to analyze extraction file: {e}")
            return {"error": str(e)}
            
    def _create_overall_summary(self, analyses: List[Dict]) -> Dict:
        """Create overall summary from all chat analyses"""
        all_keywords = []
        all_issues = []
        all_actions = []
        
        for analysis in analyses:
            if 'analysis' in analysis:
                analysis_data = analysis['analysis']
                if isinstance(analysis_data, dict):
                    all_keywords.extend(analysis_data.get('keywords', []))
                    all_issues.append(analysis_data.get('issues', ''))
                    all_actions.append(analysis_data.get('actions', ''))
                    
        return {
            "total_keywords": len(set(all_keywords)),
            "common_keywords": list(set(all_keywords))[:10],
            "main_issues": [issue for issue in all_issues if issue and issue != "문제점 정보 없음"],
            "required_actions": [action for action in all_actions if action and action != "조치사항 정보 없음"]
        }
        
    def save_analysis(self, analysis: Dict, output_path: str):
        """Save analysis results to file"""
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Analysis saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis: {e}")

def main():
    """Main function for testing"""
    summarizer = LogiAISummarizer()
    
    # Test with latest extraction file
    latest_file = "data/hvdc_whatsapp_extraction_20250724_212859.json"
    
    if Path(latest_file).exists():
        print("🤖 MACHO-GPT AI 분석 시작...")
        analysis = summarizer.analyze_extraction_file(latest_file)
        
        # Save results
        output_file = f"reports/ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summarizer.save_analysis(analysis, output_file)
        
        print(f"✅ AI 분석 완료: {output_file}")
    else:
        print(f"❌ 파일을 찾을 수 없음: {latest_file}")

if __name__ == "__main__":
    main() 