import os
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ges.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Enable WAL mode for better concurrency in SQLite
if "sqlite" in DATABASE_URL:
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True) # Email_ID from CSV
    thread_id = Column(String, index=True)
    thread_sequence = Column(Integer)
    channel_type = Column(String)
    department = Column(String)
    conversation_category = Column(String)
    client_project_topic = Column(String)
    thread_title = Column(String)
    sent_timestamp = Column(DateTime)
    from_name = Column(String)
    from_email = Column(String)
    sender_role = Column(String)
    to_group = Column(String)
    cc = Column(String, nullable=True)
    subject = Column(String)
    email_body = Column(Text)
    attachment_name = Column(String, nullable=True)
    priority = Column(String)
    
    # Flag to indicate if this email has been processed by AI
    processed_by_ai = Column(Boolean, default=False)

    tasks = relationship("Task", back_populates="email")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email_id = Column(String, ForeignKey("emails.id"))
    task_description = Column(Text)
    owner = Column(String)
    due_date = Column(String, nullable=True) # Storing as string to handle flexible formats extracted by AI
    status = Column(String, default="Open")
    
    email = relationship("Email", back_populates="tasks")

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    thread_id = Column(String, index=True)
    topic = Column(String)
    summary = Column(Text)
    decisions = Column(Text, nullable=True)
    follow_ups = Column(Text, nullable=True)
    created_date = Column(DateTime)

class ExecutiveReport(Base):
    __tablename__ = "executive_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    top_topics = Column(Text)
    open_tasks = Column(Integer)
    overdue_tasks = Column(Integer)
    key_decisions = Column(Text)
    risks_bottlenecks = Column(Text)
    workload_summary = Column(Text)
    recommendations = Column(Text)
    created_at = Column(DateTime)

# Create the tables
Base.metadata.create_all(bind=engine)
