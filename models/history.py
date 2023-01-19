import datetime
from hashlib import new

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.orm import relationship

from base import Base

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    state_id = Column(String, ForeignKey("states.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    state = relationship("States", foreign_keys=[state_id])

    name = Column(String, nullable=False)
    beamline = Column(String, nullable=False)
    #Usually a bitmask
    nBeamClassRange = Column(String, nullable=False)
    neVRange = Column(String, nullable=False)
    nTran = Column(String, nullable=False)
    nRate = Column(String, nullable=False)

    ap_name = Column(String, nullable=True)
    ap_ygap = Column(String, nullable=True)
    ap_ycenter = Column(String, nullable=True)
    ap_xgap = Column(String, nullable=True)
    ap_xcenter = Column(String, nullable=True)

    damage_limit = Column(String, nullable=True)
    pulse_energy = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    special = Column(Boolean, default=False)
    reactive_temp = Column(String, nullable=True)
    reactive_pressure = Column(String, nullable=True)


    def __init__ (self,state_id,name,beamline,nBeamClassRange,neVRange,nTran,nRate,ap_name,ap_ygap,ap_ycenter,ap_xgap,ap_xcenter,damage_limit,pulse_energy,notes,special,reactive_temp,reactive_pressure):
        self.state_id = state_id
        self.name = name
        self.beamline = beamline
        self.nBeamClassRange = nBeamClassRange
        self.neVRange = neVRange
        self.nTran = nTran
        self.nRate = nRate
        self.ap_name = ap_name
        self.ap_ygap = ap_ygap
        self.ap_ycenter = ap_ycenter
        self.ap_xgap = ap_xgap
        self.ap_xcenter = ap_xcenter

        self.damage_limit = damage_limit
        self.pulse_energy = pulse_energy
        self.notes = notes

        if special == '' or special == None:
            special=False
        self.special = special
        self.reactive_temp = reactive_temp
        self.reactive_pressure = reactive_pressure

