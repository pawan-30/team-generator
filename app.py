import os
from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_teams', methods=['POST'])
def generate_teams():
    data = request.get_json()
    names = data['names']
    num_teams = int(data['num_teams'])
    is_ranked = data.get('is_ranked', False)

    teams = [[] for _ in range(num_teams)]
    team_ratings = [0] * num_teams  # Track total rating per team
    team_sizes = [0] * num_teams  # Track number of players per team

    if is_ranked:
        players = []
        for item in names:
            try:
                name, rating = item.rsplit('(', 1)  # Extract name and rating
                rating = int(rating[:-1])  # Remove closing bracket
                players.append((name.strip(), rating))
            except ValueError:
                continue  # Skip invalid entries

        # Sort players by rating (highest first)
        players.sort(key=lambda x: x[1], reverse=True)

        # Distribute players using a balanced approach
        for player in players:
            min_team = team_ratings.index(min(team_ratings))  # Find the weakest team
            teams[min_team].append(player)
            team_ratings[min_team] += player[1]  # Update team rating
            team_sizes[min_team] += 1  # Increment player count
    else:
        random.shuffle(names)
        for i, name in enumerate(names):
            teams[i % num_teams].append((name, None))  # No rating for unranked mode
            team_sizes[i % num_teams] += 1  # Increment player count

    # Calculate final team ratings (average rating out of 10)
    final_ratings = []
    for i in range(num_teams):
        if team_sizes[i] > 0:
            avg_rating = round(team_ratings[i] / team_sizes[i], 1)  # Average rating
        else:
            avg_rating = 0  # No players, no rating
        final_ratings.append(avg_rating)

    return jsonify({'teams': teams, 'final_ratings': final_ratings})

port = int(os.environ.get("PORT", 8082))  # Use Railway's assigned port

if __name__ == '__main__':
     app.run(debug=False, host="0.0.0.0", port=port)
