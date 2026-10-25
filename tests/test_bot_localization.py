from bot.localization import resolve_language, get_text


def test_language_resolution():
    """Verify default language is Russian and tester ID resolves to English."""
    assert resolve_language(123456789) == "ru"
    assert resolve_language(None) == "ru"
    assert resolve_language(1124083635) == "en"


def test_localized_text_output():
    """Verify correct language content rendering for user roles."""
    # Russian for standard user
    ru_start = get_text("start_message", user_id=987654)
    assert "Добро пожаловать" in ru_start

    # English for tester user
    en_start = get_text("start_message", user_id=1124083635)
    assert "Welcome" in en_start

    # Debtors header
    ru_debtors = get_text("debtors_header", user_id=987654, month="2026-10")
    assert "Список должников" in ru_debtors

    en_debtors = get_text("debtors_header", user_id=1124083635, month="2026-10")
    assert "Debtors list" in en_debtors
