from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    ForeignKey,
    DateTime,
    Boolean,
    Float
)
from sqlalchemy.orm import relationship, declarative_base
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
    
    memberships = relationship("GroupMember", back_populates="user", foreign_keys="GroupMember.user_id")
    academic_student = relationship(
        "AcademicStudent",
        back_populates="user",
        uselist=False,
        foreign_keys="AcademicStudent.user_id"
    )
    weights = relationship("Weight", back_populates="user", foreign_keys="Weight.user_id")
    registrations = relationship("Registration", back_populates="user", foreign_keys="Registration.user_id")
    swap_requests_from = relationship(
        "SwapRequest",
        back_populates="from_user_rel",
        foreign_keys="SwapRequest.from_user"
    )
    swap_requests_to = relationship(
        "SwapRequest",
        back_populates="to_user_rel",
        foreign_keys="SwapRequest.to_user"
    )


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    invite_code = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    members = relationship("GroupMember", back_populates="group", foreign_keys="GroupMember.group_id")
    subjects = relationship("Subject", back_populates="group", foreign_keys="Subject.group_id")
    academic_students = relationship("AcademicStudent", back_populates="group", foreign_keys="AcademicStudent.group_id")
    labs = relationship("Lab", back_populates="group", foreign_keys="Lab.group_id")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="student")
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])
    group = relationship("Group", back_populates="members", foreign_keys=[group_id])


class AcademicStudent(Base):
    __tablename__ = "academic_students"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    group = relationship("Group", back_populates="academic_students", foreign_keys=[group_id])
    user = relationship("User", back_populates="academic_student", foreign_keys=[user_id])


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    name = Column(String, nullable=False)
    
    group = relationship("Group", back_populates="subjects", foreign_keys=[group_id])
    weights = relationship("Weight", back_populates="subject", foreign_keys="Weight.subject_id")
    labs = relationship("Lab", back_populates="subject", foreign_keys="Lab.subject_id")


class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    date = Column(DateTime)
    is_closed = Column(Boolean, default=False)
    
    group = relationship("Group", back_populates="labs", foreign_keys=[group_id])
    subject = relationship("Subject", back_populates="labs", foreign_keys=[subject_id])
    priorities = relationship("Priority", back_populates="lab", foreign_keys="Priority.lab_id")
    registrations = relationship("Registration", back_populates="lab", foreign_keys="Registration.lab_id")
    queue = relationship("Queue", back_populates="lab", uselist=False, foreign_keys="Queue.lab_id")


class Priority(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True)
    lab_id = Column(Integer, ForeignKey("labs.id"))
    name = Column(String)
    emoji = Column(String)
    priority_value = Column(Integer)
    affects_weight = Column(Boolean, default=True)
    
    lab = relationship("Lab", back_populates="priorities", foreign_keys=[lab_id])
    registrations = relationship("Registration", back_populates="priority", foreign_keys="Registration.priority_id")


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True)
    lab_id = Column(Integer, ForeignKey("labs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    requested_priority_id = Column(Integer, ForeignKey("priorities.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lab = relationship("Lab", back_populates="registrations", foreign_keys=[lab_id])
    user = relationship("User", back_populates="registrations", foreign_keys=[user_id])
    priority = relationship("Priority", foreign_keys=[priority_id])
    requested_priority = relationship("Priority", foreign_keys=[requested_priority_id])


class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True)
    lab_id = Column(Integer, ForeignKey("labs.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lab = relationship("Lab", back_populates="queue", foreign_keys=[lab_id])
    entries = relationship("QueueEntry", back_populates="queue", foreign_keys="QueueEntry.queue_id")


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(Integer, primary_key=True)
    queue_id = Column(Integer, ForeignKey("queues.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    position = Column(Integer)
    priority_group = Column(Integer)
    
    queue = relationship("Queue", back_populates="entries", foreign_keys=[queue_id])
    user = relationship("User", foreign_keys=[user_id])


class Weight(Base):
    __tablename__ = "weights"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    value = Column(Float, default=1.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    group = relationship("Group", foreign_keys=[group_id])
    user = relationship("User", back_populates="weights", foreign_keys=[user_id])
    subject = relationship("Subject", back_populates="weights", foreign_keys=[subject_id])


class SwapRequest(Base):
    __tablename__ = "swap_requests"

    id = Column(Integer, primary_key=True)
    lab_id = Column(Integer, ForeignKey("labs.id"))
    from_user = Column(Integer, ForeignKey("users.id"))
    to_user = Column(Integer, ForeignKey("users.id"))
    from_position = Column(Integer)
    to_position = Column(Integer)
    status = Column(String, default="pending")
    
    lab = relationship("Lab", foreign_keys=[lab_id])
    from_user_rel = relationship("User", back_populates="swap_requests_from", foreign_keys=[from_user])
    to_user_rel = relationship("User", back_populates="swap_requests_to", foreign_keys=[to_user])