from fastapi import FastAPI, APIRouter, HTTPException, Query, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import math
import razorpay
import hmac
import hashlib


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Razorpay client
razorpay_client = razorpay.Client(auth=(os.environ['RAZORPAY_KEY_ID'], os.environ['RAZORPAY_KEY_SECRET']))

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
    state: str
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
    state: str
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
    state: str
    latitude: float
    longitude: float
    price: float
    availability: bool
    operating_hours: str
    type: str
    distance: Optional[float] = None  # Distance in km

class BookingCreate(BaseModel):
    parking_spot_id: str
    user_name: str
    user_email: str
    user_phone: str
    vehicle_number: str
    start_time: datetime
    duration_hours: int  # Duration in hours

class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parking_spot_id: str
    user_name: str
    user_email: str
    user_phone: str
    vehicle_number: str
    start_time: datetime
    end_time: datetime
    duration_hours: int
    total_amount: float
    payment_status: str = "pending"  # pending, paid, failed, refunded
    booking_status: str = "active"  # active, completed, cancelled
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BookingResponse(BaseModel):
    id: str
    parking_spot_id: str
    parking_spot_name: str
    parking_spot_address: str
    user_name: str
    user_email: str
    user_phone: str
    vehicle_number: str
    start_time: datetime
    end_time: datetime
    duration_hours: int
    total_amount: float
    payment_status: str
    booking_status: str
    razorpay_order_id: Optional[str] = None
    created_at: datetime

class RazorpayOrderCreate(BaseModel):
    booking_id: str

class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    booking_id: str


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
    spots = await db.parking_spots.find({}, {"_id": 0}).to_list(10000)
    
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
    area: str = Query(None, description="Area name"),
    city: str = Query(None, description="City name"),
    state: str = Query(None, description="State name")
):
    """Search parking spots by area, city, and/or state"""
    query = {}
    if area:
        query["area"] = {"$regex": area, "$options": "i"}
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if state:
        query["state"] = {"$regex": state, "$options": "i"}
    
    if not query:
        raise HTTPException(status_code=400, detail="Please provide at least one search parameter")
    
    spots = await db.parking_spots.find(query, {"_id": 0}).to_list(1000)
    return [ParkingSpotResponse(**spot) for spot in spots]

@api_router.get("/parking/all", response_model=List[ParkingSpotResponse])
async def get_all_parking():
    """Get all parking spots"""
    spots = await db.parking_spots.find({}, {"_id": 0}).to_list(10000)
    return [ParkingSpotResponse(**spot) for spot in spots]

# Booking APIs
@api_router.post("/bookings/create")
async def create_booking(booking_input: BookingCreate):
    """Create a new booking"""
    # Get parking spot details
    parking_spot = await db.parking_spots.find_one({"id": booking_input.parking_spot_id}, {"_id": 0})
    if not parking_spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")
    
    if not parking_spot['availability']:
        raise HTTPException(status_code=400, detail="Parking spot is not available")
    
    # Calculate end time and total amount
    end_time = booking_input.start_time + timedelta(hours=booking_input.duration_hours)
    total_amount = parking_spot['price'] * booking_input.duration_hours
    
    # Create booking
    booking = Booking(
        parking_spot_id=booking_input.parking_spot_id,
        user_name=booking_input.user_name,
        user_email=booking_input.user_email,
        user_phone=booking_input.user_phone,
        vehicle_number=booking_input.vehicle_number,
        start_time=booking_input.start_time,
        end_time=end_time,
        duration_hours=booking_input.duration_hours,
        total_amount=total_amount
    )
    
    # Save booking to database
    doc = booking.model_dump()
    doc['start_time'] = doc['start_time'].isoformat()
    doc['end_time'] = doc['end_time'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.bookings.insert_one(doc)
    
    return {
        "booking_id": booking.id,
        "total_amount": total_amount,
        "parking_spot_name": parking_spot['name'],
        "message": "Booking created successfully. Proceed with payment."
    }

@api_router.post("/bookings/create-razorpay-order")
async def create_razorpay_order(order_data: RazorpayOrderCreate):
    """Create Razorpay order for payment"""
    # Get booking details
    booking = await db.bookings.find_one({"id": order_data.booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Create Razorpay order
    amount_in_paise = int(booking['total_amount'] * 100)  # Convert to paise
    order_data_razorpay = {
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"booking_{booking['id']}",
        "notes": {
            "booking_id": booking['id'],
            "parking_spot_id": booking['parking_spot_id']
        }
    }
    
    try:
        razorpay_order = razorpay_client.order.create(data=order_data_razorpay)
        
        # Update booking with Razorpay order ID
        await db.bookings.update_one(
            {"id": order_data.booking_id},
            {"$set": {"razorpay_order_id": razorpay_order['id']}}
        )
        
        return {
            "order_id": razorpay_order['id'],
            "amount": razorpay_order['amount'],
            "currency": razorpay_order['currency'],
            "booking_id": booking['id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Razorpay order: {str(e)}")

@api_router.post("/bookings/verify-payment")
async def verify_payment(payment_data: PaymentVerification):
    """Verify Razorpay payment signature"""
    # Verify signature
    generated_signature = hmac.new(
        os.environ['RAZORPAY_KEY_SECRET'].encode(),
        f"{payment_data.razorpay_order_id}|{payment_data.razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    if generated_signature != payment_data.razorpay_signature:
        # Payment verification failed
        await db.bookings.update_one(
            {"id": payment_data.booking_id},
            {"$set": {"payment_status": "failed"}}
        )
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    # Payment verified successfully
    await db.bookings.update_one(
        {"id": payment_data.booking_id},
        {"$set": {
            "payment_status": "paid",
            "razorpay_payment_id": payment_data.razorpay_payment_id
        }}
    )
    
    return {"message": "Payment verified successfully", "booking_id": payment_data.booking_id}

@api_router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """Get booking details"""
    booking = await db.bookings.find_one({"id": booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get parking spot details
    parking_spot = await db.parking_spots.find_one({"id": booking['parking_spot_id']}, {"_id": 0})
    
    # Parse datetime strings back to datetime objects
    if isinstance(booking['start_time'], str):
        booking['start_time'] = datetime.fromisoformat(booking['start_time'])
    if isinstance(booking['end_time'], str):
        booking['end_time'] = datetime.fromisoformat(booking['end_time'])
    if isinstance(booking['created_at'], str):
        booking['created_at'] = datetime.fromisoformat(booking['created_at'])
    
    return {
        **booking,
        "parking_spot_name": parking_spot['name'] if parking_spot else "Unknown",
        "parking_spot_address": parking_spot['address'] if parking_spot else "Unknown"
    }

@api_router.get("/bookings/user/{email}")
async def get_user_bookings(email: str):
    """Get all bookings for a user"""
    bookings = await db.bookings.find({"user_email": email}, {"_id": 0}).to_list(1000)
    
    # Get parking spot details for each booking
    result = []
    for booking in bookings:
        parking_spot = await db.parking_spots.find_one({"id": booking['parking_spot_id']}, {"_id": 0})
        
        # Parse datetime strings
        if isinstance(booking['start_time'], str):
            booking['start_time'] = datetime.fromisoformat(booking['start_time'])
        if isinstance(booking['end_time'], str):
            booking['end_time'] = datetime.fromisoformat(booking['end_time'])
        if isinstance(booking['created_at'], str):
            booking['created_at'] = datetime.fromisoformat(booking['created_at'])
        
        result.append({
            **booking,
            "parking_spot_name": parking_spot['name'] if parking_spot else "Unknown",
            "parking_spot_address": parking_spot['address'] if parking_spot else "Unknown"
        })
    
    return result


@api_router.post("/parking/seed")
async def seed_parking_data():
    """Seed sample parking data for all major Indian cities"""
    # Clear existing data to allow reseeding
    await db.parking_spots.delete_many({})
    
    # Comprehensive Indian parking data across all states
    indian_parking_data = [
        # Rajasthan
        {"name": "Electricity Board Area Parking", "address": "Near Power House, Electricity Board Area", "area": "Electricity Board Area", "city": "Kota", "state": "Rajasthan", "latitude": 25.1826, "longitude": 75.8368, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Power House Multi-Level Parking", "address": "Electricity Board Complex", "area": "Electricity Board Area", "city": "Kota", "state": "Rajasthan", "latitude": 25.1830, "longitude": 75.8375, "price": 30.0, "availability": True, "operating_hours": "6:00 AM - 10:00 PM", "type": "garage"},
        {"name": "Industrial Area Parking Zone", "address": "Industrial Area Road", "area": "Electricity Board Area", "city": "Kota", "state": "Rajasthan", "latitude": 25.1820, "longitude": 75.8360, "price": 15.0, "availability": False, "operating_hours": "24/7", "type": "street"},
        {"name": "Chambal Garden Parking", "address": "Near Chambal Garden", "area": "Amar Colony", "city": "Kota", "state": "Rajasthan", "latitude": 25.1460, "longitude": 75.8572, "price": 10.0, "availability": True, "operating_hours": "5:00 AM - 10:00 PM", "type": "street"},
        {"name": "Seven Wonders Park Parking", "address": "Kishore Sagar Lake Road", "area": "Civil Lines", "city": "Kota", "state": "Rajasthan", "latitude": 25.1831, "longitude": 75.8347, "price": 20.0, "availability": True, "operating_hours": "8:00 AM - 8:00 PM", "type": "garage"},
        {"name": "Pink City Parking Plaza", "address": "MI Road", "area": "City Center", "city": "Jaipur", "state": "Rajasthan", "latitude": 26.9124, "longitude": 75.7873, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Hawa Mahal Street Parking", "address": "Near Hawa Mahal", "area": "Old City", "city": "Jaipur", "state": "Rajasthan", "latitude": 26.9239, "longitude": 75.8267, "price": 15.0, "availability": True, "operating_hours": "6:00 AM - 11:00 PM", "type": "street"},
        {"name": "Amber Fort Parking", "address": "Amber Fort Road", "area": "Amber", "city": "Jaipur", "state": "Rajasthan", "latitude": 26.9855, "longitude": 75.8513, "price": 20.0, "availability": True, "operating_hours": "8:00 AM - 6:00 PM", "type": "garage"},
        {"name": "Jodhpur Clock Tower Parking", "address": "Near Ghanta Ghar", "area": "Sardar Market", "city": "Jodhpur", "state": "Rajasthan", "latitude": 26.2941, "longitude": 73.0240, "price": 15.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Mehrangarh Fort Parking", "address": "Fort Road", "area": "Fort Area", "city": "Jodhpur", "state": "Rajasthan", "latitude": 26.2983, "longitude": 73.0181, "price": 30.0, "availability": True, "operating_hours": "9:00 AM - 6:00 PM", "type": "garage"},
        {"name": "Lake Pichola Parking", "address": "Near City Palace", "area": "Old City", "city": "Udaipur", "state": "Rajasthan", "latitude": 24.5761, "longitude": 73.6832, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Nahargarh Fort Parking", "address": "Fort Road", "area": "Aravalli Hills", "city": "Bundi", "state": "Rajasthan", "latitude": 25.4382, "longitude": 75.6359, "price": 10.0, "availability": True, "operating_hours": "8:00 AM - 6:00 PM", "type": "street"},
        
        # Delhi
        {"name": "Connaught Place Parking", "address": "Block A, Connaught Place", "area": "Connaught Place", "city": "Delhi", "state": "Delhi", "latitude": 28.6315, "longitude": 77.2167, "price": 40.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "India Gate Parking Area", "address": "Rajpath", "area": "Central Delhi", "city": "Delhi", "state": "Delhi", "latitude": 28.6129, "longitude": 77.2295, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Red Fort Parking", "address": "Netaji Subhash Marg", "area": "Old Delhi", "city": "Delhi", "state": "Delhi", "latitude": 28.6562, "longitude": 77.2410, "price": 35.0, "availability": True, "operating_hours": "9:00 AM - 7:00 PM", "type": "garage"},
        {"name": "Qutub Minar Parking", "address": "Mehrauli", "area": "South Delhi", "city": "Delhi", "state": "Delhi", "latitude": 28.5245, "longitude": 77.1855, "price": 25.0, "availability": True, "operating_hours": "7:00 AM - 6:00 PM", "type": "garage"},
        {"name": "Saket Mall Parking", "address": "Select Citywalk", "area": "Saket", "city": "Delhi", "state": "Delhi", "latitude": 28.5244, "longitude": 77.2066, "price": 50.0, "availability": True, "operating_hours": "10:00 AM - 11:00 PM", "type": "garage"},
        
        # Maharashtra
        {"name": "Gateway of India Parking", "address": "Apollo Bunder", "area": "Colaba", "city": "Mumbai", "state": "Maharashtra", "latitude": 18.9220, "longitude": 72.8347, "price": 50.0, "availability": False, "operating_hours": "24/7", "type": "garage"},
        {"name": "Marine Drive Parking Zone", "address": "Marine Drive", "area": "South Mumbai", "city": "Mumbai", "state": "Maharashtra", "latitude": 18.9432, "longitude": 72.8236, "price": 35.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Bandra Kurla Complex Parking", "address": "BKC Main Road", "area": "BKC", "city": "Mumbai", "state": "Maharashtra", "latitude": 19.0633, "longitude": 72.8679, "price": 60.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "CST Station Parking", "address": "Chhatrapati Shivaji Terminus", "area": "Fort", "city": "Mumbai", "state": "Maharashtra", "latitude": 18.9401, "longitude": 72.8350, "price": 40.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Shivaji Nagar Parking Plaza", "address": "FC Road", "area": "Shivajinagar", "city": "Pune", "state": "Maharashtra", "latitude": 18.5304, "longitude": 73.8436, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Koregaon Park Parking", "address": "North Main Road", "area": "Koregaon Park", "city": "Pune", "state": "Maharashtra", "latitude": 18.5435, "longitude": 73.8957, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Sitabuldi Fort Parking", "address": "Central Avenue", "area": "Sitabuldi", "city": "Nagpur", "state": "Maharashtra", "latitude": 21.1499, "longitude": 79.0855, "price": 15.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        
        # Karnataka
        {"name": "MG Road Metro Parking", "address": "MG Road", "area": "Central Bangalore", "city": "Bangalore", "state": "Karnataka", "latitude": 12.9760, "longitude": 77.6060, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Brigade Road Parking", "address": "Brigade Road", "area": "Central Bangalore", "city": "Bangalore", "state": "Karnataka", "latitude": 12.9726, "longitude": 77.6081, "price": 40.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Cubbon Park Parking", "address": "Kasturba Road", "area": "Cubbon Park", "city": "Bangalore", "state": "Karnataka", "latitude": 12.9767, "longitude": 77.5926, "price": 20.0, "availability": True, "operating_hours": "6:00 AM - 10:00 PM", "type": "street"},
        {"name": "Electronic City Parking Hub", "address": "Phase 1", "area": "Electronic City", "city": "Bangalore", "state": "Karnataka", "latitude": 12.8397, "longitude": 77.6771, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Mysore Palace Parking", "address": "Sayyaji Rao Road", "area": "Central Mysore", "city": "Mysore", "state": "Karnataka", "latitude": 12.3052, "longitude": 76.6550, "price": 15.0, "availability": True, "operating_hours": "10:00 AM - 6:00 PM", "type": "garage"},
        {"name": "Chamundi Hills Parking", "address": "Chamundi Hills Road", "area": "Chamundi Hills", "city": "Mysore", "state": "Karnataka", "latitude": 12.2725, "longitude": 76.6729, "price": 10.0, "availability": True, "operating_hours": "7:00 AM - 7:00 PM", "type": "street"},
        
        # Tamil Nadu
        {"name": "Marina Beach Parking", "address": "Kamarajar Salai", "area": "Marina Beach", "city": "Chennai", "state": "Tamil Nadu", "latitude": 13.0499, "longitude": 80.2824, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "T Nagar Parking Plaza", "address": "Pondy Bazaar", "area": "T Nagar", "city": "Chennai", "state": "Tamil Nadu", "latitude": 13.0418, "longitude": 80.2341, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Vadapalani Parking", "address": "Arcot Road", "area": "Vadapalani", "city": "Chennai", "state": "Tamil Nadu", "latitude": 13.0502, "longitude": 80.2120, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Meenakshi Temple Parking", "address": "Madurai Main", "area": "Central Madurai", "city": "Madurai", "state": "Tamil Nadu", "latitude": 9.9195, "longitude": 78.1193, "price": 15.0, "availability": True, "operating_hours": "5:00 AM - 10:00 PM", "type": "garage"},
        {"name": "Gandhipuram Parking Hub", "address": "Gandhipuram", "area": "Central Coimbatore", "city": "Coimbatore", "state": "Tamil Nadu", "latitude": 11.0183, "longitude": 76.9674, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        
        # West Bengal
        {"name": "Park Street Parking", "address": "Park Street", "area": "Central Kolkata", "city": "Kolkata", "state": "West Bengal", "latitude": 22.5542, "longitude": 88.3519, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Howrah Bridge Parking", "address": "Strand Road", "area": "Howrah", "city": "Kolkata", "state": "West Bengal", "latitude": 22.5851, "longitude": 88.3470, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Victoria Memorial Parking", "address": "Queens Way", "area": "Maidan", "city": "Kolkata", "state": "West Bengal", "latitude": 22.5448, "longitude": 88.3426, "price": 25.0, "availability": True, "operating_hours": "10:00 AM - 6:00 PM", "type": "garage"},
        {"name": "New Market Parking", "address": "Lindsay Street", "area": "New Market", "city": "Kolkata", "state": "West Bengal", "latitude": 22.5561, "longitude": 88.3526, "price": 15.0, "availability": True, "operating_hours": "10:00 AM - 9:00 PM", "type": "street"},
        
        # Gujarat
        {"name": "Sabarmati Ashram Parking", "address": "Ashram Road", "area": "Sabarmati", "city": "Ahmedabad", "state": "Gujarat", "latitude": 23.0600, "longitude": 72.5805, "price": 15.0, "availability": True, "operating_hours": "8:30 AM - 6:30 PM", "type": "street"},
        {"name": "CG Road Parking Plaza", "address": "CG Road", "area": "Navrangpura", "city": "Ahmedabad", "state": "Gujarat", "latitude": 23.0340, "longitude": 72.5569, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Law Garden Parking", "address": "Law Garden", "area": "Ellisbridge", "city": "Ahmedabad", "state": "Gujarat", "latitude": 23.0255, "longitude": 72.5575, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Rani ki Vav Parking", "address": "Patan Main Road", "area": "Patan", "city": "Patan", "state": "Gujarat", "latitude": 23.8589, "longitude": 72.1026, "price": 10.0, "availability": True, "operating_hours": "8:00 AM - 6:00 PM", "type": "garage"},
        
        # Telangana
        {"name": "Charminar Parking", "address": "Charminar Road", "area": "Old City", "city": "Hyderabad", "state": "Telangana", "latitude": 17.3616, "longitude": 78.4747, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Hitech City Parking Hub", "address": "Hitech City Main Road", "area": "Madhapur", "city": "Hyderabad", "state": "Telangana", "latitude": 17.4485, "longitude": 78.3908, "price": 40.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Banjara Hills Parking", "address": "Road No. 1", "area": "Banjara Hills", "city": "Hyderabad", "state": "Telangana", "latitude": 17.4239, "longitude": 78.4422, "price": 35.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Hussain Sagar Lake Parking", "address": "Tank Bund Road", "area": "Hussain Sagar", "city": "Hyderabad", "state": "Telangana", "latitude": 17.4239, "longitude": 78.4738, "price": 15.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        
        # Kerala
        {"name": "Marine Drive Parking", "address": "Marine Drive", "area": "Ernakulam", "city": "Kochi", "state": "Kerala", "latitude": 9.9667, "longitude": 76.2833, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Fort Kochi Parking", "address": "Princess Street", "area": "Fort Kochi", "city": "Kochi", "state": "Kerala", "latitude": 9.9652, "longitude": 76.2419, "price": 15.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Kovalam Beach Parking", "address": "Beach Road", "area": "Kovalam", "city": "Thiruvananthapuram", "state": "Kerala", "latitude": 8.4004, "longitude": 76.9781, "price": 20.0, "availability": True, "operating_hours": "6:00 AM - 10:00 PM", "type": "street"},
        {"name": "Calicut Beach Parking", "address": "Beach Road", "area": "Calicut Beach", "city": "Kozhikode", "state": "Kerala", "latitude": 11.2494, "longitude": 75.7719, "price": 15.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        
        # Uttar Pradesh
        {"name": "Taj Mahal Parking Complex", "address": "East Gate", "area": "Taj Ganj", "city": "Agra", "state": "Uttar Pradesh", "latitude": 27.1751, "longitude": 78.0421, "price": 50.0, "availability": True, "operating_hours": "6:00 AM - 7:00 PM", "type": "garage"},
        {"name": "Agra Fort Parking", "address": "Rakabganj", "area": "Agra Fort", "city": "Agra", "state": "Uttar Pradesh", "latitude": 27.1795, "longitude": 78.0211, "price": 30.0, "availability": True, "operating_hours": "6:00 AM - 6:00 PM", "type": "garage"},
        {"name": "Hazratganj Parking Plaza", "address": "Hazratganj", "area": "Central Lucknow", "city": "Lucknow", "state": "Uttar Pradesh", "latitude": 26.8551, "longitude": 80.9429, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Dashashwamedh Ghat Parking", "address": "Ghat Road", "area": "Old Varanasi", "city": "Varanasi", "state": "Uttar Pradesh", "latitude": 25.3105, "longitude": 83.0102, "price": 15.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        
        # Punjab
        {"name": "Golden Temple Parking", "address": "Golden Temple Road", "area": "Old City", "city": "Amritsar", "state": "Punjab", "latitude": 31.6200, "longitude": 74.8765, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Jallianwala Bagh Parking", "address": "Near Golden Temple", "area": "Old City", "city": "Amritsar", "state": "Punjab", "latitude": 31.6219, "longitude": 74.8795, "price": 15.0, "availability": True, "operating_hours": "10:00 AM - 6:00 PM", "type": "street"},
        {"name": "Sector 17 Market Parking", "address": "Sector 17", "area": "City Center", "city": "Chandigarh", "state": "Punjab", "latitude": 30.7411, "longitude": 76.7869, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Rock Garden Parking", "address": "Sector 1", "area": "Rock Garden", "city": "Chandigarh", "state": "Punjab", "latitude": 30.7523, "longitude": 76.8102, "price": 20.0, "availability": True, "operating_hours": "9:00 AM - 7:00 PM", "type": "garage"},
        
        # Haryana
        {"name": "Cyber Hub Parking", "address": "DLF Cyber City", "area": "Cyber Hub", "city": "Gurgaon", "state": "Haryana", "latitude": 28.4951, "longitude": 77.0891, "price": 50.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Kingdom of Dreams Parking", "address": "Sector 29", "area": "Leisure Valley", "city": "Gurgaon", "state": "Haryana", "latitude": 28.4636, "longitude": 77.0769, "price": 40.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Ambience Mall Parking", "address": "NH-8", "area": "Ambience Island", "city": "Gurgaon", "state": "Haryana", "latitude": 28.5012, "longitude": 77.1039, "price": 30.0, "availability": True, "operating_hours": "10:00 AM - 11:00 PM", "type": "garage"},
        
        # Madhya Pradesh
        {"name": "Khajuraho Temple Parking", "address": "Western Group", "area": "Khajuraho", "city": "Khajuraho", "state": "Madhya Pradesh", "latitude": 24.8318, "longitude": 79.9199, "price": 25.0, "availability": True, "operating_hours": "6:00 AM - 6:00 PM", "type": "garage"},
        {"name": "Van Vihar Parking", "address": "Van Vihar Road", "area": "Van Vihar", "city": "Bhopal", "state": "Madhya Pradesh", "latitude": 23.2357, "longitude": 77.4039, "price": 15.0, "availability": True, "operating_hours": "8:00 AM - 6:00 PM", "type": "street"},
        {"name": "Upper Lake Parking", "address": "VIP Road", "area": "Bhopal Lake", "city": "Bhopal", "state": "Madhya Pradesh", "latitude": 23.2445, "longitude": 77.3943, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        
        # Goa
        {"name": "Baga Beach Parking", "address": "Baga Beach Road", "area": "Baga", "city": "Panaji", "state": "Goa", "latitude": 15.5557, "longitude": 73.7519, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Calangute Beach Parking", "address": "Beach Road", "area": "Calangute", "city": "Panaji", "state": "Goa", "latitude": 15.5394, "longitude": 73.7531, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Basilica of Bom Jesus Parking", "address": "Old Goa", "area": "Old Goa", "city": "Panaji", "state": "Goa", "latitude": 15.5008, "longitude": 73.9114, "price": 20.0, "availability": True, "operating_hours": "9:00 AM - 6:00 PM", "type": "garage"},
        
        # Andhra Pradesh
        {"name": "Tirupati Temple Parking", "address": "Temple Road", "area": "Tirumala", "city": "Tirupati", "state": "Andhra Pradesh", "latitude": 13.6833, "longitude": 79.3472, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Visakhapatnam Beach Parking", "address": "Beach Road", "area": "RK Beach", "city": "Visakhapatnam", "state": "Andhra Pradesh", "latitude": 17.7231, "longitude": 83.3250, "price": 15.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Vijayawada Parking Hub", "address": "MG Road", "area": "Benz Circle", "city": "Vijayawada", "state": "Andhra Pradesh", "latitude": 16.5062, "longitude": 80.6480, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        
        # Uttarakhand
        {"name": "Mall Road Parking", "address": "The Mall", "area": "Mall Road", "city": "Nainital", "state": "Uttarakhand", "latitude": 29.3919, "longitude": 79.4542, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Mussoorie Mall Parking", "address": "Mall Road", "area": "Mussoorie", "city": "Dehradun", "state": "Uttarakhand", "latitude": 30.4547, "longitude": 78.0763, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Haridwar Har Ki Pauri Parking", "address": "Har Ki Pauri Road", "area": "Har Ki Pauri", "city": "Haridwar", "state": "Uttarakhand", "latitude": 29.9457, "longitude": 78.1642, "price": 20.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        
        # Himachal Pradesh
        {"name": "Mall Road Shimla Parking", "address": "Mall Road", "area": "Central Shimla", "city": "Shimla", "state": "Himachal Pradesh", "latitude": 31.1048, "longitude": 77.1734, "price": 35.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Manali Mall Road Parking", "address": "Mall Road", "area": "Old Manali", "city": "Manali", "state": "Himachal Pradesh", "latitude": 32.2396, "longitude": 77.1887, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Dharamshala McLeod Ganj Parking", "address": "Temple Road", "area": "McLeod Ganj", "city": "Dharamshala", "state": "Himachal Pradesh", "latitude": 32.2396, "longitude": 76.3206, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        
        # Jammu & Kashmir
        {"name": "Dal Lake Parking", "address": "Boulevard Road", "area": "Dal Gate", "city": "Srinagar", "state": "Jammu and Kashmir", "latitude": 34.1086, "longitude": 74.8570, "price": 30.0, "availability": True, "operating_hours": "24/7", "type": "street"},
        {"name": "Gulmarg Parking Hub", "address": "Main Market", "area": "Gulmarg", "city": "Srinagar", "state": "Jammu and Kashmir", "latitude": 34.0484, "longitude": 74.3806, "price": 40.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
        {"name": "Vaishno Devi Parking", "address": "Katra Base", "area": "Katra", "city": "Jammu", "state": "Jammu and Kashmir", "latitude": 32.9926, "longitude": 74.9317, "price": 25.0, "availability": True, "operating_hours": "24/7", "type": "garage"},
    ]
    
    # Create parking spots
    count = 0
    for data in indian_parking_data:
        parking_obj = ParkingSpot(**data)
        doc = parking_obj.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.parking_spots.insert_one(doc)
        count += 1
    
    return {"message": "Successfully seeded parking data for Indian cities", "count": count}


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
