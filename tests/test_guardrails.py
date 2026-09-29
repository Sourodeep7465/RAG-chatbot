"""Unit tests for guardrail classifier."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.guardrails.classifier import classify_intent, should_refuse, get_refusal_message


# === REFUSE CASES (10) ===

def test_should_i_buy():
    """Should refuse 'should I buy' queries."""
    assert should_refuse("Should I buy HDFC Small Cap?")
    assert classify_intent("Should I buy HDFC Small Cap?") == "ADVICE"


def test_should_i_invest():
    """Should refuse 'should I invest' queries."""
    assert should_refuse("Should I invest in HDFC Flexi Cap?")
    assert classify_intent("Should I invest in HDFC Flexi Cap?") == "ADVICE"


def test_is_it_good():
    """Should refuse 'is it good' queries."""
    assert should_refuse("Is HDFC Small Cap a good fund?")
    assert classify_intent("Is HDFC Small Cap a good fund?") == "ADVICE"


def test_will_it_go_up():
    """Should refuse 'will it go up' queries."""
    assert should_refuse("Will HDFC Small Cap go up?")
    assert classify_intent("Will HDFC Small Cap go up?") == "ADVICE"


def test_recommend():
    """Should refuse 'recommend' queries."""
    assert should_refuse("Can you recommend a good mutual fund?")
    assert classify_intent("Can you recommend a good mutual fund?") == "ADVICE"


def test_which_is_better():
    """Should refuse 'which is better' queries."""
    assert should_refuse("Which is better, HDFC Large Cap or HDFC Small Cap?")
    assert classify_intent("Which is better, HDFC Large Cap or HDFC Small Cap?") == "OPINION"


def test_which_should_i_choose():
    """Should refuse 'which should I choose' queries."""
    assert should_refuse("Which should I choose, HDFC Flexi Cap or HDFC Balanced Advantage?")
    assert classify_intent("Which should I choose, HDFC Flexi Cap or HDFC Balanced Advantage?") == "OPINION"


def test_my_portfolio():
    """Should refuse 'my portfolio' queries."""
    assert should_refuse("What should I do with my portfolio?")
    assert classify_intent("What should I do with my portfolio?") == "PORTFOLIO"


def test_how_much_should_i_invest():
    """Should refuse 'how much should I invest' queries."""
    assert should_refuse("How much should I invest in HDFC Small Cap?")
    assert classify_intent("How much should I invest in HDFC Small Cap?") == "ADVICE"


def test_best_fund():
    """Should refuse 'best fund' queries."""
    assert should_refuse("What is the best mutual fund to invest in?")
    assert classify_intent("What is the best mutual fund to invest in?") == "ADVICE"


# === ALLOW CASES (10) ===

def test_expense_ratio():
    """Should allow expense ratio queries."""
    assert not should_refuse("What is the expense ratio of HDFC Small Cap?")
    assert classify_intent("What is the expense ratio of HDFC Small Cap?") == "FACTUAL"


def test_exit_load():
    """Should allow exit load queries."""
    assert not should_refuse("What is the exit load of HDFC Flexi Cap?")
    assert classify_intent("What is the exit load of HDFC Flexi Cap?") == "FACTUAL"


def test_minimum_sip():
    """Should allow minimum SIP queries."""
    assert not should_refuse("What is the minimum SIP for HDFC Large Cap?")
    assert classify_intent("What is the minimum SIP for HDFC Large Cap?") == "FACTUAL"


def test_lock_in():
    """Should allow lock-in queries."""
    assert not should_refuse("What is the lock-in period for ELSS?")
    assert classify_intent("What is the lock-in period for ELSS?") == "FACTUAL"


def test_riskometer():
    """Should allow riskometer queries."""
    assert not should_refuse("What is the riskometer of HDFC Small Cap?")
    assert classify_intent("What is the riskometer of HDFC Small Cap?") == "FACTUAL"


def test_benchmark():
    """Should allow benchmark queries."""
    assert not should_refuse("What is the benchmark of HDFC Balanced Advantage?")
    assert classify_intent("What is the benchmark of HDFC Balanced Advantage?") == "FACTUAL"


def test_how_to_download_statement():
    """Should allow 'how to download' queries."""
    assert not should_refuse("How to download capital gains statement?")
    assert classify_intent("How to download capital gains statement?") == "FACTUAL"


def test_nav():
    """Should allow NAV queries."""
    assert not should_refuse("What is the NAV of HDFC Large Cap?")
    assert classify_intent("What is the NAV of HDFC Large Cap?") == "FACTUAL"


def test_fund_manager():
    """Should allow fund manager queries."""
    assert not should_refuse("Who is the fund manager of HDFC Flexi Cap?")
    assert classify_intent("Who is the fund manager of HDFC Flexi Cap?") == "FACTUAL"


def test_asset_allocation():
    """Should allow asset allocation queries."""
    assert not should_refuse("What is the asset allocation of HDFC Balanced Advantage?")
    assert classify_intent("What is the asset allocation of HDFC Balanced Advantage?") == "FACTUAL"


# === TRICKY CASES ===

def test_comparison_facts_allowed():
    """Comparison of plain facts should be allowed."""
    assert not should_refuse("What is the expense ratio of HDFC Large Cap and HDFC Small Cap?")
    assert classify_intent("What is the expense ratio of HDFC Large Cap and HDFC Small Cap?") == "FACTUAL"


def test_comparison_recommendation_refused():
    """Comparison asking for a pick should be refused."""
    assert should_refuse("Which is better, HDFC Large Cap or HDFC Small Cap? I need to pick one.")
    assert classify_intent("Which is better, HDFC Large Cap or HDFC Small Cap? I need to pick one.") == "OPINION"


def test_refusal_message_contains_link():
    """Refusal message should contain an educational link."""
    msg = get_refusal_message("Should I buy HDFC Small Cap?")
    assert "amfiindia.com" in msg or "sebi.gov.in" in msg


def test_refusal_message_polite():
    """Refusal message should be polite and mention facts-only."""
    msg = get_refusal_message("Should I buy HDFC Small Cap?")
    assert "factual" in msg.lower() or "facts" in msg.lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
