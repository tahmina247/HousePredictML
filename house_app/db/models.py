from .database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from typing import Optional, List
from datetime import datetime
from passlib.hash import bcrypt


class UserProfile(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fio: Mapped[str] = mapped_column(String(200))
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    date_registered: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tokens: Mapped['RefreshToken'] = relationship('RefreshToken', back_populates='user',
                                                  cascade='all, delete-orphan')

    def set_passwords(self, password: str):
        self.hashed_password = bcrypt.hash(password)

    def check_passwords(self, password: str):
        return bcrypt.verify(password, self.hashed_password)


class RefreshToken(Base):
    __tablename__ = 'RefreshToken'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped[UserProfile] = relationship(UserProfile, back_populates='tokens')


class HouseModel(Base):
    __tablename__ = 'HouseModel'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    GrLivArea: Mapped[int] = mapped_column(Integer)
    YearBuilt: Mapped[int] = mapped_column(Integer)
    GarageCars: Mapped[int] = mapped_column(Integer)
    TotalBsmtSF: Mapped[int] = mapped_column(Integer)
    FullBath: Mapped[int] = mapped_column(Integer)
    OverallQual: Mapped[int] = mapped_column(Integer)
    Neighborhood: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

