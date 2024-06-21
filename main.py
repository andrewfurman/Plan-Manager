from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PlanDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    link_to_plan_document = db.Column(db.String(255), nullable=True)
    plan_document_text = db.Column(db.Text, nullable=True)
    lob = db.Column(db.String(50), nullable=True)
    hmo_ppo = db.Column(db.String(50), nullable=True)
    effective_date = db.Column(db.Date, nullable=True)
    cost_share_overview = db.Column(db.Text, nullable=True)
    geography = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"PlanDocument(id={self.id}, link_to_plan_document={self.link_to_plan_document})"

@app.route('/')
def index():
    plans = PlanDocument.query.all()
    return render_template('index.html', plans=plans)

@app.route('/add_plan_form')
def add_plan_form():
    return render_template('add_plan.html')

# Route to handle form submission and add a plan
@app.route('/add_plan', methods=['POST'])
def add_plan():
    link = request.form.get('link_to_plan_document')
    new_plan = PlanDocument(link_to_plan_document=link)
    db.session.add(new_plan)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # Initialize the database and create the table
    with app.app_context():
        db.create_all()