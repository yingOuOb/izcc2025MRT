from typing import Optional

from . import db
from ..core.team import Team


class Teams(db.Model):
    __tablename__ = "teams"
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(32), unique=True, nullable=False)
    players = db.Column(db.PickleType(), nullable=False)
    admins = db.Column(db.PickleType(), nullable=False)
    point = db.Column(db.Integer, default=10)

    start_location_defined = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(64), default="")
    target_location = db.Column(db.String(64), default="")

    point_log = db.Column(db.PickleType(), default=[])
    event_log = db.Column(db.PickleType(), default=[])
    step = db.Column(db.Integer, default=0)

    current_mission_finished = db.Column(db.Boolean, default=True)
    current_card = db.Column(db.String(64), nullable=True)

    imprisoned_time = db.Column(db.Integer, default=0)
    is_imprisoned = db.Column(db.Boolean, default=False)

    stations = db.Column(db.PickleType(), default=[])
    owned_stations = db.Column(db.PickleType(), default=[])
    combos = db.Column(db.PickleType(), default=[])
    choice = db.Column(db.PickleType(), default=[])

    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def __init__(self, team:Team) -> None:
        self.name: str = team.name
        self.start_location_defined: bool = team.start_location_defined
        self.location: str = team.location
        self.target_location: Optional[str] = team.target_location
        self.players = team.players if team.players is not None else []
        self.admins = team.admins if team.admins is not None else []
        
        self.point_log: list[dict] = team.point_log if team.point_log is not None else [] # {"point": int, "reason": str, "time": str}
        self.event_log: list[dict] = team.event_log if team.event_log is not None else [] # {"event": str, "time": str}
        self.point: int = team.point
        self.step: int = team.step
        
        self.current_mission_finished: bool = team.current_mission_finished
        self.current_card: Optional[str] = team.current_card
        
        self.imprisoned_time: int = team.imprisoned_time
        self.is_imprisoned: bool = team.is_imprisoned
        
        self.stations: list[str] = team.stations
        self.owned_stations: list[str] = team.owned_stations
        self.combos: list[str] = team.combos
        self.choice: list[str] = team.choice
    
    def __repr__(self):
        return f"<Team {self.name}>"