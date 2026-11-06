from gemini_client import ask_gemini


def check_complaint_descriptor(
    complaint,
    descriptor
):

    prompt = f"""
    Complaint Type: {complaint}

    Descriptor: {descriptor}

    Are these consistent?

    Reply only:
    YES
    or
    NO
    """

    return ask_gemini(prompt)