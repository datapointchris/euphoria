from flask import Blueprint, render_template


blueprint = Blueprint(
    'portfolio',
    __name__,
    template_folder='templates/portfolio',
    static_folder='static',
)


@blueprint.route('/')
def index():
    return render_template('index.html')
