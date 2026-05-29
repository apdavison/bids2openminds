"""Validation tests for the BIDS -> openMINDS v5 neuroimaging mappings.

These check that the mapping data added to ``mapping.py`` stays consistent with
both sides it bridges:

* every openMINDS term name resolves via ``by_name()`` against the v5
  controlled-term classes (catches typos / renamed instances), and
* every value of the closed BIDS enums is covered (catches BIDS spec drift).

The mappings themselves are data only; the object-creation code that will consume
them is a separate, later step, so nothing here exercises object creation.
"""

import pytest

import openminds.v5.controlled_terms as ct
import openminds.v5.neuroimaging as ni
from bidsschematools import schema as bst

from bids2openminds import mapping


_BIDS_SCHEMA = bst.load_schema()


def _bids_enum(field):
    """Return the list of allowed values for a closed BIDS metadata enum."""
    return _BIDS_SCHEMA.objects.metadata[field]["enum"]


# --- Term resolution: every mapped name must exist in v5 controlled_terms ----

# (mapping dict, controlled-term class) pairs whose values are term names.
_NAME_MAPS = [
    (mapping.MAP_2_MRI_WEIGHTING, ct.MRIWeighting),
    (mapping.MAP_2_MT_PULSE_SHAPE, ct.PulseShape),
    (mapping.MAP_2_MRI_SPOILING_TECHNIQUE, ct.MRISpoilingTechnique),
    (mapping.MAP_2_MRI_PARALLEL_ACQUISITION_TECHNIQUE, ct.MRIParallelAcquisitionTechnique),
    (mapping.MAP_2_MRI_SPATIAL_ENCODING, ct.SpatialEncoding),
    (mapping.MAP_2_CONTRAST_AGENT, ct.MolecularEntity),
]


@pytest.mark.parametrize(
    "name, term_class",
    [
        (name, term_class)
        for mapping_dict, term_class in _NAME_MAPS
        for name in mapping_dict.values()
        if name is not None
    ],
)
def test_term_names_resolve(name, term_class):
    assert term_class.by_name(name).name == name


# --- BIDS enum coverage: every (meaningful) enum value must be mapped --------

# BIDS field -> (mapping dict, sentinel values that intentionally map to None).
_ENUM_COVERAGE = {
    "MTPulseShape": (mapping.MAP_2_MT_PULSE_SHAPE, ()),
    "SpoilingType": (mapping.MAP_2_MRI_SPOILING_TECHNIQUE, ()),
    "MRAcquisitionType": (mapping.MAP_2_MRI_SPATIAL_ENCODING, ()),
    "ContrastBolusIngredient": (mapping.MAP_2_CONTRAST_AGENT, ("UNKNOWN", "NONE")),
}


@pytest.mark.parametrize("field", sorted(_ENUM_COVERAGE))
def test_bids_enum_fully_covered(field):
    mapping_dict, sentinels = _ENUM_COVERAGE[field]
    missing = [
        value for value in _bids_enum(field)
        if value not in sentinels and value not in mapping_dict
    ]
    assert not missing, f"{field} enum values missing from mapping: {missing}"


# --- Suffix sanity: weighting keys are real BIDS anat suffixes ---------------

def test_mri_weighting_keys_are_anat_suffixes():
    from ancpbids import model_latest as _schema
    schema_suffixes = {e.value["value"] for e in _schema.SuffixEnum}
    unknown = [s for s in mapping.MAP_2_MRI_WEIGHTING if s not in schema_suffixes]
    assert not unknown, f"MAP_2_MRI_WEIGHTING keys not in BIDS suffixes: {unknown}"


# --- Encoding direction: all 6 axes, each a signed unit 3-vector -------------

def test_encoding_direction_complete_and_unit_vectors():
    assert set(mapping.MAP_2_ENCODING_DIRECTION) == {"i", "i-", "j", "j-", "k", "k-"}
    for axis, vector in mapping.MAP_2_ENCODING_DIRECTION.items():
        assert len(vector) == 3, axis
        assert sorted(abs(c) for c in vector) == [0, 0, 1], axis


# --- Field -> property index validity: class exists, property is real --------

@pytest.mark.parametrize(
    "field, class_name, prop",
    [(field, cls, prop) for field, (cls, prop) in mapping.BIDS_FIELD_2_OPENMINDS_PROPERTY.items()],
)
def test_field_property_targets_exist(field, class_name, prop):
    cls = getattr(ni, class_name, None)
    assert cls is not None, f"{field}: unknown openMINDS neuroimaging class {class_name!r}"
    prop_names = {p.name for p in cls.properties}
    assert prop in prop_names, f"{field}: {class_name} has no property {prop!r}"
