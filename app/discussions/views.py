from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask.ext.login import current_user, login_required

from app.causes.models import Cause
from app.causes.views import cause_required

from .forms import PostForm
from .models import Post, Comment

mod = Blueprint('discussions', __name__)

@mod.route('/cause/<slug>/posts')
@cause_required
def posts(slug):
    cause = Cause.query.filter_by(slug=slug).first()
    context = {
        "cause": cause,
        "posts": cause.posts.all()
    }
    return render_template('discussions/list.html', **context)


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
        return redirect(url_for('.posts', slug=cause.slug))

    context = {
        "cause": cause,
        "form": form,
    }

    return render_template('discussions/post_form.html', **context)

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
        return redirect(url_for('.posts', slug=cause.slug))

    context = {
        "cause": cause,
        "form": form,
    }

    return render_template('discussions/post_form.html', **context)
