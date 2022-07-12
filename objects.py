import datetime
import enum


class User:
    id: int
    login: str
    password: str
    email: str
    phone: str
    registr_date: datetime.date
    rating: int
    role: int


class Composition:
    id: int
    name: str
    comp_id: int
    comp_name: str
    price: int
    instrument: str
    status: int


class Purchase:
    id: int
    c_id: int
    comp_id: int
    user_id: int
    date: datetime.datetime


class Composer(User):
    bio: str
    c_amount: int
