# -*- coding: utf-8 -*-
"""Tips content by category and language."""

MULTIPLICATION_TIPS = """
🎯 **МЕТОДЫ БЫСТРОГО УМНОЖЕНИЯ**

**1. Умножение на 11**
Для числа AB: A×11 = A(A+B)B
Пример: 23×11 = 2(2+3)3 = 253

**2. Умножение на 25**
Умножь на 100 и раздели на 4
Пример: 24×25 = 2400÷4 = 600

**3. Квадраты чисел, оканчивающихся на 5**
N5² = N(N+1)×100 + 25
Пример: 35² = 3×4×100 + 25 = 1225

**4. Умножение чисел рядом с круглым числом**
(100-a)(100-b) = 10000 - 100(a+b) + ab
Пример: 98×97 = 10000 - 100(2+3) + 2×3 = 9506

**5. Разложение на множители**
24×15 = (8×3)×15 = 8×45 = 360
"""

MULTIPLICATION_TIPS_EN = """
🎯 **QUICK MULTIPLICATION METHODS**

**1. Multiplying by 11**
For number AB: A×11 = A(A+B)B
Example: 23×11 = 2(2+3)3 = 253

**2. Multiplying by 25**
Multiply by 100 and divide by 4
Example: 24×25 = 2400÷4 = 600

**3. Squares of numbers ending in 5**
N5² = N(N+1)×100 + 25
Example: 35² = 3×4×100 + 25 = 1225

**4. Multiplying numbers near round numbers**
(100-a)(100-b) = 10000 - 100(a+b) + ab
Example: 98×97 = 10000 - 100(2+3) + 2×3 = 9506

**5. Factoring**
24×15 = (8×3)×15 = 8×45 = 360
"""

DIVISION_TIPS = """
🎯 **МЕТОДЫ БЫСТРОГО ДЕЛЕНИЯ**

**1. Деление на 25**
Умножь на 4
Пример: 100÷25 = 100×4÷100 = 4

**2. Деление на 5**
Умножь на 2 и раздели на 10
Пример: 125÷5 = 125×2÷10 = 25

**3. Проверка делимости на 9**
Сумма цифр должна делиться на 9
Пример: 369 → 3+6+9=18 → делится на 9

**4. Деление больших чисел**
Используй длинное деление или разложи на части
Пример: 456÷12 = 400÷12 + 56÷12 = 33⅓ + 4⅔ = 38

**5. Приблизительное деление**
Используй округление для быстрой оценки
Пример: 1247÷3 ≈ 1200÷3 = 400, уточни затем
"""

DIVISION_TIPS_EN = """
🎯 **QUICK DIVISION METHODS**

**1. Dividing by 25**
Multiply by 4
Example: 100÷25 = 100×4÷100 = 4

**2. Dividing by 5**
Multiply by 2 and divide by 10
Example: 125÷5 = 125×2÷10 = 25

**3. Divisibility by 9**
Sum of digits must be divisible by 9
Example: 369 → 3+6+9=18 → divisible by 9

**4. Dividing large numbers**
Use long division or break into parts
Example: 456÷12 = 400÷12 + 56÷12 = 33⅓ + 4⅔ = 38

**5. Approximate division**
Use rounding for quick estimates
Example: 1247÷3 ≈ 1200÷3 = 400, then refine
"""

GENERAL_TIPS = """
💡 **ОБЩИЕ СОВЕТЫ**

**Практика делает совершенство**
- Тренируйтесь регулярно и постоянно
- Начните с легкого уровня
- Постепенно переходите к более сложным примерам

**Способы отработки**
1. Решайте примеры вслух - это помогает закрепить
2. Используйте метод проверки - умножьте результат
3. Учите таблицу умножения для чисел до 20

**Развитие умственного счета**
- Расбивайте числа на части
- Используйте известные вам факты
- Ищите закономерности и подсказки в числах

**Советы для серьезной практики**
- Уделяйте 5-10 минут в день
- Попробуйте считать без помощников
- Отслеживайте свой прогресс
"""

GENERAL_TIPS_EN = """
💡 **GENERAL TIPS**

**Practice makes perfect**
- Train regularly and consistently
- Start with the easy level
- Gradually move to harder examples

**Ways to practice**
1. Solve out loud - it helps to remember
2. Use the check method - multiply the result
3. Learn the times table up to 20

**Mental math development**
- Break numbers into parts
- Use facts you already know
- Look for patterns and clues in numbers

**Serious practice tips**
- Spend 5-10 minutes a day
- Try counting without aids
- Track your progress
"""


def get_tips(category: str, lang: str = "ru") -> str:
    """Return tips text for category (multiplication, division, general) and language."""
    if lang == "en":
        tips = {
            "multiplication": MULTIPLICATION_TIPS_EN,
            "division": DIVISION_TIPS_EN,
            "general": GENERAL_TIPS_EN,
        }
    else:
        tips = {
            "multiplication": MULTIPLICATION_TIPS,
            "division": DIVISION_TIPS,
            "general": GENERAL_TIPS,
        }
    return tips.get(category, GENERAL_TIPS if lang != "en" else GENERAL_TIPS_EN)
