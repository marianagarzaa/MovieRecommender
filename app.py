from flask import Flask, render_template, request
import json

app = Flask(__name__)

# load the scraped data
with open('movies.json') as f:
    MOVIES = json.load(f)

@app.route('/', methods=['GET','POST'])
def index():
    movies = MOVIES
    # grab form values
    min_rating = request.form.get('min_rating', type=float)
    selected_genres      = [g.lower() for g in request.form.getlist('genres')]
    if request.method == 'POST':
        if min_rating is not None:
            movies = [m for m in movies if m['rating'] >= min_rating]
        if selected_genres:
            movies = [
              m for m in movies
              if all(genre in (g.lower() for g in m['genres']) for genre in selected_genres)
            ]

    # gather all unique genres for the dropdown
    all_genres = sorted({g for m in MOVIES for g in m['genres']})
    return render_template(
      'index.html',
      movies=movies,
      genres=all_genres
    )

if __name__ == '__main__':
    app.run(debug=True)
