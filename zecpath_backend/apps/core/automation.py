def get_application_status(score):

    if score >= 70:
        return "SHORTLISTED"

    elif score < 40:
        return "REJECTED"

    return "PENDING"