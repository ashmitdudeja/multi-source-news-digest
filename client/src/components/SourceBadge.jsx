export default function SourceBadge({ source }) {
  const config = {
    NewsAPI: { bg: 'bg-blue-500/20', text: 'text-blue-300', border: 'border-blue-500/30' },
    'The Guardian': { bg: 'bg-teal-500/20', text: 'text-teal-300', border: 'border-teal-500/30' },
    'BBC News': { bg: 'bg-orange-500/20', text: 'text-orange-300', border: 'border-orange-500/30' },
    Reuters: { bg: 'bg-amber-500/20', text: 'text-amber-300', border: 'border-amber-500/30' },
  };

  const fallback = { bg: 'bg-white/10', text: 'text-white/70', border: 'border-white/20' };
  const { bg, text, border } = config[source] || fallback;

  return (
    <span className={`pill ${bg} ${text} border ${border} text-[11px]`}>
      {source}
    </span>
  );
}
