from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
import pydantic

from schem import CreateArticle, UpdateArticle
from models import Article, Session

app = Flask('app')

def validate(schema_class, json_data):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except pydantic.ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise HttpError(400, error)

@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response):
    request.session.close()
    return response


class HttpError(Exception):
    def __init__(self, status_code: int, description: str):
        self.status_code = status_code
        self.description = description


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({"error": error.description})
    response.status_code = error.status_code
    return response


def get_article_id(article_id: int):
    article = request.session.get(Article, article_id)
    return article

def add_article(art: Article):
    try:
        request.session.add(art)
        request.session.commit()
    except IntegrityError as err:
        raise HttpError(409, "user already exists")
    return art

class ArticleView(MethodView):

    def get(self, article_id: int):
        article = get_article_id(article_id)
        if article is None:
            return jsonify({'error': 'article is not found'})
        return jsonify(article.json)

    def post(self):
        json_data = validate(CreateArticle, request.json)
        art = Article(**json_data)
        add_article(art)
        return jsonify({'id': art.id})

    def delete(self, article_id):
        art = get_article_id(article_id)
        request.session.delete(art)
        request.session.commit()
        return jsonify({'delete':f'id: {article_id}'})

    def patch(self, article_id: int):
        json_data = validate(UpdateArticle, request.json)
        art = get_article_id(article_id)
        for field, value in json_data.items():
            setattr(art, field, value)
        add_article(art)

        return jsonify(art.json)


article_view = ArticleView.as_view('aticle_view')

app.add_url_rule('/api', view_func=article_view, methods=['POST'])
app.add_url_rule('/api/<int:article_id>', view_func=article_view, methods=['GET', 'DELETE', 'PATCH'])

app.run(debug=True)
