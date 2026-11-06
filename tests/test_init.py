def test_vyapaar_strategies_import():
    import vyapaar_strategies

    assert vyapaar_strategies.__version__ == "0.1.0"
    assert vyapaar_strategies.TurtleBreakout is not None
    assert vyapaar_strategies.RiskParity is not None
