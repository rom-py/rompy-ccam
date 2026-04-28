from importlib.metadata import entry_points


def test_config_entrypoint():
    eps = entry_points(group="rompy.config")
    names = [ep.name for ep in eps]
    assert "ccam" in names
