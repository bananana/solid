from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask.ext.login import current_user, login_required

from app.causes.models import Cause
from app.causes.views import cause_required

from .forms import PostForm, CommentForm
from .models import Post, Comment

mod = Blueprint('discussions', __name__)

@mod.route('/cause/<slug>/posts')
@cause_required
def post_list(slug):
    cause = Cause.query.filter_by(slug=slug).first()
    context = {
        "cause": cause,
        "posts": cause.posts.all()
    }
    return render_template('discussions/post_list.html', **context)


@mod.route('/cause/<slug>/posts/add', methods=('GET', 'POST'))
@login_required
@cause_required
def post_add(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    form = PostForm(request.form)

    post = Post.create(commit=False)

    if form.validate_on_submit():
        form.populate_obj(post)
        post.author = current_user
        post.cause = cause
        post.save()
        flash('Post added!', 'success')
        return redirect(url_for('.post_list', slug=cause.slug))

    context = {
        "cause": cause,
        "form": form,
    }

    return render_template('discussions/post_form.html', **context)


@mod.route('/cause/<slug>/posts/<pk>')
@login_required
@cause_required
def post_detail(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()
    post = cause.posts.filter_by(id=pk).one()

    context = {
        'cause': cause,
        'post': post
    }

    return render_template('discussions/post.html', **context)


@mod.route('/cause/<slug>/posts/<pk>/edit', methods=('GET', 'POST'))
@login_required
@cause_required
def post_edit(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()
    post = cause.posts.filter_by(id=pk).one()

    form = PostForm(request.form, post)

    if form.validate_on_submit():
        form.populate_obj(post)
        post.save()
        flash('Post updated!', 'success')
        return redirect(url_for('.post_detail', slug=cause.slug, pk=post.id))

    context = {
        "cause": cause,
        "form": form,
    }

    return render_template('discussions/post_form.html', **context)


@mod.route('/cause/<slug>/posts/<pk>/comments/add', methods=('GET', 'POST'))
@login_required
@cause_required
def comment_add(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()
    post = cause.posts.filter_by(id=pk).one()

    form = CommentForm(request.form)

    comment = Comment.create(commit=False)

    if form.validate_on_submit():
        form.populate_obj(comment)
        comment.author = current_user
        comment.post = post
        comment.save()
        flash('Comment added!', 'success')
        return redirect(url_for('.post_detail', slug=cause.slug, pk=post.id))

    context = {
        "cause": cause,
        "post": post,
        "form": form,
    }

    return render_template('discussions/comment_form.html', **context)
