export default function StatsBar({ stats }) {
  const items = [
    { label: 'Articles', value: stats?.total_articles ?? 0, icon: '📰' },
    { label: 'Clusters', value: stats?.total_clusters ?? 0, icon: '🗂️' },
    { label: 'Summaries', value: stats?.total_summaries ?? 0, icon: '✨' },
    { label: 'Sources', value: stats?.sources?.length ?? 0, icon: '🌐' },
  ];

  return (
    <div className="flex flex-wrap justify-center gap-3 sm:gap-6">
      {items.map((item) => (
        <div
          key={item.label}
          className="glass rounded-xl px-4 py-2.5 flex items-center gap-2.5 min-w-[120px] justify-center"
        >
          <span className="text-lg">{item.icon}</span>
          <div>
            <p className="text-white font-semibold text-lg leading-tight">{item.value}</p>
            <p className="text-white/40 text-xs">{item.label}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
