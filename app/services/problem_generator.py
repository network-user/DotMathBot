import random
from typing import Optional

from app.utils.constants import Difficulty, DIFFICULTY_CONFIG, TrainingMode


class Problem:
    def __init__(self, first_num: int, second_num: int, operation: str, answer: int):
        self.first_num = first_num
        self.second_num = second_num
        self.operation = operation
        self.answer = answer

    def __str__(self) -> str:
        return f"{self.first_num} {self.operation} {self.second_num}"


class ProblemGenerator:
    @staticmethod
    def generate_problems(
        difficulty: Difficulty,
        mode: TrainingMode,
        count: int,
    ) -> list[Problem]:
        config = DIFFICULTY_CONFIG[difficulty]

        min_num: int = int(config.get("min_num", 2))
        max_num: int = int(config.get("max_num", 100))

        mul_small_factor_max: Optional[int] = config.get("mul_small_factor_max")

        div_max_dividend: int = int(config.get("div_max_dividend", max_num))
        div_max_divisor: int = int(config.get("div_max_divisor", max_num))
        div_max_quotient: int = int(config.get("div_max_quotient", max_num))

        problems: list[Problem] = []

        for _ in range(count):
            if mode == TrainingMode.MULTIPLICATION_ONLY:
                problem = ProblemGenerator._generate_multiplication(
                    min_num=min_num,
                    max_num=max_num,
                    small_factor_max=mul_small_factor_max,
                )
            elif mode == TrainingMode.DIVISION_ONLY:
                problem = ProblemGenerator._generate_division(
                    max_dividend=div_max_dividend,
                    max_divisor=div_max_divisor,
                    max_quotient=div_max_quotient,
                )
            elif mode in (TrainingMode.MIXED, TrainingMode.CHOOSE_ANSWER):
                if random.choice((True, False)):
                    problem = ProblemGenerator._generate_multiplication(
                        min_num=min_num,
                        max_num=max_num,
                        small_factor_max=mul_small_factor_max,
                    )
                else:
                    problem = ProblemGenerator._generate_division(
                        max_dividend=div_max_dividend,
                        max_divisor=div_max_divisor,
                        max_quotient=div_max_quotient,
                    )
            else:
                problem = ProblemGenerator._generate_multiplication(
                    min_num=min_num,
                    max_num=max_num,
                    small_factor_max=mul_small_factor_max,
                )

            problems.append(problem)

        return problems

    @staticmethod
    def _generate_multiplication(
        *,
        min_num: int,
        max_num: int,
        small_factor_max: Optional[int],
    ) -> Problem:
        if small_factor_max:
            a = random.randint(min_num, max_num)
            b = random.randint(2, int(small_factor_max))
        else:
            a = random.randint(min_num, max_num)
            b = random.randint(min_num, max_num)

        return Problem(a, b, "×", a * b)

    @staticmethod
    def _generate_division(
        *,
        max_dividend: int,
        max_divisor: int,
        max_quotient: int,
    ) -> Problem:
        max_dividend = max(4, int(max_dividend))
        max_divisor = max(2, int(max_divisor))
        max_quotient = max(2, int(max_quotient))

        for _ in range(300):
            divisor = random.randint(2, max_divisor)
            quotient = random.randint(2, max_quotient)
            dividend = divisor * quotient
            if dividend <= max_dividend:
                return Problem(dividend, divisor, "÷", quotient)

        divisor = 2
        quotient = max(2, min(max_quotient, max_dividend // divisor))
        return Problem(divisor * quotient, divisor, "÷", quotient)

    @staticmethod
    def generate_variants(correct_answer: int, variants_count: int) -> list[tuple[int, bool]]:
        variants_count = max(2, int(variants_count))
        correct_answer = int(correct_answer)

        out: list[tuple[int, bool]] = [(correct_answer, True)]
        used = {correct_answer}

        spread = max(5, abs(correct_answer) // 4)

        attempts = 0
        while len(out) < variants_count and attempts < 200:
            attempts += 1
            offset = random.randint(1, spread)
            wrong = correct_answer + offset if random.choice((True, False)) else correct_answer - offset
            wrong = max(0, wrong)

            if wrong in used:
                continue

            used.add(wrong)
            out.append((wrong, False))

        random.shuffle(out)
        return out
