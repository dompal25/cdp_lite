SEGMENTS = {
    "active_high_value": {
        "type": "rule",
        "file": "src/cdp/segments/definitions/active_high_value.yaml"
    },
    "likely_to_buy_30d": {
        "type": "ml",
        "model": "data/artifacts/propensity_30d.joblib",
        "threshold": 0.6
    }
}
