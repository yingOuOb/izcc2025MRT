from datetime import datetime
from typing import Optional

from ..game_config import START_STATION

class Team:
    def __init__(self, name: str, players: Optional[list[str]]=None, admins: Optional[list[str]]=None, location: Optional[str]=None) -> None:
        self.name: str = name
        self.start_location_defined: bool = location is not None
        self.location: str = location or START_STATION
        self.target_location: Optional[str] = location or START_STATION
        self.players = players if players is not None else []
        self.admins = admins if admins is not None else []
        
        self.point_log: list[dict] = [] # {"point": int, "reason": str, "time": str}
        self.event_log: list[dict] = [] # {"event": str, "time": str}
        self.point: int = 10
        self.step: int = 0
        
        self.current_mission_finished: bool = True # 用2表示正在移動過程 # 開玩笑的別這麼做
        self.current_card: Optional[str] = None
        
        self.imprisoned_time: int = 0
        self.is_imprisoned: bool = False
        
        self.stations: list[str] = []
        self.owned_stations: list[str] = []
        self.combos: list[str] = []
        self.choice: list[str] = []
        
        
    def __str__(self) -> str:
        return self.name
    
    
    def __repr__(self) -> str:
        return self.name
    
    
    def add_point_log(self, point: int, reason: str) -> None:
        data = {
            "point": point,
            "reason": reason,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.point_log.append(data)

    def add_event_log(self, event: str) -> None:
        data = {
            "event": event,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.event_log.append(data)