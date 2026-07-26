#!/usr/bin/env bash
# Clone each fixture, run all rules, compare findings to expected.
# Exits non-zero if any fixture deviates from expected.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES_DIR="$REPO_ROOT/fixtures/_cloned"
MANIFEST="$REPO_ROOT/fixtures/manifest.yaml"
SGCONFIG="$REPO_ROOT/sgconfig.yml"

mkdir -p "$FIXTURES_DIR"

# Require ast-grep + yq + jq
for tool in ast-grep yq jq git; do
    command -v "$tool" >/dev/null 2>&1 || {
        echo "ERROR: $tool not installed"
        exit 1
    }
done

fail_count=0
pass_count=0

# Read fixture names
fixture_names=$(yq -r '.fixtures[].name' "$MANIFEST")

for name in $fixture_names; do
    echo ""
    echo "=== Fixture: $name ==="

    source=$(yq -r ".fixtures[] | select(.name == \"$name\") | .source" "$MANIFEST")
    pin_ref=$(yq -r ".fixtures[] | select(.name == \"$name\") | .pin_ref" "$MANIFEST")
    classification=$(yq -r ".fixtures[] | select(.name == \"$name\") | .classification" "$MANIFEST")

    # pin_ref is a full commit SHA (enforced below), so we cannot use
    # `git clone --branch` (refs only) or `git reset --hard origin/$pin_ref`
    # (no such remote-tracking ref). Fetch the single commit by SHA instead —
    # GitHub serves reachable-SHA fetches, so this stays a shallow, cheap fetch.
    case "$pin_ref" in
        [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*)
            [ "${#pin_ref}" -eq 40 ] || {
                echo "  ERROR: pin_ref for '$name' must be a full 40-char commit SHA (got '$pin_ref')"
                exit 1
            }
            ;;
        *)
            echo "  ERROR: pin_ref for '$name' must be a commit SHA, not a branch ('$pin_ref')."
            echo "         A branch-pinned corpus cannot attribute a findings change to a rule change."
            exit 1
            ;;
    esac

    target_dir="$FIXTURES_DIR/$name"
    if [ ! -d "$target_dir/.git" ]; then
        echo "  Initialising $name from $source @ ${pin_ref:0:12}..."
        git init -q "$target_dir"
        git -C "$target_dir" remote add origin "$source"
    fi
    if [ "$(git -C "$target_dir" rev-parse HEAD 2>/dev/null)" = "$pin_ref" ]; then
        echo "  Already at ${pin_ref:0:12}"
    else
        echo "  Fetching ${pin_ref:0:12}..."
        git -C "$target_dir" fetch -q --depth 1 origin "$pin_ref" 2>&1 | tail -2
        git -C "$target_dir" checkout -q --detach FETCH_HEAD 2>&1 | tail -1
    fi

    # Run ast-grep
    findings_json="$FIXTURES_DIR/${name}-findings.json"
    ast-grep scan --json --config "$SGCONFIG" "$target_dir" 2>/dev/null > "$findings_json" || true

    # Aggregate findings by rule_id
    actual=$(jq -r 'group_by(.ruleId) | map({(.[0].ruleId): length}) | add // {}' "$findings_json")

    # Compare to expected
    expected=$(yq -o=json ".fixtures[] | select(.name == \"$name\") | .expected_findings // {}" "$MANIFEST")

    echo "  Classification: $classification"
    echo "  Expected: $expected"
    echo "  Actual:   $actual"

    if [ "$(echo "$actual" | jq -S .)" = "$(echo "$expected" | jq -S .)" ]; then
        echo "  ✓ PASS"
        pass_count=$((pass_count + 1))
    else
        echo "  ✗ FAIL — findings differ from expected"
        echo "  Diff:"
        diff <(echo "$expected" | jq -S .) <(echo "$actual" | jq -S .) || true
        fail_count=$((fail_count + 1))
    fi
done

echo ""
echo "===================="
echo "Pass: $pass_count"
echo "Fail: $fail_count"
echo "===================="

if [ "$fail_count" -gt 0 ]; then
    exit 1
fi
