CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- AIRPORTS
CREATE TABLE airports (
    id              SERIAL PRIMARY KEY,
    iata_code       VARCHAR(3) NOT NULL UNIQUE,
    icao_code       VARCHAR(4),
    name            VARCHAR(255) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    country         VARCHAR(100) NOT NULL,
    continent       VARCHAR(50) NOT NULL,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    timezone        VARCHAR(100),
    elevation_ft    INT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX idx_airports_iata      ON airports(iata_code);
CREATE INDEX idx_airports_country   ON airports(country);
CREATE INDEX idx_airports_continent ON airports(continent);

-- AIRLINES
CREATE TABLE airlines (
    id              SERIAL PRIMARY KEY,
    iata_code       VARCHAR(3) NOT NULL UNIQUE,
    icao_code       VARCHAR(4),
    name            VARCHAR(255) NOT NULL,
    country         VARCHAR(100) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    founded_year    INT,
    alliance        VARCHAR(50)
);
CREATE INDEX idx_airlines_iata    ON airlines(iata_code);
CREATE INDEX idx_airlines_country ON airlines(country);

-- AIRCRAFT
CREATE TABLE aircraft (
    id              SERIAL PRIMARY KEY,
    model           VARCHAR(100) NOT NULL,
    manufacturer    VARCHAR(100) NOT NULL,
    seat_capacity   INT NOT NULL,
    range_km        INT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- ROUTES
CREATE TABLE routes (
    id                  SERIAL PRIMARY KEY,
    airline_id          INT NOT NULL REFERENCES airlines(id) ON DELETE RESTRICT,
    origin_airport_id   INT NOT NULL REFERENCES airports(id) ON DELETE RESTRICT,
    dest_airport_id     INT NOT NULL REFERENCES airports(id) ON DELETE RESTRICT,
    distance_km         INT NOT NULL,
    avg_duration_mins   INT NOT NULL,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (airline_id, origin_airport_id, dest_airport_id)
);
CREATE INDEX idx_routes_airline     ON routes(airline_id);
CREATE INDEX idx_routes_origin      ON routes(origin_airport_id);
CREATE INDEX idx_routes_dest        ON routes(dest_airport_id);
CREATE INDEX idx_routes_origin_dest ON routes(origin_airport_id, dest_airport_id);

-- FLIGHTS
CREATE TABLE flights (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flight_number   VARCHAR(10) NOT NULL,
    route_id        INT NOT NULL REFERENCES routes(id) ON DELETE RESTRICT,
    aircraft_id     INT NOT NULL REFERENCES aircraft(id) ON DELETE RESTRICT,
    scheduled_dep   TIMESTAMPTZ NOT NULL,
    scheduled_arr   TIMESTAMPTZ NOT NULL,
    actual_dep      TIMESTAMPTZ,
    actual_arr      TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                        CHECK (status IN ('scheduled','boarding','departed',
                                          'in_air','landed','cancelled','diverted')),
    dep_delay_mins  INT DEFAULT 0,
    arr_delay_mins  INT DEFAULT 0,
    seats_available INT NOT NULL,
    seats_sold      INT NOT NULL DEFAULT 0,
    base_price      NUMERIC(10,2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_flights_route         ON flights(route_id);
CREATE INDEX idx_flights_aircraft      ON flights(aircraft_id);
CREATE INDEX idx_flights_status        ON flights(status);
CREATE INDEX idx_flights_scheduled_dep ON flights(scheduled_dep DESC);
CREATE INDEX idx_flights_flight_number ON flights(flight_number);
CREATE INDEX idx_flights_route_date    ON flights(route_id, scheduled_dep DESC);
CREATE INDEX idx_flights_status_date   ON flights(status, scheduled_dep DESC);

-- FLIGHT DELAYS
CREATE TABLE flight_delays (
    id              BIGSERIAL PRIMARY KEY,
    flight_id       UUID NOT NULL REFERENCES flights(id) ON DELETE CASCADE,
    delay_category  VARCHAR(50) NOT NULL
                        CHECK (delay_category IN ('weather','technical','crew',
                                                   'air_traffic','security','other')),
    delay_mins      INT NOT NULL,
    notes           TEXT,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_delays_flight_id ON flight_delays(flight_id);
CREATE INDEX idx_delays_category  ON flight_delays(delay_category);

-- REVIEWS
CREATE TABLE reviews (
    id              BIGSERIAL PRIMARY KEY,
    flight_id       UUID NOT NULL REFERENCES flights(id) ON DELETE CASCADE,
    airline_id      INT NOT NULL REFERENCES airlines(id) ON DELETE CASCADE,
    overall_rating  NUMERIC(3,1) NOT NULL CHECK (overall_rating BETWEEN 1 AND 10),
    seat_comfort    INT CHECK (seat_comfort BETWEEN 1 AND 5),
    food_rating     INT CHECK (food_rating BETWEEN 1 AND 5),
    staff_rating    INT CHECK (staff_rating BETWEEN 1 AND 5),
    punctuality     INT CHECK (punctuality BETWEEN 1 AND 5),
    review_text     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_reviews_flight_id      ON reviews(flight_id);
CREATE INDEX idx_reviews_airline_id     ON reviews(airline_id);
CREATE INDEX idx_reviews_rating         ON reviews(overall_rating DESC);
CREATE INDEX idx_reviews_airline_rating ON reviews(airline_id, overall_rating DESC);

-- QUERY LOGS
CREATE TABLE query_logs (
    id                  BIGSERIAL PRIMARY KEY,
    natural_language    TEXT NOT NULL,
    generated_sql       TEXT NOT NULL,
    sql_hash            VARCHAR(64) NOT NULL,
    execution_time_ms   NUMERIC(10,3),
    total_cost          NUMERIC(10,4),
    rows_returned       INT,
    had_seq_scan        BOOLEAN NOT NULL DEFAULT FALSE,
    explain_output      JSONB,
    suggestions         JSONB,
    was_cached          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_query_logs_hash       ON query_logs(sql_hash);
CREATE INDEX idx_query_logs_created_at ON query_logs(created_at DESC);
CREATE INDEX idx_query_logs_seq_scan   ON query_logs(had_seq_scan) WHERE had_seq_scan = TRUE;

-- VIEWS
CREATE OR REPLACE VIEW vw_flight_summary AS
SELECT f.id, f.flight_number,
    al.name AS airline, al.iata_code AS airline_code,
    orig.iata_code AS origin, orig.city AS origin_city, orig.country AS origin_country,
    dest.iata_code AS destination, dest.city AS dest_city, dest.country AS dest_country,
    f.scheduled_dep, f.scheduled_arr, f.status,
    f.dep_delay_mins, f.arr_delay_mins,
    f.seats_available, f.seats_sold, f.base_price,
    ac.model AS aircraft_model, r.distance_km
FROM flights f
JOIN routes r      ON r.id = f.route_id
JOIN airlines al   ON al.id = r.airline_id
JOIN airports orig ON orig.id = r.origin_airport_id
JOIN airports dest ON dest.id = r.dest_airport_id
JOIN aircraft ac   ON ac.id = f.aircraft_id;

CREATE OR REPLACE VIEW vw_airline_stats AS
SELECT al.id, al.name, al.iata_code, al.country, al.alliance,
    COUNT(DISTINCT f.id)  AS total_flights,
    COUNT(DISTINCT r.id)  AS total_routes,
    AVG(f.dep_delay_mins) AS avg_dep_delay,
    AVG(f.arr_delay_mins) AS avg_arr_delay,
    COUNT(CASE WHEN f.status = 'cancelled' THEN 1 END) AS cancelled_flights,
    AVG(rv.overall_rating) AS avg_rating,
    COUNT(rv.id)           AS total_reviews
FROM airlines al
LEFT JOIN routes r   ON r.airline_id = al.id
LEFT JOIN flights f  ON f.route_id = r.id
LEFT JOIN reviews rv ON rv.airline_id = al.id
GROUP BY al.id, al.name, al.iata_code, al.country, al.alliance;

-- TRIGGER: auto-calculate delay minutes
CREATE OR REPLACE FUNCTION update_flight_delay_mins()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.actual_dep IS NOT NULL AND NEW.scheduled_dep IS NOT NULL THEN
        NEW.dep_delay_mins := EXTRACT(EPOCH FROM (NEW.actual_dep - NEW.scheduled_dep)) / 60;
    END IF;
    IF NEW.actual_arr IS NOT NULL AND NEW.scheduled_arr IS NOT NULL THEN
        NEW.arr_delay_mins := EXTRACT(EPOCH FROM (NEW.actual_arr - NEW.scheduled_arr)) / 60;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_flight_delays
    BEFORE INSERT OR UPDATE ON flights
    FOR EACH ROW EXECUTE FUNCTION update_flight_delay_mins();
