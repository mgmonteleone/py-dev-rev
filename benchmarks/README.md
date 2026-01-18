# Performance Benchmarks

Performance benchmarking suite for the DevRev Python SDK.

## Overview

These benchmarks measure SDK performance in key areas:

- **HTTP Client**: Request/response overhead
- **Models**: Pydantic model serialization/deserialization
- **Pagination**: Memory and time efficiency for large datasets

## Requirements

```bash
pip install devrev-python-sdk[benchmark]
# or
pip install pytest-benchmark
```

## Running Benchmarks

```bash
# Run all benchmarks
pytest benchmarks/ --benchmark-only

# Run with detailed output
pytest benchmarks/ -v --benchmark-verbose

# Run specific benchmark
pytest benchmarks/bench_models.py --benchmark-only

# Save results to JSON
pytest benchmarks/ --benchmark-json=results.json

# Compare with previous run
pytest benchmarks/ --benchmark-compare
```

## Benchmark Files

| File | Description |
|------|-------------|
| `bench_models.py` | Model creation and serialization |
| `bench_http_client.py` | HTTP request/response overhead |
| `bench_pagination.py` | Pagination performance |
| `conftest.py` | Shared fixtures |

## Interpreting Results

```
--------------------------- benchmark: 3 tests --------------------------
Name                  Mean        StdDev     Median     Min        Max
------------------------------------------------------------------------
test_model_create    1.23μs      0.12μs     1.21μs    1.05μs    1.89μs
test_model_dump      2.45μs      0.23μs     2.41μs    2.11μs    3.12μs
test_model_parse     3.67μs      0.34μs     3.62μs    3.21μs    4.23μs
------------------------------------------------------------------------
```

- **Mean**: Average execution time
- **StdDev**: Standard deviation (lower = more consistent)
- **Median**: Middle value (less affected by outliers)

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Model creation | <5μs | Pydantic v2 is fast |
| Model serialization | <10μs | With validation |
| HTTP overhead | <1ms | Connection pooling |
| Pagination (1000 items) | <100ms | Memory-efficient |

## Continuous Benchmarking

Benchmarks can be integrated into CI:

```yaml
- name: Run benchmarks
  run: pytest benchmarks/ --benchmark-json=output.json

- name: Compare with baseline
  run: pytest-benchmark compare baseline.json output.json
```

