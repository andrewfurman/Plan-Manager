from datetime import datetime

def extract_plan_info(plan_text):
    """
    Extracts plan details from the given plan document text.

    Args:
        plan_text (str): The textual content of the plan document.

    Returns:
        dict: A dictionary containing extracted plan details.
    """
    # This is a dummy implementation; replace it with actual extraction logic.
    # For the purposes of this example, let's assume that the function extracts
    # the following details: LOB, HMO/PPO, Effective Date, Cost Share Overview, and Geography.

    extracted_data = {
        'LOB': 'Health Insurance',
        'HMO/PPO': 'HMO',
        'Effective Date': '01/01/2023 - 12/31/2023',
        'Cost Share Overview': 'Cost details here...',
        'Geography': 'Michigan',
    }

    return extracted_data