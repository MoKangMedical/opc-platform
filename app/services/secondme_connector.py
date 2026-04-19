"""
OPC SuperAgent - SecondMe Connector
数字分身创建/查询/管理
"""

import os
import json
import httpx
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

SECONDME_API = "https://app.mindos.com/gate/lab"
SECONDME_TOKEN = "lba_at_b68964ac5cbb50eee8ac87eaadfe122fe5d8261684971e379656435f019f7b4d"


@dataclass
class SecondMeProfile:
    """SecondMe 数字分身"""
    user_id: str = ""
    nickname: str = ""
    route: str = ""
    homepage: str = ""
    focus_areas: List[str] = field(default_factory=list)
    bio: str = ""
    avatar_url: str = ""


class SecondMeConnector:
    """SecondMe API 连接器"""

    def __init__(self, api_base: str = SECONDME_TOKEN, token: str = SECONDME_TOKEN):
        self.api_base = SECONDME_API
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self._cache: Dict[str, Any] = {}

    async def _request(self, method: str, path: str, data: dict = None) -> Optional[dict]:
        """发送请求"""
        url = f"{self.api_base}{path}"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                if method == "GET":
                    resp = await client.get(url, headers=self.headers)
                elif method == "POST":
                    resp = await client.post(url, headers=self.headers, json=data)
                else:
                    return None

                if resp.status_code == 200:
                    return resp.json()
                else:
                    logger.warning(f"SecondMe API {method} {path} returned {resp.status_code}")
                    return None
        except Exception as e:
            logger.error(f"SecondMe API error: {e}")
            return None

    async def get_user_profile(self, user_id: str = "2268309") -> Optional[SecondMeProfile]:
        """获取用户数字分身"""
        cache_key = f"profile_{user_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        data = await self._request("GET", f"/user/{user_id}")
        if data:
            profile = SecondMeProfile(
                user_id=str(data.get("id", user_id)),
                nickname=data.get("nickname", ""),
                route=data.get("route", ""),
                homepage=data.get("homepage", f"https://second.me/{data.get('route', '')}"),
                focus_areas=data.get("focus_areas", []),
                bio=data.get("bio", ""),
            )
            self._cache[cache_key] = profile
            return profile

        # 返回默认profile
        return SecondMeProfile(
            user_id=user_id,
            nickname="Lin",
            route="xiaolin110",
            homepage="https://second.me/xiaolin110",
            focus_areas=["罕见病研究", "临床研究方法学", "AI制药", "消费医疗", "数字医疗创业"],
        )

    async def create_agent_from_secondme(
        self, user_id: str = "2268309"
    ) -> Optional[dict]:
        """从SecondMe创建Agent"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            return None

        agent_card = {
            "agent_id": f"sm_{profile.user_id}",
            "name": f"{profile.nickname}的Agent",
            "owner_name": profile.nickname,
            "avatar": "🧠",
            "role": " · ".join(profile.focus_areas[:2]) if profile.focus_areas else "数字分身",
            "organization": "SecondMe",
            "skills": profile.focus_areas,
            "bio": profile.bio or f"基于SecondMe创建的数字分身，擅长{', '.join(profile.focus_areas[:3])}",
            "secondme_route": profile.route,
            "capabilities": ["数字分身", "知识问答", "项目匹配"],
            "status": "online",
        }
        return agent_card

    async def chat_with_secondme(
        self, route: str, message: str
    ) -> Optional[str]:
        """与SecondMe数字分身对话"""
        data = await self._request("POST", f"/chat/{route}", {
            "message": message,
            "stream": False,
        })
        if data:
            return data.get("response", data.get("content", ""))
        return None

    async def list_available_personas(self) -> List[dict]:
        """获取可用的数字分身列表"""
        data = await self._request("GET", "/personas")
        if data and isinstance(data, list):
            return data
        return []


# 全局实例
_connector = None

def get_connector() -> SecondMeConnector:
    global _connector
    if _connector is None:
        _connector = SecondMeConnector()
    return _connector
