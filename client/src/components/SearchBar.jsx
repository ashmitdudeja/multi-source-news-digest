import { useState } from 'react';
import { useDebounce } from '../hooks/useDebounce';

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  // Notify parent when debounced value changes
  useState(() => {
    onSearch?.(debouncedQuery);
  }, [debouncedQuery]);

  return (
    <div className="relative mb-6">
      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <svg
          className="w-4 h-4 text-white/30"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          onSearch?.(e.target.value);
        }}
        placeholder="Search topics, headlines..."
        className="w-full pl-11 pr-4 py-3 glass rounded-xl text-white/90 text-sm placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-accent-blue/50 transition-all"
        id="search-input"
      />
      {query && (
        <button
          onClick={() => {
            setQuery('');
            onSearch?.('');
          }}
          className="absolute inset-y-0 right-0 pr-4 flex items-center text-white/30 hover:text-white/60"
        >
          ✕
        </button>
      )}
    </div>
  );
}
