import React, { useState } from 'react';
import VideoTranscription from './VideoTranscription';
import AlertMessage from './AlertMessage';
import { VideoQA } from './VideoQA';

interface Video {
  id: string;
  title: string;
  url: string;
  description: string;
  created_at: string;
  transcription?: string;
  status: string;
}

interface VideoListProps {
  videos: Video[];
  onEdit: (video: Video) => void;
  onDelete: (id: string) => void;
}

const VideoList: React.FC<VideoListProps> = ({ videos, onEdit, onDelete }) => {
  const [expandedVideo, setExpandedVideo] = useState<string | null>(null);
  const [expandedChat, setExpandedChat] = useState<string | null>(null);

  const toggleTranscription = (videoId: string) => {
    setExpandedVideo(expandedVideo === videoId ? null : videoId);
  };

  const toggleChat = (videoId: string) => {
    setExpandedChat(expandedChat === videoId ? null : videoId);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      processing: {
        color: 'bg-yellow-100 text-yellow-800',
        text: 'Transcription en cours'
      },
      completed: {
        color: 'bg-green-100 text-green-800',
        text: 'Transcription terminée'
      },
      failed: {
        color: 'bg-red-100 text-red-800',
        text: 'Échec de la transcription'
      },
      pending: {
        color: 'bg-gray-100 text-gray-800',
        text: 'En attente'
      }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.text}
      </span>
    );
  };

  return (
    <div className="grid gap-6 mt-6">
      {videos.map((video) => (
        <div
          key={video.id}
          className="bg-white shadow rounded-lg p-6 space-y-4"
        >
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center space-x-3">
                <h3 className="text-lg font-medium text-gray-900">{video.title}</h3>
                {getStatusBadge(video.status)}
              </div>
              <p className="mt-1 text-sm text-gray-500">{video.description}</p>
              <div className="mt-2 space-x-4">
                <a
                  href={video.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-600 hover:text-indigo-500 inline-block"
                >
                  Voir la vidéo
                </a>
                {video.status === 'completed' && (
                  <>
                  <button
                    onClick={() => toggleTranscription(video.id)}
                    className="text-sm text-indigo-600 hover:text-indigo-500"
                  >
                    {expandedVideo === video.id ? 'Masquer la transcription' : 'Voir la transcription'}
                  </button>
                  <button
                  onClick={() => toggleChat(video.id)}
                  className="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  {expandedChat === video.id ? 'Masquer le chat' : 'Voir le chat'}
                </button>
                </>
                )}
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => onEdit(video)}
                className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded"
              >
                Modifier
              </button>
              <button
                onClick={() => onDelete(video.id)}
                className="text-sm bg-red-100 hover:bg-red-200 text-red-700 px-3 py-1 rounded"
              >
                Supprimer
              </button>
            </div>
          </div>
          {expandedVideo === video.id && (
            <VideoTranscription 
              transcription={video.transcription || ''} 
              isLoading={video.status === 'processing'}
            />
          )}
          {expandedChat === video.id && (
            <VideoQA 
              videoId={video.id}
            />
          )}
          {video.status === 'failed' && (
            <AlertMessage
              message="La transcription a échoué. Vous pouvez réessayer en modifiant la vidéo."
              type="error"
            />
          )}
          <div className="text-xs text-gray-500">
            Ajoutée le {new Date(video.created_at).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
};

export default VideoList; 