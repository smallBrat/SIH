

import { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { ChevronRight, CheckCircle, AlertTriangle } from "lucide-react";
import { ImageWithFallback } from "./components/figma/ImageWithFallback";

type PipelineStage = {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
};

type AlertStatus = {
  isStable: boolean;
  lastUpdated: string;
};

const STAGE_META: Omit<PipelineStage, "imageUrl">[] = [
  {
    id: "stage1",
    title: "Stage 1: Baseline Image",
    description: "Enhanced preprocessing with noise reduction and contrast enhancement",
  },
  {
    id: "stage2",
    title: "Stage 2: New Captured Image", 
    description: "Latest image with same preprocessing and size normalization",
  },
  {
    id: "stage3", 
    title: "Stage 3: Size-Preserved Pit Detection",
    description: "Accurate change detection preserving original change sizes - eliminates false positives while maintaining true change dimensions",
  },
  {
    id: "stage4",
    title: "Stage 4: Enhanced Pit Area Detection",
    description: "YOLO segmentation creates precise pit-only mask, isolating pure mining area from all non-pit actors",
  },
  {
    id: "stage5",
    title: "Stage 5: Pit-Only Visualization",
    description: "Color-coded superposition showing rockfall changes ONLY in pit areas, excluding all non-pit actors",
  },
];

export default function App() {
  const [pipelineStages, setPipelineStages] = useState<PipelineStage[]>([]);
  const [alertStatus, setAlertStatus] = useState<AlertStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Helper to fetch images for each stage
  const fetchStageImages = async () => {
    const baseUrl = "http://127.0.0.1:5000/image/";
    const stages: PipelineStage[] = await Promise.all(
      STAGE_META.map(async (meta) => {
        try {
          // Use image endpoint for each stage
          return {
            ...meta,
            imageUrl: `${baseUrl}${meta.id}`,
          };
        } catch {
          return {
            ...meta,
            imageUrl: "", // fallback
          };
        }
      })
    );
    return stages;
  };

  // Fetch pipeline status and images
  const fetchPipeline = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get status (alert, scores, etc)
      const statusRes = await axios.get("http://127.0.0.1:5000/status");
      if (!statusRes.data.success) throw new Error(statusRes.data.error || "Unknown error");
      const result = statusRes.data.result;

      // Compose alertStatus
      const alert: AlertStatus = {
        isStable: !result.alert,
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

      // Compose pipelineStages with image URLs
      const stages = await fetchStageImages();
      setPipelineStages(stages);
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
    return <div className="text-center mt-20">Loading pipeline...</div>;
  }
  if (error) {
    return <div className="text-center mt-20 text-red-600">Error: {error}</div>;
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
          <p className="text-muted-foreground">Real-time geological monitoring and change detection system</p>
        </div>

        {/* Image Processing Pipeline */}
        <div className="mb-6">
          <h2 className="text-xl mb-4 text-center">5-Stage Rockfall Detection Pipeline</h2>
          <div className="flex items-center justify-center gap-4 pb-4 px-2">
            {pipelineStages.map((stage, index) => (
              <div key={index} className="flex-1 max-w-xs">
                <div className="bg-white rounded-lg shadow-lg p-3 h-auto border border-gray-200">
                  <ImageWithFallback
                    src={stage.imageUrl}
                    alt={stage.title}
                    className="w-full h-40 object-contain rounded mb-2"
                  />
                  <h3 className="text-sm font-semibold text-center mb-1 line-clamp-1">{stage.title}</h3>
                  <p className="text-xs text-gray-600 text-center line-clamp-2">{stage.description}</p>
                </div>
              </div>
            ))}
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
          <p>System Status: Active • Monitoring Interval: 15 minutes • Next Scan: 14:45</p>
        </div>
      </div>
    </div>
  );
}
