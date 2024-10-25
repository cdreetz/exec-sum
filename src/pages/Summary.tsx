import React, { useState } from "react";
import { ScrollArea } from "../components/ui/scroll-area";
import { Input } from "../components/ui/input";
import {
  Card,
  CardHeader,
  CardContent,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Loader2 } from "lucide-react";
import SummaryStatusList from "../components/SummaryStatusList";

interface Document {
  name: string;
  type: string;
  file: File;
}

interface SummaryRequest {
  id: string;
  status: 'processing' | 'complete' | 'error';
  downloadUrl: string | null;
}


const DocumentUpload: React.FC<{
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
}> = ({ onFileUpload }) => (
  <div>
    <h3 className="text-lg font-semibold mb-2">Upload Documents</h3>
    <Input
      type="file"
      multiple
      onChange={onFileUpload}
      className="file:underline file:hover:cursor-pointer"
    />
  </div>
);

const DocumentList: React.FC<{
  documents: Document[];
  onDocumentTypeChange: (index: number, type: string) => void;
  onDocumentRemove: (index: number) => void;
}> = ({ documents, onDocumentTypeChange, onDocumentRemove }) => (
  <div>
    <h3 className="text-lg font-semibold mb-2">Uploaded Documents</h3>
    <ScrollArea className="h-40 border rounded p-2">
      {documents.map((doc, index) => (
        <div key={index} className="flex items-center justify-between mb-2">
          <span className="flex-grow">{doc.name}</span>
          <select
            value={doc.type}
            onChange={(e) => onDocumentTypeChange(index, e.target.value)}
            className="border rounded p-1 mr-2"
          >
            <option value="Unknown">Unknown</option>
            <option value="Report">Report</option>
            <option value="Presentation">Presentation</option>
            <option value="Spreadsheet">Spreadsheet</option>
          </select>
          <button
            onClick={() => onDocumentRemove(index)}
            className="text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      ))}
    </ScrollArea>
  </div>
);

const SummaryTypeSelector: React.FC<{
  summaryType: string;
  onSummaryTypeChange: (type: string) => void;
}> = ({ summaryType, onSummaryTypeChange }) => (
  <div>
    <h3 className="text-lg font-semibold mb-2">Summary Type</h3>
    <select
      value={summaryType}
      onChange={(e) => onSummaryTypeChange(e.target.value)}
      className="w-full border rounded p-2"
    >
      <option value="">Select a summary type</option>
      <option value="Executive">Executive</option>
      <option value="Technical">Technical</option>
      <option value="Financial">Financial</option>
    </select>
  </div>
);

const SummaryDisplay: React.FC<{ summary: string }> = ({ summary }) => (
  <div>
    <h3 className="text-lg font-semibold mb-2">Generated Summary</h3>
    <ScrollArea className="h-40 border rounded p-2">
      <p>{summary}</p>
    </ScrollArea>
  </div>
);

const Summary: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [summaryType, setSummaryType] = useState<string>("");
  const [summary, setSummary] = useState<string>("");
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'complete' | 'error'>('idle');
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [summaryRequests, setSummaryRequests] = useState<SummaryRequest[]>([]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const newDocuments = Array.from(files).map((file) => ({
        name: file.name,
        type: "Unknown",
        file: file,
      }));
      setDocuments([...documents, ...newDocuments]);
    }
  };

  const handleDocumentTypeChange = (index: number, type: string) => {
    const updatedDocuments = [...documents];
    updatedDocuments[index].type = type;
    setDocuments(updatedDocuments);
  };

  const handleDocumentRemove = (index: number) => {
    const updatedDocuments = [...documents];
    updatedDocuments.splice(index, 1);
    setDocuments(updatedDocuments);
  };

  const generateSummary = async () => {
    if (documents.length === 0 || !summaryType) {
      setStatus('error');
      setSummary('Please upload documents and select a summary type');
      return;
    }

    const requestId = Date.now().toString();
    const newRequest: SummaryRequest = {
      id: requestId,
      status: 'processing',
      downloadUrl: null,
    };
    setSummaryRequests([...summaryRequests, newRequest]);

    const formData = new FormData();
    documents.forEach((doc, index) => {
      formData.append(`file`, doc.file);
      formData.append(`type`, doc.type);
    });
    formData.append("summary_type", summaryType);

    try {
      setStatus('processing');
      const response = await fetch('http://localhost:8000/generate_summary', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to generate summary');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      setSummaryRequests(prevRequests =>
        prevRequests.map(req =>
          req.id === requestId
            ? { ...req, status: 'complete', downloadUrl: url }
            : req
        )
      );

      setDocuments([]);
      setSummaryType("");
      setStatus('idle');
      setSummary('');
    } catch (error) {
      setDocuments([]);
      console.error('Error generating summary:', error);
      setSummaryRequests(prevRequests =>
        prevRequests.map(req =>
          req.id === requestId
            ? { ...req, status: 'error' }
            : req
        )
      );
    }
  };

  const downloadSummary = () => {
    if (downloadUrl) {
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = 'summary.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="flex w-full max-w-6xl mx-auto mt-8 space-x-4">
      <Card className="w-2/3 border border-solid border-[#5c5c5c] rounded-[0.25rem]">
        <CardHeader className="relative">
          <div className="absolute top-0 left-0 right-0 h-1/4 bg-[#005288]"></div>
          <CardTitle className="relative z-10">Executive Summary Generator</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <DocumentUpload onFileUpload={handleFileUpload} />
            <DocumentList
              documents={documents}
              onDocumentTypeChange={handleDocumentTypeChange}
              onDocumentRemove={handleDocumentRemove}
            />
            <SummaryTypeSelector
              summaryType={summaryType}
              onSummaryTypeChange={setSummaryType}
            />
            <div className="flex justify-center space-x-4">
              <Button
                onClick={generateSummary}
                disabled={status === 'processing' || documents.length === 0 || !summaryType}
                className="bg-[#0078ae] hover:bg-[#005b84] text-white font-['Source_Sans_Pro_Web',_'Helvetica_Neue',_Helvetica,_Roboto,_Arial,_sans-serif] text-[1.06rem] border border-solid border-[#5c5c5c] rounded-[0.25rem]"
              >
                {status === 'processing' ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  'Generate Summary'
                )}
              </Button>
              <Button
                onClick={() => {
                  setDocuments([]);
                  setSummaryType("");
                }}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-['Source_Sans_Pro_Web',_'Helvetica_Neue',_Helvetica,_Roboto,_Arial,_sans-serif] text-[1.06rem] border border-solid border-[#5c5c5c] rounded-[0.25rem]"
              >
                Reset
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
      <SummaryStatusList requests={summaryRequests} />
    </div>
  );
};

export default Summary;
