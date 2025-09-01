import pytest
import os


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "manual: marks tests as manual (deselect with '-m \"not manual\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically skip manual tests unless explicitly requested."""
    # Check if we're explicitly running manual tests
    markexpr = config.getoption("-m", default="")
    run_manual_env = os.getenv("RUN_MANUAL_TESTS", "").lower() in ("1", "true", "yes")
    
    # If we're explicitly asking for manual tests, don't skip them
    if "manual" in markexpr or run_manual_env:
        return
    
    # If we're explicitly excluding manual tests, let pytest handle it
    if "not manual" in markexpr:
        return
    
    # Check if we're running specific tests (like from VS Code test explorer)
    # If only one item is collected and it's a manual test, allow it to run
    if len(items) == 1 and "manual" in items[0].keywords:
        return
    
    # Check if we're running a small subset of tests that are all manual
    manual_items = [item for item in items if "manual" in item.keywords]
    if len(items) <= 5 and len(manual_items) == len(items):
        return
    
    # Otherwise, automatically skip manual tests when running larger test suites
    skip_manual = pytest.mark.skip(reason="Manual test - use 'pytest -m manual' or set RUN_MANUAL_TESTS=1")
    for item in items:
        if "manual" in item.keywords:
            item.add_marker(skip_manual)
