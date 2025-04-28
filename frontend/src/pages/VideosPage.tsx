import React, { useState, useEffect } from 'react';
import VideoForm from '../components/VideoForm';
import VideoList from '../components/VideoList';
import { API_URL } from '../constants';
interface Video {
  id: string;
  title: string;
  url: string;
  description: string;
  created_at: string;
}

const VideosPage: React.FC = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [editingVideo, setEditingVideo] = useState<Video | null>(null);

  const fetchVideos = async () => {
    try {
      const response = await fetch(`${API_URL}/videos`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setVideos(data);
    } catch (error) {
      console.error('Erreur lors de la récupération des vidéos:', error);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  const handleSubmit = async (videoData: { title: string; url: string; description: string }) => {
    try {
      const url = editingVideo 
        ? `${API_URL}/videos/${editingVideo.id}`
        : `${API_URL}/videos`;
      
      const method = editingVideo ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(videoData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      fetchVideos();
      setIsFormVisible(false);
      setEditingVideo(null);
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement de la vidéo:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette vidéo ?')) {
      try {
        const response = await fetch(`${API_URL}/videos/${id}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        fetchVideos();
      } catch (error) {
        console.error('Erreur lors de la suppression de la vidéo:', error);
      }
    }
  };

  const handleEdit = (video: Video) => {
    setEditingVideo(video);
    setIsFormVisible(true);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Gestion des vidéos</h1>
        <button
          onClick={() => {
            setEditingVideo(null);
            setIsFormVisible(!isFormVisible);
          }}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          {isFormVisible ? 'Fermer' : 'Ajouter une vidéo'}
        </button>
      </div>

      {isFormVisible && (
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            {editingVideo ? 'Modifier la vidéo' : 'Ajouter une nouvelle vidéo'}
          </h2>
          <VideoForm
            onSubmit={handleSubmit}
            initialData={editingVideo || undefined}
          />
        </div>
      )}

      <VideoList
        videos={videos}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default VideosPage; 