import matplotlib.pyplot as plt
import streamlit as st

from src.question_mix_config import LR_QUESTION_RANGES, RC_QUESTION_RANGES
from src.simulator import run_lsat_simulations, summarize_simulation_results


st.set_page_config(
    page_title="LSAT Score Simulator",
    layout="wide",
)

st.title("Question Type Accuracy Inputs")
st.write(
    "Enter your estimated accuracy percentage for each question type. "
    "The simulator will use these inputs to estimate your LSAT score range."
)

accuracy_by_question_type = {}


lr_frequency_groups = {
    "Higher Frequency": [
        "strengthen",
        "weaken",
        "flaw",
        "necessary_assumption",
        "inference_must_be_true",
    ],
    "Medium Frequency": [
        "sufficient_assumption",
        "method_of_reasoning",
        "parallel_reasoning",
        "principle",
    ],
    "Lower Frequency": [
        "main_point",
        "resolve_paradox",
        "evaluate_argument",
        "point_at_issue",
        "parallel_flaw",
        "cannot_be_true",
    ],
}

rc_frequency_groups = {
    "Higher Frequency": [
        "detail",
        "inference",
    ],
    "Medium Frequency": [
        "main_point_primary_purpose",
        "function_role",
        "author_attitude_tone",
        "method_structure",
        "comparative_relationship",
    ],
    "Lower Frequency": [
        "application",
    ],
}


def format_question_type_name(question_type: str) -> str:
    """
    Convert a snake_case question type into a readable label.
    """
    name_overrides = {
        "inference_must_be_true": "Inference / Must Be True",
        "main_point_primary_purpose": "Main Point / Primary Purpose",
        "author_attitude_tone": "Author Attitude / Tone",
    }

    return name_overrides.get(question_type, question_type.replace("_", " ").title())


def render_accuracy_input(
    question_type: str,
    question_ranges: dict[str, tuple[int, int]],
    key_prefix: str,
    range_multiplier: int = 1,
) -> float:
    """
    Render a compact accuracy input row and return the accuracy as a decimal.
    """
    minimum_count, maximum_count = question_ranges[question_type]
    minimum_count *= range_multiplier
    maximum_count *= range_multiplier

    label = (
        f"{format_question_type_name(question_type)} Accuracy % "
        f"({minimum_count}-{maximum_count} questions)"
    )

    label_column, input_column, percent_column = st.columns([5, 1.2, 0.3])

    with label_column:
        st.markdown(f"**{label}**")

    with input_column:
        accuracy_percentage = st.number_input(
            label,
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=1.0,
            key=f"{key_prefix}_{question_type}",
            label_visibility="collapsed",
        )

    with percent_column:
        st.markdown("%")

    return accuracy_percentage / 100


def render_frequency_group(
    group_name: str,
    question_types: list[str],
    question_ranges: dict[str, tuple[int, int]],
    key_prefix: str,
    range_multiplier: int = 1,
) -> dict[str, float]:
    """
    Render one frequency group and return accuracy values by question type.
    """
    group_results = {}

    with st.container(border=True):
        st.markdown(f"#### {group_name}")

        for question_type in question_types:
            group_results[question_type] = render_accuracy_input(
                question_type=question_type,
                question_ranges=question_ranges,
                key_prefix=key_prefix,
                range_multiplier=range_multiplier,
            )

    return group_results


left_column, right_column = st.columns(2)

with left_column:
    with st.container(border=True):
        st.subheader("Logical Reasoning")
        st.caption("Ranges reflect both scored LR sections combined.")

        for group_name, question_types in lr_frequency_groups.items():
            accuracy_by_question_type.update(
                render_frequency_group(
                    group_name=group_name,
                    question_types=question_types,
                    question_ranges=LR_QUESTION_RANGES,
                    key_prefix="lr",
                    range_multiplier=2,
                )
            )

with right_column:
    with st.container(border=True):
        st.subheader("Reading Comprehension")
        st.caption("Ranges reflect the scored RC section.")

        for group_name, question_types in rc_frequency_groups.items():
            accuracy_by_question_type.update(
                render_frequency_group(
                    group_name=group_name,
                    question_types=question_types,
                    question_ranges=RC_QUESTION_RANGES,
                    key_prefix="rc",
                    range_multiplier=1,
                )
            )


st.divider()

with st.container(border=True):
    st.subheader("Simulation Settings")

    settings_column, button_column = st.columns([2, 1])

    with settings_column:
        number_of_simulations = st.number_input(
            "Number of Simulations",
            min_value=1_000,
            max_value=50_000,
            value=10_000,
            step=1_000,
        )

    with button_column:
        st.write("")
        st.write("")
        run_button = st.button("Run Simulation", use_container_width=True)


if run_button:
    results = run_lsat_simulations(
        accuracy_by_question_type=accuracy_by_question_type,
        number_of_simulations=int(number_of_simulations),
    )

    summary = summarize_simulation_results(results)

    st.subheader("Estimated Score Results")

    metric_columns = st.columns(4)

    metric_columns[0].metric(
        "Expected Scaled Score",
        summary["expected_scaled_score"],
    )

    metric_columns[1].metric(
        "Median Scaled Score",
        summary["median_scaled_score"],
    )

    metric_columns[2].metric(
        "Likely Low",
        summary["low_estimate_10th_percentile"],
    )

    metric_columns[3].metric(
        "Likely High",
        summary["high_estimate_90th_percentile"],
    )

    st.write(
        f"Expected raw score: **{summary['expected_raw_score']}** "
        f"out of **77** questions."
    )

    st.caption(
        "Scaled score conversion is an approximation. Actual LSAT conversions vary by test form."
    )

    st.subheader("Scaled Score Distribution")

    fig, ax = plt.subplots()
    ax.hist(results["scaled_score"], bins=20)
    ax.set_xlabel("Estimated Scaled Score")
    ax.set_ylabel("Simulation Count")
    ax.set_title("Simulated LSAT Score Distribution")

    st.pyplot(fig)

    with st.expander("View Raw Simulation Results"):
        st.dataframe(results)