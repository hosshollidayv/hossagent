"""Concrete, synthetic HossTracker stories for the public guided-demo surface."""

import json
from typing import Any

from hosstracker_scenario_dental import DENTAL_READINESS_SCENARIO
from hosstracker_scenario_healthcare import PRIOR_AUTHORIZATION_SCENARIO
from product_demos import PRODUCT_DEMOS

HOSSTRACKER_SCENARIOS: dict[str, dict[str, Any]] = {
    "public-records": PRODUCT_DEMOS["hosstracker"],
    "dental-readiness": DENTAL_READINESS_SCENARIO,
    "prior-authorization": PRIOR_AUTHORIZATION_SCENARIO,
}


def get_hosstracker_scenario(slug: str) -> dict[str, Any] | None:
    """Return one configured use-case story, or ``None`` for an unknown slug."""
    return HOSSTRACKER_SCENARIOS.get(slug)


def serialize_hosstracker_scenario(slug: str) -> str:
    """Serialize a scenario safely for an embedded JSON script element."""
    scenario = get_hosstracker_scenario(slug)
    if scenario is None:
        raise KeyError(slug)
    return json.dumps(scenario, separators=(",", ":")).replace("</", "<\\/")
