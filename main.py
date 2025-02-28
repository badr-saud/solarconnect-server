import random
from asyncio import timeout
from datetime import datetime, time, timedelta
from enum import verify
from typing import List

import ping3
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth

app = FastAPI()

# middleware - CORS for front end communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schemas
class LightStatus(BaseModel):
    percentage: int
    status: str


class BatteryStatus(BaseModel):
    percentage: int
    estimated_time: str


class DataUsage(BaseModel):
    current_usage: int
    total_limit: int
    percentage_used: int


class Speed(BaseModel):
    upload: float
    download: float


class LogEntry(BaseModel):
    device_name: str
    mac_address: str
    ip_address: str
    device_type: str
    log_time: str
    data_usage: str


class SpeedHistory(BaseModel):
    timestamp: datetime
    upload_speed: float
    download_speed: float


# Dummy Data
speed_history_data = [
    SpeedHistory(
        timestamp=(datetime(2025, 1, random.randint(1, 6), 2) + timedelta(hours=i)),
        upload_speed=15 + random.randint(1, 10) * 0.5,
        download_speed=25 + random.randint(1, 10) * 0.7,
    )
    for i in range(10)  # Generate 10 dummy entries
]
light_status = LightStatus(percentage=70, status="Good")
battery_status = BatteryStatus(percentage=75, estimated_time="9 hr 40 min")
data_usage = DataUsage(current_usage=120, total_limit=500, percentage_used=24)
speed = Speed(upload=21.53, download=45.53)

logs = [
    LogEntry(
        device_name="Weng-MBP",
        mac_address="2E:57:78:5A:85:37",
        ip_address="37.26.77.113",
        device_type="Laptop",
        log_time="3h ago",
        data_usage="12.97GB",
    ),
    LogEntry(
        device_name="Fiigo_MBP",
        mac_address="0D:6A:7D:8F:A2:8A",
        ip_address="19.10.17.89",
        device_type="Desktop",
        log_time="5m ago",
        data_usage="312.43MB",
    ),
]

ROUTER_IP = "192.168.100.1"
USERNAME = "root"
# PASSWORD = "DkGVfz9A"
PASSWORD = "HBMRMuq4"


# EndPoints
@app.get("/light-status", response_model=LightStatus)
async def get_light_status():
    return light_status


@app.get("/battery-status", response_model=BatteryStatus)
async def get_battery_status():
    return battery_status

@app.get("/data-usage", response_model=DataUsage)
async def get_data_usage():
    return data_usage


@app.get("/speed", response_model=Speed)
async def get_speed():
    return speed


@app.get("/logs", response_model=List[LogEntry])
async def get_logs():
    return logs


@app.get("/speed-history", response_model=List[SpeedHistory])
async def get_speed_history():
    return speed_history_data


@app.get("/router/status")
async def get_router_status(request):
    try:
        response_time = ping3.ping(ROUTER_IP)

        if response_time is None:
            return {"status": "offline"}

        router_url = f"http//{ROUTER_IP}"
        response = request.get(
            router_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=5, verify=False
        )

        return {
            "status": "Online",
            "response_time_ms": round(response_time * 1000, 2),
            "http_status": response.status_code,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
