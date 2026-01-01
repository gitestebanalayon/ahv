from typing import List, Generic, TypeVar
from ninja import Schema

T = TypeVar('T')

class ListResponse(Schema):
    data: List
    totalData: int
    totalPages: int
    currentPage: int