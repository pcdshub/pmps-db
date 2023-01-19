import sqlalchemy
from base import Base

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.orm import relationship
# Define the User data-model
class User(Base):
    # Relationships
    roles = relationship('Role', secondary='user_roles')

# Define the Role data-model
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), unique=True)

# Define the UserRoles association table
class UserRoles(Base):
    __tablename__ = 'user_roles'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id', ondelete='CASCADE'))
    role_id = Column(Integer(), ForeignKey('roles.id', ondelete='CASCADE'))