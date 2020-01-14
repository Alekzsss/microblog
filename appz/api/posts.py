from appz.api import bp
from appz import db
from flask import request, jsonify, g, url_for
from flask_login import current_user
from appz.models import Post, User
from appz.api.auth import token_auth
from appz.api.errors import bad_request
from guess_language import guess_language


@bp.route('/posts/<int:id>', methods=['GET'])
@token_auth.login_required
def get_post(id):
    return jsonify(Post.query.get_or_404(id).to_dict())

@bp.route('/posts', methods=['GET'])
@token_auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Post.to_collection_dict(Post.query, page, per_page, 'api.get_posts')
    return jsonify(data)

@bp.route('/users/<int:id>/posts', methods=['GET'])
@token_auth.login_required
def get_user_posts(id):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Post.to_collection_dict(Post.query.filter_by(user_id=id), page, per_page, 'api.get_user_posts', id=id)
    return jsonify(data)

@bp.route('/posts', methods=['POST'])
@token_auth.login_required
def create_post():
    data = request.get_json() or {}
    if 'body' not in data:
        return bad_request('you must include post message')
    body = data.get('body')
    language = guess_language(body)
    if language == 'UNKNOWN' or len(language) > 5:
        language = ''
    post = Post(body=body, author=g.current_user, language=language)
    db.session.add(post)
    db.session.commit()
    response = jsonify(post.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_posts', id=post.id)
    return response