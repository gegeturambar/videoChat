import React, { useState } from 'react';
import { API_URL } from '../constants';
interface VideoQAProps {
  videoId: string;
}

interface QAResponse {
  answer: string;
  confidence: string;
}

export const VideoQA = ({ videoId }: VideoQAProps) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<QAResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/qa/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question.trim(), video_id: videoId }),
      });

      if (!response.ok) {
        throw new Error('Failed to get answer');
      }

      const data = await response.json();
      setAnswer(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-4">
      <h3 className="text-lg font-semibold mb-4">Poser une question sur cette vidéo</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Posez votre question à propos de la vidéo..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className={`w-full py-2 px-4 rounded-md text-white font-medium
            ${isLoading || !question.trim() 
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600'
            }`}
        >
          {isLoading ? 'Recherche en cours...' : 'Poser la question'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {answer && !error && (
        <div className="mt-4 space-y-2">
          <div className="p-4 bg-gray-50 rounded-md">
            <p className="text-gray-800">{answer.answer}</p>
            <div className="mt-2 text-sm text-gray-500">
              Confiance: {Number(answer.confidence) * 100}%
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 