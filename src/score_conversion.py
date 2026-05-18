def estimate_scaled_score(raw_score: int, total_questions: int = 77) -> int:
    """
    Estimate LSAT scaled score from raw score using an approximate
    post-Logic-Games LSAT conversion table.

    This follows the LSAT Demon-style idea:
    raw score -> percent correct -> scaled score estimate.

    Replace this later with PrepTest-specific official conversion tables.
    """
    percent_correct = raw_score / total_questions

    conversion_table = [
        (0.975, 180),
        (0.950, 178),
        (0.925, 176),
        (0.900, 173),
        (0.875, 171),
        (0.850, 168),
        (0.825, 166),
        (0.800, 164),
        (0.775, 162),
        (0.750, 160),
        (0.725, 158),
        (0.700, 156),
        (0.675, 154),
        (0.650, 152),
        (0.625, 150),
        (0.600, 148),
        (0.575, 146),
        (0.550, 144),
        (0.525, 142),
        (0.500, 140),
        (0.450, 137),
        (0.400, 134),
        (0.350, 131),
        (0.300, 128),
        (0.250, 125),
        (0.000, 120),
    ]

    for minimum_percent_correct, scaled_score in conversion_table:
        if percent_correct >= minimum_percent_correct:
            return scaled_score

    return 120