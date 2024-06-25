from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from parsing import parse_plan_data  # Import the parsing function
from extract_plan_info import extract_plan_info  # Import the new extract_plan_info function

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

    parsed_data = parse_plan_data(raw_data)

    new_plan = PlanDocument(
        link_to_plan_document=link,
        plan_document_text=parsed_data
    )
    db.session.add(new_plan)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/view_plan/<int:plan_id>')
def view_plan(plan_id):
    plan = PlanDocument.query.get_or_404(plan_id)
    return render_template('view_plan.html', plan=plan)

@app.route('/update_plan/<int:plan_id>', methods=['POST'])
def update_plan(plan_id):
    plan = PlanDocument.query.get_or_404(plan_id)
    if not plan.plan_document_text:
        return jsonify({"error": "Plan document text is empty"}), 400

    print(f"Updating plan with id: {plan_id}")
    extracted_data = extract_plan_info(plan.plan_document_text)
    print(f"Extracted data: {extracted_data}")

    if 'error' in extracted_data:
        return jsonify({"error": f"Error during extraction: {extracted_data['error']}"}), 400

    try:
        plan.lob = extracted_data.get('LOB', plan.lob)
        plan.hmo_ppo = extracted_data.get('HMO/PPO', plan.hmo_ppo)
        effective_date_str = extracted_data.get('Effective Date', None)

        if effective_date_str:
            try:
                plan.effective_date = datetime.strptime(effective_date_str.split(' - ')[0], '%m/%d/%Y').date()
            except ValueError as e:
                print(f"Error parsing Effective Date: {str(e)}")
                return jsonify({"error": f"Error parsing Effective Date: {str(e)}"}), 400
        else:
            plan.effective_date = None  # or some default/fallback value if desired

        plan.cost_share_overview = extracted_data.get('Cost Share Overview', plan.cost_share_overview)
        plan.geography = extracted_data.get('Geography', plan.geography)

        db.session.commit()
        print(f"Plan with id {plan_id} updated successfully.")
        return jsonify({"message": "Plan updated successfully"})

    except Exception as e:
        print(f"Error updating plan with id {plan_id}: {str(e)}")
        return jsonify({"error": f"Error updating plan: {str(e)}"}), 500

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

app.jinja_env.filters['truncate_lines'] = truncate_lines

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    with app.app_context():
        db.create_all()