import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.orm import relationship

from base import Base

class Devices(Base):
    __tablename__ = 'devices'
    device_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=True)
    plc = Column(String)    
    access_group = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __init__(self, name, plc, access_group, device_type=None):
        self.name = name
        self.plc = plc
        self.access_group = access_group
        self.device_type = device_type
