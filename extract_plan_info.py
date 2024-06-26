import os
import requests
from datetime import datetime
from models import db, PlanDocument

API_URL = "https://api.openai.com/v1/chat/completions"
your_openai_api_key = os.environ['OPENAI_API_KEY']

def extract_plan_info(plan_text):
    """
    Extracts plan details from the given plan document text by calling the OpenAI API.

    Args:
        plan_text (str): The textual content of the plan document.

    Returns:
        dict: A dictionary containing the extracted details.
    """
    content = f"""
    Below is a plan document that describes a health insurance plan. I need to gather information on this plan to know more about it. Can you please extract the following information from the plan document in the below JSON format?

    JSON Format:

    {{
        "Plan Name": "sample plan name",
        "LOB": "Medicare/Medicaid/Employer Group/Individual Marketplace/Dual Eligible",
        "Geography": "sample geography",
        "Effective Date": "MM/DD/YYYY",
        "Cost Share Overview": "Multi-sentance Description of Deductible / Out of Pocket Maximum / Copays / Coinsurance for different services. This cost share overviewnot be formatted in JSON",
        "HMO/PPO" : "HMO / PPO / EPO depending on the type of plan, if not specified, write PPO",
        "Notes:": "Any other notes that make this health insurance coverage unique, including exclusions, limitations, etc"
    }}

    Plan Document Describing the Plan:
    {plan_text}
    """

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {your_openai_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            response_content = response_json["choices"][0]["message"]["content"]
            try:
                # Find the start of the JSON object and parse it
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                json_str = response_content[json_start:json_end]
                extracted_details = eval(json_str)  # Safely parse the JSON string to a Python dictionary
                return extracted_details

            except Exception as e:
                return {"status": "Error parsing JSON response", "error": str(e)}
        else:
            return {"status": "Invalid response structure"}
    else:
        return {"status": "Failed to get response from OpenAI API", "status_code": response.status_code}

def extract_plan_info_and_save(plan_text):
    """
    Extracts plan details from the given plan document text by calling the OpenAI API
    and saves the information to the database.

    Args:
        plan_text (str): The textual content of the plan document.

    Returns:
        dict: A dictionary containing status and any error messages.
    """
    extracted_details = extract_plan_info(plan_text)

    if 'status' in extracted_details and 'error' in extracted_details:
        return extracted_details

    try:
        # Save to database
        new_plan = PlanDocument(
            link_to_plan_document=None,  # Adjust this based on your application needs
            plan_document_text=plan_text,
            lob=extracted_details.get('LOB', None),
            hmo_ppo=extracted_details.get('HMO/PPO', None),
            geography=extracted_details.get('Geography', None),
            cost_share_overview=extracted_details.get('Cost Share Overview', None),
            name_of_plan=extracted_details.get('Plan Name', None),
            payer=None  # or fill in with actual value if available
        )

        effective_date_str = extracted_details.get('Effective Date', None)
        if effective_date_str:
            try:
                new_plan.effective_date = datetime.strptime(effective_date_str.split(' - ')[0], '%m/%d/%Y').date()
            except ValueError as e:
                print(f"Error parsing Effective Date: {str(e)}")
                return {"status": "Error parsing Effective Date", "error": str(e)}

        db.session.add(new_plan)
        db.session.commit()
        return {"status": "Plan added successfully"}

    except Exception as e:
        return {"status": "Error saving plan to database", "error": str(e)}