
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from base import Base

class DeviceStates(Base):
    __tablename__ = 'device_states'
    id = Column(Integer, primary_key=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    state_id = Column(String, ForeignKey("states.id"))

    device = relationship("Devices", foreign_keys=[device_id])
    state = relationship("States", foreign_keys=[state_id])

    def __init__(self, device_id, state_id):
        self.device_id = device_id
        self.state_id = state_id
