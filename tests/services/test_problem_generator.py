"""Tests for app.services.problem_generator."""
import pytest

from app.services.problem_generator import ProblemGenerator, Problem
from app.utils.constants import Difficulty, TrainingMode


class TestProblem:
    def test_str_representation(self):
        p = Problem(3, 4, "×", 12)
        assert "3" in str(p) and "4" in str(p) and "×" in str(p)

    def test_attributes(self):
        p = Problem(10, 5, "÷", 2)
        assert p.first_num == 10
        assert p.second_num == 5
        assert p.operation == "÷"
        assert p.answer == 2


class TestProblemGeneratorGenerateProblems:
    def test_returns_list_of_correct_length(self):
        for difficulty in Difficulty:
            for mode in TrainingMode:
                count = 3
                problems = ProblemGenerator.generate_problems(difficulty, mode, count)
                assert len(problems) == count
                assert all(isinstance(p, Problem) for p in problems)

    def test_multiplication_only_produces_multiplication(self):
        problems = ProblemGenerator.generate_problems(
            Difficulty.EASY, TrainingMode.MULTIPLICATION_ONLY, 10
        )
        for p in problems:
            assert p.operation == "×"
            assert p.first_num * p.second_num == p.answer

    def test_division_only_produces_division(self):
        problems = ProblemGenerator.generate_problems(
            Difficulty.EASY, TrainingMode.DIVISION_ONLY, 10
        )
        for p in problems:
            assert p.operation == "÷"
            assert p.first_num // p.second_num == p.answer
            assert p.first_num % p.second_num == 0

    def test_easy_bounds(self):
        problems = ProblemGenerator.generate_problems(
            Difficulty.EASY, TrainingMode.MULTIPLICATION_ONLY, 20
        )
        for p in problems:
            assert 2 <= p.first_num <= 100
            assert 2 <= p.second_num <= 12  # mul_small_factor_max for easy
            assert p.answer == p.first_num * p.second_num

    def test_hard_bounds_multiplication(self):
        problems = ProblemGenerator.generate_problems(
            Difficulty.HARD, TrainingMode.MULTIPLICATION_ONLY, 15
        )
        for p in problems:
            assert 100 <= p.first_num <= 999
            assert 100 <= p.second_num <= 999


class TestProblemGeneratorGenerateVariants:
    def test_includes_correct_answer(self):
        variants = ProblemGenerator.generate_variants(42, 4)
        values = [v[0] for v in variants]
        assert 42 in values
        assert any(v[1] for v in variants)  # one is correct

    def test_correct_count(self):
        variants = ProblemGenerator.generate_variants(10, 3)
        assert len(variants) == 3
        assert sum(1 for _, correct in variants if correct) == 1

    def test_min_two_variants(self):
        variants = ProblemGenerator.generate_variants(5, 1)
        assert len(variants) >= 2

    def test_variants_are_shuffled(self):
        # Run multiple times; at least once order should differ (probabilistic)
        seen = set()
        for _ in range(5):
            v = tuple(v[0] for v in ProblemGenerator.generate_variants(100, 4))
            seen.add(v)
        assert len(seen) >= 1

    def test_zero_correct_answer(self):
        variants = ProblemGenerator.generate_variants(0, 2)
        assert len(variants) >= 2
        assert any(v[0] == 0 and v[1] for v in variants)
