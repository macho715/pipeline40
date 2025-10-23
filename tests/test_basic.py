import importlib

def test_scaffold_exists():
    m = importlib.import_module('src.core.app'.replace('/', '.'))
    assert hasattr(m, 'run')

def test_app_runs():
    from src.core.app import run
    assert run() == 'ok'
