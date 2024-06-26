# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PlanDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    link_to_plan_document = db.Column(db.String(255), nullable=True)
    plan_document_text = db.Column(db.Text, nullable=True)
    lob = db.Column(db.String(50), nullable=True)
    hmo_ppo = db.Column(db.String(50), nullable=True)
    effective_date = db.Column(db.Date, nullable=True)
    cost_share_overview = db.Column(db.Text, nullable=True)
    geography = db.Column(db.String(50), nullable=True)
    name_of_plan = db.Column(db.String(100), nullable=True)
    payer = db.Column(db.String(100), nullable=True)
    summarized_plan_coverage = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"PlanDocument(id={self.id}, link_to_plan_document={self.link_to_plan_document})"