import streamlit as st
import matplotlib.pyplot as plt

from src.question_mix_config import LR_QUESTION_RANGES, RC_QUESTION_RANGES
from src.simulator import run_lsat_simulations, summarize_simulation_results


st.set_page_config(
    page_title="LSAT Score Simulator",
    layout="wide",
)

st.title("LSAT Score Simulator")
st.write(
    "Enter your estimated accuracy for each question type. "
    "The app will simulate possible LSAT outcomes and estimate your scaled score range."
)

st.sidebar.header("Simulation Settings")

number_of_simulations = st.sidebar.slider(
    "Number of simulations",
    min_value=1_000,
    max_value=50_000,
    value=10_000,
    step=1_000,
)

st.header("Logical Reasoning Accuracy")

accuracy_by_question_type = {}

lr_columns = st.columns(3)

for index, question_type in enumerate(LR_QUESTION_RANGES.keys()):
    with lr_columns[index % 3]:
        accuracy_by_question_type[question_type] = (
            st.slider(
                question_type.replace("_", " ").title(),
                min_value=0,
                max_value=100,
                value=70,
                step=1,
                key=f"lr_{question_type}",
            )
            / 100
        )

st.header("Reading Comprehension Accuracy")

rc_columns = st.columns(3)

for index, question_type in enumerate(RC_QUESTION_RANGES.keys()):
    with rc_columns[index % 3]:
        accuracy_by_question_type[question_type] = (
            st.slider(
                question_type.replace("_", " ").title(),
                min_value=0,
                max_value=100,
                value=70,
                step=1,
                key=f"rc_{question_type}",
            )
            / 100
        )

run_button = st.button("Run Simulation")

if run_button:
    results = run_lsat_simulations(
        accuracy_by_question_type=accuracy_by_question_type,
        number_of_simulations=number_of_simulations,
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

    st.subheader("Scaled Score Distribution")

    fig, ax = plt.subplots()
    ax.hist(results["scaled_score"], bins=20)
    ax.set_xlabel("Estimated Scaled Score")
    ax.set_ylabel("Simulation Count")
    ax.set_title("Simulated LSAT Score Distribution")

    st.pyplot(fig)

    st.subheader("Raw Simulation Results")
    st.dataframe(results)