import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.orm import relationship

from base import Base

class Devices(Base):
    __tablename__ = 'devices'
    device_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    plc = Column(String, nullable=False)    
    access_group = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __init__(self, name, plc, access_group, device_type):
        self.name = name
        self.plc = plc
        self.access_group = access_group
        self.device_type = device_type
