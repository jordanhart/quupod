from flask import Blueprint, render_template, request, redirect, url_for
from queue import app
from queue.views import requires
from queue.public.controllers import unresolved_inquiries, resolving_inquiries
from .models import User, Inquiry
from .controllers import *
from .forms import *
import flask_login


admin = Blueprint('admin', __name__, url_prefix='/admin')

#########
# ADMIN #
#########

@admin.route('/')
@flask_login.login_required
@requires('staff')
def home():
    """admin homepage"""
    assignments = get_assignments()
    return render_template('admin.html', assignments=assignments)

@requires('staff')
@admin.route('/clear/<string:location>', methods=['POST', 'GET'])
@admin.route('/clear', methods=['POST', 'GET'])
def clear(location=None):
    """Clear all inquiries, period. Or, clear all inquiries for a location."""
    if location:
        return 'Not yet implemented.'
    if request.method == 'POST':
        return render_template('confirm.html', **clear_unfinished())
    return render_template('confirm.html',
        message='Are you sure? This will clear all resolving and unresolved. \
        <form method="POST"><input type="submit" value="clear"></form>',
        action='admin home',
        url=url_for('admin.home'))

@requires('staff')
@admin.route('/help')
def help():
    """automatically selects next inquiry"""
    inquiry = get_latest_inquiry()
    if not inquiry:
        return render_template('confirm.html',
            title='All done!',
            message='No more inquiries to process!',
            url=url_for('admin.home'),
            action='admin home')
    lock_inquiry(inquiry)
    return redirect(url_for('admin.help_inquiry', id=inquiry.id))

@requires('staff')
@admin.route('/help/<string:id>', methods=['POST', 'GET'])
def help_inquiry(id):
    """automatically selects next inquiry or reloads inquiry """
    inquiry = get_inquiry(id)
    if request.method == 'POST':
        resolve_inquiry(inquiry)
        return redirect(url_for('admin.help'))
    return render_template('help.html', inquiry=inquiry)

##############
# ASSIGNMENT #
##############

@requires('staff')
@admin.route('/assignment/create', methods=['POST', 'GET'])
def assignment_create():
    """create a new assignment"""
    form = AssignmentForm(request.form)
    if request.method == 'POST' and form.validate():
        assignment = create_assignment(request.form)
        return redirect(url_for('admin.assignment_detail', id=assignment.id))
    return render_template('form.html', form=form, title='Create Assignment')

@requires('/admin')
@admin.route('/assignment/<string:id>/edit', methods=['POST', 'GET'])
def assignment_edit(id):
    assignment = get_assignment(id=id)
    form = AssignmentForm(request.form, obj=assignment)
    if request.method == 'POST' and form.validate():
        assignment = edit_assignment(assignment, request.form)
        return redirect(url_for('admin.assignment_detail', id=assignment.id))
    return render_template('form.html', form=form, title='Edit Assignment')

@requires('/admin')
@admin.route('/assignment/<string:id>', methods=['POST', 'GET'])
def assignment_detail(id):
    assignment = get_assignment(id=id)
    problems = get_problems(assignment)
    return render_template('assignment_detail.html', assignment=assignment,
        problems=problems)


#############
# ANALYTICS #
#############

@requires('staff')
@admin.route('/analytics')
def analytics():
    """analytics for requests"""
    return render_template('analytics.html')