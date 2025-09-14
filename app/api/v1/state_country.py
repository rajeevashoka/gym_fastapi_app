from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models, schemas

router = APIRouter()

# StateCountry endpoints
@router.post("/state_country/", response_model=schemas.StateCountry)
def create_state_country(state_country: schemas.StateCountryCreate, db: Session = Depends(get_db)):
    # Check if state-country combination already exists
    db_state_country = db.query(models.StateCountry).filter(
        models.StateCountry.state_name == state_country.state_name,
        models.StateCountry.country_name == state_country.country_name
    ).first()
    
    if db_state_country:
        raise HTTPException(
            status_code=400,
            detail="State-Country combination already exists"
        )
    
    db_state_country = models.StateCountry(
        state_name=state_country.state_name,
        country_name=state_country.country_name
    )
    
    db.add(db_state_country)
    db.commit()
    db.refresh(db_state_country)
    return db_state_country

@router.get("/state_country/", response_model=list[schemas.StateCountry])
def read_state_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    state_countries = db.query(models.StateCountry).offset(skip).limit(limit).all()
    return state_countries

@router.get("/state_country/{state_country_id}", response_model=schemas.StateCountry)
def read_state_country(state_country_id: int, db: Session = Depends(get_db)):
    db_state_country = db.query(models.StateCountry).filter(models.StateCountry.id == state_country_id).first()
    if db_state_country is None:
        raise HTTPException(status_code=404, detail="State-Country not found")
    return db_state_country

@router.delete("/state_country/{state_country_id}")
def delete_state_country(state_country_id: int, db: Session = Depends(get_db)):
    db_state_country = db.query(models.StateCountry).filter(models.StateCountry.id == state_country_id).first()
    if db_state_country is None:
        raise HTTPException(status_code=404, detail="State-Country not found")
    
    db.delete(db_state_country)
    db.commit()
    return {"message": "State-Country deleted successfully"}

# Pincode endpoints
@router.post("/pincode/", response_model=schemas.Pincode)
def create_pincode(pincode: schemas.PincodeCreate, db: Session = Depends(get_db)):
    # Check if pincode already exists
    db_pincode = db.query(models.Pincode).filter(models.Pincode.pincode == pincode.pincode).first()
    if db_pincode:
        raise HTTPException(
            status_code=400,
            detail="Pincode already exists"
        )
    
    # Check if state_country exists
    db_state_country = db.query(models.StateCountry).filter(
        models.StateCountry.id == pincode.state_country_id
    ).first()
    if not db_state_country:
        raise HTTPException(
            status_code=404,
            detail="State-Country not found"
        )
    
    db_pincode = models.Pincode(
        pincode=pincode.pincode,
        state_country_id=pincode.state_country_id
    )
    
    db.add(db_pincode)
    db.commit()
    db.refresh(db_pincode)
    return db_pincode

@router.get("/pincode/", response_model=list[schemas.Pincode])
def read_pincodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pincodes = db.query(models.Pincode).offset(skip).limit(limit).all()
    return pincodes

@router.get("/pincode/{pincode_id}", response_model=schemas.Pincode)
def read_pincode(pincode_id: int, db: Session = Depends(get_db)):
    db_pincode = db.query(models.Pincode).filter(models.Pincode.id == pincode_id).first()
    if db_pincode is None:
        raise HTTPException(status_code=404, detail="Pincode not found")
    return db_pincode

@router.get("/pincode/by_code/{pincode}", response_model=schemas.Pincode)
def read_pincode_by_code(pincode: str, db: Session = Depends(get_db)):
    db_pincode = db.query(models.Pincode).filter(models.Pincode.pincode == pincode).first()
    if db_pincode is None:
        raise HTTPException(status_code=404, detail="Pincode not found")
    return db_pincode

@router.delete("/pincode/{pincode_id}")
def delete_pincode(pincode_id: int, db: Session = Depends(get_db)):
    db_pincode = db.query(models.Pincode).filter(models.Pincode.id == pincode_id).first()
    if db_pincode is None:
        raise HTTPException(status_code=404, detail="Pincode not found")
    
    db.delete(db_pincode)
    db.commit()
    return {"message": "Pincode deleted successfully"}