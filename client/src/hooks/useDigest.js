import { useState, useEffect, useCallback } from 'react';
import { getDigest } from '../api/client';

export function useDigest(page = 1, limit = 10) {
  const [clusters, setClusters] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDigest(page, limit);
      setClusters(data.data?.clusters || []);
      setPagination(data.data?.pagination || null);
      setMeta(data.meta || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [page, limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { clusters, pagination, meta, loading, error, refetch: fetchData };
}
