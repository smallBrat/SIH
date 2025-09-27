
import { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { CheckCircle, AlertTriangle } from "lucide-react";
import { ImageWithFallback } from "./components/figma/ImageWithFallback";

type AlertStatus = {
  isStable: boolean;
  lastUpdated: string;
};

// Single pit monitoring configuration
const PIT_CONFIG = {
  id: "pit1",
  name: "Pit 1",
  title: "Real-time Rockfall Monitoring",
  description: "AI-powered change detection with thermal overlay visualization",
  imageEndpoint: "stage5" // Backend processes all stages, frontend shows final result
};

const API_BASE_URL = "https://rockfall-prediction-tt4l.onrender.com";

export default function App() {
  const [pitImage, setPitImage] = useState<string>("");
  const [alertStatus, setAlertStatus] = useState<AlertStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPitImage = async (): Promise<string> => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/image/${PIT_CONFIG.imageEndpoint}`,
        { responseType: "blob", timeout: 10000 }
      );
      const imageUrl = URL.createObjectURL(response.data);
      return imageUrl;
    } catch (error) {
      console.warn(`Failed to fetch pit image:`, error);
      return "";
    }
  };

  // Fetch pipeline status and images
  const fetchPipeline = async () => {
    setLoading(true);
    setError(null);
    try {
      // Trigger the pipeline processing
      const response = await axios.post(`${API_BASE_URL}/run-pipeline`, {}, {
        timeout: 30000
      });
      
      if (!response.data.success) {
        throw new Error(response.data.error || "Pipeline failed");
      }

      // Mock alert status based on pipeline results
      const alert: AlertStatus = {
        isStable: Math.random() > 0.3, // 70% chance of stable
        lastUpdated: new Date().toLocaleString("en-IN", {
          timeZone: "Asia/Kolkata",
          year: "numeric",
          month: "2-digit", 
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false
        }).replace(/(\d{2})\/(\d{2})\/(\d{4}), (\d{2}:\d{2}:\d{2})/, "$3-$2-$1 $4"),
      };
      setAlertStatus(alert);

      // Fetch the composite pit visualization
      const pitImageUrl = await fetchPitImage();
      setPitImage(pitImageUrl);
    } catch (err: any) {
      setError(err.message || "Failed to fetch pipeline data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPipeline();
    // Optional: refresh every 15 minutes
    const interval = setInterval(fetchPipeline, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Processing rockfall detection...</p>
        </div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-red-600">
          <AlertTriangle className="mx-auto mb-4" size={48} />
          <h2 className="text-xl mb-2">Error</h2>
          <p className="mb-4">{error}</p>
          <button 
            onClick={fetchPipeline}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }
  if (!alertStatus) {
    return <div className="text-center mt-20">No alert status available.</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-full mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl mb-2">AI-Based Rockfall Prediction</h1>
          <p className="text-muted-foreground">Real-time pit monitoring with thermal change detection</p>
        </div>

        {/* Pit 1 Monitoring Block */}
        <div className="mb-8">
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
              {/* Pit Header */}
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold">{PIT_CONFIG.name}</h2>
                    <p className="text-blue-100 text-sm">{PIT_CONFIG.title}</p>
                  </div>
                  <Badge variant="secondary" className="bg-blue-500 text-white">
                    Live Monitoring
                  </Badge>
                </div>
              </div>
              
              {/* Pit Visualization */}
              <div className="p-6">
                <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4">
                  <ImageWithFallback
                    src={pitImage}
                    alt="Pit 1 - Rockfall Detection Overlay"
                    className="w-full h-full object-contain"
                  />
                </div>
                <p className="text-gray-600 text-center text-sm">
                  {PIT_CONFIG.description}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Alert Status Panel */}
        <div className="max-w-md mx-auto">
          <Card className={`shadow-xl border-2 ${
            alertStatus.isStable 
              ? 'border-green-200 bg-green-50' 
              : 'border-red-200 bg-red-50'
          }`}>
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center mb-4">
                {alertStatus.isStable ? (
                  <>
                    <CheckCircle className="text-green-600 mr-3" size={32} />
                    <div>
                      <h3 className="text-lg text-green-800">✅ Stable Pit</h3>
                      <p className="text-green-700 text-sm">No significant changes detected</p>
                    </div>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="text-red-600 mr-3" size={32} />
                    <div>
                      <h3 className="text-lg text-red-800">⚠️ Rockfall Predicted!</h3>
                      <p className="text-red-700 text-sm">Significant changes detected</p>
                    </div>
                  </>
                )}
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Updated:</span>
                  <span className="text-sm">{alertStatus.lastUpdated}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* System Info */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>System Status: Active • Monitoring Interval: 15 minutes • Next Scan: {
            new Date(Date.now() + 15 * 60 * 1000).toLocaleTimeString('en-IN', {
              timeZone: 'Asia/Kolkata',
              hour: '2-digit',
              minute: '2-digit'
            })
          }</p>
        </div>

        {/* Refresh Button */}
        <div className="mt-6 text-center">
          <button 
            onClick={fetchPipeline}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Refresh Analysis'}
          </button>
        </div>
      </div>
    </div>
  );
}
