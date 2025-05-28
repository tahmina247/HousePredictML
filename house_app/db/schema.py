from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List


class UserCreateSchema(BaseModel):
    id: int
    fio: str
    username: str
    password: str
    date_registered: datetime

    class Config:
        from_attributes = True


class HouseModelCreateSchema(BaseModel):
    GrLivArea: int
    YearBuilt: int
    GarageCars: int
    TotalBsmtSF: int
    FullBath: int
    OverallQual:int
    Neighborhood: Optional[str] = None
    price: Optional[int] = None


class HouseModelOutSchema(BaseModel):
    id: int
    GrLivArea: int
    YearBuilt: int
    GarageCars: int
    TotalBsmtSF: int
    FullBath: int
    OverallQual: int
    Neighborhood: Optional[str]
    price: Optional[int] = None


class HouseModelEditSchema(BaseModel):
    GrLivArea: Optional[int] = None
    YearBuilt: Optional[int] = None
    GarageCars: Optional[int] = None
    TotalBsmtSF: Optional[int] = None
    FullBath: Optional[int] = None
    OverallQual: Optional[int] = None
    Neighborhood: Optional[str] = None