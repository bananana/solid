from flask import (Blueprint, render_template, url_for, redirect, request,
                   flash, abort)
from flask_login import current_user, login_required

from app.causes.models import Cause
from app.causes.views import cause_required
from app.log.models import LogEvent, LogEventType
from app.users.models import User

from .forms import PostForm, CommentForm, PostDeleteForm
from .models import Post, Comment

from ..email import send_email


mod = Blueprint('posts', __name__)


@mod.route('/cause/<slug>/posts')
@cause_required
def post_list(slug):
    cause = Cause.query.filter_by(slug=slug).first()
    context = {
        "cause": cause,
        "posts": cause.posts.all()
    }
    return render_template('posts/post_list.html', **context)


@mod.route('/cause/<slug>/posts/add', methods=('GET', 'POST'))
@login_required
@cause_required
def post_add(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if current_user not in cause.creators.all() and not current_user.is_admin:
        flash('You must be a cause creator or an admin to post.', 'error')
        return redirect(url_for('causes.cause_detail', slug=slug))

    form = PostForm(request.form)

    post = Post.create(commit=False)

    if form.validate_on_submit():
        form.populate_obj(post)
        post.author = current_user
        post.cause = cause
        post.save()

        if current_user in cause.creators.all() or current_user.is_admin:
            send_email('"{0.title}" - "{1.title}"'.format(post, cause),
                       [s.email for s in cause.supporters.all() if s.id != current_user.id],
                       {'cause': cause, 'post': post},
                       'email/post_supporters.txt')
        else:
            send_email('"{0.title}" - "{1.title}"'.format(post, cause),
                    set([s.email for s in cause.creators.all() 
                         + User.query.filter_by(is_admin=True).all()]),
                       {'cause': cause, 'post': post},
                       'email/post_creators.txt')


        flash('Post added!', 'success')
        LogEvent._log('post_add', post, user=current_user)
        return redirect(url_for('.post_list', slug=cause.slug))

    context = {
        "cause": cause,
        "form": form,
    }

    return render_template('posts/post_form.html', **context)


@mod.route('/cause/<slug>/posts/<pk>')
@cause_required
def post_detail(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()
    post = cause.posts.filter_by(id=pk).one()

    comment_form = CommentForm(request.form)

    context = {
        'cause': cause,
        'post': post,
        'comment_form': comment_form
    }

    return render_template('posts/post.html', **context)


@mod.route('/cause/<slug>/posts/<pk>/edit', methods=('GET', 'POST'))
@login_required
@cause_required
def post_edit(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()
    post = cause.posts.filter_by(id=pk).one()

    if current_user.id is not post.author.id and not current_user.is_admin:
        abort(403)

    form = PostForm(request.form, obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)
        post.save()
        flash('Post updated!', 'success')
        return redirect(url_for('.post_detail', slug=cause.slug, pk=post.id))

    context = {
        "cause": cause,
        "form": form,
        "post": post,
    }

    return render_template('posts/post_form.html', **context)


@mod.route('/cause/<slug>/posts/<pk>/delete', methods=('GET', 'POST'))
@login_required
@cause_required
def post_delete(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()
    post = cause.posts.filter_by(id=pk).one()

    if current_user.id is not post.author.id and not current_user.is_admin:
        abort(403)

    form = PostDeleteForm(request.form, obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)
        post.delete()
        flash('Post deleted!', 'success')
        return redirect(url_for('.post_list', slug=cause.slug))

    context = {
        "cause": cause,
        "form": form,
        "post": post,
    }

    return render_template('posts/delete.html', **context)


@mod.route('/cause/<slug>/posts/<pk>/comments/add', methods=('GET', 'POST'))
@login_required
@cause_required
def comment_add(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()
    post = cause.posts.filter_by(id=pk).first()

    if cause is None or post is None:
        abort(404)

    form = CommentForm(request.form)

    comment = Comment.create(commit=False)

    if form.validate_on_submit():
        form.populate_obj(comment)
        comment.author = current_user
        comment.post = post
        comment.save()

        recipients  = set([c.author.email for c in post.comments.all()])

        if post.author is not None:
            recipients.add(post.author.email)

        send_email('New comment on "{0.title}"'.format(post),
                   list(recipients),
                   {'post': post, 'comment': comment},
                   'email/post_comment.txt')

        flash('Comment added!', 'success')
        LogEvent._log('post_reply', post, user=current_user)
        return redirect(url_for('.post_detail', slug=cause.slug, pk=post.id))

    context = {
        "cause": cause,
        "post": post,
        "form": form,
    }

    return render_template('posts/comment_form.html', **context)
