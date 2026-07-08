"""Release-level configuration for the public certificate package.

This module is the single source of truth for release metadata and the
certified decimal threshold used by the public verifier. Functional replay
modules import these values instead of carrying hard-coded release constants.
"""
from __future__ import annotations

from decimal import Decimal

PACKAGE_NAME = "lebesgue-universal-cover-new-lower-bound-certificate"
"""Canonical Python package/distribution name used in ``pyproject.toml``."""

RELEASE_VERSION = "0.15.4"
"""Canonical release version used by packaging metadata and citation files."""

RELEASE_TAG = f"v{RELEASE_VERSION}"
"""Human-readable release tag used in release notes and README files."""

CERTIFIED_THRESHOLD_TEXT = "0.833"
"""Exact decimal threshold certified by the bundled finite records."""

CERTIFIED_THRESHOLD = Decimal(CERTIFIED_THRESHOLD_TEXT)
"""Decimal representation of the certified threshold for numeric checks."""

CLAIM_SCOPE = "normalized convex Brass-Sharifi three-test-set certificate model"
"""Public claim boundary for the certified lower-bound statement."""

PAPER_TITLE = "A Certified Lower Bound for Lebesgue's Universal Cover Problem"
"""Canonical paper title used by LaTeX, citation metadata, and README checks."""

REQUIRES_PYTHON = ">=3.10"
"""Python version constraint supported by the public verifier."""

RUNTIME_DEPENDENCIES = ("loguru>=0.7.0",)
"""Runtime dependencies required by the public command-line verifier."""
