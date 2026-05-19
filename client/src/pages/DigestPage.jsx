import { useState, useMemo } from 'react';
import { useDigest } from '../hooks/useDigest';
import ClusterCard from '../components/ClusterCard';
import TopicFilter from '../components/TopicFilter';
import SearchBar from '../components/SearchBar';
import SubscribeModal from '../components/SubscribeModal';
import { ClusterSkeleton } from '../components/Skeleton';

export default function DigestPage() {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSubscribe, setShowSubscribe] = useState(false);
  const { clusters, pagination, meta, loading, error, refetch } = useDigest(page, 20);

  // Client-side search filter
  const filteredClusters = useMemo(() => {
    if (!searchQuery.trim()) return clusters;
    const q = searchQuery.toLowerCase();
    return clusters.filter(
      (cluster) =>
        cluster.topic?.toLowerCase().includes(q) ||
        cluster.articles?.some(
          (a) =>
            a.title?.toLowerCase().includes(q) ||
            a.summary?.toLowerCase().includes(q)
        )
    );
  }, [clusters, searchQuery]);

  return (
    <div>
      {/* Controls Row */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
        <div className="flex-1">
          <SearchBar onSearch={setSearchQuery} />
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowSubscribe(true)}
            className="pill bg-gradient-to-r from-accent-blue to-accent-purple text-white border-0 px-4 py-2 hover:shadow-lg hover:shadow-accent-blue/20 transition-all text-sm"
            id="subscribe-button"
          >
            ✉ Subscribe
          </button>
          {meta?.last_updated && (
            <span className="text-white/30 text-xs whitespace-nowrap">
              Updated {new Date(meta.last_updated).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Topic Filter */}
      <TopicFilter activeTopic={null} />

      {/* Error State */}
      {error && (
        <div className="text-center py-16">
          <div className="glass rounded-2xl p-8 max-w-md mx-auto">
            <p className="text-red-400 text-lg mb-2">Failed to load digest</p>
            <p className="text-white/40 text-sm mb-4">{error}</p>
            <button
              onClick={refetch}
              className="px-6 py-2 bg-accent-blue/20 text-accent-blue rounded-xl hover:bg-accent-blue/30 transition-colors"
              id="retry-button"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div>
          {[...Array(3)].map((_, i) => (
            <ClusterSkeleton key={i} />
          ))}
        </div>
      )}

      {/* Clusters */}
      {!loading && !error && (
        <>
          {filteredClusters.length > 0 ? (
            <>
              {filteredClusters.map((cluster, i) => (
                <ClusterCard key={cluster.id} cluster={cluster} index={i} />
              ))}

              {/* Load More */}
              {pagination && pagination.page < pagination.total_pages && (
                <div className="text-center mt-8 mb-4">
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    className="px-8 py-3 glass rounded-xl text-white/70 hover:text-white hover:bg-white/5 transition-all"
                    id="load-more-button"
                  >
                    Load More
                    <span className="text-white/30 text-xs ml-2">
                      Page {pagination.page} of {pagination.total_pages}
                    </span>
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-16">
              <div className="glass rounded-2xl p-8 max-w-md mx-auto">
                <p className="text-4xl mb-4">📭</p>
                <p className="text-white/60 text-lg mb-2">No articles yet</p>
                <p className="text-white/30 text-sm">
                  {searchQuery
                    ? 'No results match your search. Try different keywords.'
                    : 'The digest is empty. Articles will appear after the next fetch cycle.'}
                </p>
              </div>
            </div>
          )}
        </>
      )}

      {/* Subscribe Modal */}
      <SubscribeModal isOpen={showSubscribe} onClose={() => setShowSubscribe(false)} />
    </div>
  );
}
