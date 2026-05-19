import { useState, useEffect } from 'react';
import { getTopics } from '../api/client';

export function useTopics() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTopics() {
      try {
        const data = await getTopics();
        setTopics(data.data || []);
      } catch (err) {
        console.error('Failed to fetch topics:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchTopics();
  }, []);

  return { topics, loading };
}
