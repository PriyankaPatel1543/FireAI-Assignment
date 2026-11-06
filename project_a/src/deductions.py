def calculate_standard_deduction(salary, regime):
    """
    Calculate standard deduction for FY 2024-25.
    """

    if salary < 0:
        raise ValueError("Salary cannot be negative")

    if regime == "old":
        deduction_limit = 50000

    elif regime == "new":
        deduction_limit = 75000

    else:
        raise ValueError("Regime must be 'old' or 'new'")

    return min(salary, deduction_limit)


def calculate_taxable_salary(salary, regime):
    """
    Calculate taxable salary after standard deduction.
    """

    standard_deduction = calculate_standard_deduction(
        salary, regime
    )

    taxable_salary = salary - standard_deduction

    return taxable_salary



def calculate_80c_deduction(amount):
    """
    Section 80C deduction.
    Maximum limit: Rs. 1,50,000.
    """

    if amount < 0:
        raise ValueError("Deduction amount cannot be negative")

    return min(amount, 150000)


def calculate_80ccd_1b_deduction(amount):
    """
    Additional deduction under Section 80CCD(1B).
    Maximum limit: Rs. 50,000.
    """

    if amount < 0:
        raise ValueError("Deduction amount cannot be negative")

    return min(amount, 50000)


def calculate_chapter_via_deductions(
    regime,
    section_80c=0,
    section_80ccd_1b=0
):
    """
    Calculate eligible deductions under Sections 80C
    and 80CCD(1B).
    """

    if regime == "new":
        return {
            "80C": 0,
            "80CCD_1B": 0,
            "total": 0
        }

    if regime != "old":
        raise ValueError("Invalid tax regime")

    deduction_80c = calculate_80c_deduction(section_80c)

    deduction_80ccd = calculate_80ccd_1b_deduction(
        section_80ccd_1b
    )

    return {
        "80C": deduction_80c,
        "80CCD_1B": deduction_80ccd,
        "total": deduction_80c + deduction_80ccd
    }

METRO_CITIES = {"delhi", "mumbai", "kolkata", "chennai"}


def calculate_hra_exemption(basic_salary, hra_received, rent_paid, is_metro):
    """Annual figures. Exemption = min of 3 amounts (Sec 10(13A), Rule 2A)."""
    for v in (basic_salary, hra_received, rent_paid):
        if v < 0:
            raise ValueError("Amounts cannot be negative")

    rent_minus_10pct = max(0, rent_paid - 0.10 * basic_salary)
    pct_of_basic = (0.50 if is_metro else 0.40) * basic_salary

    return min(hra_received, rent_minus_10pct, pct_of_basic)


def calculate_80d_deduction(self_premium, parents_premium,
                            self_senior=False, parents_senior=False):
    """Sec 80D: limit 25,000 per group, 50,000 if that group is senior."""
    if self_premium < 0 or parents_premium < 0:
        raise ValueError("Premium cannot be negative")

    self_limit = 50000 if self_senior else 25000
    parents_limit = 50000 if parents_senior else 25000

    return min(self_premium, self_limit) + min(parents_premium, parents_limit)


def calculate_home_loan_deduction(interest):
    """Sec 24(b): self-occupied house, max 2,00,000."""
    if interest < 0:
        raise ValueError("Interest cannot be negative")
    return min(interest, 200000)