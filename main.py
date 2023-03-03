import requests
import openai
import flask
import json
import dotenv
import os

dotenv.load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_KEY')
MDBLIST_KEY = os.getenv('MDBLIST_KEY')

app = flask.Flask(__name__)


def get_reviews(imdb_id):
    return requests.get(f'https://mdblist.com/api/?apikey={MDBLIST_KEY}&i={imdb_id}').json()


def handle_reviews(raw):
    title = raw['title']
    reviews = []
    length = 0
    i = 0
    for review in raw['reviews']:
        if (len(review["content"]) + length) < 4000:
            reviews.append(f'Review {i}: "{review["content"]}"')
            i += 1
            length += len(review["content"])
    return reviews, title, length, i


def ask_chatgpt(reviews, title):
    input = f"""
    Here are a couple reviews of the movie "{title}" in the language English could you consider all of them and based on them make an extensive review in the language Spanish, that looks like it was written by a professional film critic and also that you do not notice that you based it on other reviews? The review should contain in a subtle way the good, the bad and end with a general summary.
    Remember that the review needs to be in Spanish.
    These are the reviews:
    {reviews}
    """
    openai.api_key = OPENAI_KEY
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": input}])
    output = completion.choices[0].message.content
    output.encode('utf-8').decode('unicode_escape')
    return output


@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return flask.render_template('index.html')
    elif flask.request.method == 'POST':
        imdb_id = flask.request.form['imdb_id']
        raw = get_reviews(imdb_id)
        reviews, title, length, i = handle_reviews(raw)
        output = ask_chatgpt(reviews, title)
        return flask.render_template('output.html', output=output, title=title, i=i, length=length)


if __name__ == '__main__':
    app.run()
