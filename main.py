from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from parsing import parse_plan_data  # Import the parsing function
import requests
from flask import jsonify

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

@app.route('/add_plan', methods=['POST'])
def add_plan():
    link = request.form.get('link_to_plan_document')
    raw_data = request.form.get('link_to_plan_document')

    # Use the updated parsing function
    parsed_data = parse_plan_data(raw_data)

    new_plan = PlanDocument(
        link_to_plan_document=link,
        plan_document_text=parsed_data
    )
    db.session.add(new_plan)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # Initialize the database and create the table
    with app.app_context():
        db.create_all()

@app.template_filter('truncate_lines')
def truncate_lines(text, max_lines=4, max_length=200):
    if not text:
        return ''

    lines = text.split('\n')[:max_lines]
    truncated_lines = []

    for line in lines:
        truncated_line = (line[:max_length] + '...') if len(line) > max_length else line
        truncated_lines.append(truncated_line)

    return '\n'.join(truncated_lines)
# Register the custom filter with the Jinja environment
app.jinja_env.filters['truncate_lines'] = truncate_lines

@app.route('/view_plan/<int:plan_id>')
def view_plan(plan_id):
    plan = PlanDocument.query.get_or_404(plan_id)
    return render_template('view_plan.html', plan=plan)

@app.route('/update_plan/<int:plan_id>', methods=['POST'])
def update_plan(plan_id):
    plan = PlanDocument.query.get_or_404(plan_id)

    if not plan.plan_document_text:
        return jsonify({"error": "Plan document text is empty"}), 400

    api_url = 'https://extract-plan-info.replit.app/extract-plan-details'
    headers = {'Content-Type': 'application/json'}
    payload = {'text': plan.plan_document_text}

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        
        plan.lob = data.get('LOB')
        plan.hmo_ppo = data.get('HMO/PPO')
        
        effective_date_str = data.get('Effective Date')
        if effective_date_str:
            try:
                plan.effective_date = datetime.strptime(effective_date_str.split(' - ')[0], '%m/%d/%Y').date()  # Only use the start date
            except ValueError as e:
                return jsonify({"error": f"Error parsing Effective Date: {str(e)}"}), 400
        else:
            plan.effective_date = None  # or some default/fallback value if desired

        plan.cost_share_overview = data.get('Cost Share Overview')
        plan.geography = data.get('Geography')

        db.session.commit()
        return jsonify({"message": "Plan updated successfully"})
    else:
        return jsonify({"error": "Failed to extract plan details"}), 500