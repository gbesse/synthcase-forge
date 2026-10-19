"""Constraint-derived synthetic cohorts and independently verified counterfactuals."""

from .engine import generate, counterfactual, verify_row

__all__ = ["generate", "counterfactual", "verify_row"]
