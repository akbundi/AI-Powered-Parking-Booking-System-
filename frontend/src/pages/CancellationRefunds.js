import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const CancellationRefunds = () => {
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
            <CardTitle className="text-3xl font-bold">Cancellation & Refunds Policy</CardTitle>
            <p className="text-sm text-gray-500 mt-2">Last updated: {new Date().toLocaleDateString()}</p>
          </CardHeader>
          <CardContent className="prose prose-sm max-w-none space-y-6">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Cancellation Policy</h2>
              <p className="text-gray-700 leading-relaxed">
                At MyParkingService, we understand that plans can change. We offer flexible cancellation options for your parking bookings.
              </p>
              
              <div className="mt-4 space-y-3">
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-green-900">Free Cancellation</h3>
                  <p className="text-green-800 text-sm mt-1">
                    Cancel up to 24 hours before your scheduled parking time for a full refund.
                  </p>
                </div>
                
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-yellow-900">Partial Refund</h3>
                  <p className="text-yellow-800 text-sm mt-1">
                    Cancel between 24 hours and 2 hours before scheduled time - 50% refund of booking amount.
                  </p>
                </div>
                
                <div className="bg-red-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-red-900">No Refund</h3>
                  <p className="text-red-800 text-sm mt-1">
                    Cancellations made less than 2 hours before scheduled time are non-refundable.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">How to Cancel</h2>
              <ol className="list-decimal list-inside space-y-2 text-gray-700">
                <li>Log in to your MyParkingService account</li>
                <li>Go to "My Bookings" section</li>
                <li>Select the booking you wish to cancel</li>
                <li>Click on "Cancel Booking" button</li>
                <li>Confirm your cancellation</li>
              </ol>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Refund Process</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Refunds are processed within 5-7 business days</li>
                <li>The refund will be credited to the original payment method</li>
                <li>You will receive an email confirmation once the refund is processed</li>
                <li>Bank processing time may vary depending on your financial institution</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Special Circumstances</h2>
              <p className="text-gray-700 leading-relaxed">
                In case of unforeseen circumstances such as natural disasters, medical emergencies, or parking facility closures, 
                we may offer full refunds regardless of the cancellation timeline. Please contact our support team with relevant documentation.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Contact Us</h2>
              <p className="text-gray-700 leading-relaxed">
                If you have any questions about our cancellation and refund policy, please contact us at:
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

export default CancellationRefunds;