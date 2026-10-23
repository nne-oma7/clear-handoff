from sqlalchemy import Column, Integer, String, Text

from database import Base


class ComplaintRecord(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    original_message = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    answers = Column(Text, nullable=False, default="{}")
    missing_information = Column(Text, nullable=False, default="[]")
    status = Column(String, nullable=False, default="received")
    contact_name = Column(String, nullable=False, default="")
    contact_email = Column(String, nullable=False, default="")
    contact_phone = Column(String, nullable=False, default="")
    created_at = Column(String, nullable=False)