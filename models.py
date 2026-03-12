from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    ForeignKey,
    DateTime,
    Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    telegram_id = Column(BigInteger, unique=True, nullable=False)

    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    display_name = Column(String, nullable=True)

    is_premium = Column(Boolean, default=False)
    gender = Column(String, default="unknown")

    created_at = Column(DateTime, default=datetime.utcnow)

    memberships = relationship("GroupMember", back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))

    invite_code = Column(String, unique=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("GroupMember", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    role = Column(String, default="student")

    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memberships")
    group = relationship("Group", back_populates="members")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey("groups.id"))

    name = Column(String, nullable=False)


class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey("groups.id"))

    subject_id = Column(Integer, ForeignKey("subjects.id"))

    date = Column(DateTime)

    is_closed = Column(Boolean, default=False)


class Priority(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True)

    lab_id = Column(Integer, ForeignKey("labs.id"))

    name = Column(String)

    emoji = Column(String)

    priority_value = Column(Integer)

    affects_weight = Column(Boolean, default=True)


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True)

    lab_id = Column(Integer, ForeignKey("labs.id"))

    user_id = Column(Integer, ForeignKey("users.id"))

    priority_id = Column(Integer, ForeignKey("priorities.id"))

    requested_priority_id = Column(Integer, ForeignKey("priorities.id"))

    created_at = Column(DateTime, default=datetime.utcnow)


class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True)

    lab_id = Column(Integer, ForeignKey("labs.id"))

    created_at = Column(DateTime, default=datetime.utcnow)


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(Integer, primary_key=True)

    queue_id = Column(Integer, ForeignKey("queues.id"))

    user_id = Column(Integer, ForeignKey("users.id"))

    position = Column(Integer)

    priority_group = Column(Integer)


class Weight(Base):
    __tablename__ = "weights"

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey("groups.id"))

    user_id = Column(Integer, ForeignKey("users.id"))

    subject_id = Column(Integer, ForeignKey("subjects.id"))

    value = Column(Integer, default=0)


class SwapRequest(Base):
    __tablename__ = "swap_requests"

    id = Column(Integer, primary_key=True)

    lab_id = Column(Integer, ForeignKey("labs.id"))

    from_user = Column(Integer, ForeignKey("users.id"))

    to_user = Column(Integer, ForeignKey("users.id"))

    from_position = Column(Integer)

    to_position = Column(Integer)

    status = Column(String, default="pending")