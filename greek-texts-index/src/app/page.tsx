'use client';

import { useState, useEffect } from 'react';
import { WorksTable } from '@/components/WorksTable';
import { GreekWork } from '@/types/work';

export default function Home() {
  const [works, setWorks] = useState<GreekWork[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWorks = async () => {
      try {
        const response = await fetch('/api/works');
        const data = await response.json();
        setWorks(data);
      } catch (error) {
        console.error('Error fetching works:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWorks();
  }, []);

  const toggleFavorite = (work: GreekWork) => {
    setWorks(prevWorks =>
      prevWorks.map(w =>
        w.id === work.id ? { ...w, isFavorite: !w.isFavorite } : w
      )
    );

    // Save favorites to localStorage
    const favorites = works
      .filter(w => w.id === work.id ? !w.isFavorite : w.isFavorite)
      .map(w => w.id);
    localStorage.setItem('favoriteWorks', JSON.stringify(favorites));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            First 1K Greek Works Index
          </h1>
          <WorksTable works={works} onToggleFavorite={toggleFavorite} />
        </div>
      </div>
    </main>
  );
}
