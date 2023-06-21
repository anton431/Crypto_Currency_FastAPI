from pydantic import BaseModel


class CitySchema(BaseModel):
    name: str
    population: int

    class Config:
        orm_mode = True
