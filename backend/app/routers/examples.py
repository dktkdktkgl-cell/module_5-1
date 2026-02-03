from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Example
from app.schemas import ExampleCreate, ExampleResponse

router = APIRouter(prefix="/api/examples", tags=["examples"])


@router.get("/", response_model=list[ExampleResponse])
def get_examples(db: Session = Depends(get_db)):
    return db.query(Example).all()


@router.get("/{example_id}", response_model=ExampleResponse)
def get_example(example_id: int, db: Session = Depends(get_db)):
    example = db.query(Example).filter(Example.id == example_id).first()
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    return example


@router.post("/", response_model=ExampleResponse)
def create_example(example: ExampleCreate, db: Session = Depends(get_db)):
    db_example = Example(**example.model_dump())
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example


@router.delete("/{example_id}")
def delete_example(example_id: int, db: Session = Depends(get_db)):
    example = db.query(Example).filter(Example.id == example_id).first()
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    db.delete(example)
    db.commit()
    return {"message": "Deleted successfully"}
