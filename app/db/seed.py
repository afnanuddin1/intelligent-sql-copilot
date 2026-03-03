"""
Seed the database with realistic flight data.
Run with:  python -m app.db.seed
"""
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.sync_database_url)

AIRPORTS = [
    ("JFK","KJFK","John F Kennedy International","New York","United States","North America",40.6413,-73.7781,"America/New_York",13),
    ("LHR","EGLL","Heathrow Airport","London","United Kingdom","Europe",51.4700,-0.4543,"Europe/London",83),
    ("CDG","LFPG","Charles de Gaulle Airport","Paris","France","Europe",49.0097,2.5479,"Europe/Paris",392),
    ("DXB","OMDB","Dubai International","Dubai","UAE","Asia",25.2532,55.3657,"Asia/Dubai",62),
    ("SIN","WSSS","Changi Airport","Singapore","Singapore","Asia",1.3644,103.9915,"Asia/Singapore",22),
    ("NRT","RJAA","Narita International","Tokyo","Japan","Asia",35.7720,140.3929,"Asia/Tokyo",41),
    ("SYD","YSSY","Kingsford Smith Airport","Sydney","Australia","Oceania",-33.9461,151.1772,"Australia/Sydney",21),
    ("GRU","SBGR","Sao Paulo Guarulhos","Sao Paulo","Brazil","South America",-23.4356,-46.4731,"America/Sao_Paulo",750),
    ("ORD","KORD","O Hare International","Chicago","United States","North America",41.9742,-87.9073,"America/Chicago",668),
    ("AMS","EHAM","Amsterdam Airport Schiphol","Amsterdam","Netherlands","Europe",52.3086,4.7639,"Europe/Amsterdam",-3),
    ("HKG","VHHH","Hong Kong International","Hong Kong","China","Asia",22.3080,113.9185,"Asia/Hong_Kong",9),
    ("ICN","RKSI","Incheon International","Seoul","South Korea","Asia",37.4602,126.4407,"Asia/Seoul",23),
    ("FRA","EDDF","Frankfurt Airport","Frankfurt","Germany","Europe",50.0379,8.5622,"Europe/Berlin",111),
    ("LAX","KLAX","Los Angeles International","Los Angeles","United States","North America",33.9425,-118.4081,"America/Los_Angeles",125),
    ("BOM","VABB","Chhatrapati Shivaji International","Mumbai","India","Asia",19.0896,72.8656,"Asia/Kolkata",14),
    ("CAI","HECA","Cairo International","Cairo","Egypt","Africa",30.1219,31.4056,"Africa/Cairo",114),
    ("JNB","FAOR","OR Tambo International","Johannesburg","South Africa","Africa",-26.1367,28.2411,"Africa/Johannesburg",1694),
    ("YYZ","CYYZ","Toronto Pearson International","Toronto","Canada","North America",43.6777,-79.6248,"America/Toronto",173),
    ("MXP","LIMC","Milan Malpensa Airport","Milan","Italy","Europe",45.6306,8.7281,"Europe/Rome",234),
    ("MEX","MMMX","Mexico City International","Mexico City","Mexico","North America",19.4363,-99.0721,"America/Mexico_City",2230),
]

AIRLINES = [
    ("AA","AAL","American Airlines","United States",1926,"Oneworld"),
    ("BA","BAW","British Airways","United Kingdom",1974,"Oneworld"),
    ("LH","DLH","Lufthansa","Germany",1953,"Star Alliance"),
    ("EK","UAE","Emirates","UAE",1985,None),
    ("SQ","SIA","Singapore Airlines","Singapore",1972,"Star Alliance"),
    ("NH","ANA","All Nippon Airways","Japan",1952,"Star Alliance"),
    ("QF","QFA","Qantas","Australia",1920,"Oneworld"),
    ("UA","UAL","United Airlines","United States",1926,"Star Alliance"),
    ("KL","KLM","KLM Royal Dutch Airlines","Netherlands",1919,"SkyTeam"),
    ("CX","CPA","Cathay Pacific","Hong Kong",1946,"Oneworld"),
    ("KE","KAL","Korean Air","South Korea",1962,"SkyTeam"),
    ("LA","LAN","LATAM Airlines","Chile",1929,None),
]

AIRCRAFT = [
    ("Boeing 737-800","Boeing",162,5765),
    ("Boeing 777-300ER","Boeing",396,13650),
    ("Boeing 787-9","Boeing",296,14140),
    ("Airbus A320","Airbus",150,6150),
    ("Airbus A380","Airbus",555,15200),
    ("Airbus A350-900","Airbus",314,15000),
    ("Boeing 747-400","Boeing",416,13450),
    ("Airbus A321neo","Airbus",180,7400),
]


def seed():
    with engine.connect() as conn:
        print("Seeding airports...")
        for a in AIRPORTS:
            conn.execute(text("""
                INSERT INTO airports (iata_code,icao_code,name,city,country,continent,latitude,longitude,timezone,elevation_ft)
                VALUES (:iata,:icao,:name,:city,:country,:continent,:lat,:lon,:tz,:elev)
                ON CONFLICT (iata_code) DO NOTHING
            """), dict(zip(["iata","icao","name","city","country","continent","lat","lon","tz","elev"], a)))

        print("Seeding airlines...")
        for al in AIRLINES:
            conn.execute(text("""
                INSERT INTO airlines (iata_code,icao_code,name,country,founded_year,alliance)
                VALUES (:iata,:icao,:name,:country,:year,:alliance)
                ON CONFLICT (iata_code) DO NOTHING
            """), dict(zip(["iata","icao","name","country","year","alliance"], al)))

        print("Seeding aircraft...")
        for ac in AIRCRAFT:
            conn.execute(text("""
                INSERT INTO aircraft (model,manufacturer,seat_capacity,range_km)
                VALUES (:model,:mfr,:seats,:range)
            """), dict(zip(["model","mfr","seats","range"], ac)))

        conn.commit()

        airport_ids = {r[0]: r[1] for r in conn.execute(text("SELECT iata_code, id FROM airports"))}
        airline_ids = {r[0]: r[1] for r in conn.execute(text("SELECT iata_code, id FROM airlines"))}
        aircraft_ids = [r[0] for r in conn.execute(text("SELECT id FROM aircraft"))]
        airport_list = list(airport_ids.keys())

        print("Seeding routes...")
        route_ids = []
        for airline_code, airline_id in airline_ids.items():
            pairs = set()
            attempts = 0
            while len(pairs) < random.randint(8, 14) and attempts < 100:
                orig = random.choice(airport_list)
                dest = random.choice(airport_list)
                if orig != dest and (orig, dest) not in pairs:
                    pairs.add((orig, dest))
                attempts += 1
            for orig, dest in pairs:
                distance = random.randint(500, 12000)
                result = conn.execute(text("""
                    INSERT INTO routes (airline_id,origin_airport_id,dest_airport_id,distance_km,avg_duration_mins)
                    VALUES (:a,:o,:d,:dist,:dur)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """), {"a": airline_id, "o": airport_ids[orig], "d": airport_ids[dest],
                       "dist": distance, "dur": int(distance / 13)})
                row = result.fetchone()
                if row:
                    route_ids.append(row[0])

        conn.commit()
        print(f"   {len(route_ids)} routes created")

        print("Seeding flights...")
        now = datetime.now(timezone.utc)
        delay_cats = ["weather","technical","crew","air_traffic","security","other"]
        statuses = ["scheduled","departed","in_air","landed","cancelled"]
        weights  = [0.30, 0.10, 0.15, 0.40, 0.05]
        flight_count = 0

        for route_id in route_ids:
            dur_row = conn.execute(text("SELECT avg_duration_mins, airline_id FROM routes WHERE id=:id"), {"id": route_id}).fetchone()
            dur, airline_id = dur_row[0], dur_row[1]
            airline_code = conn.execute(text("SELECT iata_code FROM airlines WHERE id=:id"), {"id": airline_id}).fetchone()[0]

            for _ in range(random.randint(15, 28)):
                dep = now - timedelta(days=random.randint(0,90), hours=random.randint(0,23), minutes=random.choice([0,15,30,45]))
                arr = dep + timedelta(minutes=dur)
                status = random.choices(statuses, weights=weights)[0]
                ac_id  = random.choice(aircraft_ids)
                seats  = random.choice([150,162,180,296,314,396,416,555])
                sold   = random.randint(int(seats*0.4), seats)

                actual_dep = actual_arr = None
                dep_delay = arr_delay = 0
                if status in ("departed","in_air","landed"):
                    dep_delay = random.choices([0, random.randint(1,30), random.randint(31,120)], weights=[0.6,0.3,0.1])[0]
                    actual_dep = dep + timedelta(minutes=dep_delay)
                    if status == "landed":
                        actual_arr = arr + timedelta(minutes=dep_delay + random.randint(-5,15))
                        arr_delay = int((actual_arr - arr).total_seconds() / 60)

                res = conn.execute(text("""
                    INSERT INTO flights
                        (flight_number,route_id,aircraft_id,scheduled_dep,scheduled_arr,
                         actual_dep,actual_arr,status,dep_delay_mins,arr_delay_mins,
                         seats_available,seats_sold,base_price,created_at)
                    VALUES (:fn,:rid,:ac,:sdep,:sarr,:adep,:aarr,:st,:dd,:ad,:seats,:sold,:price,:now)
                    RETURNING id
                """), {
                    "fn": f"{airline_code}{random.randint(100,9999)}",
                    "rid": route_id, "ac": ac_id,
                    "sdep": dep, "sarr": arr,
                    "adep": actual_dep, "aarr": actual_arr,
                    "st": status, "dd": dep_delay, "ad": arr_delay,
                    "seats": seats, "sold": sold,
                    "price": round(random.uniform(80, 1800), 2),
                    "now": now,
                })
                flight_id = res.fetchone()[0]
                flight_count += 1

                if dep_delay > 15:
                    conn.execute(text("""
                        INSERT INTO flight_delays (flight_id,delay_category,delay_mins,recorded_at)
                        VALUES (:fid,:cat,:mins,:now)
                    """), {"fid": flight_id, "cat": random.choice(delay_cats), "mins": dep_delay, "now": now})

                if status == "landed" and random.random() > 0.5:
                    conn.execute(text("""
                        INSERT INTO reviews (flight_id,airline_id,overall_rating,seat_comfort,food_rating,staff_rating,punctuality,created_at)
                        VALUES (:fid,:aid,:overall,:seat,:food,:staff,:punct,:now)
                    """), {
                        "fid": flight_id, "aid": airline_id,
                        "overall": round(random.uniform(4.0, 10.0), 1),
                        "seat": random.randint(2,5), "food": random.randint(1,5),
                        "staff": random.randint(2,5),
                        "punct": 5 if dep_delay == 0 else random.randint(1,4),
                        "now": now,
                    })

                if flight_count % 500 == 0:
                    conn.commit()
                    print(f"   {flight_count} flights...")

        conn.commit()
        print(f"Done! {flight_count} flights seeded.")


if __name__ == "__main__":
    seed()
