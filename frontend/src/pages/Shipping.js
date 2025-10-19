import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Shipping = () => {
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
            <CardTitle className="text-3xl font-bold">Shipping & Delivery Policy</CardTitle>
            <p className="text-sm text-gray-500 mt-2">Last updated: {new Date().toLocaleDateString()}</p>
          </CardHeader>
          <CardContent className="prose prose-sm max-w-none space-y-6">
            <section>
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                <p className="text-blue-900 font-semibold">
                  MyParkingService is a digital service platform for parking space bookings.
                </p>
                <p className="text-blue-800 text-sm mt-2">
                  As we provide a service-based platform and not physical products, traditional shipping does not apply.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Service Delivery</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Our "delivery" refers to the digital confirmation and access to your booked parking space:
              </p>
              
              <div className="space-y-3">
                <div className="bg-white border border-gray-200 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900">Instant Booking Confirmation</h3>
                  <p className="text-gray-700 text-sm mt-1">
                    Upon successful payment, you will receive an instant booking confirmation via email and SMS (if provided).
                  </p>
                </div>
                
                <div className="bg-white border border-gray-200 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900">Digital Booking Pass</h3>
                  <p className="text-gray-700 text-sm mt-1">
                    A digital parking pass with QR code will be sent to your registered email within 2 minutes of booking.
                  </p>
                </div>
                
                <div className="bg-white border border-gray-200 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900">Access Instructions</h3>
                  <p className="text-gray-700 text-sm mt-1">
                    Detailed instructions on how to access your parking spot, including maps and contact numbers, will be provided.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">What You'll Receive</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Booking confirmation email with booking ID</li>
                <li>QR code for parking facility entry (where applicable)</li>
                <li>Parking spot details (location, slot number, if assigned)</li>
                <li>Parking facility contact information</li>
                <li>Duration and validity of your booking</li>
                <li>Receipt and invoice for your records</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Delivery Timeline</h2>
              <div className="bg-green-50 p-4 rounded-lg">
                <ul className="space-y-2 text-gray-700">
                  <li><span className="font-semibold">Booking Confirmation:</span> Instant</li>
                  <li><span className="font-semibold">Email with Details:</span> Within 2 minutes</li>
                  <li><span className="font-semibold">SMS (if opted):</span> Within 5 minutes</li>
                  <li><span className="font-semibold">Booking Pass:</span> Immediate access in your account</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Didn't Receive Your Confirmation?</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                If you haven't received your booking confirmation within 5 minutes:
              </p>
              <ol className="list-decimal list-inside space-y-2 text-gray-700">
                <li>Check your spam/junk folder</li>
                <li>Verify the email address provided during booking</li>
                <li>Log in to your MyParkingService account to view booking details</li>
                <li>Contact our support team immediately</li>
              </ol>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Physical Permits (If Applicable)</h2>
              <p className="text-gray-700 leading-relaxed">
                Some parking facilities may require physical permits for long-term bookings. In such cases:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 mt-2">
                <li>Permits can be collected at the parking facility reception</li>
                <li>Valid government ID is required for collection</li>
                <li>Collection hours will be mentioned in your booking confirmation</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Contact Support</h2>
              <p className="text-gray-700 leading-relaxed">
                For any issues with receiving your booking confirmation or accessing your parking spot:
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

export default Shipping;