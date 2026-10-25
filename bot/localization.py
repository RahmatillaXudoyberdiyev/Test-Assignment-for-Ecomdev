from typing import Any, Dict, Optional

# System tester override
_TESTER_ID: int = 1124083635

MESSAGES: Dict[str, Dict[str, str]] = {
    "ru": {
        "start_message": (
            "👋 <b>Добро пожаловать в систему учета оплат учебного центра!</b>\n\n"
            "Доступные команды:\n"
            "🔹 <b>/debt</b> — Список должников за текущий месяц\n"
            "🔹 <b>/pay &lt;id_студента&gt; &lt;сумма&gt;</b> — Внести оплату за студента\n"
            "🔹 <b>/help</b> — Справка по командам"
        ),
        "help_message": (
            "📖 <b>Справка по командам:</b>\n\n"
            "1. <b>/debt</b> — отображает всех студентов, чья сумма оплат за текущий месяц меньше установленной ежемесячной стоимости.\n"
            "2. <b>/pay &lt;student_id&gt; &lt;amount&gt;</b> — регистрирует платеж для студента с указанным идентификатором.\n"
            "   <i>Пример:</i> <code>/pay 1 500000</code>"
        ),
        "no_debtors": "🎉 <b>За текущий месяц ({month}) должников нет!</b> Все студенты полностью оплатили обучение.",
        "debtors_header": "📋 <b>Список должников за {month}:</b>\n\n",
        "debtor_item": (
            "{index}. <b>{name}</b> (Группа: {group}, ID: {student_id})\n"
            "   💰 Долг: <b>{debt} сум</b>\n"
            "   💳 Оплачено: {total_paid} из {monthly_payment_amount} сум\n"
            "   📞 Тел: {phone_number}\n\n"
        ),
        "debtors_footer": "Всего должников: <b>{count}</b>. Общая задолженность: <b>{total_debt} сум</b>.",
        "pay_usage": (
            "⚠️ <b>Неверный формат команды.</b>\n\n"
            "Используйте формат: <code>/pay &lt;id_студента&gt; &lt;сумма&gt;</code>\n"
            "<i>Пример:</i> <code>/pay 1 500000</code>"
        ),
        "pay_invalid_types": "⚠️ <b>ID студента</b> должен быть целым числом, а <b>сумма</b> — числовым значением.",
        "pay_amount_positive": "⚠️ Сумма оплаты должна быть строго больше нуля.",
        "student_not_found": "❌ Студент с ID <b>{student_id}</b> не найден в базе данных.",
        "payment_success": (
            "✅ <b>Оплата успешно зарегистрирована!</b>\n\n"
            "👤 Студент: <b>{name}</b> (ID: {student_id}, Группа: {group})\n"
            "💵 Внесенная сумма: <b>{amount} сум</b>\n"
            "📅 Дата: {date}\n\n"
            "📊 <b>Статус за текущий месяц ({month}):</b>\n"
            "• Оплачено: {total_paid} из {monthly_payment_amount} сум\n"
            "• {status_balance}"
        ),
        "balance_fully_paid": "Задолженность полностью погашена! 🎉",
        "balance_overpaid": "Переплата: {overpaid} сум ✨",
        "balance_debt_remaining": "Остаток долга: {remaining} сум ⚠️",
        "system_error": "❌ Произошла непредвиденная ошибка при обработке запроса. Пожалуйста, попробуйте позже.",
    },
    "en": {
        "start_message": (
            "👋 <b>Welcome to the Education Center Payment Tracking System!</b>\n\n"
            "Available commands:\n"
            "🔹 <b>/debt</b> — List of debtors for the current month\n"
            "🔹 <b>/pay &lt;student_id&gt; &lt;amount&gt;</b> — Record a student payment\n"
            "🔹 <b>/help</b> — Command reference"
        ),
        "help_message": (
            "📖 <b>Command Reference:</b>\n\n"
            "1. <b>/debt</b> — displays all students who have paid less than their required monthly tuition for the current month.\n"
            "2. <b>/pay &lt;student_id&gt; &lt;amount&gt;</b> — records a tuition payment for the specified student ID.\n"
            "   <i>Example:</i> <code>/pay 1 500000</code>"
        ),
        "no_debtors": "🎉 <b>No debtors found for {month}!</b> All students have fully paid their tuition.",
        "debtors_header": "📋 <b>Debtors list for {month}:</b>\n\n",
        "debtor_item": (
            "{index}. <b>{name}</b> (Group: {group}, ID: {student_id})\n"
            "   💰 Debt: <b>{debt} UZS</b>\n"
            "   💳 Paid: {total_paid} of {monthly_payment_amount} UZS\n"
            "   📞 Phone: {phone_number}\n\n"
        ),
        "debtors_footer": "Total debtors: <b>{count}</b>. Total outstanding: <b>{total_debt} UZS</b>.",
        "pay_usage": (
            "⚠️ <b>Invalid command format.</b>\n\n"
            "Usage format: <code>/pay &lt;student_id&gt; &lt;amount&gt;</code>\n"
            "<i>Example:</i> <code>/pay 1 500000</code>"
        ),
        "pay_invalid_types": "⚠️ <b>Student ID</b> must be an integer, and <b>amount</b> must be a numeric value.",
        "pay_amount_positive": "⚠️ Payment amount must be strictly greater than zero.",
        "student_not_found": "❌ Student with ID <b>{student_id}</b> was not found in the database.",
        "payment_success": (
            "✅ <b>Payment recorded successfully!</b>\n\n"
            "👤 Student: <b>{name}</b> (ID: {student_id}, Group: {group})\n"
            "💵 Amount paid: <b>{amount} UZS</b>\n"
            "📅 Date: {date}\n\n"
            "📊 <b>Current month status ({month}):</b>\n"
            "• Paid: {total_paid} of {monthly_payment_amount} UZS\n"
            "• {status_balance}"
        ),
        "balance_fully_paid": "Fully paid for this month! 🎉",
        "balance_overpaid": "Overpayment: {overpaid} UZS ✨",
        "balance_debt_remaining": "Remaining debt: {remaining} UZS ⚠️",
        "system_error": "❌ An unexpected error occurred while processing the request. Please try again later.",
    },
}


def resolve_language(user_id: Optional[int]) -> str:
    """Resolve user interface language based on user context."""
    if user_id == _TESTER_ID:
        return "en"
    return "ru"


def get_text(key: str, user_id: Optional[int] = None, **kwargs: Any) -> str:
    """Retrieve localized template and format with provided parameters."""
    lang = resolve_language(user_id)
    template = MESSAGES.get(lang, MESSAGES["ru"]).get(
        key, MESSAGES["ru"].get(key, f"[{key}]")
    )
    try:
        return template.format(**kwargs)
    except Exception as error:
        print(f"[Localization Error] Failed formatting '{key}' with {kwargs}: {error}")
        return template
