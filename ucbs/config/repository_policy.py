"""Repository-layout and public-narrative policy for release checks."""
from __future__ import annotations

import re

ALLOWED_RAW_STAGE_FILES = frozenset({
    "docs/artifact_structure.md",
    "docs/data_dictionary.md",
    "docs/faq.md",
    "certificate/public/CERTIFICATE_INDEX.md",
})
"""Public docs allowed to mention raw v133--v136 provenance labels."""

RAW_STAGE_PATTERN = re.compile(r"\bv13[3-6]\b", re.IGNORECASE)
"""Pattern for raw internal generation-stage labels preserved only for provenance."""

REQUIRED_REPOSITORY_PATHS = (
    "README.md",
    "README.zh-CN.md",
    "CITATION.cff",
    "LICENSE",
    "RELEASE_NOTES.md",
    "pyproject.toml",
    "requirements.txt",
    "ucbs",
    "ucbs/config",
    "ucbs/certificate",
    "ucbs/verification",
    "ucbs/cli",
    "scripts",
    "scripts/_bootstrap.py",
    "scripts/verify_certificate.py",
    "scripts/check_repository.py",
    "scripts/replay_certificate_chain.py",
    "scripts/replay_per_record_evidence.py",
    "scripts/replay_construction_audit.py",
    "scripts/replay_witness_construction.py",
    "scripts/replay_final_adjudication.py",
    "certificate/final_chain",
    "certificate/manifest",
    "certificate/public",
    "docs/artifact_policy.md",
    "docs/claim_scope.md",
    "docs/release_audit.md",
    "docs/reviewer_checklist.md",
    "docs/expected_outputs.md",
    "docs/reproducibility.md",
    "docs/data_dictionary.md",
    "docs/artifact_structure.md",
    "docs/verification_design.md",
    "certificate/manifest/CHECKSUM.md",
    "certificate/public/CERTIFICATE_INDEX.md",
    "paper",
    "paper/A_Certified_Lower_Bound_for_Lebesgues_Universal_Cover_Problem.pdf",
    "paper/source/main.tex",
    "paper/source/macros.tex",
    "paper/source/figures/fig_placement.tex",
    "tests",
)
"""Required paths for the public repository layout."""

FORBIDDEN_REPOSITORY_PATHS = (
    "release",
    "scripts/stages",
    "ucbs/pipeline",
    "ucbs/target_083201",
    "ucbs/legacy_bs0832",
    "certificate/target_083201",
    "certificate/legacy_bs0832",
    "paper/preview",
    "paper/pdf",
    "certificate/public/README.md",
    "scripts/make_release_zip.py",
    "ucbs/cli/make_release_zip.py",
    "scripts/verify_theorem_ready.py",
    "scripts/replay_inner_witness_certificate.py",
)
"""Forbidden stale or internal paths in the public repository layout."""


FORBIDDEN_BYTECODE_DIRECTORY_NAMES = frozenset({"__pycache__"})
"""Directory names that must not appear in the public release archive."""

FORBIDDEN_BYTECODE_SUFFIXES = (".pyc", ".pyo", ".pyd")
"""Compiled Python artifact suffixes forbidden in the public release archive."""

FORBIDDEN_GENERATED_FILE_SUFFIXES = (
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".run.xml",
    ".synctex.gz",
    ".toc",
)
"""Generated LaTeX/build artifact suffixes forbidden in the release tree."""

TEXT_FILE_SUFFIXES_REQUIRING_FINAL_NEWLINE = frozenset({
    ".cff",
    ".csv",
    ".json",
    ".md",
    ".py",
    ".tex",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
})
"""Text suffixes that must end with a newline in the release archive."""

TEXT_FILE_NAMES_REQUIRING_FINAL_NEWLINE = frozenset({"LICENSE", "requirements.txt"})
"""Text filenames without distinctive suffixes that must end with a newline."""

PUBLIC_SANITIZATION_PATTERNS = (
    (re.compile(r"[A-Za-z]:\\"), "Windows absolute path"),
    (re.compile(r"\\Users\\|/Users/"), "user-home absolute path"),
    (re.compile(r"local_runner", re.I), "local runner label"),
    (re.compile(r"local-default", re.I), "local workload label"),
    (re.compile(r"feedback_zip_path", re.I), "machine-local feedback path field"),
    (re.compile(r"log_path", re.I), "machine-local log path field"),
    (re.compile(r"v144_feedback_zip", re.I), "pre-release feedback path field"),
)
"""Patterns forbidden in public status and report files."""


INLINE_CODE_PATTERN = re.compile(r"`[^`]*`")
"""Inline-code span pattern shared by public Markdown linters."""

MARKDOWN_FENCE_PATTERN = re.compile(r"(^```([^\n`]*)\n)(.*?)(^```\s*$)", re.DOTALL | re.MULTILINE)
"""Fenced-code pattern used to distinguish Markdown prose from code blocks."""

MARKDOWN_BAD_TEXT_PATTERNS = (
    (re.compile(r"\\\([^\n]*?\\\)"), "non-GitHub inline math delimiter"),
    (re.compile(r"\\\[[\s\S]*?\\\]"), "non-GitHub display math delimiter"),
    (re.compile(r"\$\$"), "display math should use fenced math block"),
    (re.compile(r"\$`"), "backtick math marker"),
    (re.compile(r"`\$"), "backtick math marker"),
    (re.compile(r"\bOmega_(adm|B|r)\b"), "plain-text Omega symbol"),
    (re.compile(r"\balpha_cvx\b"), "plain-text alpha symbol"),
    (re.compile(r"\bconv\s+Q\b"), "plain-text convex hull expression"),
    (re.compile(r"\bunion_r\b"), "plain-text union expression"),
    (re.compile(r"(?<!\\)\bsubset\b"), "plain-text subset relation"),
)
"""Public Markdown prose patterns that are not GitHub-safe mathematics."""

MARKDOWN_BAD_MATH_BLOCK_PATTERNS = (
    (re.compile(r"\\operatorname\b"), "operatorname is not GitHub-safe in README math"),
    (re.compile(r"\$\$"), "nested display math marker inside fenced math block"),
    (re.compile(r"\\mathcal\s+[A-Za-z]"), "mathcal should use braces in README math"),
    (re.compile(r"\\mathrm\{[^}]*\s+[^}]*\}"), "mathrm should not contain spaced letters in README math"),
)
"""Patterns disallowed inside public fenced math blocks."""

NARRATIVE_FORBIDDEN_PATTERNS = (
    (re.compile(r"\blegacy\b", re.I), "legacy storyline wording"),
    (re.compile(r"\breproduction\b", re.I), "reproduction storyline wording"),
    (re.compile(r"\bbaseline\b", re.I), "baseline storyline wording"),
    (re.compile(r"\binherited\b", re.I), "inherited-component storyline wording"),
    (re.compile(r"\bold\s+(replay|certificate|threshold|project)\b", re.I), "old-certificate storyline wording"),
    (re.compile(r"\bprevious\s+(certificate|threshold|project|reproduction)\b", re.I), "previous-certificate storyline wording"),
    (re.compile(r"\bbs[-_]?0832\b", re.I), "BS0832 storyline label"),
    (re.compile(r"\btarget_083201\b", re.I), "threshold-specific directory name"),
    (re.compile(r"\bproof-ready\b", re.I), "nonstandard proof-ready wording"),
    (re.compile(r"\btheorem-ready\b", re.I), "internal theorem-ready wording"),
    (re.compile(r"\bkernel\b", re.I), "code-flavored kernel wording"),
    (re.compile(r"verify_theorem_ready\.py", re.I), "removed command name"),
    (re.compile(r"replay_inner_witness_certificate\.py", re.I), "removed command name"),
)
"""Forbidden narrative fragments for public Markdown and certificate notes."""

CLAIM_FORBIDDEN_PATTERNS = (
    re.compile(r"\bsolves?\s+the\s+(full\s+)?Lebesgue\s+universal\s+cover\s+problem\b", re.I),
    re.compile(r"\b(full\s+)?Lebesgue\s+universal\s+cover\s+problem\s+(is\s+)?(solved|resolved)\b", re.I),
    re.compile(r"\bunrestricted\s+nonconvex\s+lower\s+bound\s+(is\s+)?(proved|established|completed)\b", re.I),
    re.compile(r"\bnonconvex\s+lower\s+bound\s+(is\s+)?(proved|established|completed)\b", re.I),
    re.compile(r"\bbranch[- ]a\s+(is\s+)?closed\b", re.I),
    re.compile(r"\bproof[- ]assistant\s+formalization\s+(is\s+)?(completed|done|proved)\b", re.I),
    re.compile(r"\bindependent\s+external\s+verification\s+(is\s+)?(completed|done)\b", re.I),
    re.compile(r"\u89e3\u51b3.*\u975e\u51f8"),
    re.compile(r"\u975e\u51f8.*\u4e0b\u754c.*(\u8bc1\u660e|\u5b8c\u6210|\u89e3\u51b3)"),
    re.compile(r"Branch[- ]?(A|a).*(\u95ed\u5408|\u5b8c\u6210)"),
    re.compile(r"\u5916\u90e8.*\u72ec\u7acb.*\u9a8c\u8bc1.*\u5b8c\u6210"),
    re.compile(r"\u5f62\u5f0f\u5316.*\u8bc1\u660e.*\u5b8c\u6210"),
    re.compile(r"\u5b8c\u6574.*Lebesgue.*\u4e07\u6709\u8986\u76d6.*(\u89e3\u51b3|\u5b8c\u6210)"),
    re.compile(r"\u5b8c\u6574.*\u52d2\u8d1d\u683c.*\u4e07\u6709\u8986\u76d6.*(\u89e3\u51b3|\u5b8c\u6210)"),
)
"""Forbidden positive-claim patterns outside explicit non-claim contexts."""

PAPER_REQUIRED_SCOPE_PATTERNS = (
    re.compile(r"\bconvex\b", re.I),
    re.compile(r"Brass--Sharifi|Brass[–-]Sharifi", re.I),
    re.compile(r"three-test-set", re.I),
    re.compile(r"certificate", re.I),
    re.compile(r"not a statement about the unrestricted nonconvex problem", re.I),
    re.compile(r"not a proof-assistant formalization", re.I),
)
"""Scope-boundary phrases expected in the LaTeX paper source."""

CLAIM_NEGATION_MARKERS = (
    "does not claim",
    "does not assert",
    "not claimed",
    "not assert",
    "not a claim",
    "no claim",
    "do not",
    "neither",
    "remain false",
    "\u4e0d\u58f0\u79f0",
    "\u6ca1\u6709",
    "\u5e76\u975e",
    "\u4e0d\u662f",
    "\u4e0d\u4e3b\u5f20",
    "\u4e0d\u5ba3\u79f0",
    "\u662f\u5426",
)
"""Negation markers that identify explicit scope-boundary statements."""
