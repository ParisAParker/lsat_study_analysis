import random
from typing import Dict, List

import numpy as np
import pandas as pd

from src.question_mix_config import (
    LR_QUESTION_RANGES,
    RC_QUESTION_RANGES,
    TOTAL_LR_QUESTIONS_PER_SECTION,
    TOTAL_RC_QUESTIONS,
)
from src.score_conversion import estimate_scaled_score


def generate_section_question_mix(
    question_ranges: dict[str, tuple[int, int]],
    total_questions: int,
    high_frequency_question_types: list[str],
    low_frequency_question_types: list[str],
) -> list[str]:
    """
    Generate a simulated section based on question-type count ranges.

    If too many questions are generated, remove lower-frequency question types first.
    If too few questions are generated, add higher-frequency question types first.
    """
    section_question_types = []

    for question_type, (minimum_count, maximum_count) in question_ranges.items():
        count = random.randint(minimum_count, maximum_count)
        section_question_types.extend([question_type] * count)

    while len(section_question_types) > total_questions:
        removable_question_types = [
            question_type
            for question_type in section_question_types
            if question_type in low_frequency_question_types
        ]

        if not removable_question_types:
            removable_question_types = section_question_types

        question_type_to_remove = random.choice(removable_question_types)
        section_question_types.remove(question_type_to_remove)

    while len(section_question_types) < total_questions:
        question_type_to_add = random.choice(high_frequency_question_types)
        section_question_types.append(question_type_to_add)

    random.shuffle(section_question_types)
    return section_question_types


def generate_lsat_question_mix() -> list[str]:
    """
    Generate the scored question mix for a modern LSAT:
    two Logical Reasoning sections and one Reading Comprehension section.
    """
    high_frequency_lr_types = [
        "strengthen",
        "weaken",
        "flaw",
        "necessary_assumption",
        "inference_must_be_true",
    ]

    low_frequency_lr_types = [
        "main_point",
        "resolve_paradox",
        "evaluate_argument",
        "point_at_issue",
        "parallel_flaw",
        "cannot_be_true",
    ]

    high_frequency_rc_types = [
        "detail",
        "inference",
        "main_point_primary_purpose",
    ]

    low_frequency_rc_types = [
        "author_attitude_tone",
        "comparative_relationship",
        "application",
    ]

    lr_section_1 = generate_section_question_mix(
        LR_QUESTION_RANGES,
        TOTAL_LR_QUESTIONS_PER_SECTION,
        high_frequency_lr_types,
        low_frequency_lr_types,
    )

    lr_section_2 = generate_section_question_mix(
        LR_QUESTION_RANGES,
        TOTAL_LR_QUESTIONS_PER_SECTION,
        high_frequency_lr_types,
        low_frequency_lr_types,
    )

    rc_section = generate_section_question_mix(
        RC_QUESTION_RANGES,
        TOTAL_RC_QUESTIONS,
        high_frequency_rc_types,
        low_frequency_rc_types,
    )

    return lr_section_1 + lr_section_2 + rc_section


def simulate_lsat_once(accuracy_by_question_type: dict[str, float]) -> dict:
    """
    Simulate one LSAT attempt and return raw score and scaled score.
    """
    question_mix = generate_lsat_question_mix()
    correct_answers = 0

    for question_type in question_mix:
        probability_correct = accuracy_by_question_type.get(question_type, 0.70)

        if random.random() < probability_correct:
            correct_answers += 1

    scaled_score = estimate_scaled_score(
        raw_score=correct_answers,
        total_questions=len(question_mix),
    )

    return {
        "raw_score": correct_answers,
        "total_questions": len(question_mix),
        "scaled_score": scaled_score,
    }


def run_lsat_simulations(
    accuracy_by_question_type: dict[str, float],
    number_of_simulations: int = 10_000,
) -> pd.DataFrame:
    """
    Run many LSAT simulations and return the results as a DataFrame.
    """
    simulation_results = [
        simulate_lsat_once(accuracy_by_question_type)
        for _ in range(number_of_simulations)
    ]

    return pd.DataFrame(simulation_results)


def summarize_simulation_results(results: pd.DataFrame) -> dict:
    """
    Summarize LSAT simulation results.
    """
    return {
        "expected_scaled_score": round(results["scaled_score"].mean(), 1),
        "median_scaled_score": round(results["scaled_score"].median(), 1),
        "low_estimate_10th_percentile": int(np.percentile(results["scaled_score"], 10)),
        "high_estimate_90th_percentile": int(np.percentile(results["scaled_score"], 90)),
        "expected_raw_score": round(results["raw_score"].mean(), 1),
        "median_raw_score": round(results["raw_score"].median(), 1),
    }