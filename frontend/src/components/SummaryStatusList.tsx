import React from "react";
import { Card, CardHeader, CardContent, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Loader2 } from "lucide-react";

interface SummaryRequest {
  id: string;
  status: 'processing' | 'complete' | 'error';
  downloadUrl: string | null;
}

interface SummaryStatusListProps {
  requests: SummaryRequest[];
}

const SummaryStatusList: React.FC<SummaryStatusListProps> = ({ requests }) => {
  const downloadSummary = (url: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = 'summary.docx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Card className="w-1/3 border border-solid border-[#5c5c5c] rounded-[0.25rem]">
      <CardHeader>
        <CardTitle>Summary Requests</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {requests.map((request) => (
            <div key={request.id} className="flex items-center justify-between">
              <span>Summary #{request.id}</span>
              {request.status === 'processing' && (
                <Loader2 className="h-4 w-4 animate-spin" />
              )}
              {request.status === 'complete' && request.downloadUrl && (
                <Button onClick={() => downloadSummary(request.downloadUrl!)}>
                  Download
                </Button>
              )}
              {request.status === 'error' && (
                <span className="text-red-500">Error</span>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default SummaryStatusList;
