import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_dataset():
    data = pd.read_csv("C:/Users/roicy/Downloads/Project3/social/social_media_dataset.csv")
    return data

def get_recommendations(user_input=None, num_recommendations=5):
    data = load_dataset()
    data['PostContent'] = data['PostContent'].fillna('')
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(data['PostContent'])
    
    # Calculate cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Get recommendations based on user_input if provided
    if user_input:
        user_tfidf = vectorizer.transform([user_input])
        user_sim = cosine_similarity(user_tfidf, tfidf_matrix)
        similar_indices = user_sim.argsort()[0][-num_recommendations:][::-1]
    else:
        # Default to most similar to the first post if no user input
        similar_indices = cosine_sim[0].argsort()[-num_recommendations:][::-1]
    
    # Get recommended posts
    recommendations = data.iloc[similar_indices]['PostContent'].values
    return recommendations

# Example usage
user_input = "Looking for interesting social media posts about technology."
recommendations = get_recommendations(user_input)
for i, recommendation in enumerate(recommendations, 1):
    print(f"Recommendation {i}: {recommendation}")
