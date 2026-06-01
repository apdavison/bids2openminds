from ancpbids import model_latest as _schema
from bids2openminds import mapping


def test_techniques_covers_all_schema_suffixes():
    techniques = mapping.build_techniques_mapping(_schema)
    missing = [e.value["value"] for e in _schema.SuffixEnum if e.value["value"] not in techniques]
    assert not missing, f"Suffixes missing from MAP_2_TECHNIQUES: {missing}"


def test_experimental_approaches_covers_all_schema_datatypes():
    approaches = mapping.build_approaches_mapping(_schema)
    missing = [e.value["value"] for e in _schema.DatatypeEnum if e.value["value"] not in approaches]
    assert not missing, f"Datatypes missing from MAP_2_EXPERIMENTAL_APPROACHES: {missing}"
