from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:////Users/lking/Documents/Projects/pmps/pmps.db")
Session = sessionmaker(bind=engine)

Base = declarative_base()
"""
session = None
def get_session():
    if session is None:
        #make session
        #import this session to other files
    try:
        #catch sqlalchemy exceptions
        #on exceptions create a new session
"""