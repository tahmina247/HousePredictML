from house_app.db.database import SessionLocal
from house_app.db.models import HouseModel
from house_app.db.schema import HouseModelCreateSchema, HouseModelEditSchema, HouseModelOutSchema
from sqlalchemy.orm import Session
from typing import List
from fastapi import Depends, HTTPException, APIRouter
import joblib
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler, scale
from sklearn.linear_model import LinearRegression


BASE_DIR = Path(__file__).resolve().parent.parent.parent

house_model_router = APIRouter(prefix='/house', tags=['House'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@house_model_router.post('/', response_model=HouseModelOutSchema)
async def house_create(house: HouseModelCreateSchema, db: Session=Depends(get_db)):
    house_db = HouseModel(**house.dict())
    db.add(house_db)
    db.commit()
    db.refresh(house_db)
    return house_db


@house_model_router.get('/', response_model=List[HouseModelOutSchema])
async def house_list(db: Session=Depends(get_db)):
    return db.query(HouseModel).all()


@house_model_router.get('/{house_id}', response_model=HouseModelOutSchema)
async def house_detail(house_id: int, db: Session=Depends(get_db)):
    house_db = db.query(HouseModel).filter(HouseModel.id == house_id).first()
    if not house_db:
        raise HTTPException(status_code=404, detail='house is not fount')
    return house_db


@house_model_router.put('/{house_id}', response_model=HouseModelOutSchema)
async def house_update(house_id: int, house: HouseModelEditSchema, db: Session=Depends(get_db)):
    house_db = db.query(HouseModel).filter(HouseModel.id == house_id).first()
    if not house_db:
        raise HTTPException(status_code=404, detail='house is not fount')

    for house_key , house_value in house.dict().items():
        setattr(house_db, house_key, house_value)

    db.commit()
    db.refresh(house_db)
    return house_db


@house_model_router.delete('/{house_id}', response_model=dict)
async def house_delete(house_id: int, db: Session=Depends(get_db)):
    house_db = db.query(HouseModel).filter(HouseModel.id == house_id).first()
    if not house_db:
        raise HTTPException(status_code=404, detail='house is not found')

    db.delete(house_db)
    db.commit()
    return {'message': 'this house is deleted'}


scaler = StandardScaler()

model_path = BASE_DIR / 'house_price_model_job.pkl'
scaler_path = BASE_DIR / 'scaler.pkl'

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

model_features = [
    "GrLivArea",
    "YearBuilt",
    "GarageCars",
    "TotalBsmtSF",
    "FullBath",
    "OverallQual",

]

@house_model_router.post('/predict/')
async def predict_price(house: HouseModelCreateSchema, db: Session=Depends(get_db)):
    house
    input_data = {
        "GrLivArea": house.GrLivArea,
        "YearBuilt": house.YearBuilt,
        "GarageCars": house.GarageCars,
        "TotalBsmtSF": house.TotalBsmtSF,
        "FullBath": house.FullBath,
        "OverallQual": house.OverallQual
    }

    input_df = pd.DataFrame([input_data])

    input_scaled = scaler.transform(input_df)
    predicted_price = model.predict(input_scaled)[0]
    return {'predicted_price': round(predicted_price, 2)}
