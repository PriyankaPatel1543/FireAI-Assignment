from src.input_parser import normalize


def test_monthly_rent_converted():
    inp, missing, _ = normalize({"salary_annual": 1200000, "rent_monthly": 15000,
                                 "basic_salary_annual": 600000,
                                 "hra_received_annual": 240000, "city": "Mumbai"})
    assert inp["rent_paid"] == 180000 and inp["is_metro"] is True and missing == []


def test_rent_without_hra_details_asks():
    _, missing, _ = normalize({"salary_annual": 1200000, "rent_monthly": 15000})
    assert missing == ["basic_salary", "hra_received", "city"]


def test_pays_rent_without_amount_asks():
    _, missing, _ = normalize({"salary_annual": 1200000, "pays_rent": True})
    assert missing == ["rent_amount", "basic_salary", "hra_received", "city"]