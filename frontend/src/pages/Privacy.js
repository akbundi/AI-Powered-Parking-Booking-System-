import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Privacy = () => {
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
            <CardTitle className="text-3xl font-bold">Privacy Policy</CardTitle>
            <p className="text-sm text-gray-500 mt-2">Last updated: {new Date().toLocaleDateString()}</p>
          </CardHeader>
          <CardContent className="prose prose-sm max-w-none space-y-6">
            <section>
              <p className="text-gray-700 leading-relaxed">
                At MyParkingService, we are committed to protecting your privacy and ensuring the security of your personal information. 
                This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our service.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Information We Collect</h2>
              
              <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2">Personal Information</h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Name, email address, and phone number</li>
                <li>Vehicle registration details</li>
                <li>Payment information (processed securely through payment gateways)</li>
                <li>Booking history and preferences</li>
              </ul>

              <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2">Automatically Collected Information</h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>IP address and device information</li>
                <li>Browser type and version</li>
                <li>Location data (with your permission)</li>
                <li>Usage data and preferences</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">How We Use Your Information</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We use the collected information for the following purposes:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Processing your parking bookings and payments</li>
                <li>Sending booking confirmations and updates</li>
                <li>Providing customer support and responding to inquiries</li>
                <li>Improving our service and user experience</li>
                <li>Sending promotional offers (with your consent)</li>
                <li>Preventing fraud and ensuring security</li>
                <li>Complying with legal obligations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Data Sharing and Disclosure</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We do not sell your personal information. We may share your information with:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li><span className="font-semibold">Parking Facility Partners:</span> To facilitate your bookings</li>
                <li><span className="font-semibold">Payment Processors:</span> To process transactions securely</li>
                <li><span className="font-semibold">Service Providers:</span> Who assist in operating our platform</li>
                <li><span className="font-semibold">Legal Authorities:</span> When required by law</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Data Security</h2>
              <p className="text-gray-700 leading-relaxed">
                We implement appropriate technical and organizational measures to protect your personal information against 
                unauthorized access, alteration, disclosure, or destruction. However, no method of transmission over the internet 
                or electronic storage is 100% secure.
              </p>
              <div className="mt-3 bg-blue-50 p-4 rounded-lg">
                <p className="text-blue-900 text-sm">
                  <span className="font-semibold">Security Measures:</span> SSL encryption, secure payment gateways, 
                  regular security audits, and access controls.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Your Rights</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                You have the following rights regarding your personal information:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li><span className="font-semibold">Access:</span> Request a copy of your personal data</li>
                <li><span className="font-semibold">Correction:</span> Update or correct your information</li>
                <li><span className="font-semibold">Deletion:</span> Request deletion of your account and data</li>
                <li><span className="font-semibold">Opt-out:</span> Unsubscribe from marketing communications</li>
                <li><span className="font-semibold">Data Portability:</span> Receive your data in a portable format</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Cookies and Tracking</h2>
              <p className="text-gray-700 leading-relaxed">
                We use cookies and similar tracking technologies to enhance your experience on our platform. 
                You can control cookie settings through your browser preferences.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Children's Privacy</h2>
              <p className="text-gray-700 leading-relaxed">
                Our service is not intended for children under 18 years of age. We do not knowingly collect 
                personal information from children.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Changes to Privacy Policy</h2>
              <p className="text-gray-700 leading-relaxed">
                We may update this Privacy Policy from time to time. We will notify you of any changes by posting 
                the new Privacy Policy on this page and updating the "Last updated" date.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Contact Us</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                If you have any questions about this Privacy Policy or wish to exercise your rights, please contact us:
              </p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700"><span className="font-semibold">Email:</span> <a href="mailto:abhinavnew16@gmail.com" className="text-blue-600 hover:underline">abhinavnew16@gmail.com</a></p>
                <p className="text-gray-700"><span className="font-semibold">Address:</span> Bundi, Rajasthan, India</p>
              </div>
            </section>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Privacy;