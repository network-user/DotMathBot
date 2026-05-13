"""Math problem generator.

Supports 7 operations: +, -, *, /, /-with-remainder, x^n, sqrt(x).
Per-operation ranges come from OPERATION_RANGES; multiplication/division
keep their legacy DIFFICULTY_CONFIG entries.

Wrong-answer variants use a Gaussian spread around the correct answer
(no clipping to zero, except for ops whose result cannot be negative).
"""
from __future__ import annotations

import json
import math
import random
from typing import Optional

from app.utils.constants import (
    DIFFICULTY_CONFIG,
    Difficulty,
    OPERATION_RANGES,
    TrainingMode,
)


class Problem:
    def __init__(
        self,
        first_num: int,
        second_num: int,
        operation: str,
        answer: int,
        *,
        formatted_text: str | None = None,
        metadata: dict | None = None,
    ):
        self.first_num = first_num
        self.second_num = second_num
        self.operation = operation
        self.answer = answer
        self.formatted_text = formatted_text or f"{first_num} {operation} {second_num}"
        self.metadata = metadata or {}

    def __str__(self) -> str:
        return self.formatted_text

    @property
    def metadata_json(self) -> str | None:
        return json.dumps(self.metadata) if self.metadata else None


# Superscript digits for power formatting (e.g. 12² instead of 12^2).
_SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _to_superscript(n: int) -> str:
    return str(n).translate(_SUPERSCRIPT)


class ProblemGenerator:
    @staticmethod
    def generate_problems(
        difficulty: Difficulty,
        mode: TrainingMode,
        count: int,
    ) -> list[Problem]:
        out: list[Problem] = []
        for _ in range(count):
            out.append(ProblemGenerator._generate_one(difficulty, mode))
        return out

    @staticmethod
    def _generate_one(difficulty: Difficulty, mode: TrainingMode) -> Problem:
        if mode == TrainingMode.ADDITION_ONLY:
            return ProblemGenerator._generate_addition(difficulty)
        if mode == TrainingMode.SUBTRACTION_ONLY:
            return ProblemGenerator._generate_subtraction(difficulty)
        if mode == TrainingMode.DIVISION_REMAINDER:
            return ProblemGenerator._generate_division_remainder(difficulty)
        if mode == TrainingMode.POWER_ONLY:
            return ProblemGenerator._generate_power(difficulty)
        if mode == TrainingMode.SQRT_ONLY:
            return ProblemGenerator._generate_sqrt(difficulty)
        if mode == TrainingMode.MULTIPLICATION_ONLY:
            return ProblemGenerator._generate_multiplication(difficulty)
        if mode == TrainingMode.DIVISION_ONLY:
            return ProblemGenerator._generate_division(difficulty)

        # MIXED and CHOOSE_ANSWER → sample uniformly across all operations.
        choices = (
            ProblemGenerator._generate_multiplication,
            ProblemGenerator._generate_division,
            ProblemGenerator._generate_addition,
            ProblemGenerator._generate_subtraction,
            ProblemGenerator._generate_division_remainder,
            ProblemGenerator._generate_power,
            ProblemGenerator._generate_sqrt,
        )
        return random.choice(choices)(difficulty)

    # ---- Operations -------------------------------------------------------

    @staticmethod
    def _generate_addition(difficulty: Difficulty) -> Problem:
        cfg = OPERATION_RANGES["add"][difficulty]
        a = random.randint(cfg["min"], cfg["max"])
        b = random.randint(cfg["min"], cfg["max"])
        return Problem(a, b, "+", a + b)

    @staticmethod
    def _generate_subtraction(difficulty: Difficulty) -> Problem:
        cfg = OPERATION_RANGES["sub"][difficulty]
        a = random.randint(cfg["min"], cfg["max"])
        b = random.randint(cfg["min"], cfg["max"])
        # Keep a >= b so the answer is non-negative; subtraction with
        # negative result is reserved for the variant-generation step.
        if a < b:
            a, b = b, a
        return Problem(a, b, "−", a - b)

    @staticmethod
    def _generate_multiplication(difficulty: Difficulty) -> Problem:
        cfg = DIFFICULTY_CONFIG[difficulty]
        small_factor_max: Optional[int] = cfg.get("mul_small_factor_max")
        mul_max_factor: Optional[int] = cfg.get("mul_max_factor")
        min_num = int(cfg.get("min_num", 2))
        max_num = int(cfg.get("max_num", 100))

        if small_factor_max:
            a = random.randint(min_num, max_num)
            b = random.randint(2, int(small_factor_max))
        elif mul_max_factor:
            # Hard: cap both factors so the product stays readable.
            a = random.randint(10, int(mul_max_factor))
            b = random.randint(10, int(mul_max_factor))
        else:
            a = random.randint(min_num, max_num)
            b = random.randint(min_num, max_num)
        return Problem(a, b, "×", a * b)

    @staticmethod
    def _generate_division(difficulty: Difficulty) -> Problem:
        """Exact integer division: pick (divisor, quotient) so dividend ≤ max."""
        cfg = DIFFICULTY_CONFIG[difficulty]
        max_dividend = int(cfg.get("div_max_dividend", 100))
        max_divisor = max(2, int(cfg.get("div_max_divisor", 12)))
        max_quotient = max(2, int(cfg.get("div_max_quotient", 12)))

        # Pick divisor first, then constrain quotient by max_dividend — no brute force.
        divisor = random.randint(2, max_divisor)
        upper_q = min(max_quotient, max_dividend // divisor)
        if upper_q < 2:
            upper_q = 2
        quotient = random.randint(2, upper_q)
        return Problem(divisor * quotient, divisor, "÷", quotient)

    @staticmethod
    def _generate_division_remainder(difficulty: Difficulty) -> Problem:
        cfg = OPERATION_RANGES["div_remainder"][difficulty]
        divisor = random.randint(2, cfg["divisor_max"])
        quotient = random.randint(1, cfg["quotient_max"])
        remainder = random.randint(1, min(divisor - 1, cfg["remainder_max"]))
        dividend = divisor * quotient + remainder
        # Answer is the integer quotient. The remainder is exposed via metadata
        # for the handler to render and validate.
        formatted = f"{dividend} ÷ {divisor} (с остатком)"
        return Problem(
            dividend,
            divisor,
            "÷r",
            quotient,
            formatted_text=formatted,
            metadata={"remainder": remainder, "dividend": dividend, "divisor": divisor},
        )

    @staticmethod
    def _generate_power(difficulty: Difficulty) -> Problem:
        cfg = OPERATION_RANGES["power"][difficulty]
        base = random.randint(cfg["base_min"], cfg["base_max"])
        exponent = random.choice(cfg["exponents"])
        result = base ** exponent
        formatted = f"{base}{_to_superscript(exponent)}"
        return Problem(
            base,
            exponent,
            "^",
            result,
            formatted_text=formatted,
            metadata={"exponent": exponent},
        )

    @staticmethod
    def _generate_sqrt(difficulty: Difficulty) -> Problem:
        cfg = OPERATION_RANGES["sqrt"][difficulty]
        result = random.randint(cfg["result_min"], cfg["result_max"])
        radicand = result * result
        formatted = f"√{radicand}"
        return Problem(
            radicand,
            0,
            "√",
            result,
            formatted_text=formatted,
            metadata={"radicand": radicand},
        )

    # ---- Variants ---------------------------------------------------------

    @staticmethod
    def generate_variants(
        correct_answer: int,
        variants_count: int,
        *,
        allow_negative: bool = False,
    ) -> list[tuple[int, bool]]:
        """Gaussian spread around the correct answer; reject duplicates.

        ``allow_negative`` should be True only for subtraction-like ops where
        a near-zero correct answer could legitimately produce negative wrong
        answers.
        """
        variants_count = max(2, int(variants_count))
        correct_answer = int(correct_answer)

        out: list[tuple[int, bool]] = [(correct_answer, True)]
        used = {correct_answer}

        sigma = max(2.0, abs(correct_answer) * 0.15)

        attempts = 0
        while len(out) < variants_count and attempts < 200:
            attempts += 1
            candidate = round(random.gauss(correct_answer, sigma))
            if not allow_negative and candidate < 0:
                continue
            if candidate in used:
                continue
            used.add(candidate)
            out.append((candidate, False))

        # Sequential-offset fallback if Gaussian sampling couldn't fill variants.
        offset = 1
        while len(out) < variants_count and offset < 1000:
            for sign in (1, -1):
                candidate = correct_answer + sign * offset
                if not allow_negative and candidate < 0:
                    continue
                if candidate not in used:
                    used.add(candidate)
                    out.append((candidate, False))
                    if len(out) >= variants_count:
                        break
            offset += 1

        random.shuffle(out)
        return out
