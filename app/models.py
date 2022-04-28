from typing import Optional, Type
from app import db

from flask_login import UserMixin
from sqlalchemy import Column, Float, String, UniqueConstraint, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256

from runner.checkerlib import Checker


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)

    # username / password auth
    username = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)

    # LTI auth
    tool_consumer_id = Column(Integer, ForeignKey("tool_consumer.id"), nullable=True)
    lti_user_id = Column(String, nullable=True)

    # User info
    email = Column(String, default="")
    full_name = Column(String, default="")

    # User permissions
    is_admin = Column(Boolean, default=False)

    assignments = relationship("Assignment", backref="user", lazy=True, cascade="all, delete")

    __table_args__ = (
        UniqueConstraint("tool_consumer_id", "lti_user_id"),
    )

    def set_password(self, password: str) -> None:
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password_hash)

    def __str__(self) -> str:
        return f"{self.full_name} (id={self.id})"


class Problem(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String)
    statement = Column(String)
    checker_name = Column(String, nullable=True)
    checker_config = Column(String, default="{}")

    tool_consumer_id = Column(Integer, ForeignKey("tool_consumer.id"), nullable=True)
    resource_link_id = Column(String, nullable=True)
    course_name = Column(String, nullable=True)

    assignments = relationship("Assignment", backref="problem", lazy=True, cascade="all, delete")

    __table_args__ = (
        UniqueConstraint("tool_consumer_id", "resource_link_id"),
    )

    def get_checker(self) -> Optional[Type[Checker]]:
        return Checker._all_checkers.get(self.checker_name)

    def __str__(self) -> str:
        return f"{self.title} (id={self.id})"


class Assignment(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problem.id"), nullable=False)

    source_code = Column(String, default="")
    arch = Column(String, default="")

    started_at = Column(DateTime, server_default=db.func.now())
    grade = Column(Integer, default=0)

    lti_consumer_key = Column(String)
    lti_assignment_id = Column(String)
    lti_callback_url = Column(String)

    is_instructor = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("user_id", "problem_id"),
    )

    submissions = relationship("Submission", backref="assignment", lazy=True, cascade="all, delete")

    def __str__(self) -> str:
        return f"{self.user.full_name} - {self.problem.title}"


class Submission(db.Model):
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=True)

    source_code = Column(String)
    arch = Column(String)

    submitted_at = Column(DateTime, server_default=db.func.now())
    grade = Column(Integer, default=0)
    comment = Column(String)


class DebugSession(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user = relationship("User")
    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=True)
    assignment = relationship("Assignment")

    source_code = Column(String, nullable=False)
    arch = Column(String, nullable=False)

    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    is_interactive = Column(Boolean, nullable=False)

    cpu_time_used = Column(Float, nullable=True)
    real_time_used = Column(Float, nullable=True)
    memory_used = Column(Integer, nullable=True)


class ToolConsumer(db.Model):
    id = Column(Integer, primary_key=True)

    consumer_key = Column(String, nullable=False, unique=True)
    consumer_secret = Column(String, nullable=False)

    instance_id = Column(String, nullable=True)
    instance_name = Column(String, nullable=True)

    in_use = Column(Boolean, nullable=False, default=False)

    users = relationship("User", backref="tool_consumer", lazy=False, cascade="all, delete")
    problems = relationship("Problem", backref="tool_consumer", lazy=False, cascade="all, delete")
