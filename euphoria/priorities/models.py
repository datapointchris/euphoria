from euphoria import priorities_db as db
from datetime import datetime


class Task(db.Model):
    """Data Model for Events Happening"""

    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=False, unique=False, nullable=False)
    category = db.Column(db.String(64), index=False, unique=False, nullable=True)
    subcategory1 = db.Column(db.String(64), index=False, unique=False, nullable=True)
    subcategory2 = db.Column(db.String(64), index=False, unique=False, nullable=True)
    priority = db.Column(db.Integer, index=False, unique=False, nullable=False)
    add_date = db.Column(
        db.DateTime(timezone=True),
        index=False,
        unique=False,
        nullable=False,
        default=datetime.now(),
    )
    complete_date = db.Column(
        db.DateTime(timezone=True), index=False, unique=False, nullable=True
    )

    def __repr__(self):
        return f'Task(name = {self.name}, priority = {self.priority}, category = {self.category}, subcategory1 = {self.subcategory1}, subcategory2 = {self.subcategory2}, , add_date = {self.add_date}, complete_date = {self.complete_date})'

    @property
    def time_to_complete(self):
        if self.complete_date:
            return f'{(self.complete_date - self.add_date).days + 1} days'
        else:
            return 'Task Not Completed'
