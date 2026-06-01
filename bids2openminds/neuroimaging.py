"""
Create openMINDS v5 ``neuroimaging`` objects from a BIDS dataset.

This module turns per-file MRI metadata (BIDS JSON sidecars + NIfTI headers) into
linked openMINDS v5 objects:

- an MRI acquisition activity per imaging file — ``StaticMRIAcquisition`` for
  anatomical scans, ``DynamicMRIAcquisition`` for functional scans,
- the scanner and coil devices (``MRIScanner``, ``MRICoil``) and their usages
  (``MRIScannerUsage``, ``MRICoilUsage``), carrying the sequence parameters, and
- a ``GridVolume`` (3-D, anatomical) or ``GridVolumeSequence`` (4-D, functional)
  describing the image file itself.

The object graph mirrors the openMINDS model: the acquisition takes the
``SubjectState`` as ``input``, links to its ``MRIScannerUsage`` via ``device`` and
to the image ``File`` via ``output``; the ``MRIScannerUsage`` links back to the
``SubjectState`` via ``used_specimen`` and to its coils via ``used_coils``; and the
grid-volume's ``obtained_with`` points at the same ``MRIScannerUsage``.

It is intentionally v5-only — the ``neuroimaging`` module does not exist in
openMINDS v4 — so :func:`create_mri_acquisitions` is a no-op for other versions.
Field-to-property and value-to-controlled-term decisions come from
:mod:`bids2openminds.mapping`. Units are taken directly from the BIDS sidecar
(BIDS already standardises them) and never converted.

First implementation: covers the ``anat`` and ``func`` datatypes, one acquisition
per NIfTI file. Required openMINDS properties that BIDS does not supply are filled
in on a best-effort basis (NIfTI-derived geometry/orientation, a placeholder
``Protocol``, reused ``BehavioralProtocol``s) and otherwise left empty — the
conversion validates with ``ignore=["required", "value"]``.
"""

import os

import pandas as pd

from . import openminds_version as om
from . import mapping
from .utility import read_nifti_geometry, read_bids_metadata

# Datatypes handled in this first implementation.
_HANDLED_DATATYPES = ("anat", "func")
_NIFTI_EXTENSIONS = (".nii", ".nii.gz")


# --- small value builders --------------------------------------------------

def _quantitative_value(value, unit_name=None):
    """Build a ``QuantitativeValue``; return None if ``value`` is missing."""
    if value is None:
        return None
    unit = om.controlled_terms.UnitOfMeasurement.by_name(unit_name) if unit_name else None
    return om.core.QuantitativeValue(value=value, unit=unit)


def _quantitative_value_array(values, unit_name=None):
    """Build a ``QuantitativeValueArray``; return None if ``values`` is empty."""
    if not values:
        return None
    unit = om.controlled_terms.UnitOfMeasurement.by_name(unit_name) if unit_name else None
    return om.core.QuantitativeValueArray(values=list(values), unit=unit)


def _term(term_class, name):
    """Resolve a controlled-term instance by name; None if missing/unresolvable."""
    if not name:
        return None
    try:
        return term_class.by_name(name)
    except KeyError:
        return None


def _int_or_none(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _int_list(values):
    if not values:
        return None
    try:
        return [int(v) for v in values]
    except (TypeError, ValueError):
        return None


# --- device objects --------------------------------------------------------

def _get_or_create_scanner(metadata, cache, collection):
    """Return the ``MRIScanner`` for this sidecar, creating and caching it once.

    Deduplicated across files by (manufacturer, model, serial, station, field
    strength) so a dataset acquired on one scanner yields a single hardware node.
    """
    manufacturer = metadata.get("Manufacturer")
    model = metadata.get("ManufacturersModelName")
    serial = metadata.get("DeviceSerialNumber")
    station = metadata.get("StationName")
    field_strength = metadata.get("MagneticFieldStrength")

    key = (manufacturer, model, serial, station, field_strength)
    if key in cache:
        return cache[key]

    scanner = om.neuroimaging.MRIScanner(
        name=model or station or "MRI scanner",
        # openMINDS has no Tesla unit, so the field strength is stored value-only.
        magnetic_field_strength=_quantitative_value(field_strength),
        serial_number=serial,
        internal_identifier=station,
        type=_term(om.controlled_terms.DeviceType, "MRI scanner"),
    )
    collection.add(scanner)
    cache[key] = scanner
    return scanner


def _create_coil_usage(metadata, subject_state, cache, collection):
    """Create an ``MRICoilUsage`` (and its deduped ``MRICoil``) if coil fields exist."""
    coil_name = metadata.get("ReceiveCoilName")
    active = metadata.get("ReceiveCoilActiveElements")
    n_elements = metadata.get("NumberReceiveCoilActiveElements")
    if coil_name is None and active is None and n_elements is None:
        return None

    if coil_name in cache:
        coil = cache[coil_name]
    else:
        coil = om.neuroimaging.MRICoil(
            name=coil_name or "MRI coil",
            element_count=_int_or_none(n_elements),
        )
        collection.add(coil)
        cache[coil_name] = coil

    active_elements = None
    if active is not None:
        active_elements = [s.strip() for s in str(active).split(",") if s.strip()] or None

    coil_usage = om.neuroimaging.MRICoilUsage(
        device=coil,
        active_elements=active_elements,
        # BIDS coil fields describe the receive coil.
        signal_directionality=_term(om.controlled_terms.SignalDirectionality, "signal-receiving"),
        used_specimen=subject_state,
    )
    collection.add(coil_usage)
    return coil_usage


def _create_scanner_usage(metadata, row, scanner, coil_usage, subject_state, geometry, collection):
    """Create the ``MRIScannerUsage`` holding this file's sequence parameters."""
    suffix = row.get("suffix")

    echo_time = metadata.get("EchoTime")
    echo_times = [_quantitative_value(echo_time, "second")] if echo_time is not None else None

    matrix = metadata.get("MatrixSize")
    if matrix is None and geometry is not None:
        matrix = geometry[0][:3]
    voxel = metadata.get("AcquisitionVoxelSize")
    if voxel is None and geometry is not None:
        voxel = geometry[1][:3]

    pe_direction = metadata.get("PhaseEncodingDirection")
    phase_encoding = mapping.MAP_2_ENCODING_DIRECTION.get(pe_direction) if pe_direction else None

    usage = om.neuroimaging.MRIScannerUsage(
        device=scanner,
        used_coils=[coil_usage] if coil_usage else None,
        used_specimen=subject_state,
        repetition_time=_quantitative_value(metadata.get("RepetitionTime"), "second"),
        echo_times=echo_times,
        inversion_time=_quantitative_value(metadata.get("InversionTime"), "second"),
        flip_angle=_quantitative_value(metadata.get("FlipAngle"), "arcdegree"),
        dwell_time=_quantitative_value(metadata.get("DwellTime"), "second"),
        total_read_out_time=_quantitative_value(metadata.get("TotalReadoutTime"), "second"),
        slice_timing=_quantitative_value_array(metadata.get("SliceTiming"), "second"),
        matrix_sizes=_int_list(matrix),
        voxel_size=_quantitative_value_array(voxel, "millimeter"),
        acceleration_factor=_int_or_none(metadata.get("ParallelReductionFactorInPlane")),
        number_of_discarded_volumes=_int_or_none(metadata.get("NumberOfVolumesDiscardedByScanner")),
        mri_weighting=_term(
            om.controlled_terms.MRIWeighting, mapping.MAP_2_MRI_WEIGHTING.get(suffix)),
        mt_pulse_shape=_term(
            om.controlled_terms.PulseShape,
            mapping.MAP_2_MT_PULSE_SHAPE.get(metadata.get("MTPulseShape"))),
        spoiling_technique=_term(
            om.controlled_terms.MRISpoilingTechnique,
            mapping.MAP_2_MRI_SPOILING_TECHNIQUE.get(metadata.get("SpoilingType"))),
        spatial_encoding=_term(
            om.controlled_terms.SpatialEncoding,
            mapping.MAP_2_MRI_SPATIAL_ENCODING.get(metadata.get("MRAcquisitionType"))),
        parallel_acquisition_technique=_term(
            om.controlled_terms.MRIParallelAcquisitionTechnique,
            mapping.MAP_2_MRI_PARALLEL_ACQUISITION_TECHNIQUE.get(
                metadata.get("ParallelAcquisitionTechnique"))),
        phase_encoding_directions=phase_encoding,
    )
    collection.add(usage)
    return usage


# --- data structures -------------------------------------------------------

def _create_grid(row, metadata, file_obj, usage, geometry, collection):
    """Create the ``GridVolume`` (anat) or ``GridVolumeSequence`` (func) for a file."""
    datatype = row.get("datatype")

    dimensions = None
    voxel_sizes = None
    if geometry is not None:
        shape, zooms, _ = geometry
        if len(shape) >= 3:
            dimensions = [int(d) for d in shape[:3]]
        if len(zooms) >= 3:
            voxel_sizes = [_quantitative_value(z, "millimeter") for z in zooms[:3]]
    if dimensions is None:
        dimensions = _int_list(metadata.get("MatrixSize"))
    if voxel_sizes is None and metadata.get("AcquisitionVoxelSize"):
        voxel_sizes = [_quantitative_value(v, "millimeter")
                       for v in metadata["AcquisitionVoxelSize"][:3]]

    if datatype == "func":
        number_of_volumes = None
        if geometry is not None and len(geometry[0]) >= 4:
            number_of_volumes = int(geometry[0][3])
        repetition_time = metadata.get("RepetitionTime")
        temporal_frequency = (
            _quantitative_value(1.0 / repetition_time, "hertz") if repetition_time else None)
        grid = om.core.GridVolumeSequence(
            name=file_obj.name,
            data_location=file_obj,
            obtained_with=usage,
            dimensions=dimensions,
            voxel_sizes=voxel_sizes,
            number_of_volumes=number_of_volumes,
            temporal_sampling_frequency=temporal_frequency,
        )
    else:
        grid = om.core.GridVolume(
            name=file_obj.name,
            data_location=file_obj,
            obtained_with=usage,
            dimensions=dimensions,
            voxel_sizes=voxel_sizes,
        )
    collection.add(grid)
    return grid


# --- acquisition activity --------------------------------------------------

def _create_acquisition(row, metadata, subject_state, usage, file_obj, dataset_version,
                        behavioral_protocols_dict, protocol, geometry, collection):
    """Create the ``StaticMRIAcquisition``/``DynamicMRIAcquisition`` for a file."""
    datatype = row.get("datatype")
    class_name = mapping.MAP_2_MRI_ACQUISITION_TYPE.get(datatype)
    if class_name is None:
        return None
    acquisition_cls = getattr(om.neuroimaging, class_name)

    specimen_orientation = None
    if geometry is not None:
        specimen_orientation = _term(
            om.controlled_terms.AnatomicalAxesOrientation, "".join(geometry[2]))

    common = dict(
        lookup_label=file_obj.name,
        inputs=[subject_state] if subject_state else None,
        device=usage,
        outputs=[file_obj],
        is_part_of=dataset_version,
        protocols=[protocol] if protocol else None,
        specimen_orientation=specimen_orientation,
    )

    if class_name == "DynamicMRIAcquisition":
        behavioral = None
        task = row.get("task")
        if task is not None and not pd.isna(task) and behavioral_protocols_dict:
            behavioral_protocol = behavioral_protocols_dict.get(task)
            behavioral = [behavioral_protocol] if behavioral_protocol else None
        repetition_time = metadata.get("RepetitionTime")
        acquisition = acquisition_cls(
            behavioral_protocols=behavioral,
            volume_acquisition_time=_quantitative_value(repetition_time, "second"),
            number_of_discarded_volumes=_int_or_none(
                metadata.get("NumberOfVolumesDiscardedByUser")),
            volume_timing=_quantitative_value_array(metadata.get("VolumeTiming"), "second"),
            delay_time=_quantitative_value(metadata.get("DelayTime"), "second"),
            **common,
        )
    else:
        acquisition = acquisition_cls(**common)

    collection.add(acquisition)
    return acquisition


def _placeholder_protocol(collection):
    """Create a single shared placeholder ``Protocol`` (required by acquisitions)."""
    protocol = om.core.Protocol(
        name="MRI acquisition protocol",
        description=(
            "Placeholder protocol generated from BIDS; the acquisition protocol "
            "details are not available in the dataset."
        ),
    )
    collection.add(protocol)
    return protocol


def _resolve_subject_state(row, subject_state_dict):
    """Find the ``SubjectState`` for a file's subject/session, or None."""
    subject = row.get("subject")
    if subject is None or pd.isna(subject):
        return None
    states = subject_state_dict.get(f"{subject}")
    if not states:
        return None
    session = row.get("session")
    session_key = "" if (session is None or pd.isna(session)) else f"{session}"
    state = states.get(session_key)
    if state is None and len(states) == 1:
        # Tolerate a session-key mismatch when there is only one candidate state.
        state = next(iter(states.values()))
    return state


# --- orchestrator ----------------------------------------------------------

def create_mri_acquisitions(layout_df, bids_layout, file_by_path, subject_state_dict,
                            behavioral_protocols_dict, dataset_version, collection):
    """Create MRI acquisition objects for every anat/func NIfTI file in the dataset.

    Parameters:
    - layout_df (pd.DataFrame): the file table (columns include path, suffix,
      datatype, extension, subject, session, task).
    - bids_layout: the ancpBIDS ``BIDSLayout`` (used to locate the dataset root;
      sidecar metadata is resolved directly by :func:`utility.read_bids_metadata`).
    - file_by_path (dict): maps an absolute file path to its openMINDS ``File``.
    - subject_state_dict (dict): ``{subject: {session_key: SubjectState}}``.
    - behavioral_protocols_dict (dict): ``{task: BehavioralProtocol}`` or None.
    - dataset_version: the ``DatasetVersion`` these acquisitions belong to.
    - collection: the openMINDS ``Collection`` to add objects to.

    Returns:
    - list: the acquisition objects created (empty when not running under v5).
    """
    if om.version != "v5" or om.neuroimaging is None:
        return []

    scanner_cache = {}
    coil_cache = {}
    protocol = None
    acquisitions = []
    base_dir = os.path.abspath(bids_layout.get_dataset().base_dir_)

    for _, row in layout_df.iterrows():
        if row.get("datatype") not in _HANDLED_DATATYPES:
            continue
        if row.get("extension") not in _NIFTI_EXTENSIONS:
            continue
        file_obj = file_by_path.get(row.get("path"))
        if file_obj is None:
            continue

        metadata = read_bids_metadata(row.get("path"), base_dir)
        geometry = read_nifti_geometry(row.get("path"))
        subject_state = _resolve_subject_state(row, subject_state_dict)

        scanner = _get_or_create_scanner(metadata, scanner_cache, collection)
        coil_usage = _create_coil_usage(metadata, subject_state, coil_cache, collection)
        usage = _create_scanner_usage(
            metadata, row, scanner, coil_usage, subject_state, geometry, collection)
        _create_grid(row, metadata, file_obj, usage, geometry, collection)

        if protocol is None:
            protocol = _placeholder_protocol(collection)
        acquisition = _create_acquisition(
            row, metadata, subject_state, usage, file_obj, dataset_version,
            behavioral_protocols_dict, protocol, geometry, collection)
        if acquisition is not None:
            acquisitions.append(acquisition)

    return acquisitions
