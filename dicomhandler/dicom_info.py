"""Dicomhandler.

Python tool for integrating.
`DICOM <https://www.dicomstandard.org/>` information and processing.
DICOM radiotherapy structures. It allows to modify the structures.
(expand, contract, rotate, translate) and to obtain statistics.
from these modifications without the need to use CT or MRI images.
and to create new DICOM files with this information, which are.
compatible with the commercial systems of treatment planning such as.
`Eclipse <https://www.varian.com/>` and.
`Brainlab Elements <https://www.brainlab.com/>`.
It is possible to extract the information from the structures.
in an easy *excelable* form.

.. moduleauthor:: Alejandro Rojas <alexrojas@ciencias.unam.mx>
.. moduleauthor:: Jerónimo Fontinós <jerofoti@gmail.com>
.. moduleauthor:: Nicola Maddalozzo <nicolamaddalozzo95@gmail.com>

"""
import copy
from collections import defaultdict
import warnings

import numpy as np

import pandas as pd

from pydicom.multival import MultiValue

import xlsxwriter


class Dicominfo:
    """Class Dicominfo.

    Allow to integrate the characteristics.
    and properties of the different DICOM files, which have.
    complementary information of each patient.
    The files accepted are:
    - **Structures:** RS.dcm.
    - **Treatment plan:** RP.dcm.
    - **Treatment dose:** RD.dcm.
    .. note::
    **Important:** Dicominfo not allows to merge information from
    different patients. Only one RS, RP and RD is accepted per patient,
    per instantiation.

    """

    def __init__(self, *args):
        """Initialize dicominfo object.

        Initialize Dicominfo objects.

        Example
        ------
        >>> import pydicom
        >>> import os
        # import the class from the dicomhandler.
        >>> import dicomhandler.dicom_info as dh
        # construct the object.
        >>> file = os.listdir(os.chdir('./path'))
        >>> struct = pydicom.dcmread(file[0])
        >>> plan = pydicom.dcmread(file[1])
        >>> dicom = dh.Dicom_info(struct, plan)


        Parameters
        ----------
        *args : pydicom.dataset.FileDataset
        DICOM files from a patient.

        Methods
        -------
        anonymize(name=True, birth=True, operator=True, creation=True)
        Allows to overwrite the patient's information.
        structure_to_excel(name_file, names=[])
        It creates DICOM contour in *excelable* form.
        mlc_to_excel(name_file)
        It creates DICOM plan information in *excelable* form.
        rotate(struct, angle, key, *args)
        It allows to rotate all the points for a single structure.
        translate(struct, delta, key, *args)
        It allows to translate all the points for a single structure.
        add_margin(struct, margin)
        It allows to expand or subtract margin for a single structure.

        Returns
        -------
        pydicom.dataset.FileDataset
        Dicominfo object with DICOM properties.

        Raises, Warnings
        -------
        Patients Name do not match.
        Patients BirthDate do not match.
        ValueError
            Modality not supported.
            One > dicom of the same modality.

        """
        self.dicom_struct = None
        self.dicom_dose = None
        self.dicom_plan = None
        self.PatientName = None
        self.PatientBirthDate = None
        self.PatientID = None
        if args:
            patient = args[0]
            temp_name = patient.PatientName
            temp_id = patient.PatientID
            temp_birthdate = patient.PatientBirthDate
            temp_modality = patient.Modality
            for files in args[1:]:
                if temp_name != files.PatientName:
                    warnings.warn(
                        "Patients Name do not match,\
                                first argument of patient name will be used"
                    )
                if temp_id != files.PatientID:
                    raise ValueError("Patient ID's do not match")
                if temp_birthdate != files.PatientBirthDate:
                    warnings.warn(
                        "Patients BirthDate do not match,\
                                first argument of birthdate will be used"
                    )
                if temp_modality == files.Modality:
                    raise ValueError("One > dicom of the same modality")
            for files in args[:]:
                if files.Modality == "RTSTRUCT":
                    self.dicom_struct = files
                elif files.Modality == "RTDOSE":
                    self.dicom_dose = files
                elif files.Modality == "RTPLAN":
                    self.dicom_plan = files
                else:
                    raise ValueError("Modality not supported")
            self.PatientName = patient.PatientName
            self.PatientBirthDate = patient.PatientBirthDate
            self.PatientID = patient.PatientID

    def anonymize(self, name=True, birth=True, operator=True, creation=True):
        """Method anonymize.

        In many cases, it is important to anonymize the patient's information.
        for research and statistics. `anonymize` method allows to overwrite.
        the name, birth date of the patient, the operator's name and the.
        creation of the plan.
        By default, it modifies a DICOM object with the following values:
        - Patient Name, 'PatientName',
        - Patient Birth Date, '19720101',
        - Operators Name, 'OperatorName',
        - Instance Creation Date, '19720101'

        Example
        -------
        # anonymize name, birthdate, operator.
        # no anonymize creation date.
        >>> dicom = dicom.anonymize(creation=False)


        Parameters
        ----------
        name : bool
            By default True. Anonymize the patient name.
        birth : bool
            By default True. Anonymize the patient birth date.
        operator : bool
            By default True. Anonymize the operator name.
        creation : bool
            By default True. Anonymize the instance creation date.

        Returns
        -------
        pydicom.dataset.FileDataset
            Object with DICOM properties of the anonymized files.

        Warnings
        -------
        Anonymize should be run after adding data to the object.

        """
        dicom_copy = copy.deepcopy(self)

        empty_di = all(
            [
                self.dicom_struct is None,
                self.dicom_dose is None,
                self.dicom_plan is None,
                self.PatientName is None,
                self.PatientBirthDate is None,
                self.PatientID is None,
            ]
        )

        if empty_di:
            warnings.warn(
                "anonymize should be run after adding data to the object"
            )
            return dicom_copy

        if name:
            dicom_copy.PatientName = "PatientName"
            if dicom_copy.dicom_struct is not None:
                dicom_copy.dicom_struct.PatientName = "PatientName"

            if dicom_copy.dicom_plan is not None:
                dicom_copy.dicom_plan.PatientName = "PatientName"

            if dicom_copy.dicom_dose is not None:
                dicom_copy.dicom_dose.PatientName = "PatientName"

        if birth:
            dicom_copy.PatientBirthDate = "19720101"
            if dicom_copy.dicom_struct is not None:
                (dicom_copy.dicom_struct.PatientBirthDate) = "19720101"

            if dicom_copy.dicom_plan is not None:
                (dicom_copy.dicom_plan.PatientBirthDate) = "19720101"

            if dicom_copy.dicom_dose is not None:
                (dicom_copy.dicom_dose.PatientBirthDate) = "19720101"

        if operator:
            dicom_copy.OperatorsName = "OperatorName"
            if dicom_copy.dicom_struct is not None:
                dicom_copy.dicom_struct.OperatorsName = "OperatorName"

            if dicom_copy.dicom_plan is not None:
                dicom_copy.dicom_plan.OperatorsName = "OperatorName"

            if dicom_copy.dicom_dose is not None:
                dicom_copy.dicom_dose.OperatorsName = "OperatorName"

        if creation:
            dicom_copy.InstanceCreationDate = "19720101"
            if dicom_copy.dicom_struct is not None:
                (dicom_copy.dicom_struct.InstanceCreationDate) = "19720101"

            if dicom_copy.dicom_plan is not None:
                (dicom_copy.dicom_plan.InstanceCreationDate) = "19720101"

            if dicom_copy.dicom_dose is not None:
                (dicom_copy.dicom_dose.InstanceCreationDate) = "19720101"

        return dicom_copy

    def structure_to_excel(self, name_file, names=[]):
        """Method structure to excel.

        The information of the cartesian coordinates (relative positions).
        for all or some structures is extracted in an .xlsx file.
        for posprocessing.
        It creates DICOM contour in *excelable* form.
        The Contour Data for each organ is set on different sheets.
        The file is created in the same directory with the name name.xlsx.

        Example
        -------
        # extract the coordinates of the structures Eye Right and Tumor.
        >>> dicom.structure_to_excel('outputfile', ['Eye Right', 'Tumor'])
        # extract the coordinates of the all structures.
        >>> dicom.structure_to_excel('outputfile', [])


        Parameters
        ----------
        name_file : str
            Name of the output file.
        names : list
            List of str, with the name of the structures to create the
            excel file. By default [] which corresponds to all structures.
            .. note::
            **Important:** For all structures, it could be a slow process
            to take couple of minutes.

        Returns
        -------
        Excel file.

        Raises
        ------
        ValueError
            Name not founded.

        """
        dicom_copy = copy.deepcopy(self)
        extension = ".xlsx"
        name_file = name_file + extension
        names_aux, n_all = {}, {}
        for item, _ in enumerate(
            dicom_copy.dicom_struct.StructureSetROISequence
        ):
            names_aux[
                (dicom_copy.dicom_struct.StructureSetROISequence[item].ROIName)
            ] = item
        if len(names) == 0:
            n_all = names_aux
        else:
            for name in names:
                if name in names_aux.keys():
                    n_all[name] = names_aux[name]
                else:
                    raise ValueError(f"{name} not founded.")
        file_open = open(name_file, "w")
        workbook = xlsxwriter.Workbook(name_file)
        for name in n_all:
            worksheet = workbook.add_worksheet(name)
            for num, _ in enumerate(
                dicom_copy.dicom_struct.ROIContourSequence[
                    n_all[name]
                ].ContourSequence
            ):
                worksheet.write_row(
                    0,
                    3 * num,
                    [f"x{num} [mm]", f"y{num} [mm]", f"z{num} [mm]"],
                )
                count = 0
                while count < int(
                    len(
                        dicom_copy.dicom_struct.ROIContourSequence[n_all[name]]
                        .ContourSequence[num]
                        .ContourData
                    )
                    / 3
                ):
                    x = float(
                        dicom_copy.dicom_struct.ROIContourSequence[n_all[name]]
                        .ContourSequence[num]
                        .ContourData[3 * count]
                    )
                    y = float(
                        dicom_copy.dicom_struct.ROIContourSequence[n_all[name]]
                        .ContourSequence[num]
                        .ContourData[3 * count + 1]
                    )
                    z = float(
                        dicom_copy.dicom_struct.ROIContourSequence[n_all[name]]
                        .ContourSequence[num]
                        .ContourData[3 * count + 2]
                    )
                    worksheet.write_row(1 + count, 3 * num, [x, y, z])
                    count = count + 1
        workbook.close()
        file_open.close()

    def mlc_to_excel(self, name_file):
        """Method MLC to excel.

        The information of the MLC positions, control points.
        gantry angles, gantry orientation and table angle are.
        reported in an .xlsx file for posprocessing for numerical.
        simulations.
        The date for each beam is set on different sheets.
        The file is created in the same directory with the name name.xlsx.

        Example
        -------
        # extract the MLC relative positions and checkpoints.
        >>> dicom.mlc_to_excel('outputfile')


        Parameters
        ----------
        name_file : str
            Name of the output file.

        Returns
        -------
        Excel file.

        Raises
        ------
        ValueError
            Plan not loaded.

        """
        dicom_copy = copy.deepcopy(self)
        extension = ".xlsx"
        name_file = name_file + extension
        if dicom_copy.dicom_plan is None:
            raise ValueError("Plan not loaded")
        file_open = open(name_file, "w")
        workbook = xlsxwriter.Workbook(name_file)
        for number, _ in enumerate(dicom_copy.dicom_plan.BeamSequence):
            worksheet = workbook.add_worksheet(f"Beam {number}")
            for controlpoint, _ in enumerate(
                dicom_copy.dicom_plan.BeamSequence[number].ControlPointSequence
            ):
                gantry_angle = (
                    dicom_copy.dicom_plan.BeamSequence[number]
                    .ControlPointSequence[controlpoint]
                    .GantryAngle
                )
                gantry_direction = (
                    dicom_copy.dicom_plan.BeamSequence[number]
                    .ControlPointSequence[controlpoint]
                    .GantryRotationDirection
                )
                table_direction = (
                    dicom_copy.dicom_plan.BeamSequence[number]
                    .ControlPointSequence[0]
                    .PatientSupportAngle
                )
                if controlpoint == 0:
                    mlc = np.array(
                        dicom_copy.dicom_plan.BeamSequence[number]
                        .ControlPointSequence[controlpoint]
                        .BeamLimitingDevicePositionSequence[2]
                        .LeafJawPositions
                    )
                else:
                    mlc = list(
                        np.array(
                            dicom_copy.dicom_plan.BeamSequence[number]
                            .ControlPointSequence[controlpoint]
                            .BeamLimitingDevicePositionSequence[0]
                            .LeafJawPositions
                        )
                    )
                worksheet.write_row(
                    controlpoint,
                    0,
                    [
                        f"ControlPoint{controlpoint}",
                        "GantryAngle",
                        gantry_angle,
                        "GantryDirection",
                        gantry_direction,
                        "TableDirection",
                        table_direction,
                        "MLC",
                    ],
                )
                for leaf, _ in enumerate(mlc):
                    worksheet.write_row(controlpoint, 8 + leaf, [mlc[leaf]])
        workbook.close()
        file_open.close()

    def areas_to_df(self):
        dicom_copy = copy.deepcopy(self)
  
        if dicom_copy.dicom_plan is None:
            raise ValueError("Plan not loaded")
        n_laminas = len(dicom_copy.dicom_plan.BeamSequence[0] \
                                                 .BeamLimitingDeviceSequence[2] \
                                                 .LeafPositionBoundaries) - 1
                                               
        for i,_ in enumerate(dicom_copy.dicom_plan.BeamSequence):
           
            if (n_laminas != len(dicom_copy.dicom_plan.BeamSequence[i] \
                                             .BeamLimitingDeviceSequence[2] \
                                             .LeafPositionBoundaries) - 1):
                raise ValueError("The number of leaves is different among the beams")
        
       
                                             
            
        df_cols = ['beam', 'checkpoint', 'area', 'gantry_angle', 'gantry_direction', 'table']
        dict_laminas = defaultdict(list) 
        leaf_pos = dicom_copy.dicom_plan.BeamSequence[0].BeamLimitingDeviceSequence[2].LeafPositionBoundaries
        
        for i,j in enumerate(leaf_pos[:len(leaf_pos)-1]):
            dict_laminas[i+1].append(abs(j - leaf_pos[i+1])) 
        rows_df = []
        for i,_ in enumerate(dicom_copy.dicom_plan.BeamSequence) :
            table = dicom_copy.dicom_plan.BeamSequence[i].ControlPointSequence[0].PatientSupportAngle   
            if isinstance(table, float) is False:
                raise TypeError("table angle must be a float")     
            gantry_direction = dicom_copy.dicom_plan.BeamSequence[i].ControlPointSequence[0].GantryRotationDirection
            if isinstance(gantry_direction, str) is False:
                raise TypeError("gantry_direction must be a string") 
            for j, _ in enumerate(dicom_copy.dicom_plan.BeamSequence[i].ControlPointSequence) :
   
                gantry_angle = dicom_copy.dicom_plan.BeamSequence[i].ControlPointSequence[j].GantryAngle
                if isinstance(gantry_angle, float) is False:
                    raise TypeError("gantry_angle must be a float")
                if j == 0 :
                    mlc_positions = dicom_copy.dicom_plan.BeamSequence[i] \
                                         .ControlPointSequence[j] \
                                         .BeamLimitingDevicePositionSequence[2] \
                                         .LeafJawPositions
                else :
                    mlc_positions = dicom_copy.dicom_plan.BeamSequence[i] \
                                         .ControlPointSequence[j] \
                                         .BeamLimitingDevicePositionSequence[0] \
                                         .LeafJawPositions
        
                A = np.array(mlc_positions[:len(mlc_positions)//2])
                B = np.array(mlc_positions[len(mlc_positions)//2:len(mlc_positions)])
                diff = abs(A-B)
                dict_lamina_prov = copy.deepcopy(dict_laminas)
                for z, elem_diff in enumerate(diff) :
                    dict_lamina_prov[z+1].append(elem_diff)
        
                area = 0
       
                for values in dict_lamina_prov.values():
                    area+=values[0]*values[1]
                rows_df.append([i+1,j+1,round(area,4),gantry_angle, gantry_direction, table])
        df = pd.DataFrame(rows_df, columns=df_cols)
        return df


    def info_to_dataframe(self, targets=[]):
        
        """
        Method info to dataframe.
        The information of the prescribed dose, reference points in targets.
        dose to references points, maximum, minimun and mean radius and.
        the center of mass and distance to isocenter for each target.
        are summarized in a dataframe.
        The information is reported for all targets in the dicom plan.
        It is necessary to include at least the structure and plan files.
        Names' targets must match. If not, add manually as the examples.
        Please verify that names are in concordance from both files.
        Example
        -------
        # Obtain dataframe with the names matched.
        >>> import pydicom
        >>> import os
        # import the class from the dicomhandler.
        >>> import dicomhandler.dicom_info as dh
        # construct the object.
        >>> file = os.listdir(os.chdir('./DICOMfiles'))
        >>> plan = pydicom.dcmread(file[0], force = True)
        >>> struct = pydicom.dcmread(file[1], force = True)
        >>> dicom = dh.Dicom_info(struct, plan)
        # Call method info_to_dataframe
        >>> dicom.info_to_dataframe()
        # Obtain dataframe with the names missmatched.
        >>> targets = ['1 GTV +2.0 mm',
                      '2 GTV +2.0 mm',
                      '3 PTV +1.0 mm',
                      '4 PTV +1.0 mm',
                      '5 PTV +1.0 mm']
        >>> dicom.info_to_dataframe(targets)
        Parameters
        ----------
        targets : list
            List of names' targets. By default target = [].
        Returns
        -------
        Dataframe with information from DICOM files.
        Raises, Warnings
        ------
        ValueError
            Length of target names must be {len(names)}.
            You must load plan and structure files.
            Verify the correct names between plan and structures.
        """
        counter = 0
        dictionary_p = {}
        dictionary_s = {}
        names_p, names_s, dose, dose_ref, coordinates = [], [], [], [], []
        dist2iso, dist2iso_struct, radius_contour, centermass = [], [], [], []
        radiusmax, radiusmin, radiusmean = [], [], []
        n_id = {}
        dicom_copy = copy.deepcopy(self)
        df_plan_struct = pd.DataFrame()
        if (dicom_copy.dicom_plan is None) or (
            dicom_copy.dicom_struct is None
        ):
            raise ValueError("You must load plan and structure files.")
        isocenter_plan = np.array(
            dicom_copy.dicom_plan.BeamSequence[0]
            .ControlPointSequence[0]
            .IsocenterPosition
        )
        while counter < len(dicom_copy.dicom_plan.DoseReferenceSequence) / 2:
            names_p.append(
                dicom_copy.dicom_plan.DoseReferenceSequence[
                    counter * 2
                ].DoseReferenceDescription
            )
            dose.append(
                round(
                    dicom_copy.dicom_plan.DoseReferenceSequence[
                        counter * 2
                    ].TargetPrescriptionDose,
                    2,
                )
            )
            dose_ref.append(
                round(
                    dicom_copy.dicom_plan.DoseReferenceSequence[
                        counter * 2 + 1
                    ].TargetPrescriptionDose,
                    2,
                )
            )
            coordinates.append(
                dicom_copy.dicom_plan.DoseReferenceSequence[
                    counter * 2 + 1
                ].DoseReferencePointCoordinates
            )
            dist2iso.append(
                round(
                    np.linalg.norm(
                        np.array(
                            dicom_copy.dicom_plan.DoseReferenceSequence[
                                counter * 2 + 1
                            ].DoseReferencePointCoordinates
                            - isocenter_plan
                        )
                    ),
                    1,
                )
            )
            counter = counter + 1
        for i, _ in enumerate(dicom_copy.dicom_struct.StructureSetROISequence):
            n_id[
                (dicom_copy.dicom_struct.StructureSetROISequence[i].ROIName)
            ] = i
            names_s.append(dicom_copy.dicom_struct.StructureSetROISequence[i].ROIName)
        
        if len(targets) == 0:
            targets = names_p
            warnings.warn(
                        "It is not guaranteed that for each element in the pydicom structure there is the corresponding element in the pydicom plan"
                    )
            
        elif len(targets) != len(names_p):
            raise ValueError(f"Length of target names must be {len(names_p)}.")
        else :
            for i, target in enumerate(targets):
                s = names_p[i][:4]

                if target.startswith(s) == False :
                    raise ValueError(f"{names_p} has not a structure named {target}. Verify the names of the target structures.")    
        
        targets = list(set(names_s).intersection(targets))
                
        for name in targets:
            
            mean_values1 = []
            for num, _ in enumerate(
                    dicom_copy.dicom_struct.ROIContourSequence[
                        n_id[name]
                    ].ContourSequence
                ):
                counter1 = 0
                xmean1, ymean1, zmean1 = [], [], []
                while counter1 < int(
                        len(
                            dicom_copy.dicom_struct.ROIContourSequence[
                                n_id[name]
                            ]
                            .ContourSequence[num]
                            .ContourData
                        )
                        / 3
                    ):
                    xmean1.append(
                            dicom_copy.dicom_struct.ROIContourSequence[
                                n_id[name]
                            ]
                            .ContourSequence[num]
                            .ContourData[3 * counter1]
                        )
                    ymean1.append(
                            dicom_copy.dicom_struct.ROIContourSequence[
                                n_id[name]
                            ]
                            .ContourSequence[num]
                            .ContourData[3 * counter1 + 1]
                        )
                    zmean1.append(
                            dicom_copy.dicom_struct.ROIContourSequence[
                                n_id[name]
                            ]
                            .ContourSequence[num]
                            .ContourData[3 * counter1 + 2]
                        )
                    counter1 = counter1 + 1
                xmean1 = np.mean(xmean1)
                ymean1 = np.mean(ymean1)
                zmean1 = np.mean(zmean1)
                mean_values1.append([xmean1, ymean1, zmean1])
            centermass1 = np.mean(mean_values1, axis=0)
            for num, _ in enumerate(
                dicom_copy.dicom_struct.ROIContourSequence[
                        n_id[name]
                    ].ContourSequence
                ):
                counter2 = 0
                while counter2 < int(
                        len(
                            dicom_copy.dicom_struct.ROIContourSequence[
                                n_id[name]
                            ]
                            .ContourSequence[num]
                            .ContourData
                        )
                        / 3
                    ):
                    basepoint = np.array(
                            [
                                (
                                    dicom_copy.dicom_struct.ROIContourSequence[
                                        n_id[name]
                                    ]
                                    .ContourSequence[num]
                                    .ContourData[3 * counter2]
                                ),
                                (
                                    dicom_copy.dicom_struct.ROIContourSequence[
                                        n_id[name]
                                    ]
                                    .ContourSequence[num]
                                    .ContourData[3 * counter2 + 1]
                                ),
                                (
                                    dicom_copy.dicom_struct.ROIContourSequence[
                                        n_id[name]
                                    ]
                                    .ContourSequence[num]
                                    .ContourData[3 * counter2 + 2]
                                ),
                            ]
                        )
                    radius_contour.append(
                            round(
                                np.linalg.norm(
                                    np.array((basepoint - centermass1))
                                ),
                                2,
                            )
                        )
                    counter2 = counter2 + 1
            for value, _ in enumerate(centermass1):
                centermass1[value] = round(centermass1[value], 3)
        
            centermass.append(centermass1)
            radiusmax.append(round(np.max(radius_contour), 2))
            radiusmin.append(round(np.min(radius_contour), 2))
            radiusmean.append(round(np.mean(radius_contour), 2))
            radius_contour = []
            dist2iso_struct.append(
                round(
                    np.linalg.norm(np.array(centermass1 - isocenter_plan)), 1
                )
            )
        dictionary_p["Target"] = names_p

        

        dictionary_p["Prescribed dose [Gy]"] = dose

        dictionary_p["Reference point dose [Gy]"] = dose_ref

        dictionary_p["Reference coordinates [mm]"] = coordinates

        dictionary_p["Distance to iso [mm]"] = dist2iso

        df_plan = pd.DataFrame(dictionary_p)
        
        for i, target in enumerate(targets):
            for _, name_p in enumerate(names_p):
                s = name_p[:4]
                if target.startswith(s) :
                    targets[i] = name_p
                    
            
        dictionary_s["Target"] = targets
        dictionary_s["Structure coordinates [mm]"] = centermass
      
        dictionary_s["Max radius [mm]"] = radiusmax
        
        dictionary_s["Min radius [mm]"] = radiusmin
       
        dictionary_s["Mean radius [mm]"] = radiusmean
        
        dictionary_s["Distance to iso (from structure) [mm]"] = dist2iso_struct
        
        
        df_struct = pd.DataFrame(dictionary_s)
        
        df_plan_struct = pd.merge(df_plan, df_struct, how='left', on=['Target'])
        if df_plan_struct.isnull().values.any() == True:
            warnings.warn(
                        "The returned dataframe contains NaN values because not all the elements in pydicom plan has the corresponding element in the pydicom structure"
                    )    
        print(df_plan_struct)#.iloc[:,5])
        return df_plan_struct
    
    def rotate(self, struct, angle, key, *args):
        """Method rotate.

        It allows to rotate all the points for a single structure.
        Rotation transformations are defined at the origin.
        For that reason it is necessary to bring the coordinates.
        to the origin before rotating. You can.
        `rotate <https://simple.wikipedia.org/wiki/Pitch,_yaw,_and_roll>'.
        an arbritrary structure (organ at risk, lesion or support.
        structure) in any of the 3 degrees of freedom roll, pitch or yaw.
        with the angle (in grades) of your choice.
        .. note::
            **Additional advantage:** You can accumulate rotations
            and traslations to study any combination.

        Example
        -------
        # rotate tumor 1.0º in yaw in isocenter.
        >>> moved = dicom.rotate('tumor', 1.0, 'yaw')
        # rotate lesion 1o in roll in [0.0, 0.0, 0.0].
        >>> iso = [0.0, 0.0, 0.0]
        >>> dicom.rotate('tumor', 1.0, 'yaw', iso)

        Parameters
        ----------
        struct : str
            Name of the structure to rotate
        angle : float
            Angle in degrees (positive or negative).
            Maximum angle allowed 360º.
        key : str
            Direction of rotation ('roll', 'pitch' or 'yaw')
        *args : list
            Origin in a list of float elements [x, y, z].
            By default, it is considered the isocenter of the
            structure file (last structure in RS DICOM called Coord 1).
            If not is able this structure, you can add an
            arbritrarly point.

        Returns
        -------
        pydicom.dataset.FileDataset
            Object with DICOM properties of the rotated structure.

        Raises
        ------
        TypeError, ValueError
            Angle is a float o int!.
            Angle is > 360º.
            Choose a correct key: roll, pitch, yaw.
            Type an origin [x,y,z] with float elements.
            One slice did not have all points of 3 elements.
            Type a correct name.

        """
        dicom_copy = copy.deepcopy(self)
        if (
            isinstance(angle, float) is False
            and isinstance(angle, int) is False
        ):
            raise TypeError("Angle is a float o int!")
        elif abs(angle) > 360:
            raise ValueError("Angle is > 360º")
        else:
            angle = np.radians(angle)
        n_id = {}
        length = len(dicom_copy.dicom_struct.StructureSetROISequence)
        if key in ["roll", "pitch", "yaw"]:
            pass
        else:
            raise ValueError("Choose a correct key: roll, pitch, yaw")
        for i, _ in enumerate(dicom_copy.dicom_struct.StructureSetROISequence):
            n_id[
                (dicom_copy.dicom_struct.StructureSetROISequence[i].ROIName)
            ] = i
        if struct in n_id:
            if not args:
                origin = (
                    dicom_copy.dicom_struct.ROIContourSequence[length - 1]
                    .ContourSequence[0]
                    .ContourData
                )
            elif len(args[0]) == 3 and all(
                isinstance(x, float) for x in args[0]
            ):
                origin = args[0]
            else:
                raise ValueError("Type an origin [x,y,z] with float elements")
            m = {
                "roll": np.array(
                    [
                        [1, 0, 0, 0],
                        [0, np.cos(angle), -np.sin(angle), 0],
                        [0, np.sin(angle), np.cos(angle), 0],
                        [0, 0, 0, 1],
                    ]
                ),
                "pitch": np.array(
                    [
                        [np.cos(angle), 0, np.sin(angle), 0],
                        [0, 1, 0, 0],
                        [-np.sin(angle), 0, np.cos(angle), 0],
                        [0, 0, 0, 1],
                    ]
                ),
                "yaw": np.array(
                    [
                        [np.cos(angle), -np.sin(angle), 0, 0],
                        [np.sin(angle), np.cos(angle), 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1],
                    ]
                ),
                "point2iso": np.array(
                    [
                        [1, 0, 0, -origin[0]],
                        [0, 1, 0, -origin[1]],
                        [0, 0, 1, -origin[2]],
                        [0, 0, 0, 1],
                    ]
                ),
                "iso2point": np.array(
                    [
                        [1, 0, 0, origin[0]],
                        [0, 1, 0, origin[1]],
                        [0, 0, 1, origin[2]],
                        [0, 0, 0, 1],
                    ]
                ),
            }
            for num, _ in enumerate(
                dicom_copy.dicom_struct.ROIContourSequence[
                    n_id[struct]
                ].ContourSequence
            ):
                if (
                    len(
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData
                    )
                    % 3
                    != 0
                ):
                    raise ValueError(
                        "One slice did not have all points of 3 elements"
                    )
                contour_rotated = []
                counter = 0
                while counter < int(
                    len(
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData
                    )
                    / 3
                ):
                    rotation = (
                        m["iso2point"]
                        @ m[key]
                        @ m["point2iso"]
                        @ [
                            float(
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * counter]
                            ),
                            float(
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * counter + 1]
                            ),
                            float(
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * counter + 2]
                            ),
                            1.0,
                        ]
                    )
                    contour_rotated.append(rotation[0])
                    contour_rotated.append(rotation[1])
                    contour_rotated.append(rotation[2])
                    counter = counter + 1
                (
                    dicom_copy.dicom_struct.ROIContourSequence[n_id[struct]]
                    .ContourSequence[num]
                    .ContourData
                ) = MultiValue(float, contour_rotated)
        else:
            raise ValueError("Type a correct name")
        return dicom_copy

    def translate(self, struct, delta, key, *args):
        """Method translate.

        It allows to translate all the points for a single structure.
        Rotation transformations are defined at the origin.
        For that reason it is necessary to bring the coordinates.
        to the origin before rotating.
        .. note::
            **Additional advantage:** You can accumulate rotations
            and traslations to study any combination.

        Example
        -------
        # translate tumor 1.0 mm in x in isocenter.
        >>> moved = dicom.translate('tumor', 1.0, 'x')
        # translate lesion 1.0 mm in x in [0.0, 0.0, 0.0].
        >>> iso = [0.0, 0.0, 0.0]
        >>> dicom.translate('tumor', 1.0, 'x', iso)


        Parameters
        ----------
        struct : str
            Name of the structure to translate
        delta : float
            Shift in mm (positive or negative).
            Maximum displacement allowed: 1000 mm (clinical perspective).
            More than 1000 mm has not relevance in patient displacement.
        key : str
            Direction of rotation ('x', 'y' or 'z')
        *args : list
            Origin in a list of float elements [x, y, z].
            By default, it is considered the isocenter of the
            structure file (last structure in RS DICOM called Coord 1).
            If not is able this structure, you can add an
            arbritrarly point.

        Returns
        -------
        pydicom.dataset.FileDataset
            Object with DICOM properties of the translated structure.

        Raises
        ------
        TypeError, ValueError
            delta is float or int!.
            delta is > 1000 mm.
            Choose a correct key: x, y, z.
            Type an origin [x,y,z] with float elements.
            One slice do not have all points of 3 elements.
            Type a correct name.

        """
        dicom_copy = copy.deepcopy(self)
        if (
            isinstance(delta, float) is False
            and isinstance(delta, int) is False
        ):
            raise TypeError("delta is float or int!")
        elif abs(delta) > 1000:
            raise ValueError("delta is > 1000 mm")
        n_id = {}
        length = len(dicom_copy.dicom_struct.StructureSetROISequence)
        if key in ["x", "y", "z"]:
            pass
        else:
            raise ValueError("Choose a correct key: x, y, z")
        for i, _ in enumerate(dicom_copy.dicom_struct.StructureSetROISequence):
            n_id[
                (dicom_copy.dicom_struct.StructureSetROISequence[i].ROIName)
            ] = i
        if struct in n_id:
            if not args:
                origin = (
                    dicom_copy.dicom_struct.ROIContourSequence[length - 1]
                    .ContourSequence[0]
                    .ContourData
                )
            elif len(args[0]) == 3 and all(
                isinstance(x, float) for x in args[0]
            ):
                origin = args[0]
            else:
                raise ValueError("Type an origin [x,y,z] with float elements")

            m = {
                "x": np.array(
                    [
                        [1, 0, 0, delta],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1],
                    ]
                ),
                "y": np.array(
                    [
                        [1, 0, 0, 0],
                        [0, 1, 0, delta],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1],
                    ]
                ),
                "z": np.array(
                    [
                        [1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, delta],
                        [0, 0, 0, 1],
                    ]
                ),
                "point2iso": np.array(
                    [
                        [1, 0, 0, -origin[0]],
                        [0, 1, 0, -origin[1]],
                        [0, 0, 1, -origin[2]],
                        [0, 0, 0, 1],
                    ]
                ),
                "iso2point": np.array(
                    [
                        [1, 0, 0, origin[0]],
                        [0, 1, 0, origin[1]],
                        [0, 0, 1, origin[2]],
                        [0, 0, 0, 1],
                    ]
                ),
            }
            for num, _ in enumerate(
                dicom_copy.dicom_struct.ROIContourSequence[
                    n_id[struct]
                ].ContourSequence
            ):
                if (
                    len(
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData
                    )
                    % 3
                    != 0
                ):
                    raise ValueError(
                        "One slice do not have all points of 3 elements"
                    )
                contour_translat = []
                counter = 0
                while counter < int(
                    len(
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData
                    )
                    / 3
                ):
                    translation = (
                        m["iso2point"]
                        @ m[key]
                        @ m["point2iso"]
                        @ [
                            float(
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * counter]
                            ),
                            float(
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * counter + 1]
                            ),
                            float(
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * counter + 2]
                            ),
                            1.0,
                        ]
                    )
                    contour_translat.append(translation[0])
                    contour_translat.append(translation[1])
                    contour_translat.append(translation[2])
                    counter = counter + 1
                (
                    dicom_copy.dicom_struct.ROIContourSequence[n_id[struct]]
                    .ContourSequence[num]
                    .ContourData
                ) = MultiValue(float, contour_translat)
        else:
            raise ValueError("Type a correct name")
        return dicom_copy

    def add_margin(self, struct, margin):
        """Method add/subtract margin.

        It allows to expand or subtract.
        `margin<www.aapm.org/meetings/2011SS/documents/MackieUncertainty.pdf>`.
        for a single structure.
        For each point is considered the distance between the.
        mean center (xmean, ymean) of each its slice plus (minus) the margin.
        By solve a quadratic equation between the circunference.
        with centre the point :math:`(x_0, y_0)` and :math:`radius = margin`
        and the line between :math:`(x_{mean}, y_{mean})` and.
        :math:`(x_0, y_0)` is calculated the point with the margin.
        :math:`(x, y)`.
        - The quadratic equation is
        ..math::
        x = x_0 +- sqrt{margin^2 / (1 + m^2},
        where :math:`m` is the slope of the tangent line.
        - The equation of the tangent line is :math:`y = m(x - x_0) + y_0`.

        Example
        -------
        # add 0.7 mm to the tumor.
        >>> dicom.add_margin('tumor', 0.7)
        # subtract 1.2 mm to the tumor.
        >>> dicom.add_margin('tumor', -1.2)


        Parameters
        ----------
        name_struct : str
            Name of the structure to modify the margin.
        margin : float
            The expansion (positive) or substraction.
            (negative) in mm.

        Returns
        -------
        pydicom.dataset.FileDataset
            Object with DICOM properties of the structure.

        Raises
        ------
        TypeError, ValueError
            Contour needs at least 1 point.
            Type a correct name.

        """
        dicom_copy = copy.deepcopy(self)
        n_id = {}
        if isinstance(margin, float):
            pass
        else:
            raise TypeError(f"{margin} must be float")
        for item, _ in enumerate(
            dicom_copy.dicom_struct.StructureSetROISequence
        ):
            n_id[
                dicom_copy.dicom_struct.StructureSetROISequence[item].ROIName
            ] = item
        if struct in n_id:
            for num, _ in enumerate(
                dicom_copy.dicom_struct.ROIContourSequence[
                    n_id[struct]
                ].ContourSequence
            ):
                contourmargin = []
                longitude = int(
                    len(
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData
                    )
                    / 3
                )
                if longitude > 1:
                    xmean = np.mean(
                        [
                            (
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * i]
                            )
                            for i in range(longitude)
                        ]
                    )
                    ymean = np.mean(
                        [
                            (
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * i + 1]
                            )
                            for i in range(longitude)
                        ]
                    )
                    counter = 0
                    while counter < longitude:
                        x0 = (
                            dicom_copy.dicom_struct.ROIContourSequence[
                                n_id[struct]
                            ]
                            .ContourSequence[num]
                            .ContourData[3 * counter]
                        )
                        y0 = (
                            dicom_copy.dicom_struct.ROIContourSequence[
                                n_id[struct]
                            ]
                            .ContourSequence[num]
                            .ContourData[3 * counter + 1]
                        )
                        if x0 != xmean:
                            m = (ymean - y0) / (xmean - x0)
                            sol_x1 = x0 + np.sqrt(margin**2 / (1 + m**2))
                            sol_x2 = x0 - np.sqrt(margin**2 / (1 + m**2))
                            y1 = m * (sol_x1 - x0) + y0
                            y2 = m * (sol_x2 - x0) + y0
                            dist1 = (
                                (xmean - sol_x1) ** 2 + (ymean - y1) ** 2
                            ) ** 0.5
                            dist2 = (
                                (xmean - sol_x2) ** 2 + (ymean - y2) ** 2
                            ) ** 0.5
                            if margin >= 0 and dist1 >= dist2:
                                contourmargin.append(sol_x1)
                                contourmargin.append(y1)
                            elif margin >= 0 and dist1 < dist2:
                                contourmargin.append(sol_x2)
                                contourmargin.append(y2)
                            elif margin < 0 and dist1 <= dist2:
                                contourmargin.append(sol_x1)
                                contourmargin.append(y1)
                            else:
                                contourmargin.append(sol_x2)
                                contourmargin.append(y2)
                        else:
                            contourmargin.append(x0)
                            if margin >= 0 and y0 >= ymean:
                                y1 = y0 + margin
                                contourmargin.append(y1)
                            elif margin >= 0 and y0 < ymean:
                                y1 = y0 - margin
                                contourmargin.append(y1)
                            elif margin < 0 and y0 >= ymean:
                                y1 = y0 + margin
                                contourmargin.append(y1)
                            else:
                                y1 = y0 - margin
                                contourmargin.append(y1)
                        contourmargin.append(
                            (
                                dicom_copy.dicom_struct.ROIContourSequence[
                                    n_id[struct]
                                ]
                                .ContourSequence[num]
                                .ContourData[3 * counter + 2]
                            )
                        )
                        counter = counter + 1
                elif longitude == 1 and margin > 0:
                    x = (
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData[0]
                    )
                    y = (
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData[1]
                    )
                    z = (
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData[2]
                    )
                    contourmargin = [
                        x,
                        y + margin,
                        z,
                        x + margin,
                        y,
                        z,
                        x,
                        y - margin,
                        z,
                        x - margin,
                        y,
                        z,
                    ]
                elif longitude == 1 and margin <= 0:
                    contourmargin = (
                        dicom_copy.dicom_struct.ROIContourSequence[
                            n_id[struct]
                        ]
                        .ContourSequence[num]
                        .ContourData
                    )
                else:
                    raise ValueError("Contour needs at least 1 point")
                (
                    dicom_copy.dicom_struct.ROIContourSequence[n_id[struct]]
                    .ContourSequence[num]
                    .ContourData
                ) = MultiValue(float, contourmargin)
        else:
            raise ValueError("Type a correct name")
        return dicom_copy
