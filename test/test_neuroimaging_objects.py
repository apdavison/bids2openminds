"""Tests for openMINDS v5 neuroimaging object creation (anat + func).

Covers the NIfTI/sidecar helpers in isolation and an end-to-end conversion of a
minimal synthetic BIDS dataset (with *real*, non-empty NIfTI files, unlike the
empty placeholders in bids-examples) so that the NIfTI-derived geometry and
orientation are actually exercised.
"""

import json
from collections import Counter

import numpy as np
import nibabel as nib
import pytest

import openminds.v5.neuroimaging as ni
import openminds.v5.core as core

from bids2openminds import converter, utility
from bids2openminds import openminds_version as om


def _write_nifti(path, shape, voxel_sizes=(2.0, 3.0, 4.0)):
    """Write a real NIfTI file with a diagonal (RAS) affine and known geometry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    affine = np.diag(list(voxel_sizes) + [1.0])
    nib.save(nib.Nifti1Image(np.zeros(shape, dtype=np.int16), affine), str(path))


# --- helper unit tests -----------------------------------------------------

def test_read_nifti_geometry(tmp_path):
    nii = tmp_path / "img.nii.gz"
    _write_nifti(nii, (4, 5, 6), voxel_sizes=(2.0, 3.0, 4.0))
    shape, zooms, axcodes = utility.read_nifti_geometry(str(nii))
    assert shape == (4, 5, 6)
    assert zooms == (2.0, 3.0, 4.0)
    assert "".join(axcodes) == "RAS"


def test_read_nifti_geometry_empty_file_returns_none(tmp_path):
    empty = tmp_path / "empty.nii.gz"
    empty.write_bytes(b"")
    assert utility.read_nifti_geometry(str(empty)) is None


def test_read_bids_metadata_inheritance(tmp_path):
    # Root-level sidecar (inherited) overridden by a file-level sidecar.
    (tmp_path / "task-rest_bold.json").write_text(
        json.dumps({"RepetitionTime": 2.0, "EchoTime": 0.03}))
    func = tmp_path / "sub-01" / "func"
    func.mkdir(parents=True)
    data_file = func / "sub-01_task-rest_bold.nii.gz"
    data_file.write_bytes(b"")
    (func / "sub-01_task-rest_bold.json").write_text(json.dumps({"EchoTime": 0.05}))

    md = utility.read_bids_metadata(str(data_file), str(tmp_path))
    assert md["RepetitionTime"] == 2.0      # inherited from root
    assert md["EchoTime"] == 0.05           # file-level sidecar wins


# --- end-to-end conversion -------------------------------------------------

@pytest.fixture
def mini_bids(tmp_path):
    """A minimal BIDS dataset with one anat (3-D) and one func (4-D) scan."""
    root = tmp_path / "ds"
    root.mkdir()
    (root / "dataset_description.json").write_text(json.dumps(
        {"Name": "Mini neuroimaging dataset", "BIDSVersion": "1.8.0",
         "Authors": ["Ada Lovelace"]}))
    (root / "participants.tsv").write_text("participant_id\tage\tsex\nsub-01\t30\tM\n")

    _write_nifti(root / "sub-01" / "anat" / "sub-01_T1w.nii.gz", (4, 5, 6))
    (root / "sub-01" / "anat" / "sub-01_T1w.json").write_text(json.dumps(
        {"RepetitionTime": 2.3, "EchoTime": 0.003, "FlipAngle": 9,
         "MagneticFieldStrength": 3, "MRAcquisitionType": "3D"}))

    _write_nifti(root / "sub-01" / "func" / "sub-01_task-rest_bold.nii.gz", (4, 5, 6, 8))
    (root / "sub-01" / "func" / "sub-01_task-rest_bold.json").write_text(json.dumps(
        {"RepetitionTime": 3.0, "EchoTime": 0.017, "TaskName": "rest",
         "PhaseEncodingDirection": "j-", "MagneticFieldStrength": 3}))
    return root


def test_end_to_end_v5_neuroimaging(mini_bids):
    collection = converter.convert(
        str(mini_bids), save_output=False, quiet=True, openminds_version="v5")
    counts = Counter(type(n).__name__ for n in collection)

    assert counts["StaticMRIAcquisition"] == 1
    assert counts["DynamicMRIAcquisition"] == 1
    assert counts["GridVolume"] == 1          # anat, 3-D
    assert counts["GridVolumeSequence"] == 1  # func, 4-D
    assert counts["MRIScanner"] == 1
    assert counts["MRIScannerUsage"] == 2
    assert len(collection.validate(ignore=["required", "value"])) == 0

    # anat: GridVolume geometry comes from the (real) NIfTI header
    grid = next(n for n in collection if isinstance(n, core.GridVolume))
    assert grid.dimensions == [4, 5, 6]
    assert [v.value for v in grid.voxel_sizes] == [2.0, 3.0, 4.0]
    assert grid.voxel_sizes[0].unit.name == "millimeter"

    # anat: acquisition orientation derived from the affine; weighting from suffix
    static = next(n for n in collection if isinstance(n, ni.StaticMRIAcquisition))
    assert static.specimen_orientation.name == "RAS"
    assert isinstance(static.device, ni.MRIScannerUsage)
    assert static.device.mri_weighting.name == "T1 weighting"
    assert static.device.repetition_time.value == 2.3
    assert static.device.repetition_time.unit.name == "second"
    assert static.device.flip_angle.unit.name == "arcdegree"
    assert static.device.spatial_encoding.name == "three-dimensional frequency-phase-phase encoding"
    assert isinstance(static.device.device, ni.MRIScanner)  # usage -> scanner link

    # func: GridVolumeSequence + dynamic-only fields
    sequence = next(n for n in collection if isinstance(n, core.GridVolumeSequence))
    assert sequence.number_of_volumes == 8
    assert sequence.temporal_sampling_frequency.unit.name == "hertz"
    dynamic = next(n for n in collection if isinstance(n, ni.DynamicMRIAcquisition))
    assert dynamic.volume_acquisition_time.value == 3.0
    assert [bp.name for bp in dynamic.behavioral_protocols] == ["rest"]
    assert dynamic.device.phase_encoding_directions == [0, -1, 0]

    # acquisitions are linked into the dataset version and to a subject state
    assert static.is_part_of is not None
    assert static.inputs and isinstance(static.inputs[0], core.SubjectState)


def test_v4_creates_no_neuroimaging_objects(mini_bids):
    collection = converter.convert(
        str(mini_bids), save_output=False, quiet=True, openminds_version="v4")
    names = {type(n).__name__ for n in collection}
    assert "MRIScannerUsage" not in names
    assert "StaticMRIAcquisition" not in names
