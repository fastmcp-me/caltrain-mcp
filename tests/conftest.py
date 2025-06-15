from io import StringIO

import pandas as pd
import pytest

from caltrain_mcp import gtfs


@pytest.fixture(autouse=True)
def fake_gtfs(monkeypatch):
    """Inject minimal GTFS frames so load_gtfs_data() isn't needed."""
    # --- stops -------------------------------------------------
    stops_csv = """stop_id,stop_name,location_type,parent_station
100,San Francisco Caltrain,1,
101,San Francisco Caltrain Platform 1,0,100
200,Palo Alto,1,
201,Palo Alto Platform 1,0,200
"""
    gtfs.ALL_STOPS_DF = pd.read_csv(StringIO(stops_csv))
    # Ensure consistent data types for stop_id columns (like in real GTFS loading)
    gtfs.ALL_STOPS_DF["stop_id"] = gtfs.ALL_STOPS_DF["stop_id"].astype(str)

    gtfs.STATIONS_DF = gtfs.ALL_STOPS_DF[gtfs.ALL_STOPS_DF.location_type == 1].copy()
    gtfs.STATIONS_DF["normalized_name"] = (
        gtfs.STATIONS_DF.stop_name.str.lower().str.replace(" caltrain", "")
    )

    # --- calendar ---------------------------------------------
    cal_csv = """service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
WEEKDAY,1,1,1,1,1,0,0,20250101,20251231
"""
    gtfs.CALENDAR_DF = pd.read_csv(StringIO(cal_csv))

    # --- trips -------------------------------------------------
    trips_csv = "route_id,service_id,trip_id,trip_headsign,trip_short_name\n1,WEEKDAY,T1,San Jose,SJ\n"
    gtfs.TRIPS_DF = pd.read_csv(StringIO(trips_csv))

    # --- stop_times -------------------------------------------
    st_csv = """trip_id,arrival_time,departure_time,stop_id,stop_sequence
T1,08:00:00,08:00:00,101,1
T1,08:50:00,08:50:00,201,2
"""
    gtfs.STOP_TIMES_DF = pd.read_csv(StringIO(st_csv))
    # Ensure consistent data types for stop_id columns (like in real GTFS loading)
    gtfs.STOP_TIMES_DF["stop_id"] = gtfs.STOP_TIMES_DF["stop_id"].astype(str)

    def _conv(v):
        if pd.isna(v):
            return None
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)

    parent_station_str = gtfs.ALL_STOPS_DF["parent_station"].apply(_conv)
    gtfs.ALL_STOPS_DF["parent_station_str"] = parent_station_str
    grouped = (
        gtfs.ALL_STOPS_DF.dropna(subset=["parent_station_str"])
        .groupby("parent_station_str")["stop_id"]
        .apply(lambda s: s.astype(str).tolist())
    )
    gtfs.STATION_TO_PLATFORM_STOPS = grouped.to_dict()
