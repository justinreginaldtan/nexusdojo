"""Smoke tests for the generated script kata."""
import importlib

def test_main_executes() -> None:
    module = importlib.import_module("main")
    main_fn = getattr(module, "main", None)
    if callable(main_fn):
        main_fn()
