import base64
import calendar
import random
from collections import Counter
from datetime import date, datetime, time, timedelta
from io import BytesIO

from euphoria import priorities_db as db
from euphoria.priorities.helpers import calculate_average_completion_time
from euphoria.priorities.models import Task
from flask import Blueprint, redirect, render_template, request, url_for
from matplotlib.figure import Figure
from sqlalchemy import delete, select

priorities_bp = Blueprint(
    'priorities_bp',
    __name__,
    template_folder='templates/priorities',
    static_folder='static',
)

today = datetime.combine(date.today(), time())
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)
previous_7 = today - timedelta(days=7)
previous_30 = today - timedelta(days=30)
week_start = datetime.combine(
    date.fromisocalendar(today.year, today.isocalendar().week, 1), time()
)
week_end = week_start + timedelta(days=7)
_month_days = calendar.monthrange(today.year, today.month)[1]
month_start = datetime(today.year, today.month, 1)
month_end = datetime(today.year, today.month, _month_days)
year_start = datetime(today.year, 1, 1)
year_end = datetime(today.year, 12, 31)


@priorities_bp.route('/', methods=['GET'])
def priority():
    completed_today = (
        db.session.execute(
            select(Task).where(Task.complete_date > today, Task.complete_date < tomorrow)
        )
        .scalars()
        .all()
    )
    top_tasks = (
        db.session.execute(
            select(Task)
            .where(Task.complete_date.is_(None))
            .order_by(Task.priority.asc(), Task.add_date.asc())
            .limit(5 - len(completed_today))
        )
        .scalars()
        .all()
    )
    return render_template(
        'priority.html', top_tasks=top_tasks, completed_today=completed_today
    )


@priorities_bp.route('/fake/', methods=['GET'])
def fake_tasks():
    def add_fake_tasks(number):
        for _ in range(number):
            tstamp = datetime.utcnow() - timedelta(days=random.randint(0, 100))
            completed = (
                tstamp + timedelta(days=random.randint(0, 100)),
                None,
                None,
                None,
            )
            task = {
                'name': f'task {random.random()}',
                'category': 'financial',
                'subcategory1': None,
                'subcategory2': None,
                'priority': random.randint(0, 100),
                'add_date': tstamp,
                'complete_date': random.choice(completed),
            }
            db.session.add(Task(**task))
        db.session.commit()

    add_fake_tasks(100)
    return redirect(url_for('priorities_bp.priority'))


@priorities_bp.route('/add/', methods=['POST'])
def add_task():
    db.session.add(Task(**request.form))
    db.session.commit()
    return redirect(url_for('priorities_bp.priority'))


@priorities_bp.route('/complete/', methods=['POST'])
def complete_task():
    task = Task.query.filter_by(id=request.form.get('id')).first()
    task.complete_date = datetime.now()
    db.session.commit()
    return redirect(url_for('priorities_bp.priority'))


@priorities_bp.route('/delete/', methods=['POST'])
def delete_task():
    task = Task.query.filter_by(id=request.form.get('id')).first()
    db.session.execute(delete(Task).where(Task.id == task.id))
    db.session.commit()
    return redirect(url_for('priorities_bp.priority'))


@priorities_bp.route('/tasks/')
def tasks():
    tasks = (
        Task.query.filter(Task.complete_date.is_(None))
        .order_by(Task.priority.asc(), Task.add_date.asc())
        .all()
    )
    return render_template('tasks.html', tasks=tasks)


@priorities_bp.route('/completed/', methods=['GET', 'POST'])
def completed():
    # TODO: build some simple graphs in this page, on the right hand side.
    # Title goes in center of page
    # filters should be at the top on the right, graph below
    # graph should have a line at 5 per day, with the graph being divided
    # by the number of days in the filter
    # average completion time should be under the filters
    filters = {
        'all': (Task.complete_date.is_not(None),),
        'today': (Task.complete_date > today, Task.complete_date < tomorrow),
        'yesterday': (Task.complete_date > yesterday, Task.complete_date < today),
        'this_week': (Task.complete_date > week_start, Task.complete_date < week_end),
        'last_7': (Task.complete_date > previous_7, Task.complete_date < today),
        'this_month': (Task.complete_date > month_start, Task.complete_date < month_end),
        'last_30': (Task.complete_date > previous_30, Task.complete_date < today),
        'this_year': (Task.complete_date > year_start, Task.complete_date < year_end),
    }
    if request.method == 'POST':
        selected_filter = request.form.get('filter')
    else:
        selected_filter = 'all'
    query_filter = filters.get(selected_filter, 'all')
    completed = (
        db.session.execute(
            select(Task).where(*query_filter).order_by(Task.complete_date.desc())
        )
        .scalars()
        .all()
    )
    average_completion = calculate_average_completion_time(completed)

    # Graph
    fig = Figure()
    ax = fig.subplots()
    count = Counter(task.complete_date.day for task in completed)
    x = count.keys()
    y = count.values()
    ax.bar(x, y)
    # Save it to a temporary buffer.
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    # Embed the result in the html output.
    image_data = base64.b64encode(buffer.getbuffer()).decode("ascii")

    return render_template(
        'completed.html',
        completed=completed,
        average_completion=average_completion,
        filters=filters,
        selected_filter=selected_filter,
        image_data=image_data
    )





@priorities_bp.route('/image/', methods=['GET', 'POST'])
def image():
    completed = (
        db.session.execute(
            select(Task)
            .where(Task.complete_date > month_start, Task.complete_date < month_end)
            .order_by(Task.priority.asc(), Task.add_date.asc())
        )
        .scalars()
        .all()
    )

    return f"<img src='data:image/png;base64,{data}'/>"
