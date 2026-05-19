import SentimentBadge from './SentimentBadge';
import SourceBadge from './SourceBadge';

export default function ArticleCard({ article }) {
  const timeAgo = article.published_at
    ? getTimeAgo(article.published_at)
    : '';

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="glass glass-hover card-hover rounded-xl p-4 block group"
    >
      <div className="flex gap-4">
        {/* Thumbnail */}
        {article.image_url && (
          <div className="hidden sm:block flex-shrink-0 w-24 h-24 rounded-lg overflow-hidden">
            <img
              src={article.image_url}
              alt=""
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
              onError={(e) => { e.target.style.display = 'none'; }}
            />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white/90 text-sm leading-snug mb-1.5 line-clamp-2 group-hover:text-accent-blue transition-colors">
            {article.title}
          </h3>

          {article.summary && (
            <p className="text-white/50 text-xs leading-relaxed mb-2.5 line-clamp-2">
              {article.summary}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-2">
            <SourceBadge source={article.source} />
            {article.sentiment && <SentimentBadge sentiment={article.sentiment} />}
            {timeAgo && (
              <span className="text-white/30 text-[11px] ml-auto">{timeAgo}</span>
            )}
          </div>
        </div>
      </div>
    </a>
  );
}

function getTimeAgo(dateString) {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString();
  } catch {
    return '';
  }
}
