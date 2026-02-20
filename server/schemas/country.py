from datetime import date

from pydantic import BaseModel, ConfigDict


class CountryBase(BaseModel):
    name: str
    official_name: str
    wiki: str
    md_file: str

    model_config = ConfigDict(from_attributes=True)


class CountryDisplay(BaseModel):
    id: int
    name: str
    official_name: str

    model_config = ConfigDict(from_attributes=True)


# Country Schema
class DayCountryBase(BaseModel):
    country_id: int

    model_config = ConfigDict(from_attributes=True)


class DayCountryDisplay(DayCountryBase):
    id: int
    country: CountryDisplay | None
    date: date

    model_config = ConfigDict(from_attributes=True)


class CountryCount(BaseModel):
    id: int
    name: str
    count: int
    last: date | None

    model_config = ConfigDict(from_attributes=True)

