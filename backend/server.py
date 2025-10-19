from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import math


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class ParkingSpot(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str
    area: str
    city: str
    latitude: float
    longitude: float
    price: float  # Price per hour
    availability: bool
    operating_hours: str
    type: str  # "street" or "garage"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ParkingSpotCreate(BaseModel):
    name: str
    address: str
    area: str
    city: str
    latitude: float
    longitude: float
    price: float
    availability: bool = True
    operating_hours: str = "24/7"
    type: str = "street"

class ParkingSpotResponse(BaseModel):
    id: str
    name: str
    address: str
    area: str
    city: str
    latitude: float
    longitude: float
    price: float
    availability: bool
    operating_hours: str
    type: str
    distance: Optional[float] = None  # Distance in km


# Haversine formula to calculate distance between two points
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points on Earth using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return round(distance, 2)


# Routes
@api_router.get("/")
async def root():
    return {"message": "Welcome to MyParkingService API"}

@api_router.post("/parking", response_model=ParkingSpot)
async def create_parking_spot(input: ParkingSpotCreate):
    """Create a new parking spot"""
    parking_dict = input.model_dump()
    parking_obj = ParkingSpot(**parking_dict)
    
    doc = parking_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.parking_spots.insert_one(doc)
    return parking_obj

@api_router.get("/parking/nearby", response_model=List[ParkingSpotResponse])
async def get_nearby_parking(
    lat: float = Query(..., description="Latitude of user location"),
    lng: float = Query(..., description="Longitude of user location"),
    radius: float = Query(5.0, description="Search radius in kilometers")
):
    """Find parking spots within radius of given coordinates"""
    # Get all parking spots
    spots = await db.parking_spots.find({}, {"_id": 0}).to_list(1000)
    
    # Calculate distance for each spot and filter by radius
    nearby_spots = []
    for spot in spots:
        distance = calculate_distance(lat, lng, spot['latitude'], spot['longitude'])
        if distance <= radius:
            spot['distance'] = distance
            nearby_spots.append(ParkingSpotResponse(**spot))
    
    # Sort by distance
    nearby_spots.sort(key=lambda x: x.distance)
    
    return nearby_spots

@api_router.get("/parking/search", response_model=List[ParkingSpotResponse])
async def search_parking_by_area(
    area: str = Query(..., description="Area name"),
    city: str = Query(..., description="City name")
):
    """Search parking spots by area and city"""
    # Case-insensitive search
    spots = await db.parking_spots.find(
        {
            "area": {"$regex": area, "$options": "i"},
            "city": {"$regex": city, "$options": "i"}
        },
        {"_id": 0}
    ).to_list(1000)
    
    return [ParkingSpotResponse(**spot) for spot in spots]

@api_router.get("/parking/all", response_model=List[ParkingSpotResponse])
async def get_all_parking():
    """Get all parking spots"""
    spots = await db.parking_spots.find({}, {"_id": 0}).to_list(1000)
    return [ParkingSpotResponse(**spot) for spot in spots]

@api_router.post("/parking/seed")
async def seed_parking_data():
    """Seed sample parking data"""
    # Check if data already exists
    existing = await db.parking_spots.count_documents({})
    if existing > 0:
        return {"message": "Database already seeded", "count": existing}
    
    sample_data = [
        # Kota, Rajasthan, India
        {
            "name": "Electricity Board Area Parking",
            "address": "Near Power House, Electricity Board Area",
            "area": "Electricity Board Area",
            "city": "Kota",
            "latitude": 25.1826,
            "longitude": 75.8368,
            "price": 20.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "street"
        },
        {
            "name": "Power House Multi-Level Parking",
            "address": "Electricity Board Complex",
            "area": "Electricity Board Area",
            "city": "Kota",
            "latitude": 25.1830,
            "longitude": 75.8375,
            "price": 30.0,
            "availability": True,
            "operating_hours": "6:00 AM - 10:00 PM",
            "type": "garage"
        },
        {
            "name": "Industrial Area Parking Zone",
            "address": "Industrial Area Road",
            "area": "Electricity Board Area",
            "city": "Kota",
            "latitude": 25.1820,
            "longitude": 75.8360,
            "price": 15.0,
            "availability": False,
            "operating_hours": "24/7",
            "type": "street"
        },
        {
            "name": "Chambal Garden Parking",
            "address": "Near Chambal Garden",
            "area": "Amar Colony",
            "city": "Kota",
            "latitude": 25.1460,
            "longitude": 75.8572,
            "price": 10.0,
            "availability": True,
            "operating_hours": "5:00 AM - 10:00 PM",
            "type": "street"
        },
        {
            "name": "Seven Wonders Park Parking",
            "address": "Kishore Sagar Lake Road",
            "area": "Civil Lines",
            "city": "Kota",
            "latitude": 25.1831,
            "longitude": 75.8347,
            "price": 20.0,
            "availability": True,
            "operating_hours": "8:00 AM - 8:00 PM",
            "type": "garage"
        },
        # Jaipur, Rajasthan
        {
            "name": "Pink City Parking Plaza",
            "address": "MI Road",
            "area": "Jaipur City Center",
            "city": "Jaipur",
            "latitude": 26.9124,
            "longitude": 75.7873,
            "price": 25.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "garage"
        },
        {
            "name": "Hawa Mahal Street Parking",
            "address": "Near Hawa Mahal",
            "area": "Old City",
            "city": "Jaipur",
            "latitude": 26.9239,
            "longitude": 75.8267,
            "price": 15.0,
            "availability": True,
            "operating_hours": "6:00 AM - 11:00 PM",
            "type": "street"
        },
        # Delhi
        {
            "name": "Connaught Place Parking",
            "address": "Block A, Connaught Place",
            "area": "Connaught Place",
            "city": "Delhi",
            "latitude": 28.6315,
            "longitude": 77.2167,
            "price": 40.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "garage"
        },
        {
            "name": "India Gate Parking Area",
            "address": "Rajpath",
            "area": "Central Delhi",
            "city": "Delhi",
            "latitude": 28.6129,
            "longitude": 77.2295,
            "price": 30.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "street"
        },
        # Mumbai
        {
            "name": "Gateway of India Parking",
            "address": "Apollo Bunder",
            "area": "Colaba",
            "city": "Mumbai",
            "latitude": 18.9220,
            "longitude": 72.8347,
            "price": 50.0,
            "availability": False,
            "operating_hours": "24/7",
            "type": "garage"
        },
        {
            "name": "Marine Drive Parking Zone",
            "address": "Marine Drive",
            "area": "South Mumbai",
            "city": "Mumbai",
            "latitude": 18.9432,
            "longitude": 72.8236,
            "price": 35.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "street"
        },
        # New York
        {
            "name": "Times Square Parking Garage",
            "address": "234 W 42nd St",
            "area": "Midtown",
            "city": "New York",
            "latitude": 40.7580,
            "longitude": -73.9855,
            "price": 25.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "garage"
        },
        {
            "name": "Central Park West Street Parking",
            "address": "Central Park West",
            "area": "Upper West Side",
            "city": "New York",
            "latitude": 40.7829,
            "longitude": -73.9654,
            "price": 8.0,
            "availability": True,
            "operating_hours": "8:00 AM - 8:00 PM",
            "type": "street"
        },
        {
            "name": "Wall Street Parking Plaza",
            "address": "25 Broadway",
            "area": "Financial District",
            "city": "New York",
            "latitude": 40.7074,
            "longitude": -74.0113,
            "price": 30.0,
            "availability": False,
            "operating_hours": "6:00 AM - 11:00 PM",
            "type": "garage"
        },
        # San Francisco
        {
            "name": "Golden Gate Parking",
            "address": "Lincoln Blvd",
            "area": "Presidio",
            "city": "San Francisco",
            "latitude": 37.8199,
            "longitude": -122.4783,
            "price": 5.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "street"
        },
        {
            "name": "Union Square Garage",
            "address": "333 Post St",
            "area": "Downtown",
            "city": "San Francisco",
            "latitude": 37.7879,
            "longitude": -122.4074,
            "price": 18.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "garage"
        },
        {
            "name": "Fisherman's Wharf Parking",
            "address": "Pier 39",
            "area": "Waterfront",
            "city": "San Francisco",
            "latitude": 37.8087,
            "longitude": -122.4098,
            "price": 12.0,
            "availability": True,
            "operating_hours": "7:00 AM - 10:00 PM",
            "type": "garage"
        },
        # Los Angeles
        {
            "name": "Hollywood Boulevard Parking",
            "address": "6801 Hollywood Blvd",
            "area": "Hollywood",
            "city": "Los Angeles",
            "latitude": 34.1016,
            "longitude": -118.3406,
            "price": 10.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "street"
        },
        {
            "name": "Santa Monica Beach Parking",
            "address": "1550 Pacific Coast Hwy",
            "area": "Santa Monica",
            "city": "Los Angeles",
            "latitude": 34.0195,
            "longitude": -118.4912,
            "price": 8.0,
            "availability": True,
            "operating_hours": "5:00 AM - 12:00 AM",
            "type": "garage"
        },
        {
            "name": "Downtown LA Parking Structure",
            "address": "350 S Grand Ave",
            "area": "Downtown",
            "city": "Los Angeles",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "price": 15.0,
            "availability": False,
            "operating_hours": "6:00 AM - 10:00 PM",
            "type": "garage"
        },
        # Chicago
        {
            "name": "Millennium Park Garage",
            "address": "5 S Columbus Dr",
            "area": "Loop",
            "city": "Chicago",
            "latitude": 41.8826,
            "longitude": -87.6226,
            "price": 22.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "garage"
        },
        {
            "name": "Navy Pier Parking",
            "address": "600 E Grand Ave",
            "area": "Streeterville",
            "city": "Chicago",
            "latitude": 41.8917,
            "longitude": -87.6086,
            "price": 20.0,
            "availability": True,
            "operating_hours": "10:00 AM - 10:00 PM",
            "type": "garage"
        },
        {
            "name": "Wrigley Field Street Parking",
            "address": "1060 W Addison St",
            "area": "Lakeview",
            "city": "Chicago",
            "latitude": 41.9484,
            "longitude": -87.6553,
            "price": 6.0,
            "availability": True,
            "operating_hours": "24/7",
            "type": "street"
        }
    ]
    
    # Create parking spots
    for data in sample_data:
        parking_obj = ParkingSpot(**data)
        doc = parking_obj.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.parking_spots.insert_one(doc)
    
    return {"message": "Successfully seeded parking data", "count": len(sample_data)}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()