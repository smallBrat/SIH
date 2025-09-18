

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
  confidence: number;
  lastUpdated: string;
};

const STAGE_META: Omit<PipelineStage, "imageUrl">[] = [
  {
    id: "baseline",
    title: "Baseline Image",
    description: "Initial reference image captured during setup",
  },
  {
    id: "new",
    title: "New Image",
    description: "Latest captured image for comparison",
  },
  {
    id: "masked",
    title: "Masked Image",
    description: "Image after preprocessing and masking applied",
  },
  {
    id: "segmented",
    title: "Segmented Image",
    description: "Image after removing non-pit objects",
  },
  {
    id: "diff",
    title: "Change Detection Result",
    description: "Difference map highlighting changes",
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
        confidence: Math.round((result.ssim_score ?? 0) * 100),
        lastUpdated: new Date().toISOString().slice(0, 19).replace("T", " "),
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
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl mb-2">AI-Based Rockfall Prediction Demo</h1>
          <p className="text-muted-foreground">Real-time geological monitoring and change detection system</p>
        </div>

        {/* Image Processing Pipeline */}
        <div className="mb-8">
          <h2 className="text-xl mb-6 text-center">Image Processing Pipeline</h2>
          <div className="flex items-center justify-center gap-4 overflow-x-auto pb-4">
            {pipelineStages.map((stage, index) => (
              <div key={stage.id} className="flex items-center gap-4">
                {/* Stage Card */}
                <div className="flex-shrink-0">
                  <Card className="w-48 shadow-lg border-0 bg-white">
                    <CardContent className="p-4">
                      <div className="aspect-square w-full mb-3 rounded-lg overflow-hidden bg-gray-100">
                        <ImageWithFallback
                          src={stage.imageUrl}
                          alt={stage.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="text-center">
                        <h3 className="text-sm mb-1">{stage.title}</h3>
                        <p className="text-xs text-muted-foreground leading-tight">
                          {stage.description}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Arrow (if not last item) */}
                {index < pipelineStages.length - 1 && (
                  <ChevronRight className="text-gray-400 flex-shrink-0" size={24} />
                )}
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
                  <span className="text-muted-foreground">Confidence:</span>
                  <Badge variant={alertStatus.isStable ? "secondary" : "destructive"}>
                    {alertStatus.confidence}%
                  </Badge>
                </div>
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
