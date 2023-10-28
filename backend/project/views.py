from flask import Blueprint, render_template, redirect, request, jsonify

from .forms import MyForm
from .tasks import add_user

main = Blueprint('main', __name__)

@main.route('/task_status/<task_id>')
def task_status(task_id):
    task = add_user.AsyncResult(task_id)
    return jsonify({'status': task.status, 'result': task.result})

@main.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = MyForm()

    if form.validate_on_submit():
        task = add_user.delay(form.data)
        return render_template("cancel.html", task=task)

    return render_template('form.html', form=form)

@main.route("/cancel/<task_id>")
def cancel(task_id):
    task = add_user.AsyncResult(task_id)
    task.abort()
    return "CANCELED!"