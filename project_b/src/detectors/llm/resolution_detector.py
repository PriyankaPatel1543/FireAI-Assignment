from gemini_client import ask_gemini


def check_resolution_status(
    status,
    resolution
):

    prompt = f"""
    Status: {status}

    Resolution Description:
    {resolution}

    Is the description consistent with the status?

    Reply only YES or NO.
    """

    return ask_gemini(prompt)