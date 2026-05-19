import { useNavigate } from 'react-router-dom';
import ArticleCard from './ArticleCard';
import SentimentBadge from './SentimentBadge';

export default function ClusterCard({ cluster, index = 0 }) {
  const navigate = useNavigate();

  return (
    <div
      className="animate-fade-in-up opacity-0 mb-8"
      style={{ animationDelay: `${index * 80}ms`, animationFillMode: 'forwards' }}
    >
      {/* Cluster Header */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <button
          onClick={() => navigate(`/topic/${encodeURIComponent(cluster.topic)}`)}
          className="group flex items-center gap-2"
        >
          <div className="w-1.5 h-8 rounded-full bg-gradient-to-b from-accent-blue to-accent-purple" />
          <h2 className="font-display text-xl sm:text-2xl font-bold text-white/90 group-hover:text-accent-blue transition-colors">
            {cluster.topic}
          </h2>
        </button>

        <div className="flex items-center gap-2">
          <span className="text-white/30 text-sm">
            {cluster.article_count} article{cluster.article_count !== 1 ? 's' : ''}
          </span>
          {cluster.dominant_sentiment && (
            <SentimentBadge sentiment={cluster.dominant_sentiment} />
          )}
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {cluster.articles?.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </div>
  );
}
