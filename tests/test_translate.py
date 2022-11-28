from contextlib import nullcontext as does_not_raise

from dicomhandler.dicom_info import Dicominfo

import pydicom
from pydicom.multival import MultiValue

import pytest


@pytest.mark.parametrize(
    "struct, delta, key, expected",
    [
        ("cuadrad", 0, "x", pytest.raises(ValueError)),
        (2, 20.0, "x", pytest.raises(ValueError)),
        ("punto", 20.0, "x", does_not_raise()),
        ("punto", 1001, "x", pytest.raises(ValueError)),
        ("cubo", "1", "x", pytest.raises(TypeError)),
        ("cubo", 200.0, "xx", pytest.raises(ValueError)),
        ("error", 200, "x", pytest.raises(ValueError)),
        ("cubo", 200.1, "x", does_not_raise()),
    ],
)
def test_translate_input_struct(struct, delta, key, expected, patient_1):
    with expected:
        dicom_info1 = Dicominfo(patient_1)
        dicom_info1.translate(struct, delta, key)


@pytest.mark.parametrize(
    "struct, delta, key, args, expected",
    [
        ("cubo", 200.0, "x", [0.0, 0.0], pytest.raises(ValueError)),
        ("cubo", 200.0, "x", [1, 1, 1], pytest.raises(ValueError)),
        ("cubo", 200.0, "x", [0.0, 1.0, 0.0], does_not_raise()),
    ],
)
def test_translate_input_par_args(struct, delta, key, args, expected, patient_1):
    with expected:
        dicom_info1 = Dicominfo(patient_1)
        dicom_info1.translate(struct, delta, key, args)


@pytest.mark.parametrize(
    "struct, delta, key",
    [
        ("punto", 0.0, "x"),
        ("punto", 0.0, "y"),
        ("punto", 0.0, "z"),
    ],
)
def test_translate_punto_0_360(struct, delta, key, patient_1, *args):
    dicom_info1 = Dicominfo(patient_1)
    x = (
        dicom_info1.translate(struct, delta, key)
        .dicom_struct.ROIContourSequence[1]
        .ContourSequence[0]
        .ContourData
    )
    y = patient_1.ROIContourSequence[1].ContourSequence[0].ContourData
    assert len(x) == len(y)
    assert all([abs(xi - yi) <= 0.00001 for xi, yi in zip(x, y)])


@pytest.mark.parametrize(
    "struct, delta, key",
    [
        ("cubo", 0.0, "x"),
        ("cubo", 0.0, "y"),
        ("cubo", 0.0, "z"),
    ],
)
def test_translate_cubo_0_360(struct, delta, key, patient_1, *args):
    dicom_info = Dicominfo(patient_1)
    for i in range(len(dicom_info.dicom_struct.ROIContourSequence[0])):
        x = (
            dicom_info.translate(struct, delta, key)
            .dicom_struct.ROIContourSequence[0]
            .ContourSequence[i]
            .ContourData
        )
        y = patient_1.ROIContourSequence[0].ContourSequence[i].ContourData
        assert len(x) == len(y)
        assert all([abs(xi - yi) <= 0.00000001 for xi, yi in zip(x, y)])


@pytest.mark.parametrize(
    "struct, delta, key, origin, expected",
    [
        (
            "cubo",
            200.0,
            "z",
            
            MultiValue(float, [0.0, 0.0, 0.0]),
            does_not_raise(),
        ),
        (
            "cubo",
            200.0,
            "z",
            
            MultiValue(float, [0.0, 0.0, 0.0, 1]),
            pytest.raises(ValueError),
        ),
        (
            "cubo",
            200.0,
            "z",
            
            MultiValue(float, [0.0, 1.0, 0.0, 2]),
            pytest.raises(ValueError),
        ),
    ],
)
def test_translate_input_origin(struct, delta, key, patient_1, origin, expected):
    with expected:
        dicom_info2 = Dicominfo(patient_1)
        dicom_info2.translate(struct, delta, key, origin)


@pytest.mark.parametrize(
    "struct, delta1, delta2, delta3, key",
    [
        ("space", 100, 20, -120, "x"),
        ("space", 999, 1, -1000, "y"),
        ("space", 19, 21, -40, "z"),
        ("space", 100, -50, -50, "x"),
        ("space", 300, -200, -100, "y"),
        ("space", 200, 0, -200, "z"),
    ],
)
def test_translate_space(struct, delta1, delta2, delta3, key, patient_1, *args):
    dicom_info = Dicominfo(patient_1)
    for i in range(len(dicom_info.dicom_struct.ROIContourSequence[0])):
        x = (
            dicom_info.translate(struct, delta1, key)
            .translate(struct, delta2, key)
            .translate(struct, delta3, key)
            .dicom_struct.ROIContourSequence[1]
            .ContourSequence[i]
            .ContourData
        )
        y = patient_1.ROIContourSequence[1].ContourSequence[i].ContourData
        assert len(x) == len(y)
        assert all([abs(xi - yi) <= 0.00000001 for xi, yi in zip(x, y)])


@pytest.mark.parametrize(
    "struct, delta, key, expected",
    [
        ("punto", 1, "x", MultiValue(float, [2.0, 1.0, 1.0])),
        ("punto", 1, "y", MultiValue(float, [1.0, 2.0, 1.0])),
        ("punto", 1, "z", MultiValue(float, [1.0, 1.0, 2.0])),
    ],
)
def test_rotate_punto(struct, delta, key, patient_1, expected):
    dicom_info = Dicominfo(patient_1)
    for i in range(len(dicom_info.dicom_struct.ROIContourSequence[2])):
        x = (
            dicom_info.translate(struct, delta, key)
            .dicom_struct.ROIContourSequence[2]
            .ContourSequence[i]
            .ContourData
        )
        y = expected
        assert len(x) == len(y)
        assert all([abs(xi - yi) <= 0.00001 for xi, yi in zip(x, y)])
