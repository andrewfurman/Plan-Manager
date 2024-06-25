import os
import requests

API_URL = "https://api.openai.com/v1/chat/completions"
your_openai_api_key = os.environ['OPENAI_API_KEY']

def extract_plan_info(plan_text):
    """
    Extracts plan details from the given plan document text by calling the OpenAI API.

    Args:
        plan_text (str): The textual content of the plan document.

    Returns:
        dict: A dictionary containing extracted plan details.
    """
    content = f"""
    Below is a plan document that describes a health insurance plan. I need to gather information on this plan to know more about it. Can you please extract the following information from the plan document in the below JSON format?

    JSON Format:

    {{
        "Plan Name": "sample plan name",
        "LOB": "Medicare/Medicaid/Employer Group/Individual Marketplace/Dual Eligible",
        "Geography": "sample geography",
        "Effective Date": "MM/DD/YYYY",
        "Cost Share Overview": "Description of Deductible / Out of Pocket Maximum / Copays / Coinsurance for different services",
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
                return {"notes": "Error parsing JSON response", "error": str(e)}
        else:
            return {"notes": "Invalid response structure"}
    else:
        return {"notes": "Failed to get response from OpenAI API", "status_code": response.status_code}

# Example usage:
# plan_text = "Your plan text here"
# print(extract_plan_info(plan_text))