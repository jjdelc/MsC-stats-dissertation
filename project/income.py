"""
Functions to compute the poverty lines for the ENAHO dataset.
"""
import pandas as pd
import numpy as np

EXTREME_POVERTY_BY_DOMINIO = {
    1: [152, 156, 163, 171, 171, 174, 180, 190, 215, 240],
    2: [134, 139, 144, 151, 150, 153, 157, 166, 191, 212],
    3: [148, 154, 161, 165, 167, 172, 173, 181, 204, 228],
    4: [139, 145, 153, 156, 157, 161, 163, 172, 196, 217],
    5: [158, 168, 175, 179, 180, 185, 190, 202, 224, 244],
    6: [132, 136, 142, 145, 146, 151, 153, 162, 184, 203],
    7: [193, 204, 213, 221, 220, 224, 228, 239, 266, 294],
}

POVERTY_BY_DOMINIO = {
    1: [304, 314, 326, 339, 344, 351, 361, 381, 420, 451],
    2: [245, 253, 261, 271, 275, 280, 288, 304, 338, 364],
    3: [270, 279, 290, 298, 304, 312, 316, 331, 364, 392],
    4: [225, 234, 245, 250, 253, 260, 264, 278, 310, 334],
    5: [283, 294, 305, 311, 315, 324, 332, 353, 386, 410],
    6: [219, 225, 233, 238, 242, 249, 253, 268, 298, 319],
    7: [383, 399, 416, 428, 433, 441, 449, 470, 510, 546],
}


def poverty_cut(thresholds, year, domain):
    pos = 9 - (2023 - int(year))
    try:
        return thresholds[domain][pos]
    except (IndexError, KeyError):
        return None


def poor_classifier(income, extreme_poor_cut, poor_cut):
    """
    Returns the classification of poorness:
        1. Extreme poor
        2. Poor
        3. Not poor
    """
    if income <= extreme_poor_cut:
        return 1
    elif income <= poor_cut:
        return 2
    else:
        return 3


def compute_domain_inei(df):
    # For DOMINIO, we want to split the way that the INEI data is split
    # by region and rural, rather than North/Center/South.
    _D, _R = df["DOMINIO"], df["RURAL"]
    conditions = [
        # Costa Urbana
        ~_R & ((_D == 1) | (_D == 2) | (_D == 3)),
        # Costa Rural
        _R & ((_D == 1) | (_D == 2) | (_D == 3)),
        # Sierra Urbana
        ~_R & ((_D == 4) | (_D == 5) | (_D == 6)),
        # Sierra Rural
        _R & ((_D == 4) | (_D == 5) | (_D == 6)),
        # Selva Urbana
        ~_R & (_D == 7),
        # Selva Rural
        _R & (_D == 7),
        # Lima metropolitana
        _D == 8,
    ]
    choices = [1, 2, 3, 4, 5, 6, 7]
    # df["DOMINIO_INEI"] = df.select(conditions, choices, default=0)
    return np.select(conditions, choices, default=0)


MONTHLY_INCOME_COLUMN = "P530A"


def compute_poverty_thresholds(df):
    domain = compute_domain_inei(df)
    df["INEI"] = domain
    extreme_poverty_line = df.apply(
        lambda row: poverty_cut(EXTREME_POVERTY_BY_DOMINIO, row["AÑO"], row["INEI"]),
        axis=1)
    poverty_line = df.apply(
        lambda row: poverty_cut(POVERTY_BY_DOMINIO, row["AÑO"], row["INEI"]),
        axis=1)
    df["EXTREME_POVERTY_CUT"] = extreme_poverty_line
    df["POVERTY_CUT"] = poverty_line
    df["POORNESS"] = df.apply(
        lambda row: poor_classifier(row[MONTHLY_INCOME_COLUMN], row["EXTREME_POVERTY_CUT"], row["POVERTY_CUT"]),
        axis=1)
    return df

