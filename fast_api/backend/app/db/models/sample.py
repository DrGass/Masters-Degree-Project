from typing import List
from sqlalchemy import String

from sqlalchemy.orm import Session, mapped_column, Mapped, relationship

from sqlalchemy_utils import EmailType

from ..session import Base
from api.exceptions import LecturerNotFound


class Lecturer(Base):
    __tablename__ = "lecturer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    surname: Mapped[str] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    uni_email: Mapped[str] = mapped_column(EmailType, nullable=True)
    private_email: Mapped[str] = mapped_column(EmailType, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=True)
    accessibility_notes: Mapped[str] = mapped_column(String(5000), nullable=False)
    teaching_load: Mapped[str] = mapped_column(String(100), nullable=True)
    form_of_employment: Mapped[str] = mapped_column(String(100), nullable=True)
    t_subjects: Mapped[List["TakenSubject"]] = relationship(
        back_populates="t_lecturers",
        lazy="joined",
    )
    p_subjects: Mapped[List["PossibleSubject"]] = relationship(
        back_populates="p_lecturers",
        lazy="joined",
    )
    languages: Mapped[List["LecturerLanguage"]] = relationship(
        back_populates="lecturers",
        lazy="joined",
    )

    def __str__(self):
        return f"name: {self.name}, surname: {self.surname}, title: {self.title}, uni_email: {self.uni_email}, private_email: {self.private_email}, phone_number: {self.phone_number}, accessibility_notes: {self.accessibility_notes}"

    @staticmethod
    def get_all_lecturers(session: Session):
        return session.query(Lecturer).all()

    @staticmethod
    def get_lecturer_by_id(session: Session, lecturer_id: int):
        lecturer = session.query(Lecturer).filter(Lecturer.id == lecturer_id).first()
        if not lecturer:
            raise LecturerNotFound(lecturer_id)
        return lecturer
