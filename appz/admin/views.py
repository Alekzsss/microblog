import os
from config import basedir
from appz import db
from appz.models import User, Post, Role, Notification
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.view import func
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.menu import MenuLink
from flask_login import current_user
from wtforms import PasswordField
from wtforms.validators import required, EqualTo
from flask import request, flash, redirect, url_for, has_request_context
from flask_admin.form import rules
from werkzeug.security import generate_password_hash
from appz.main.routes import guess_lang
from flask_admin.contrib.sqla.filters import BooleanEqualFilter, BaseSQLAFilter, FilterEqual
from flask_babelex import lazy_gettext
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader


class AdminMixin:
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to index page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class MyAdminIndexView(AdminMixin, AdminIndexView):
    pass


class MyFileAdmin(AdminMixin, FileAdmin):
    can_upload = True
    can_download = True
    can_delete = True
    can_delete_dirs = True
    can_mkdir = True
    can_rename = True


class FilterRoleAdmin(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        return query.filter(self.column == value)

    def operation(self):
        return lazy_gettext('equals')

# class MyFilterEqual(FilterEqual):
#     def apply(self, query, value, alias=None):
#         query.name
#
# [(str(num), role) for num, role in enumerate([role.name for role in Role.query.all()], 1)]


class UserView(AdminMixin, ModelView):
    # form configuration
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    column_exclude_list = ['token', 'token_expiration', 'password_hash']
    column_list = ['id', 'username', 'email', 'about_me', 'role']
    column_details_exclude_list = ['token', 'token_expiration', 'password_hash']
    column_sortable_list = ['id', 'username', 'email', 'about_me', ('role', 'role_id')] # for relationship field   ('notifications', 'notifications.user_id')
    column_searchable_list = ['id', 'username', 'email', 'role.name']

    column_filters = ['id', 'username', 'email',
                      FilterRoleAdmin(User.role_id, 'Role', options=(('1', 'User'), ('2','Moderator'), ('3', 'Administrator'))),
                      FilterEqual(column=User.role_id, name='Role(temporary)', options=[('1', 'User'), ('2','Moderator'), ('3', 'Administrator')] )# [(str(num), role) for num, role in enumerate([role.name for role in Role.query.all()], 1)]
                      ]
    # column_choices = {
    #     'role_id': [
    #         (1, 'User'),
    #         (2, 'Moderator'),
    #         (3, 'Administrator'),
    #     ]
    # }
    # column_auto_select_related = True
    # column_editable_list = ['username', 'email']
    column_default_sort = ('username', False)
    column_labels = {'role.name': 'role',
                     'role_id': 'Role'}
    column_display_pk = True # show model's id
    create_modal = False
    edit_modal = False
    # form_extra_fields = {
    #     'password': PasswordField('Password'),
    #     'password2': PasswordField('Repeat password')
    # }
    # form_columns = ['username', 'email', 'role_id', 'about_me'] # 'password', 'password2',
    # form_excluded_columns =  ['token', 'token_expiration', 'password_hash', 'messages_sent', 'messages_received',
    #                           'followers', 'followed', 'last_seen', 'notifications', 'tasks', 'last_message_read_time',
    #                           'posts']
    # # for large queries
    # form_ajax_refs = {
    #     'role': {
    #         'fields': ['id'],
    #         'placeholder': 'Please select',
    #         'page_size': 10,
    #         'minimum_input_length': 0,
    #     }
    # }
    # form_choices = {
    #     'role_id': [
    #         ('1', 'User'),
    #         ('2', 'Moderator'),
    #         ('3', 'Administrator'),
    #     ]
    # }
    form_widget_args = {
        'username': {
            'rows': 10,
            'style': 'color: red'
        }

    }
    form_create_rules = [
        'username', 'password', 'password_check', 'role', 'email', 'about_me'
    ]
    form_edit_rules = [
        'username', 'email', 'role', 'about_me',
        rules.Text('RESET PASSWORD'),
        'new_password', 'confirm'
    ]
    form_args = {
        'username': {
            'label': 'Username',
            'validators': [required()]
        },
        'email': {
            'label': 'Your email',
            'validators': [required()]
        },
        'role': {
            'label': 'Your role',
            'validators': [required()]
        },
    }
    can_export = True

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.password = PasswordField('Password', validators=[required()])
        form_class.password_check = PasswordField('Repeat password', validators=[required(), EqualTo('password')])
        form_class.new_password = PasswordField('New Password')
        form_class.confirm = PasswordField('Confirm new Password', validators=[EqualTo('new_password')])
        return form_class

    # def scaffold_sortable_columns(self):
    #     columns = dict()
    #
    #     for n, f in self._get_model_fields():
    #         # if self.column_display_pk or type(f) != PrimaryKeyField:
    #         columns[n] = f
    #
    #     return columns

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password_hash = generate_password_hash(form.password.data)
        else:
            if form.new_password.data:
                model.password_hash = generate_password_hash(form.new_password.data)
        return super(UserView, self).on_model_change(form, model, is_created)

    def is_sortable(self, name):
        name = 'role'
        return name
    # def update_model(self, form, model):
    #     form.populate_obj(model)
    #     if form.new_password.data:
    #         model.password_hash = generate_password_hash(form.new_password.data)
    #     self.session.add(model)
    #     self._on_model_change(form, model, False)
    #     self.session.commit()
    #     return self.render('admin/index.html')


class PostView(AdminMixin, ModelView):
    form_create_rules = ['body', 'author']
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    column_list = ['body', 'timestamp', 'language', 'author']
    column_sortable_list = ['body', 'timestamp', 'language', ('author', 'author.username')]
    column_labels = {'user_id': 'User'}

    form_edit_rules = ['body']

    def on_model_change(self, form, model, is_created):
        model.language = guess_lang(form.body.data)


class RoleView(AdminMixin, ModelView):
    can_view_details = True

    column_display_pk = True


class NotificationsView(AdminMixin, BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/notify.html')

path = os.path.join(basedir, 'appz', 'static')

def init_admin(admin):
    admin.add_view(UserView(User, db.session))
    admin.add_view(PostView(Post, db.session))
    admin.add_view(RoleView(Role, db.session))
    admin.add_view(MyFileAdmin(path, '/static/', name='Files'))
    admin.add_view(NotificationsView(name='Notifications', endpoint='notify'))
    # admin.add_sub_category(name="Links", parent_name="Administration")
    # admin.add_link(MenuLink(name='Explore', url='/explore', category='Links'))
    # admin.add_link(MenuLink(name='Explore', url='/explore', category=''))
    # admin.add_link(MenuLink(name='Messages', url='/messages', category=''))
    admin.add_link(MenuLink(name='To main app', url='/', category=''))
