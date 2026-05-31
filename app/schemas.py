from pydantic import BaseModel


class DepartureResponse(BaseModel):
    trainNumber: str
    destination: str
    scheduledDepartureTime: str
    delayMinutes: int


class StationDeparturesResponse(BaseModel):
    id: str | None
    name: str
    departures: list[DepartureResponse]


class DeparturesResponse(BaseModel):
    query: str
    windowMinutes: int
    generatedAt: str
    stations: list[StationDeparturesResponse]


class ShortQueryErrorDetail(BaseModel):
    code: str
    message: str
    minLength: int


class ShortQueryErrorResponse(BaseModel):
    error: ShortQueryErrorDetail


class UpstreamErrorDetail(BaseModel):
    code: str
    message: str


class UpstreamErrorResponse(BaseModel):
    error: UpstreamErrorDetail

