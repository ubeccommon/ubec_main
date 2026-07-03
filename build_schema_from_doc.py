#!/usr/bin/env python3
"""Reconstruct PostgreSQL DDL for a schema from the UBEC comprehensive
database documentation markdown.

This parser emits ONLY what the documentation records: schemas, sequences,
tables (columns, types, nullability, defaults), primary keys, unique
constraints, foreign keys, check constraints, and btree/gin indexes.

It CANNOT and does not invent: custom type (enum/composite) definitions,
function bodies, view SQL, or row data. Those are not present in the source
document. Custom-typed columns are reconstructed as `text` and array columns as
`text[]`, each flagged in the output, because their true definitions are absent.

Usage:
    python3 build_schema_from_doc.py <doc.md> <schema_name> > schema.sql

License (code): GNU Affero General Public License v3.0
Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import re
import sys
from typing import List, Tuple, Optional


# --- Type mapping ------------------------------------------------------------
_SIMPLE_TYPES = {
    "integer(32)": "integer",
    "bigint(64)": "bigint",
    "smallint(16)": "smallint",
    "timestamp with time zone": "timestamptz",
    "timestamp without time zone": "timestamp",
    "boolean": "boolean",
    "text": "text",
    "date": "date",
    "interval": "interval",
    "jsonb": "jsonb",
    "json": "json",
    "uuid": "uuid",
    "double precision": "double precision",
    "real": "real",
    "bytea": "bytea",
    "inet": "inet",
}


def map_type(raw: str) -> Tuple[str, Optional[str]]:
    """Map a documented type to a concrete PostgreSQL type.

    Returns (pg_type, note) where note is a non-fatal fidelity warning or None.
    """
    t = raw.strip()
    if t in _SIMPLE_TYPES:
        return _SIMPLE_TYPES[t], None
    m = re.match(r"character varying\((\d+)\)$", t)
    if m:
        return f"varchar({m.group(1)})", None
    if t == "character varying":
        return "varchar", None
    m = re.match(r"character\((\d+)\)$", t)
    if m:
        return f"char({m.group(1)})", None
    if re.match(r"numeric(\(\d+(,\d+)?\))?$", t):
        return t, None
    if t == "USER-DEFINED":
        return "text", "USER-DEFINED custom type reconstructed as text"
    if t == "ARRAY":
        return "text[]", "ARRAY element type unknown; reconstructed as text[]"
    return "text", f"unrecognised type '{t}' reconstructed as text"


_CAST_RE = re.compile(r"::\"?[A-Za-z_][A-Za-z0-9_]*\"?(\[\])?")


def sanitise_default(default: str, downgraded: bool) -> Optional[str]:
    """Clean a documented DEFAULT. Strip casts to custom types when the column
    was downgraded to text/text[] so the default does not reference a missing
    type. Return None if there is no usable default."""
    d = default.strip()
    if not d:
        return None
    if downgraded:
        # e.g. 'network_node'::holonic_category -> 'network_node'
        d = _CAST_RE.sub("", d).strip()
    return d or None


# --- Parsing helpers ---------------------------------------------------------
def extract_schema_block(text: str, schema: str) -> str:
    """Return the markdown block for `## {schema}` up to the next `## ` heading."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == f"## {schema}":
            start = i
            break
    if start is None:
        sys.exit(f"Schema section '## {schema}' not found in document.")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## ") and not lines[j].startswith("### "):
            end = j
            break
    return "\n".join(lines[start:end])


def split_subsections(block: str, level: str) -> List[Tuple[str, str]]:
    """Split a block into (title, body) pairs at the given heading level
    (e.g. '#### ')."""
    lines = block.splitlines()
    out, title, buf = [], None, []
    for ln in lines:
        if ln.startswith(level) and not ln.startswith(level + "#"):
            if title is not None:
                out.append((title, "\n".join(buf)))
            title = ln[len(level):].strip()
            buf = []
        elif title is not None:
            buf.append(ln)
    if title is not None:
        out.append((title, "\n".join(buf)))
    return out


def isolate_region(block: str, header: str) -> str:
    """Return the text of a `### {header}` region within a schema block."""
    lines = block.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == f"### {header}":
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("### "):
            end = j
            break
    return "\n".join(lines[start:end])


def parse_columns(body: str) -> List[dict]:
    """Parse the `**Columns:**` markdown table into column dicts."""
    cols, in_tbl = [], False
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith("**Columns:**"):
            in_tbl = True
            continue
        if in_tbl:
            if s.startswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if len(cells) < 4:
                    continue
                if cells[0].lower() == "column" or set(cells[0]) <= {"-"}:
                    continue
                # Some columns carry an inline italic description:
                #   `colname *(human description)*` — keep only the identifier.
                clean_name = re.split(r"\s+\*\(", cells[0])[0].strip().strip("*` ")
                cols.append({
                    "name": clean_name,
                    "type": cells[1],
                    "nullable": cells[2],
                    "default": cells[3],
                })
            elif s.startswith("**"):
                break
    return cols


def parse_bullet_region(body: str, header: str) -> List[str]:
    """Return bullet lines under a `**{header}**` label until the next label."""
    out, active = [], False
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith(f"**{header}"):
            active = True
            continue
        if active:
            if s.startswith("**"):
                break
            if s.startswith("- "):
                out.append(s[2:].strip())
            elif s.startswith("-"):
                out.append(s[1:].strip())
    return out


# --- DDL emission ------------------------------------------------------------
def qi(ident: str) -> str:
    """Quote an identifier."""
    return '"' + ident.replace('"', '""') + '"'


def build(doc_path: str, schema: str) -> str:
    text = open(doc_path, encoding="utf-8").read()
    block = extract_schema_block(text, schema)

    out: List[str] = []
    warn: List[str] = []
    out.append("-- ============================================================")
    out.append(f"-- Reconstructed DDL for schema '{schema}'")
    out.append("-- Source: comprehensive database documentation (structure only)")
    out.append("-- Generated by build_schema_from_doc.py")
    out.append("--")
    out.append("-- License (code): GNU AGPL v3.0")
    out.append("-- This project uses the services of Claude and Anthropic PBC to")
    out.append("-- inform our decisions and recommendations.")
    out.append("-- ============================================================")
    out.append("")
    out.append("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    out.append('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    out.append(f"CREATE SCHEMA IF NOT EXISTS {qi(schema)};")
    out.append(f"SET search_path TO {qi(schema)}, public;")
    out.append("")

    # Sequences
    seq_region = isolate_region(block, "Sequences")
    seqs = [t for t, _ in split_subsections(seq_region, "#### ")]
    if seqs:
        out.append("-- Sequences")
        for name in seqs:
            out.append(f"CREATE SEQUENCE IF NOT EXISTS {qi(schema)}.{qi(name)};")
        out.append("")

    # Tables
    tbl_region = isolate_region(block, "Tables")
    tables = split_subsections(tbl_region, "#### ")

    fk_stmts: List[str] = []
    idx_stmts: List[str] = []

    for tname, body in tables:
        cols = parse_columns(body)
        if not cols:
            continue
        col_lines = []
        for c in cols:
            pgtype, note = map_type(c["type"])
            downgraded = note is not None and (
                "USER-DEFINED" in note or "ARRAY" in note or "unrecognised" in note
            )
            if note:
                warn.append(f"{schema}.{tname}.{c['name']}: {note}")
            parts = [f"    {qi(c['name'])} {pgtype}"]
            if c["nullable"] == "\u2717":  # ✗ => NOT NULL
                parts.append("NOT NULL")
            dflt = sanitise_default(c["default"], downgraded)
            if dflt:
                parts.append(f"DEFAULT {dflt}")
            col_lines.append(" ".join(parts))

        # Primary key -> inline
        pk_cols = None
        for pk in parse_bullet_region(body, "Primary Key"):
            m = re.search(r"\(([^)]*)\)", pk)
            if m:
                pk_cols = [x.strip() for x in m.group(1).split(",")]
        table_constraints = []
        if pk_cols:
            table_constraints.append(
                "    PRIMARY KEY (" + ", ".join(qi(c) for c in pk_cols) + ")"
            )

        # Unique constraints -> inline
        for uq in parse_bullet_region(body, "Unique Constraints"):
            m = re.search(r"\(([^)]*)\)", uq)
            if m:
                ucols = [x.strip() for x in m.group(1).split(",")]
                table_constraints.append(
                    "    UNIQUE (" + ", ".join(qi(c) for c in ucols) + ")"
                )

        # Check constraints -> inline (verbatim expression)
        for ck in parse_bullet_region(body, "Check Constraints"):
            m = re.match(r"(\S+):\s*CHECK\s*(\(.*\))\s*$", ck)
            if m:
                table_constraints.append(f"    CHECK {m.group(2)}")

        all_lines = col_lines + table_constraints
        out.append(f"CREATE TABLE IF NOT EXISTS {qi(schema)}.{qi(tname)} (")
        out.append(",\n".join(all_lines))
        out.append(");")
        out.append("")

        # Foreign keys -> deferred ALTERs
        for fk in parse_bullet_region(body, "Foreign Keys"):
            m = re.search(
                r":\s*\(([^)]*)\)\s*\u2192\s*([A-Za-z0-9_\.]+)\(([^)]*)\)", fk
            )
            if m:
                lcols = ", ".join(qi(x.strip()) for x in m.group(1).split(","))
                target = m.group(2)
                tcols = ", ".join(qi(x.strip()) for x in m.group(3).split(","))
                # qualify target schema.table with quoting
                if "." in target:
                    ts, tt = target.split(".", 1)
                    tgt = f"{qi(ts)}.{qi(tt)}"
                else:
                    tgt = f"{qi(schema)}.{qi(target)}"
                fk_stmts.append(
                    f"ALTER TABLE {qi(schema)}.{qi(tname)} "
                    f"ADD FOREIGN KEY ({lcols}) REFERENCES {tgt} ({tcols});"
                )

        # Indexes -> btree/gin only (gist needs postgis; skip, note it)
        for idx in parse_bullet_region(body, "Indexes"):
            if idx.startswith("PRIMARY") or idx.startswith("UNIQUE"):
                continue  # already covered by constraints
            m = re.match(r"(BTREE|GIN|GIST|HASH|BRIN):\s*\(([^)]*)\)", idx)
            if not m:
                continue
            method, cols_s = m.group(1), m.group(2)
            icols = ", ".join(qi(x.strip()) for x in cols_s.split(","))
            if method == "GIST":
                warn.append(f"{schema}.{tname}: GIST index on ({cols_s}) omitted "
                            f"(needs original operator class / postgis)")
                continue
            idx_stmts.append(
                f"CREATE INDEX IF NOT EXISTS "
                f"{qi('ix_' + tname + '_' + re.sub(r'[^A-Za-z0-9]+', '_', cols_s))} "
                f"ON {qi(schema)}.{qi(tname)} USING {method.lower()} ({icols});"
            )

    if fk_stmts:
        out.append("-- Foreign keys (added after all tables exist)")
        out.extend(fk_stmts)
        out.append("")
    if idx_stmts:
        out.append("-- Secondary indexes (btree/gin)")
        out.extend(idx_stmts)
        out.append("")

    out.append("-- ============================================================")
    out.append(f"-- Reconstruction notes ({len(warn)} fidelity flags)")
    out.append("-- NOT reconstructed from this document (absent in source):")
    out.append("--   * custom type / enum definitions  * function bodies")
    out.append("--   * view definitions               * trigger creation")
    out.append("--   * row data (incl. system_configuration seed)")
    out.append("-- ------------------------------------------------------------")
    for w in warn:
        out.append(f"-- FLAG: {w}")
    out.append("-- ============================================================")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: build_schema_from_doc.py <doc.md> <schema_name>")
    sys.stdout.write(build(sys.argv[1], sys.argv[2]))
