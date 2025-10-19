import { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { MapPin, Navigation, Search, Clock, DollarSign, Car, Facebook, Twitter, Instagram, Linkedin } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Toaster } from "@/components/ui/toaster";
import CancellationRefunds from "@/pages/CancellationRefunds";
import TermsConditions from "@/pages/TermsConditions";
import Shipping from "@/pages/Shipping";
import Privacy from "@/pages/Privacy";
import ContactUs from "@/pages/ContactUs";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white mt-16">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Car className="w-6 h-6" />
              <h3 className="text-xl font-bold">MyParkingService</h3>
            </div>
            <p className="text-gray-400 text-sm">
              Your trusted partner for finding and booking parking spots across India. Quick, easy, and secure.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-gray-400 hover:text-white transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-gray-400 hover:text-white transition-colors">
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/privacy" className="text-gray-400 hover:text-white transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="text-gray-400 hover:text-white transition-colors">
                  Terms & Conditions
                </Link>
              </li>
              <li>
                <Link to="/cancellation" className="text-gray-400 hover:text-white transition-colors">
                  Cancellation & Refunds
                </Link>
              </li>
              <li>
                <Link to="/shipping" className="text-gray-400 hover:text-white transition-colors">
                  Shipping Policy
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h4 className="font-semibold mb-4">Contact</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>Bundi, Rajasthan, India</li>
              <li>
                <a href="mailto:abhinavnew16@gmail.com" className="hover:text-white transition-colors">
                  abhinavnew16@gmail.com
                </a>
              </li>
            </ul>
            <div className="flex gap-4 mt-4">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>&copy; {new Date().getFullYear()} MyParkingService. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

function HomePage() {
  const [parkingSpots, setParkingSpots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [area, setArea] = useState("");
  const [city, setCity] = useState("");
  const [userLocation, setUserLocation] = useState(null);
  const { toast } = useToast();

  // Seed data on component mount
  useEffect(() => {
    const seedData = async () => {
      try {
        await axios.post(`${API}/parking/seed`);
      } catch (error) {
        console.error("Error seeding data:", error);
      }
    };
    seedData();
  }, []);

  // Find nearby parking spots
  const findNearbyParking = async () => {
    if (!navigator.geolocation) {
      toast({
        title: "Error",
        description: "Geolocation is not supported by your browser",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ lat: latitude, lng: longitude });

        try {
          const response = await axios.get(`${API}/parking/nearby`, {
            params: {
              lat: latitude,
              lng: longitude,
              radius: 10, // 10km radius
            },
          });
          setParkingSpots(response.data);
          toast({
            title: "Success",
            description: `Found ${response.data.length} parking spots nearby`,
          });
        } catch (error) {
          console.error("Error fetching nearby parking:", error);
          toast({
            title: "Error",
            description: "Failed to fetch nearby parking spots",
            variant: "destructive",
          });
        } finally {
          setLoading(false);
        }
      },
      (error) => {
        setLoading(false);
        toast({
          title: "Location Error",
          description: "Unable to retrieve your location. Please enable location services.",
          variant: "destructive",
        });
      }
    );
  };

  // Search parking by area and city
  const searchByArea = async (e) => {
    e.preventDefault();
    if (!area || !city) {
      toast({
        title: "Missing Information",
        description: "Please enter both area and city",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`${API}/parking/search`, {
        params: { area, city },
      });
      setParkingSpots(response.data);
      toast({
        title: "Success",
        description: `Found ${response.data.length} parking spots in ${area}, ${city}`,
      });
    } catch (error) {
      console.error("Error searching parking:", error);
      toast({
        title: "Error",
        description: "Failed to search parking spots",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Toaster />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <Car className="w-8 h-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-900">MyParkingService</h1>
          </div>
          <p className="text-gray-600 mt-2">Find parking spots near you or search by location</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="nearby" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
            <TabsTrigger value="nearby" className="flex items-center gap-2" data-testid="nearby-tab">
              <Navigation className="w-4 h-4" />
              Nearby Parking
            </TabsTrigger>
            <TabsTrigger value="area" className="flex items-center gap-2" data-testid="area-tab">
              <Search className="w-4 h-4" />
              Search by Area
            </TabsTrigger>
          </TabsList>

          {/* Nearby Parking Tab */}
          <TabsContent value="nearby">
            <Card className="max-w-2xl mx-auto mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Navigation className="w-5 h-5" />
                  Find Nearby Parking
                </CardTitle>
                <CardDescription>
                  Use your current location to find parking spots within 10km radius
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={findNearbyParking}
                  disabled={loading}
                  className="w-full"
                  size="lg"
                  data-testid="find-nearby-button"
                >
                  {loading ? "Searching..." : "Find Nearby Parking"}
                </Button>
                {userLocation && (
                  <p className="text-sm text-gray-600 mt-4 text-center">
                    Your location: {userLocation.lat.toFixed(4)}, {userLocation.lng.toFixed(4)}
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Search by Area Tab */}
          <TabsContent value="area">
            <Card className="max-w-2xl mx-auto mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="w-5 h-5" />
                  Search by Specific Area
                </CardTitle>
                <CardDescription>
                  Enter an area and city to find available parking spots
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={searchByArea} className="space-y-4">
                  <div>
                    <Label htmlFor="area">Area</Label>
                    <Input
                      id="area"
                      placeholder="e.g., Downtown, Midtown, Hollywood"
                      value={area}
                      onChange={(e) => setArea(e.target.value)}
                      data-testid="area-input"
                    />
                  </div>
                  <div>
                    <Label htmlFor="city">City</Label>
                    <Input
                      id="city"
                      placeholder="e.g., New York, San Francisco, Los Angeles"
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      data-testid="city-input"
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full"
                    size="lg"
                    data-testid="search-button"
                  >
                    {loading ? "Searching..." : "Search Parking"}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Results Section */}
        {parkingSpots.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center" data-testid="results-title">
              Available Parking Spots ({parkingSpots.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {parkingSpots.map((spot) => (
                <Card key={spot.id} className="hover:shadow-lg transition-shadow" data-testid="parking-spot-card">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-lg">{spot.name}</CardTitle>
                        <CardDescription className="mt-1">
                          {spot.area}, {spot.city}
                        </CardDescription>
                      </div>
                      <Badge variant={spot.availability ? "default" : "destructive"}>
                        {spot.availability ? "Available" : "Full"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-start gap-2 text-sm">
                      <MapPin className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{spot.address}</span>
                    </div>
                    
                    {spot.distance !== null && spot.distance !== undefined && (
                      <div className="flex items-center gap-2 text-sm">
                        <Navigation className="w-4 h-4 text-blue-500" />
                        <span className="font-semibold text-blue-600">{spot.distance} km away</span>
                      </div>
                    )}
                    
                    <div className="flex items-center gap-2 text-sm">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <span className="text-gray-700">${spot.price}/hour</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <span className="text-gray-700">{spot.operating_hours}</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm">
                      <Car className="w-4 h-4 text-gray-500" />
                      <span className="text-gray-700 capitalize">{spot.type} Parking</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {parkingSpots.length === 0 && !loading && (
          <div className="text-center mt-12">
            <Car className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 text-lg">No parking spots found. Try searching!</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;