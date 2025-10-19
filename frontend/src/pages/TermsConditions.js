import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const TermsConditions = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <Button
          variant="ghost"
          onClick={() => navigate("/")}
          className="mb-6"
          data-testid="back-button"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Button>

        <Card>
          <CardHeader>
            <CardTitle className="text-3xl font-bold">Terms and Conditions</CardTitle>
            <p className="text-sm text-gray-500 mt-2">Last updated: {new Date().toLocaleDateString()}</p>
          </CardHeader>
          <CardContent className="prose prose-sm max-w-none space-y-6">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Acceptance of Terms</h2>
              <p className="text-gray-700 leading-relaxed">
                By accessing and using MyParkingService, you accept and agree to be bound by the terms and provision of this agreement. 
                If you do not agree to these terms, please do not use our service.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Service Description</h2>
              <p className="text-gray-700 leading-relaxed">
                MyParkingService provides a platform for users to search, book, and pay for parking spots across various locations in India. 
                We act as an intermediary between users and parking facility owners.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">3. User Responsibilities</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>You must provide accurate and complete information when booking</li>
                <li>You are responsible for maintaining the confidentiality of your account</li>
                <li>You must arrive at the parking facility within the booked time slot</li>
                <li>You must comply with parking facility rules and regulations</li>
                <li>Any damage to the parking facility or other vehicles is your responsibility</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Booking and Payment</h2>
              <p className="text-gray-700 leading-relaxed mb-2">
                All bookings are subject to availability. Payment must be made at the time of booking through our secure payment gateway.
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Prices displayed are in Indian Rupees (INR)</li>
                <li>All payments are processed securely</li>
                <li>Booking confirmation will be sent via email</li>
                <li>No-shows without cancellation will not be refunded</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Vehicle Safety and Liability</h2>
              <p className="text-gray-700 leading-relaxed">
                While we partner with secure parking facilities, MyParkingService is not responsible for any theft, damage, or loss to your vehicle or belongings. 
                Users are advised to not leave valuables in their vehicles and ensure their vehicles are properly locked.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Modification of Service</h2>
              <p className="text-gray-700 leading-relaxed">
                We reserve the right to modify, suspend, or discontinue any aspect of our service at any time without prior notice. 
                We may also update these terms and conditions periodically.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Prohibited Activities</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Using the service for any illegal purposes</li>
                <li>Attempting to hack or compromise our systems</li>
                <li>Making fraudulent bookings</li>
                <li>Harassing other users or parking facility staff</li>
                <li>Reselling parking spots without authorization</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Intellectual Property</h2>
              <p className="text-gray-700 leading-relaxed">
                All content on MyParkingService, including text, graphics, logos, and software, is the property of MyParkingService 
                and is protected by copyright and intellectual property laws.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Governing Law</h2>
              <p className="text-gray-700 leading-relaxed">
                These terms and conditions are governed by the laws of India. Any disputes arising from the use of our service 
                shall be subject to the exclusive jurisdiction of the courts in Rajasthan, India.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Contact Information</h2>
              <p className="text-gray-700 leading-relaxed">
                For any questions regarding these terms and conditions, please contact us:
              </p>
              <div className="mt-2 text-gray-700">
                <p>Email: <a href="mailto:abhinavnew16@gmail.com" className="text-blue-600 hover:underline">abhinavnew16@gmail.com</a></p>
                <p>Address: Bundi, Rajasthan, India</p>
              </div>
            </section>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TermsConditions;