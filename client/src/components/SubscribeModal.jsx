import { useState } from 'react';
import { subscribe } from '../api/client';
import { useTopics } from '../hooks/useTopics';

export default function SubscribeModal({ isOpen, onClose }) {
  const [email, setEmail] = useState('');
  const [topic, setTopic] = useState('');
  const [status, setStatus] = useState(null); // 'success' | 'error' | null
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const { topics } = useTopics();

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !topic) return;

    setLoading(true);
    setStatus(null);
    try {
      await subscribe(email, topic);
      setStatus('success');
      setMessage(`Subscribed to "${topic}" successfully!`);
      setEmail('');
      setTopic('');
    } catch (err) {
      setStatus('error');
      setMessage(err.message || 'Failed to subscribe');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative glass rounded-2xl p-6 w-full max-w-md animate-fade-in-up border border-white/10">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white/40 hover:text-white/80 transition-colors"
        >
          ✕
        </button>

        <h2 className="font-display text-xl font-bold text-white/90 mb-1">
          Subscribe to Topics
        </h2>
        <p className="text-white/40 text-sm mb-6">
          Get notified when new articles are published about your favorite topics.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-white/60 text-sm mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="w-full px-4 py-2.5 glass rounded-xl text-white/90 text-sm placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-accent-blue/50"
              id="subscribe-email"
            />
          </div>

          <div>
            <label className="block text-white/60 text-sm mb-1.5">Topic</label>
            <select
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              required
              className="w-full px-4 py-2.5 glass rounded-xl text-white/90 text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue/50 bg-navy-light"
              id="subscribe-topic"
            >
              <option value="">Select a topic...</option>
              {topics.map((t) => (
                <option key={t.topic} value={t.topic}>
                  {t.topic} ({t.article_count} articles)
                </option>
              ))}
            </select>
          </div>

          {status && (
            <div
              className={`text-sm p-3 rounded-lg ${
                status === 'success'
                  ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}
            >
              {message}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-gradient-to-r from-accent-blue to-accent-purple text-white font-medium rounded-xl hover:shadow-lg hover:shadow-accent-blue/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            id="subscribe-submit"
          >
            {loading ? 'Subscribing...' : 'Subscribe'}
          </button>
        </form>
      </div>
    </div>
  );
}
