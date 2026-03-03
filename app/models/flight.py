import uuid
from sqlalchemy import (Column, Integer, String, Boolean, Numeric,
                        ForeignKey, Text, BigInteger, UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ
from app.db.base import Base


class Airport(Base):
    __tablename__ = "airports"
    id           = Column(Integer, primary_key=True)
    iata_code    = Column(String(3), unique=True, nullable=False)
    icao_code    = Column(String(4))
    name         = Column(String(255), nullable=False)
    city         = Column(String(100), nullable=False)
    country      = Column(String(100), nullable=False)
    continent    = Column(String(50), nullable=False)
    latitude     = Column(Numeric(9,6))
    longitude    = Column(Numeric(9,6))
    timezone     = Column(String(100))
    elevation_ft = Column(Integer)
    is_active    = Column(Boolean, default=True)


class Airline(Base):
    __tablename__ = "airlines"
    id           = Column(Integer, primary_key=True)
    iata_code    = Column(String(3), unique=True, nullable=False)
    icao_code    = Column(String(4))
    name         = Column(String(255), nullable=False)
    country      = Column(String(100), nullable=False)
    is_active    = Column(Boolean, default=True)
    founded_year = Column(Integer)
    alliance     = Column(String(50))


class Aircraft(Base):
    __tablename__ = "aircraft"
    id            = Column(Integer, primary_key=True)
    model         = Column(String(100), nullable=False)
    manufacturer  = Column(String(100), nullable=False)
    seat_capacity = Column(Integer, nullable=False)
    range_km      = Column(Integer, nullable=False)
    is_active     = Column(Boolean, default=True)


class Route(Base):
    __tablename__ = "routes"
    id                = Column(Integer, primary_key=True)
    airline_id        = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    origin_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    dest_airport_id   = Column(Integer, ForeignKey("airports.id"), nullable=False)
    distance_km       = Column(Integer, nullable=False)
    avg_duration_mins = Column(Integer, nullable=False)
    is_active         = Column(Boolean, default=True)
    __table_args__ = (UniqueConstraint("airline_id","origin_airport_id","dest_airport_id"),)


class Flight(Base):
    __tablename__ = "flights"
    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_number   = Column(String(10), nullable=False)
    route_id        = Column(Integer, ForeignKey("routes.id"), nullable=False)
    aircraft_id     = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    scheduled_dep   = Column(TIMESTAMPTZ, nullable=False)
    scheduled_arr   = Column(TIMESTAMPTZ, nullable=False)
    actual_dep      = Column(TIMESTAMPTZ)
    actual_arr      = Column(TIMESTAMPTZ)
    status          = Column(String(20), nullable=False, default="scheduled")
    dep_delay_mins  = Column(Integer, default=0)
    arr_delay_mins  = Column(Integer, default=0)
    seats_available = Column(Integer, nullable=False)
    seats_sold      = Column(Integer, default=0)
    base_price      = Column(Numeric(10,2), nullable=False)
    created_at      = Column(TIMESTAMPTZ)


class FlightDelay(Base):
    __tablename__ = "flight_delays"
    id             = Column(BigInteger, primary_key=True)
    flight_id      = Column(UUID(as_uuid=True), ForeignKey("flights.id"), nullable=False)
    delay_category = Column(String(50), nullable=False)
    delay_mins     = Column(Integer, nullable=False)
    notes          = Column(Text)
    recorded_at    = Column(TIMESTAMPTZ)


class Review(Base):
    __tablename__ = "reviews"
    id             = Column(BigInteger, primary_key=True)
    flight_id      = Column(UUID(as_uuid=True), ForeignKey("flights.id"), nullable=False)
    airline_id     = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    overall_rating = Column(Numeric(3,1), nullable=False)
    seat_comfort   = Column(Integer)
    food_rating    = Column(Integer)
    staff_rating   = Column(Integer)
    punctuality    = Column(Integer)
    review_text    = Column(Text)
    created_at     = Column(TIMESTAMPTZ)


class QueryLog(Base):
    __tablename__ = "query_logs"
    id                = Column(BigInteger, primary_key=True)
    natural_language  = Column(Text, nullable=False)
    generated_sql     = Column(Text, nullable=False)
    sql_hash          = Column(String(64), nullable=False)
    execution_time_ms = Column(Numeric(10,3))
    total_cost        = Column(Numeric(10,4))
    rows_returned     = Column(Integer)
    had_seq_scan      = Column(Boolean, default=False)
    explain_output    = Column(JSONB)
    suggestions       = Column(JSONB)
    was_cached        = Column(Boolean, default=False)
    created_at        = Column(TIMESTAMPTZ)
