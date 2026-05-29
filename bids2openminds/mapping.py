MAP_2_EXPERIMENTAL_APPROACHES = {
    "func": ["neuroimaging"],
    "dwi": [
        "neuroimaging",
        "neural connectivity",
        "anatomy"
    ],
    "fmap": ["neuroimaging"],
    "anat": [
        "neuroimaging",
        "anatomy"
    ],
    "perf": [
        "neuroimaging",
        "anatomy"
    ],
    "meg": ["neuroimaging"],
    "eeg": ["electrophysiology"],
    "ieeg": ["electrophysiology"],
    "beh": ["behavior"],
    "pet": [
        "neuroimaging",
        "radiology"
    ],
    "micr": [
        "microscopy",
        "anatomy",
        "histology"
    ],
    "nirs": ["neuroimaging"]
}

MAP_2_TECHNIQUES = {
    "angio": ["angiography"],
    "M0map": ["equilibrium magnetization mapping"],
    "FLASH": ["fast-low-angle-shot pulse sequence"], #TODO instance TBD
    "FLAIR": ["fluid attenuated inversion recovery pulse sequence"], #TODO instance TBD
    "UNIT1": None, #TODO instance TBD
    "inplaneT1": [
        "T1 pulse sequence", 
        "structural magnetic resonance imaging"
    ], #TODO sMRI
    "inplaneT2": [
        "T2 pulse sequence", 
        "structural magnetic resonance imaging"
    ], #TODO sMRI
    "R1map": None, #TODO instance TBD
    "T1map": None, #TODO instance TBD
    "MTVmap": [
        "quantitative magnetic resonance imaging",
        "macromolecular tissue volume image processing"
    ], #TODO other?
    "MTRmap": [
        "magnetization transfer imaging",
        "magnetization transfer ratio image processing",
        "magnetization transfer pulse sequence"
    ], #TODO instances
    "MTsat": [
        "magnetization transfer imaging",
        "magnetization transfer saturation image processing",
        "magnetization transfer pulse sequence"
    ], #TODO instances
    "MWFmap": [
        "myelin water imaging",
        "T2 pulse sequence",
        "myelin water fraction image processing"
    ], #TODO instances
    "S0map": None, #TODO instances
    "R2starmap": None, #TODO instance TBD
    "T2starmap": None, #TODO instance TBD
    "PDT2": None, #TODO instance TBD
    "PDw": None, #TODO instance TBD
    "PD": None, #TODO instance TBD
    "PDmap": None, #TODO instance TBD
    "Chimap": None, #TODO instance TBD
    "RB1map": None, #TODO instance TBD
    "TB1map": None, #TODO instance TBD
    "T1rho": None, #TODO instance TBD
    "T1w": None, #TODO instance TBD
    "T2w": None, #TODO instance TBD
    "T2star": None, #TODO instance TBD
    "T2starw": None, #TODO instance TBD
    "R2map": None, #TODO instance TBD
    "T2map": None, #TODO instance TBD
    "bold": None, #TODO instance TBD
    "cbv": None, #TODO instance TBD
    "phase": None, #TODO instance TBD
    "defacemask": None, #TODO instance TBD
    "epi": None, #TODO instance TBD
    "fieldmap": None, #TODO instance TBD
    "magnitude": None, #TODO instance TBD
    "magnitude1": None, #TODO instance TBD
    "magnitude2": None, #TODO instance TBD
    "phase1": None, #TODO instance TBD
    "phase2": None, #TODO instance TBD
    "phasediff": None, #TODO instance TBD
    "dwi": ["diffusion-weighted imaging"],
    "sbref": None, #TODO instance TBD
    "asl": None, #TODO instance TBD
    "m0scan": None, #TODO instance TBD
    "eeg": ["electroencephalography"],
    "ieeg": ["intracranial electroencephalography"],
    "physio": None, #TODO instance TBD
    "stim": None, #TODO instance TBD
    "beh": None, #TODO instance TBD
    "pet": ["positron emission tomography"],
    "2PE": ["two-photon fluorescence microscopy"],
    "BF": None, #TODO instance TBD
    "CARS": None, #TODO instance TBD
    "CONF": ["confocal microscopy"],
    "DIC": None, #TODO instance TBD
    "DF": None, #TODO instance TBD
    "FLUO": None, #TODO instance TBD
    "MPE": None, #TODO instance TBD
    "NLO": None, #TODO instance TBD
    "OCT": None, #TODO instance TBD
    "PC": None, #TODO instance TBD
    "PLI": ["polarized light microscopy"],
    "SEM": None, #TODO instance TBD
    "SPIM": None, #TODO instance TBD
    "SR": None, #TODO instance TBD
    "TEM": ["transmission electron microscopy"],
    "uCT": None, #TODO instance TBD
    "nirs": None, #TODO instance TBD
    "motion": None, #TODO instance TBD
}

MAP_2_UNITS = {
    "year": ["year"]
}

MAP_2_BIOLOGICALSEX = {
    "male": ["male"],
    "m": ["male"],
    "M": ["male"],
    "MALE": ["male"],
    "Male": ["male"],
    "female": ["female"],
    "f": ["female"],
    "F": ["female"],
    "FEMALE": ["female"],
    "Female": ["female"]
}

MAP_2_HANDEDNESS = {
    "left": ["left handedness"],
    "l": ["left handedness"],
    "L": ["left handedness"],
    "LEFT": ["left handedness"],
    "Left": ["left handedness"],
    "right": ["right handedness"],
    "r": ["right handedness"],
    "R": ["right handedness"],
    "RIGHT": ["right handedness"],
    "Right": ["right handedness"],
    "ambidextrous": ["ambidextrous handedness"],
    "a": ["ambidextrous handedness"],
    "A": ["ambidextrous handedness"],
    "AMBIDEXTROUS": ["ambidextrous handedness"],
    "Ambidextrous": ["ambidextrous handedness"]
}

MAP_2_SPECIES = {
    "homo sapiens": ["Homo sapiens"],
    "mus musculus": ["Mus musculus"],
    "rattus norvegicus": ["Rattus norvegicus"]
}


#sample_types = {
#    "cell line": None, #TODO instance TBD
#    "in vitro differentiated cells": None, #TODO instance TBD
#    "primary cell": None, #TODO instance TBD
#    "cell-free sample": None, #TODO instance TBD
#    "cloning host": None, #TODO instance TBD
#    "tissue": None, #TODO instance TBD
#    "whole organisms": None, #TODO instance TBD
#    "organoid": None, #TODO instance TBD
#    "technical sample": None #TODO instance TBD
#}


# =============================================================================
# openMINDS v5 "neuroimaging" module mappings (MRI only)
# =============================================================================
#
# openMINDS v5 added a `neuroimaging` module (absent in v4) containing MRI
# acquisition activities (StaticMRIAcquisition, DynamicMRIAcquisition) and MRI
# devices (MRIScanner/MRIScannerUsage, MRICoil/MRICoilUsage). The mappings below
# translate BIDS MRI metadata into the controlled terms and properties of that
# module. They are *data only*: the object-creation code that consumes them
# (in main.py) is a separate, later step and is not yet wired up.
#
# Two complementary layers:
#   1A. Value-translation dicts (MAP_2_* below): a BIDS controlled value -> the
#       NAME of an openMINDS controlled-term instance, resolved later via
#       `om.controlled_terms.<Type>.by_name(<name>)` (same pattern as
#       MAP_2_SPECIES / MAP_2_HANDEDNESS above). Every name below is verified to
#       exist in openminds.v5.controlled_terms.
#   1B. BIDS_FIELD_2_OPENMINDS_PROPERTY: a BIDS sidecar field name -> the
#       (openMINDS class, property) it populates. This is the structural index of
#       "where does this field go". For fields whose target is a controlled term,
#       the value is then translated through the relevant 1A dict (named in a
#       comment beside the entry).
#
# FUTURE DIRECTION: BIDS_FIELD_2_OPENMINDS_PROPERTY is deliberately kept as plain
# (class, property) tuples for now. The intention (see METAPLAN.md, Stage 4) is to
# later enrich it into structured "FieldMap" descriptors carrying the value kind
# (scalar / QuantitativeValue / array), and eventually to fold the 1A
# value-translation dicts into the same structure.
#
# Units are always taken directly from the BIDS sidecar: openMINDS
# QuantitativeValue carries its own unit, so values are copied across unchanged
# and never converted.

# --- 1A. Value-translation dicts -------------------------------------------

# BIDS anat suffix -> openMINDS MRIWeighting instance name.
# Feeds MRIScannerUsage.mri_weighting. NOTE: this is a *separate* vocabulary from
# MAP_2_TECHNIQUES above (which only resolves Technique/AnalysisTechnique/
# Stimulation* types via techniques_openminds); do not merge the two. Only the
# weighted-image suffixes have a weighting; quantitative maps (T1map, R2map, ...)
# and sequence-named suffixes (FLAIR, FLASH, MEGRE, ...) are intentionally absent.
MAP_2_MRI_WEIGHTING = {
    "T1w": "T1 weighting",
    "T2w": "T2 weighting",
    "T2starw": "T2-star weighting",
    "PDw": "PD weighting",
    "PD": "PD weighting",            # legacy alias of PDw
    "T1rho": "T1 rho weighting",
    "inplaneT1": "T1 weighting",
    "inplaneT2": "T2 weighting",
}

# BIDS MTPulseShape enum -> openMINDS PulseShape instance name (all 7 covered).
MAP_2_MT_PULSE_SHAPE = {
    "HARD": "rectangular pulse",
    "GAUSSIAN": "Gaussian pulse",
    "GAUSSHANN": "Gaussian-Hanning pulse",
    "SINC": "sinc pulse",
    "SINCHANN": "sinc-Hanning pulse",
    "SINCGAUSS": "sinc-Gaussian pulse",
    "FERMI": "Fermi pulse",
}

# BIDS SpoilingType enum -> openMINDS MRISpoilingTechnique instance name (all 3).
MAP_2_MRI_SPOILING_TECHNIQUE = {
    "RF": "radiofrequency spoiling",
    "GRADIENT": "gradient spoiling",
    "COMBINED": "combined spoiling",
}

# BIDS ParallelAcquisitionTechnique -> openMINDS MRIParallelAcquisitionTechnique.
# The BIDS field is free text; these are the two common values. The later
# object-creation step should match case-insensitively.
MAP_2_MRI_PARALLEL_ACQUISITION_TECHNIQUE = {
    "GRAPPA": "generalized autocalibrating partially parallel acquisition",
    "SENSE": "sensitivity encoding",
}

# BIDS MRAcquisitionType enum -> openMINDS SpatialEncoding instance name.
# Approximate: MRAcquisitionType describes the readout dimensionality.
MAP_2_MRI_SPATIAL_ENCODING = {
    "1D": "one-dimensional frequency encoding",
    "2D": "two-dimensional frequency-phase encoding",
    "3D": "three-dimensional frequency-phase-phase encoding",
}

# BIDS ContrastBolusIngredient enum -> openMINDS MolecularEntity instance name.
# The agent feeds an AmountOfChemical -> Chemical chain on the acquisition's
# `contrast_agents` (built in the later step). UNKNOWN/NONE -> no contrast agent.
MAP_2_CONTRAST_AGENT = {
    "IODINE": "iodine",
    "GADOLINIUM": "gadolinium",
    "CARBON DIOXIDE": "carbon dioxide",
    "BARIUM": "barium",
    "XENON": "xenon",
    "UNKNOWN": None,
    "NONE": None,
}

# BIDS PhaseEncodingDirection / SliceEncodingDirection (i/j/k) -> signed unit
# 3-vector for MRIScannerUsage.phase_encoding_directions (min/max 3 items).
# NOTE: i/j/k are NIfTI image axes, not scanner axes; converting to scanner
# coordinates requires the image affine (handled in the later step).
MAP_2_ENCODING_DIRECTION = {
    "i": [1, 0, 0],
    "i-": [-1, 0, 0],
    "j": [0, 1, 0],
    "j-": [0, -1, 0],
    "k": [0, 0, 1],
    "k-": [0, 0, -1],
}

# BIDS datatype -> openMINDS acquisition class name.
# DynamicMRIAcquisition *requires* behavioral_protocols and volume_acquisition_time,
# so it fits task-based fMRI (func). perf/ASL is a time series but lacks a
# behavioral protocol, so it is mapped to Static here -- FLAG FOR REVIEW once the
# object-creation step exists. Final class-selection logic lives in that step.
MAP_2_MRI_ACQUISITION_TYPE = {
    "func": "DynamicMRIAcquisition",
    "anat": "StaticMRIAcquisition",
    "dwi": "StaticMRIAcquisition",
    "fmap": "StaticMRIAcquisition",
    "perf": "StaticMRIAcquisition",
}

# --- 1B. Structural field -> (class, property) index -----------------------
#
# All property names are verified against the openminds.v5.neuroimaging classes.
# Direct/quantitative fields pass their value through (wrapped in a
# QuantitativeValue / array in the later step). Controlled-term fields carry a
# comment naming the 1A dict used to translate their value.
#
# Context-dependent cases the flat dict can't express (handled in the later step):
#   * For func, BIDS RepetitionTime ALSO supplies
#     DynamicMRIAcquisition.volume_acquisition_time (the entry below maps it to
#     MRIScannerUsage.repetition_time only).
#   * The .bval/.bvec files supply MRIScannerUsage.diffusion_encoding_parameters,
#     but those are files, not sidecar scalars, so they are not entries here.
#
# Fields with no clean target (intentionally omitted): MultibandAccelerationFactor,
# EffectiveEchoSpacing, Manufacturer/ManufacturersModelName (the latter would feed
# a HardwareProduct for MRIScanner.type -- a structured object, not a scalar).
BIDS_FIELD_2_OPENMINDS_PROPERTY = {
    # direct / quantitative passthrough
    "RepetitionTime": ("MRIScannerUsage", "repetition_time"),
    "EchoTime": ("MRIScannerUsage", "echo_times"),
    "InversionTime": ("MRIScannerUsage", "inversion_time"),
    "FlipAngle": ("MRIScannerUsage", "flip_angle"),
    "DwellTime": ("MRIScannerUsage", "dwell_time"),
    "TotalReadoutTime": ("MRIScannerUsage", "total_read_out_time"),
    "SliceTiming": ("MRIScannerUsage", "slice_timing"),
    "SliceThickness": ("MRIScannerUsage", "slice_thickness"),
    "MatrixSize": ("MRIScannerUsage", "matrix_sizes"),
    "AcquisitionVoxelSize": ("MRIScannerUsage", "voxel_size"),
    "ParallelReductionFactorInPlane": ("MRIScannerUsage", "acceleration_factor"),
    "NumberOfVolumesDiscardedByScanner": ("MRIScannerUsage", "number_of_discarded_volumes"),
    "NumberOfVolumesDiscardedByUser": ("DynamicMRIAcquisition", "number_of_discarded_volumes"),
    "VolumeTiming": ("DynamicMRIAcquisition", "volume_timing"),
    "DelayTime": ("DynamicMRIAcquisition", "delay_time"),
    "MagneticFieldStrength": ("MRIScanner", "magnetic_field_strength"),
    "DeviceSerialNumber": ("MRIScanner", "serial_number"),
    "StationName": ("MRIScanner", "internal_identifier"),
    "ReceiveCoilName": ("MRICoil", "name"),
    "ReceiveCoilActiveElements": ("MRICoilUsage", "active_elements"),
    # controlled-term fields (translate value via the named 1A dict)
    "MTPulseShape": ("MRIScannerUsage", "mt_pulse_shape"),                          # MAP_2_MT_PULSE_SHAPE
    "SpoilingType": ("MRIScannerUsage", "spoiling_technique"),                      # MAP_2_MRI_SPOILING_TECHNIQUE
    "MRAcquisitionType": ("MRIScannerUsage", "spatial_encoding"),                   # MAP_2_MRI_SPATIAL_ENCODING
    "ParallelAcquisitionTechnique": ("MRIScannerUsage", "parallel_acquisition_technique"),  # MAP_2_MRI_PARALLEL_ACQUISITION_TECHNIQUE
    "PhaseEncodingDirection": ("MRIScannerUsage", "phase_encoding_directions"),     # MAP_2_ENCODING_DIRECTION
    "ContrastBolusIngredient": ("StaticMRIAcquisition", "contrast_agents"),         # MAP_2_CONTRAST_AGENT (via AmountOfChemical chain)
}

# --- Documented gaps: controlled terms with no clean BIDS source -----------
# These openMINDS v5 neuroimaging controlled-term properties cannot be populated
# from a BIDS sidecar field, so no mapping is provided (the later step should not
# look for one):
#   * MRIFatSuppressionTechnique     -- no standard BIDS field.
#   * SignalDirectionality (MRICoilUsage.signal_directionality),
#     DeviceMountingType (MRICoil.mounting_type),
#     coil DeviceType (MRICoil.type) -- BIDS coil fields (ReceiveCoilName,
#                                       MRTransmitCoilSequence) are free text only.
#   * AnatomicalPlane (slice_orientation), AnatomicalAxesOrientation
#     (specimen_orientation) -- derived from the NIfTI affine at runtime.
#   * gradient_correction (AnalysisTechnique) -- BIDS NonlinearGradientCorrection
#     is boolean; no matching controlled-term instance.

# --- Non-MRI datatypes -----------------------------------------------------
# The openMINDS v5 "neuroimaging" module is MRI-only. PET, MEG, EEG, iEEG,
# microscopy, NIRS, motion, MRS and EMG have NO neuroimaging classes in v5, so no
# acquisition mapping is possible for them until openMINDS adds the relevant
# modules/classes. Their coarse dataset-level mappings remain in
# MAP_2_EXPERIMENTAL_APPROACHES / MAP_2_TECHNIQUES above and are unaffected.
