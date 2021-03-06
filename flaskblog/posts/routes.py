from flask import (request, Blueprint, jsonify)
from flaskblog import db
from flaskblog.models import Comment, Post, token_required
from datetime import datetime
from flaskblog.users.utils import get_a_post, get_all_posts

posts = Blueprint('posts', __name__)


@posts.route("/posts/new_post", methods=['GET', 'POST'])
@token_required
def new_post(current_user):
    post = Post.query.filter_by(title=request.json.get('title')).first()
    if not post:
        new_post = Post(
            title=request.json.get('title'),
            content=request.json.get('content'),
            user_id=current_user
        )
        db.session.add(new_post)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Your post is created.',
        }
        return jsonify(response_object)


@posts.route("/posts/<int:id>", methods=['GET', 'POST'])
@token_required
def post(current_user, id):
    post = get_a_post(id)
    comment = Comment(
        body=request.json.get('body'),
        post_id=id,
        user_id=current_user.id
    )
    db.session.add(comment)
    db.session.commit()
    comments = db.session.query(Comment).filter(Comment.post_id == id).all()
    if not post:
        posts.abort(404)
    elif comments:
        response_data = {
            'status': 'success',
            'message': 'You have commented on post'
        }
        return jsonify(response_data)
    return post


@posts.route("/posts/list", methods=['GET', 'POST'])
def all_post():
    posts = get_all_posts()
    return jsonify(posts)


@posts.route("/posts/<int:post_id>/update", methods=['GET', 'POST'])
@token_required
def update_post(a, post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        post.title=request.json.get('title'),
        post.content=request.json.get('content'),
        post.id=request.json.get('id'),
        post.updated_date = datetime.utcnow()
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Your post is updated.',
        }
    return jsonify(response_object)


@posts.route("/posts/<int:post_id>/delete", methods=['POST'])
@token_required
def delete_post(a, post_id):
    post = Post.query.filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    response_object = {
        'status': 'success',
        'message': 'Your post is deleted.',
    }
    return jsonify(response_object)


@posts.route('/posts/like_unlike/<int:user_id>/<int:post_id>/<action>')
@token_required
def like_action(current_user, user_id, post_id, action):
    post = Post.query.filter_by(id=post_id).first()
    post.likes.count()

    if action == 'like':
        current_user.like_post(post)
        db.session.commit()

    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    
    data = {'count': post.likes.count(), 'action': action}
    return jsonify(data)


@posts.route("/posts/post_comment/<int:comment_id>/delete", methods=['GET', 'POST'])
@token_required
def delete_comment(a, comment_id):
    comments = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(comments)
    db.session.commit()
    response_data = {
        'status': 'Sucess',
        'message':'Your comment has been deleted!'
    }
    return jsonify(response_data)
