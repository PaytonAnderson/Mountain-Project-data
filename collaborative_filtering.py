'''
Think:
- some way of handling low or zero experience users (cold start)
  - https://en.wikipedia.org/wiki/Cold_start_(recommender_systems)
  - Likely some form of asking a new user for information when they
    first log on to the system
- standardize the two approaches (knn vs collab_filtering)
  - this probably looks like building a test suite and defining a
    recommendation interface
'''

import sqlite3
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def get_recommendations(user_id, db_path, n_recommendations=300, similarity_threshold=0.3):
    # Connect to database
    conn = sqlite3.connect(db_path)

    # Load reviews data
    query = 'SELECT user_id, route_id, score FROM reviews LIMIT 5000;'
    reviews_df = pd.read_sql_query(query, conn)

    # Create a user-item matrix
    user_route_matrix = reviews_df.pivot_table(
        index='user_id', 
        columns='route_id', 
        values='score',
        fill_value=0
    )

    # Get the target user's ratings
    if user_id not in user_route_matrix.index:
        return pd.DataFrame(columns=['route_id', 'predicted_score'])

    # Calculate cosine similarity between the target user and all other users
    similarities = {}
    target_user_ratings = user_route_matrix.loc[user_id].values.reshape(1, -1)

    for other_user in user_route_matrix.index:
        if other_user == user_id:
            continue

        other_user_ratings = user_route_matrix.loc[other_user].values.reshape(1, -1)

        # Skip users with no common rated items
        if np.sum(np.logical_and(target_user_ratings > 0, other_user_ratings > 0)) == 0:
            continue

        sim = cosine_similarity(target_user_ratings, other_user_ratings)[0][0]
        if not np.isnan(sim) and sim > similarity_threshold:
            similarities[other_user] = sim

    # If no similar users found, return empty recommendations
    if not similarities:
        return pd.DataFrame(columns=['route_id', 'predicted_score'])

    # Get routes that similar users have rated but target user hasn't
    target_user_routes = set(user_route_matrix.columns[user_route_matrix.loc[user_id] > 0])

    # Calculate predicted scores for unrated routes
    predictions = {}

    for route in user_route_matrix.columns:
        if route in target_user_routes:
            continue  # Skip routes the user has already rated

        # Weighted average of similar users' ratings
        weighted_sum = 0
        sim_sum = 0

        for other_user, similarity in similarities.items():
            if user_route_matrix.loc[other_user, route] > 0:  # If the similar user rated this route
                weighted_sum += similarity * user_route_matrix.loc[other_user, route]
                sim_sum += similarity

        if sim_sum > 0:
            predictions[route] = weighted_sum / sim_sum

    # Create dataframe with predictions
    recommendations = pd.DataFrame({
        'route_id': list(predictions.keys()),
        'predicted_score': list(predictions.values())
    })

    # Sort by predicted score and return top n recommendations
    recommendations = recommendations.sort_values('predicted_score', ascending=False).head(n_recommendations)

    conn.close()

    return recommendations


def main():
    db_path = 'databasev2.db'
    user_id = 201159510

    recommendations = get_recommendations(user_id, db_path)

    if recommendations.empty:
        print(f'No recommendations found for user {user_id}')
    else:
        print(f'Top recommendations for user {user_id}:')
        for _, row in recommendations.iterrows():
            print(f'Route {row["route_id"]}: Predicted score {row["predicted_score"]:.2f}')


if __name__ == '__main__':
    main()
