"""
OPC Platform - 匹配算法服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Optional
import re
from collections import Counter

from app.models import User, Project, ProjectBid, Mentor

class MatchingService:
    """智能匹配服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_skill_match_score(self, user_skills: List[str], project_keywords: List[str]) -> float:
        """计算技能匹配分数"""
        if not user_skills or not project_keywords:
            return 0.0
        
        # 标准化技能名称
        user_skills_lower = [s.lower().strip() for s in user_skills]
        project_keywords_lower = [k.lower().strip() for k in project_keywords]
        
        # 计算匹配的技能数量
        matched_skills = set(user_skills_lower) & set(project_keywords_lower)
        
        # 计算分数（0-100）
        if not project_keywords_lower:
            return 0.0
        
        match_ratio = len(matched_skills) / len(project_keywords_lower)
        return min(match_ratio * 100, 100.0)
    
    def extract_keywords_from_project(self, project: Project) -> List[str]:
        """从项目中提取关键词"""
        keywords = []
        
        # 从行业提取
        if project.industry:
            keywords.append(project.industry)
        
        # 从技术领域提取
        if project.technology_field:
            # 分割技术领域（可能用逗号、分号等分隔）
            tech_keywords = re.split(r'[,;，；、\s]+', project.technology_field)
            keywords.extend([k.strip() for k in tech_keywords if k.strip()])
        
        # 从描述中提取常见技术关键词
        if project.description:
            common_tech = [
                'AI', '人工智能', '机器学习', '深度学习', 'NLP', '自然语言处理',
                '计算机视觉', 'CV', '大数据', '云计算', '区块链', 'IoT', '物联网',
                'SaaS', 'PaaS', 'API', '微服务', '容器化', 'DevOps',
                'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Angular',
                'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
                '数据分析', '数据挖掘', '数据可视化', 'BI', '商业智能',
                '电商', '金融科技', '教育科技', '医疗健康', '智能制造'
            ]
            
            description_lower = project.description.lower()
            for tech in common_tech:
                if tech.lower() in description_lower:
                    keywords.append(tech)
        
        # 去重
        return list(set(keywords))
    
    def match_users_to_project(self, project_id: int, limit: int = 20) -> List[Dict]:
        """为项目匹配合适的用户"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []
        
        # 提取项目关键词
        project_keywords = self.extract_keywords_from_project(project)
        
        # 获取所有活跃用户
        users = self.db.query(User).filter(
            User.is_active == True,
            User.skills.isnot(None)
        ).all()
        
        matches = []
        for user in users:
            if not user.skills:
                continue
            
            # 计算匹配分数
            match_score = self.calculate_skill_match_score(user.skills, project_keywords)
            
            if match_score > 0:
                matches.append({
                    "user_id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "avatar_url": user.avatar_url,
                    "skills": user.skills,
                    "match_score": match_score,
                    "match_reasons": self._get_match_reasons(user.skills, project_keywords)
                })
        
        # 按匹配分数排序
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches[:limit]
    
    def match_projects_to_user(self, user_id: int, limit: int = 20) -> List[Dict]:
        """为用户匹配合适的项目"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.skills:
            return []
        
        # 获取所有开放的项目
        projects = self.db.query(Project).filter(
            Project.status == "open"
        ).all()
        
        matches = []
        for project in projects:
            # 提取项目关键词
            project_keywords = self.extract_keywords_from_project(project)
            
            # 计算匹配分数
            match_score = self.calculate_skill_match_score(user.skills, project_keywords)
            
            if match_score > 0:
                matches.append({
                    "project_id": project.id,
                    "title": project.title,
                    "publisher_name": project.publisher_name,
                    "industry": project.industry,
                    "budget_min": project.budget_min,
                    "budget_max": project.budget_max,
                    "match_score": match_score,
                    "match_reasons": self._get_match_reasons(user.skills, project_keywords)
                })
        
        # 按匹配分数排序
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches[:limit]
    
    def _get_match_reasons(self, user_skills: List[str], project_keywords: List[str]) -> List[str]:
        """获取匹配原因"""
        user_skills_lower = [s.lower().strip() for s in user_skills]
        project_keywords_lower = [k.lower().strip() for k in project_keywords]
        
        matched_skills = set(user_skills_lower) & set(project_keywords_lower)
        return list(matched_skills)
    
    def get_mentor_matches(self, user_id: int, limit: int = 10) -> List[Dict]:
        """为用户匹配合适的导师"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 获取所有可用的导师
        mentors = self.db.query(Mentor).filter(
            Mentor.is_available == True
        ).all()
        
        matches = []
        for mentor in mentors:
            match_score = 0
            match_reasons = []
            
            # 技能匹配
            if user.skills and mentor.skills:
                mentor_skills_lower = [s.lower().strip() for s in mentor.skills]
                user_skills_lower = [s.lower().strip() for s in user.skills]
                
                matched_skills = set(user_skills_lower) & set(mentor_skills_lower)
                if matched_skills:
                    match_score += len(matched_skills) * 20
                    match_reasons.extend(list(matched_skills))
            
            # 专业领域匹配
            if user.skills and mentor.specialties:
                mentor_specialties_lower = [s.lower().strip() for s in mentor.specialties]
                user_skills_lower = [s.lower().strip() for s in user.skills]
                
                matched_specialties = set(user_skills_lower) & set(mentor_specialties_lower)
                if matched_specialties:
                    match_score += len(matched_specialties) * 15
                    match_reasons.extend([f"专业领域: {s}" for s in matched_specialties])
            
            # 评分权重
            match_score += mentor.rating * 5
            
            if match_score > 0:
                matches.append({
                    "mentor_id": mentor.id,
                    "name": mentor.name,
                    "title": mentor.title,
                    "avatar_emoji": mentor.avatar_emoji,
                    "bio": mentor.bio,
                    "skills": mentor.skills,
                    "specialties": mentor.specialties,
                    "rating": mentor.rating,
                    "hourly_rate": mentor.hourly_rate,
                    "match_score": match_score,
                    "match_reasons": list(set(match_reasons))
                })
        
        # 按匹配分数排序
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches[:limit]
    
    def get_matching_stats(self) -> Dict:
        """获取匹配统计信息"""
        total_users = self.db.query(User).filter(User.is_active == True).count()
        users_with_skills = self.db.query(User).filter(
            User.is_active == True,
            User.skills.isnot(None)
        ).count()
        
        total_projects = self.db.query(Project).filter(Project.status == "open").count()
        
        total_bids = self.db.query(ProjectBid).count()
        accepted_bids = self.db.query(ProjectBid).filter(
            ProjectBid.status == "accepted"
        ).count()
        
        return {
            "total_users": total_users,
            "users_with_skills": users_with_skills,
            "skill_coverage_rate": round(users_with_skills / total_users * 100, 2) if total_users > 0 else 0,
            "total_open_projects": total_projects,
            "total_bids": total_bids,
            "accepted_bids": accepted_bids,
            "bid_acceptance_rate": round(accepted_bids / total_bids * 100, 2) if total_bids > 0 else 0
        }
