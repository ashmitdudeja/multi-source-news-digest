import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getTopicClusters } from '../api/client';
import ClusterCard from '../components/ClusterCard';
import { ClusterSkeleton } from '../components/Skeleton';

export default function TopicPage() {
  const { name } = useParams();
  const navigate = useNavigate();
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchTopic() {
      setLoading(true);
      setError(null);
      try {
        const data = await getTopicClusters(name);
        setClusters(data.data?.clusters || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchTopic();
  }, [name]);

  return (
    <div>
      {/* Back Button + Title */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => navigate('/')}
          className="glass rounded-xl px-4 py-2 text-white/60 hover:text-white/90 hover:bg-white/5 transition-all text-sm"
          id="back-button"
        >
          ← Back to Digest
        </button>
        <div>
          <h2 className="font-display text-2xl sm:text-3xl font-bold">
            <span className="gradient-text">{decodeURIComponent(name)}</span>
          </h2>
          <p className="text-white/40 text-sm mt-1">
            Showing all clusters related to this topic
          </p>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div>
          {[...Array(2)].map((_, i) => (
            <ClusterSkeleton key={i} />
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="text-center py-16">
          <div className="glass rounded-2xl p-8 max-w-md mx-auto">
            <p className="text-red-400 text-lg mb-2">Failed to load topic</p>
            <p className="text-white/40 text-sm mb-4">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-2 bg-accent-blue/20 text-accent-blue rounded-xl hover:bg-accent-blue/30 transition-colors"
            >
              Go Back
            </button>
          </div>
        </div>
      )}

      {/* Clusters */}
      {!loading && !error && (
        <>
          {clusters.length > 0 ? (
            clusters.map((cluster, i) => (
              <ClusterCard key={cluster.id} cluster={cluster} index={i} />
            ))
          ) : (
            <div className="text-center py-16">
              <div className="glass rounded-2xl p-8 max-w-md mx-auto">
                <p className="text-4xl mb-4">🔍</p>
                <p className="text-white/60 text-lg mb-2">No articles found</p>
                <p className="text-white/30 text-sm">
                  No clusters match the topic "{decodeURIComponent(name)}".
                </p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
