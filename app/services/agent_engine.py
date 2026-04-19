"""
OPC SuperAgent - Agent Engine
能力卡片 + 技能匹配 + 项目推荐引擎
"""

import json
import os
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# 技能图谱
SKILL_GRAPH = {
    # AI核心技术
    "人工智能": ["机器学习", "深度学习", "NLP", "计算机视觉", "强化学习"],
    "大模型": ["NLP", "模型微调", "RAG", "Prompt工程"],
    "计算机视觉": ["目标检测", "图像分割", "OCR", "视觉检测"],
    "NLP": ["文本分类", "情感分析", "知识图谱", "机器翻译"],
    # 行业领域
    "智能制造": ["工业IoT", "预测性维护", "视觉检测", "数字孪生", "工艺优化"],
    "智慧农业": ["遥感分析", "无人机", "精准农业", "作物监测"],
    "智慧港口": ["无人作业", "SLAM", "自动化控制", "物流优化"],
    "安全生产": ["视频监控", "风险预警", "隐患排查", "应急指挥"],
    "医疗健康": ["医学影像", "辅助诊断", "健康管理", "电子病历"],
    "环保": ["大气监测", "水质分析", "遥感分析", "碳排放管理"],
    # 技术栈
    "无人机": ["飞行控制", "航拍", "路径规划", "遥感分析"],
    "数字孪生": ["3D建模", "实时渲染", "仿真", "工业IoT"],
    "知识图谱": ["NLP", "图数据库", "实体抽取", "关系推理"],
    "边缘计算": ["模型量化", "嵌入式部署", "实时推理"],
}


@dataclass
class SkillProfile:
    """技能画像"""
    name: str
    level: float = 1.0  # 0-1
    category: str = ""  # core, domain, tool

    def to_dict(self):
        return asdict(self)


@dataclass
class AgentProfile:
    """Agent完整画像"""
    agent_id: str
    name: str
    owner_name: str
    avatar: str = "🤖"
    role: str = ""
    organization: str = ""
    bio: str = ""
    skills: List[SkillProfile] = field(default_factory=list)
    project_ids: List[str] = field(default_factory=list)
    secondme_route: Optional[str] = None
    status: str = "online"

    def skill_names(self) -> List[str]:
        return [s.name for s in self.skills]

    def skill_vector(self, all_skills: List[str]) -> List[float]:
        """生成技能向量"""
        skill_map = {s.name: s.level for s in self.skills}
        return [skill_map.get(sk, 0.0) for sk in all_skills]


@dataclass
class ProjectMatch:
    """项目匹配结果"""
    project_id: str
    project_title: str
    publisher: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    recommendation: str = ""
    budget_display: str = ""


class MatchingEngine:
    """项目-人才匹配引擎"""

    def __init__(self, projects_path: str = None):
        self.projects: List[dict] = []
        self.all_skills: List[str] = []
        self._skill_cache: Dict[str, set] = {}

        if projects_path and os.path.exists(projects_path):
            self.load_projects(projects_path)

    def load_projects(self, path: str):
        """加载项目数据"""
        with open(path, "r", encoding="utf-8") as f:
            self.projects = json.load(f)
        self._build_skill_index()
        logger.info(f"Loaded {len(self.projects)} projects")

    def _build_skill_index(self):
        """构建技能索引"""
        skill_set = set()
        for proj in self.projects:
            proj_skills = set()
            # 从technology_field提取
            for tf in proj.get("technology_field", []):
                proj_skills.add(tf)
                # 展开子技能
                if tf in SKILL_GRAPH:
                    proj_skills.update(SKILL_GRAPH[tf])
            # 从tags提取
            for tag in proj.get("tags", []):
                proj_skills.add(tag)
            # 从industry提取
            ind = proj.get("industry", "")
            if ind:
                proj_skills.add(ind)
                if ind in SKILL_GRAPH:
                    proj_skills.update(SKILL_GRAPH[ind])

            self._skill_cache[proj.get("project_code", str(id(proj)))] = proj_skills
            skill_set.update(proj_skills)

        self.all_skills = sorted(skill_set)

    def match_agent_to_projects(
        self, agent: AgentProfile, top_k: int = 10, min_score: float = 0.1
    ) -> List[ProjectMatch]:
        """Agent匹配项目"""
        agent_skills = set(s.name.lower() for s in agent.skills)
        # 展开Agent技能
        expanded = set(agent_skills)
        for sk in agent.skills:
            if sk.name in SKILL_GRAPH:
                expanded.update(s.lower() for s in SKILL_GRAPH[sk.name])

        results = []
        for proj in self.projects:
            proj_code = proj.get("project_code", "")
            proj_skills = self._skill_cache.get(proj_code, set())
            proj_skills_lower = set(s.lower() for s in proj_skills)

            if not proj_skills_lower:
                continue

            # Jaccard相似度 + 加权
            overlap = expanded & proj_skills_lower
            union = expanded | proj_skills_lower
            score = len(overlap) / len(union) if union else 0

            # 技能等级加权
            for sk in agent.skills:
                if sk.name.lower() in overlap:
                    score += sk.level * 0.05  # bonus for expertise

            score = min(score, 1.0)

            if score >= min_score:
                matched = sorted(overlap)
                missing = sorted(proj_skills_lower - expanded)[:5]
                budget = proj.get("budget_display", "")
                if not budget and proj.get("budget_min", 0) > 0:
                    budget = f"{proj['budget_min']//10000}-{proj['budget_max']//10000}万"

                results.append(
                    ProjectMatch(
                        project_id=proj_code,
                        project_title=proj.get("title", ""),
                        publisher=proj.get("publisher_name", ""),
                        match_score=round(score, 3),
                        matched_skills=matched[:8],
                        missing_skills=missing,
                        budget_display=budget,
                        recommendation=self._gen_recommendation(score, matched, missing),
                    )
                )

        results.sort(key=lambda x: x.match_score, reverse=True)
        return results[:top_k]

    def match_project_to_agents(
        self, project_code: str, agents: List[AgentProfile], top_k: int = 5
    ) -> List[Tuple[AgentProfile, float, List[str]]]:
        """项目匹配Agent"""
        proj_skills = self._skill_cache.get(project_code, set())
        if not proj_skills:
            return []

        proj_skills_lower = set(s.lower() for s in proj_skills)
        results = []

        for agent in agents:
            agent_skills = set(s.name.lower() for s in agent.skills)
            expanded = set(agent_skills)
            for sk in agent.skills:
                if sk.name in SKILL_GRAPH:
                    expanded.update(s.lower() for s in SKILL_GRAPH[sk.name])

            overlap = expanded & proj_skills_lower
            union = expanded | proj_skills_lower
            score = len(overlap) / len(union) if union else 0

            if score > 0.1:
                results.append((agent, round(score, 3), sorted(overlap)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _gen_recommendation(self, score: float, matched: List[str], missing: List[str]) -> str:
        """生成推荐语"""
        if score > 0.6:
            return f"高度匹配！你的{', '.join(matched[:3])}经验与该项目需求高度吻合，建议立即申报。"
        elif score > 0.3:
            msg = f"较好匹配。你的核心技能{', '.join(matched[:3])}覆盖了部分需求。"
            if missing:
                msg += f" 可补充学习: {', '.join(missing[:2])}。"
            return msg
        else:
            return f"部分匹配。你的{', '.join(matched[:2])}经验可作为切入点，建议深入了解项目详情。"

    def get_skill_suggestions(self, agent_skills: List[str]) -> List[str]:
        """推荐可拓展的技能"""
        suggestions = set()
        for sk in agent_skills:
            if sk in SKILL_GRAPH:
                for related in SKILL_GRAPH[sk]:
                    if related not in agent_skills:
                        suggestions.add(related)
        return sorted(suggestions)[:10]

    def get_stats(self) -> dict:
        """统计信息"""
        industries = Counter(p.get("industry", "") for p in self.projects)
        return {
            "total_projects": len(self.projects),
            "total_skills": len(self.all_skills),
            "top_industries": industries.most_common(10),
        }


# 全局实例
_engine = None

def get_engine() -> MatchingEngine:
    global _engine
    if _engine is None:
        # 尝试多个可能的数据路径
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "jiangsu_ai_scenarios.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "jiangsu_ai_scenarios.json"),
            os.path.join(os.getcwd(), "data", "jiangsu_ai_scenarios.json"),
            "/opt/render/project/src/data/jiangsu_ai_scenarios.json",
        ]
        data_path = None
        for p in possible_paths:
            if os.path.exists(p):
                data_path = p
                break
        if data_path:
            _engine = MatchingEngine(data_path)
        else:
            _engine = MatchingEngine()
            print(f"⚠️ Warning: Could not find jiangsu_ai_scenarios.json in {possible_paths}")
    return _engine
