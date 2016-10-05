from flask import Blueprint, render_template, url_for, redirect, session, \
                  request, g, flash, abort
from flask.ext.login import login_user, logout_user, current_user, login_required

from app.users.models import User
from app.pages.models import Page
from app.pages.forms import PageForm

mod = Blueprint('admin', __name__)


@mod.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
         return redirect('/')
    return render_template('admin/index.html')

@mod.route('/admin/users')
@login_required
def admin_user_list():
    if not current_user.is_admin:
         return redirect('/')
    return render_template('admin/user_list.html', users=User.query.all())


@mod.route('/admin/pages')
@login_required
def admin_page_list():
    if not current_user.is_admin:
         return redirect('/')
    return render_template('admin/page_list.html', pages=Page.query.all())


@mod.route('/admin/pages/<pk>', methods=('GET', 'POST'))
@login_required
def admin_page_edit(pk):
    if not current_user.is_admin:
         return redirect('/')

    page = Page.query.filter_by(id=pk).first()

    if page is None:
        abort(404)

    form = PageForm(request.form, page)

    if form.validate_on_submit():
        form.populate_obj(page)
        page.update()
        flash('Page updated!', 'success')
        return redirect(url_for('.admin_page_list', pk=pk))

    context = {
         "page": page,
         "form": form
    }

    return render_template('admin/page_edit.html', **context)


@mod.route('/admin/pages/add', methods=('GET', 'POST'))
@login_required
def admin_page_add():
    if not current_user.is_admin:
         return redirect('/')

    form = PageForm(request.form)

    page = Page.create(commit=False)

    if form.validate_on_submit():
        form.populate_obj(page)
        page.save()
        flash('Page added!', 'success')
        return redirect(url_for('.admin_page_list', pk=page.pk))

    context = {
         "page": page,
         "form": form
    }

    return render_template('admin/page_edit.html', **context)