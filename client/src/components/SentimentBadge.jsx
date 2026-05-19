export default function SentimentBadge({ sentiment }) {
  const config = {
    positive: { bg: 'bg-green-500', label: 'Positive', icon: '↑' },
    negative: { bg: 'bg-red-500', label: 'Negative', icon: '↓' },
    neutral: { bg: 'bg-slate-500', label: 'Neutral', icon: '→' },
  };

  const { bg, label, icon } = config[sentiment] || config.neutral;

  return (
    <span
      className={`pill ${bg} text-white font-medium transition-transform hover:scale-105`}
      title={`Sentiment: ${label}`}
    >
      <span className="mr-1">{icon}</span>
      {label}
    </span>
  );
}
