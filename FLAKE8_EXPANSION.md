# Flake8 Rules Expansion Plan

This document outlines our phased approach to expanding Flake8 rules as our codebase compliance improves.

## Current Configuration

Our current `.flake8` configuration includes the following error codes:

```
select = E1, E2, E3, E7, E9, F4, F63, F7, F82, W2, W3, W5
```

These focus on critical errors and basic formatting issues.

## Phase 1 Expansion (at 60% compliance)

When our overall compliance reaches 60%, we'll expand the Flake8 configuration to include:

```
select = E1, E2, E3, E7, E9, F4, F63, F7, F82, W1, W2, W3, W4, W5
```

### New Rules Included

#### W1: Indentation Warning
- `W191`: Indentation contains tabs
- `W191`: Indentation contains mixed spaces and tabs

#### W4: Line Break Warning
- `W405`: Duplicate top level import of a module
- `W191`: Indentation contains mixed spaces and tabs

### Benefits

These additional rules help detect:
- Inconsistent indentation issues
- Import duplications that could lead to confusion
- Mixed whitespace which can cause subtle bugs

## Phase 2 Expansion (at 70% compliance)

When reaching 70% compliance, we'll expand to include:

```
select = E1, E2, E3, E4, E5, E7, E9, F4, F63, F7, F82, W1, W2, W3, W4, W5
```

### New Rules Included

#### E4: Import Errors
- `E401`: Multiple imports on one line
- `E402`: Module level import not at top of file

#### E5: Line Length Errors
- `E501`: Line too long

### Benefits

These rules enforce:
- Proper import organization
- Reasonable line lengths for better readability

## Phase 3 Expansion (at 80% compliance)

At 80% compliance, we'll include the remaining important rules:

```
select = E, F, W
```

Which adds:

- All remaining E-prefixed errors
- All F-prefixed errors (logical/syntax errors)
- All W-prefixed warnings

### Exclusions

We'll continue to exclude the following, which conflict with Black:
```
ignore = E203, W503
```

## Implementation Process

1. **Each phase begins with a code assessment:**
   ```bash
   flake8 --select=<new_rules> --count src/ > phase_impact.txt
   ```

2. **Create detailed reports for major categories:**
   ```bash
   flake8 --select=<category> --statistics src/
   ```

3. **Document patterns and fixes for common issues**

4. **Use batch formatting where possible:**
   ```bash
   python tools/linting/batch_format_directory.py src/first1k/<module>
   ```

5. **Update GitHub Actions to use new rules**

6. **Track progress against expanded ruleset:**
   ```bash
   python tools/linting/track_progress.py --expanded-rules
   ```

## Expected Timeline

| Phase | Compliance Target | Expected Date | New Rules |
|-------|------------------|---------------|-----------|
| Current | 40.91% | - | E1,E2,E3,E7,E9,F4,F63,F7,F82,W2,W3,W5 |
| Phase 1 | 60% | Q3 2025 | + W1,W4 |
| Phase 2 | 70% | Q4 2025 | + E4,E5 |
| Phase 3 | 80% | Q1 2026 | All E,F,W (with exclusions) | 