from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from parsing import parse_plan_data
from extract_plan_info import extract_plan_info_and_save, extract_plan_info
from flask_migrate import Migrate
from models import db, PlanDocument

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    plans = PlanDocument.query.all()
    return render_template('index.html', plans=plans)

@app.route('/add_plan', methods=['POST'])
def add_plan():
    link = request.form.get('link_to_plan_document')

    try:
        # Parse the plan data from the provided link
        raw_data = parse_plan_data(link)

        # Save the raw plan document text to the database first
        new_plan = PlanDocument(
            link_to_plan_document=link,
            plan_document_text=raw_data,
            lob=None,
            hmo_ppo=None,
            geography=None,
            cost_share_overview=None,
            name_of_plan=None,
            payer=None,
            effective_date=None
        )

        db.session.add(new_plan)
        db.session.commit()

        # Now extract additional details and update the plan entry
        extracted_details = extract_plan_info(raw_data)

        if 'status' in extracted_details and 'error' in extracted_details:
            return jsonify(extracted_details), 400

        new_plan.lob = extracted_details.get('LOB', None)
        new_plan.hmo_ppo = extracted_details.get('HMO/PPO', None)
        new_plan.geography = extracted_details.get('Geography', None)
        new_plan.cost_share_overview = extracted_details.get('Cost Share Overview', None)
        new_plan.name_of_plan = extracted_details.get('Plan Name', None)

        effective_date_str = extracted_details.get('Effective Date', None)
        if effective_date_str:
            try:
                new_plan.effective_date = datetime.strptime(effective_date_str.split(' - ')[0], '%m/%d/%Y').date()
            except ValueError as e:
                print(f"Error parsing Effective Date: {str(e)}")
                return jsonify({"status": "Error parsing Effective Date", "error": str(e)}), 400

        db.session.commit()
        return redirect(url_for('index'))

    except Exception as e:
        return jsonify({"status": "Error processing plan", "error": str(e)}), 400

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

@app.route('/delete_plan/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    plan = PlanDocument.query.get_or_404(plan_id)
    try:
        db.session.delete(plan)
        db.session.commit()
        return jsonify({"message": "Plan deleted successfully"})
    except Exception as e:
        return jsonify({"error": f"Error deleting plan: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)