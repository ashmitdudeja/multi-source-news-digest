import { useNavigate } from 'react-router-dom';
import { useTopics } from '../hooks/useTopics';

export default function TopicFilter({ activeTopic, onSelect }) {
  const { topics, loading } = useTopics();
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide py-1">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="skeleton h-8 w-24 rounded-full flex-shrink-0" />
        ))}
      </div>
    );
  }

  if (!topics.length) return null;

  return (
    <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide py-1 px-1">
      {/* All button */}
      <button
        onClick={() => {
          onSelect?.(null);
          navigate('/');
        }}
        className={`pill flex-shrink-0 border transition-all duration-200 ${
          !activeTopic
            ? 'bg-accent-blue text-white border-accent-blue shadow-lg shadow-accent-blue/20'
            : 'bg-transparent text-white/60 border-white/10 hover:border-white/30 hover:text-white/80'
        }`}
      >
        All Topics
      </button>

      {topics.map((topic) => (
        <button
          key={topic.topic}
          onClick={() => {
            onSelect?.(topic.topic);
            navigate(`/topic/${encodeURIComponent(topic.topic)}`);
          }}
          className={`pill flex-shrink-0 border transition-all duration-200 ${
            activeTopic === topic.topic
              ? 'bg-accent-purple text-white border-accent-purple shadow-lg shadow-accent-purple/20'
              : 'bg-transparent text-white/60 border-white/10 hover:border-white/30 hover:text-white/80'
          }`}
        >
          {topic.topic}
          <span className="ml-1.5 text-[10px] opacity-60">{topic.article_count}</span>
        </button>
      ))}
    </div>
  );
}
