import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from server.config import settings
from server.database import get_recent_articles, reset_clusters


async def cluster_articles():
    """
    Cluster recent articles using TF-IDF vectorization + cosine similarity
    with agglomerative threshold-based grouping.
    
    Algorithm:
    1. TfidfVectorizer on combined title + description text
    2. cosine_similarity() on the TF-IDF matrix
    3. Agglomerative clustering with configurable threshold (default 0.45)
    4. Topic naming from top TF-IDF terms per cluster
    5. Representative article = highest avg intra-cluster similarity
    """
    articles = await get_recent_articles(hours=24)
    if not articles:
        print("[Clusterer] No recent articles to cluster")
        return 0

    print(f"[Clusterer] Clustering {len(articles)} articles (threshold={settings.cluster_similarity_threshold})...")

    # Prepare text corpus: combine title + description for richer vectors
    texts = []
    valid_articles = []
    for article in articles:
        text = f"{article['title']} {article.get('description', '')}".strip()
        if text:
            texts.append(text)
            valid_articles.append(article)

    if len(valid_articles) < 2:
        # Can't cluster fewer than 2 articles — put each in its own cluster
        cluster_data = []
        for article in valid_articles:
            cluster_data.append({
                "topic": _extract_topic_from_title(article["title"]),
                "representative_title": article["title"],
                "article_ids": [article["id"]],
            })
        await reset_clusters(cluster_data)
        print(f"[Clusterer] Created {len(cluster_data)} single-article clusters")
        return len(cluster_data)

    # ─── TF-IDF Vectorization ───
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),  # unigrams + bigrams for better phrase matching
        min_df=1,
        max_df=0.95,
    )
    tfidf_matrix = vectorizer.fit_transform(texts)

    # ─── Cosine Similarity Matrix ───
    sim_matrix = cosine_similarity(tfidf_matrix)

    # ─── Agglomerative Clustering (threshold-based) ───
    threshold = settings.cluster_similarity_threshold
    n = len(valid_articles)
    assigned = [False] * n
    cluster_groups = []

    for i in range(n):
        if assigned[i]:
            continue

        # Start a new cluster with article i
        group = [i]
        assigned[i] = True

        for j in range(i + 1, n):
            if assigned[j]:
                continue

            # Check if article j is similar enough to ANY article already in the group
            for member in group:
                if sim_matrix[member][j] >= threshold:
                    group.append(j)
                    assigned[j] = True
                    break

        cluster_groups.append(group)

    # ─── Build cluster data ───
    feature_names = vectorizer.get_feature_names_out()
    cluster_data = []

    for group in cluster_groups:
        article_ids = [valid_articles[idx]["id"] for idx in group]

        # Topic naming: top TF-IDF terms for this cluster
        topic = _generate_topic_name(group, tfidf_matrix, feature_names)

        # Representative article: highest avg similarity within cluster
        if len(group) > 1:
            best_idx = group[0]
            best_avg = 0
            for idx in group:
                avg_sim = np.mean([sim_matrix[idx][other] for other in group if other != idx])
                if avg_sim > best_avg:
                    best_avg = avg_sim
                    best_idx = idx
            rep_title = valid_articles[best_idx]["title"]
        else:
            rep_title = valid_articles[group[0]]["title"]

        cluster_data.append({
            "topic": topic,
            "representative_title": rep_title,
            "article_ids": article_ids,
        })

    await reset_clusters(cluster_data)
    print(f"[Clusterer] Created {len(cluster_data)} clusters from {len(valid_articles)} articles")
    return len(cluster_data)


def _generate_topic_name(group_indices: list[int], tfidf_matrix, feature_names) -> str:
    """Generate a topic name from the top TF-IDF terms of the cluster."""
    # Average TF-IDF vectors for all articles in the group
    group_vectors = tfidf_matrix[group_indices]
    avg_vector = group_vectors.mean(axis=0)

    # Convert to array and get top terms
    avg_array = np.asarray(avg_vector).flatten()
    top_indices = avg_array.argsort()[-3:][::-1]  # Top 3 terms

    top_terms = [feature_names[i] for i in top_indices if avg_array[i] > 0]

    if top_terms:
        # Capitalize and join
        return " ".join(word.capitalize() for word in " ".join(top_terms).split()[:4])
    return "General News"


def _extract_topic_from_title(title: str) -> str:
    """Extract a simple topic from a single article's title."""
    # Remove common filler words and take first few meaningful words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of", "and", "or", "but", "with", "by", "from"}
    words = title.split()
    meaningful = [w for w in words if w.lower() not in stop_words and len(w) > 2]
    return " ".join(meaningful[:3]) if meaningful else "General"
