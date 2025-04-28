import React from 'react';

interface VideoTranscriptionProps {
  transcription: string;
  isLoading?: boolean;
}

const VideoTranscription: React.FC<VideoTranscriptionProps> = ({ transcription, isLoading = false }) => {
  if (isLoading) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!transcription) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg text-gray-500">
        Aucune transcription disponible
      </div>
    );
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-2">Transcription</h3>
      <div className="max-h-96 overflow-y-auto prose prose-sm">
        {transcription.split('\n').map((paragraph, index) => (
          <p key={index} className="mb-2">
            {paragraph}
          </p>
        ))}
      </div>
    </div>
  );
};

export default VideoTranscription; 