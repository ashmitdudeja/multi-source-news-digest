export function ClusterSkeleton() {
  return (
    <div className="mb-8">
      {/* Topic header skeleton */}
      <div className="flex items-center gap-3 mb-4">
        <div className="skeleton w-1.5 h-8 rounded-full" />
        <div className="skeleton h-7 w-48" />
        <div className="skeleton h-5 w-16" />
      </div>

      {/* Article cards skeleton grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {[...Array(3)].map((_, i) => (
          <ArticleSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

export function ArticleSkeleton() {
  return (
    <div className="glass rounded-xl p-4">
      <div className="flex gap-4">
        <div className="hidden sm:block skeleton w-24 h-24 rounded-lg flex-shrink-0" />
        <div className="flex-1">
          <div className="skeleton h-4 w-full mb-2" />
          <div className="skeleton h-4 w-3/4 mb-3" />
          <div className="skeleton h-3 w-full mb-1" />
          <div className="skeleton h-3 w-5/6 mb-3" />
          <div className="flex gap-2">
            <div className="skeleton h-5 w-16 rounded-full" />
            <div className="skeleton h-5 w-16 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}
