<h1 align="center"> <ins>egenioussBench</ins> :<br> A New Dataset for Geospatial Visual Localisation<br></h1>
<p align="center">
  <p align="center">
    <a href="https://scholar.google.com/citations?user=sAOBwmkAAAAJ">Phillipp Fanta-Jende</a>
    ·
    <a href="https://scholar.google.com/citations?user=B9VAGzcAAAAJ">Francesco Vultaggio</a>
    ·
    <a href="https://www.researchgate.net/profile/Alexander-Kern-2">Alexander Kern</a>
    ·
    <a href="https://www.tu-braunschweig.de/igp/mitarbeiter/loeper-yasmin">Yasmin Loeper</a>
    ·
    <a href="https://scholar.google.com/citations?user=Cy4pRKkAAAAJ">Markus Gerke</a>
  </p>
  <h2 align="center"><p>
    <a href="https://isprs-archives.copernicus.org/articles/XLVIII-1-W6-2025/75/2025/" align="center">Paper</a> | 
    <a href="https://www.egeniouss.eu/" align="center">Project Page</a> |
    <a href="https://zenodo.org/records/17644019" align="center">Dataset</a>
  </p></h2>
  <div align="center"></div>
</p>
<br/>
<p align="center">
    <img src="assets/egeniouss_logo.svg" alt="example" width=80%>
</p>

<p align="center">
<em>egenioussBench couples a city-scale aerial 3D mesh, a CityGML LoD2 model, and centimetre-accurate smartphone ground-truth poses to benchmark mesh- and object-based localisation under realistic, city-scale conditions.</em>
</p>

---
⚠️ **Submission deadline extended to November 2026**⚠️ 

---
## Table of Contents

* [Overview](#overview)
* [Dataset Structure](#dataset-structure)
  * [Components](#components)
    * [1. Airborne 3D Mesh](#1-airborne-3d-mesh)
    * [2. CityGML-LoD2 Model](#2-citygml-lod2-model)
    * [3. Smartphone Query Dataset](#3-smartphone-query-dataset)
* [Evaluation](#evaluation)
  * [Metrics](#metrics)
  * [Running the Evaluation Script](#running-the-evaluation-script)
* [Submissions](#submissions)
* [Baseline](#baseline)
* [Citation](#citation)
* [Acknowledgements](#acknowledgements)

---

## Overview

**egenioussBench** is a benchmark designed to evaluate visual localisation algorithms that rely on geospatial reference data.
The dataset provides:

1. **A high-resolution aerial 3D mesh** reconstructed from oblique imagery
2. **A CityGML LoD2 building model**
3. **Smartphone query images** captured from a Pixel8 with a tightly-coupled INS, providing cm-accurate, map-independent ground truth
4. **Smartphone pose priors** coming from the internal GNSS receiver

The goal is to support research on scalable localisation pipelines that operate at city scale and across different reference representations.


---

## Dataset Structure

```
egenioussBench/
├── lod2/                       # CityGML LoD2 model of Braunschweig
├── mesh/                       # Airborne 3D mesh (7.5 cm GSD)
├── metadata
│   └── camera_parameters.txt
└── query_images
    ├── test/                   # Test images
    ├── test_android_poses.csv
    ├── val/                    # Validation
    ├── val_android_poses.txt
    └── val_gt_poses.txt


```
| Split          | Purpose                | Size                     | GT Available? |
| -------------- | ---------------------- | ------------------------ | ------------- |
| **Validation** | method development     | 412 seq. images          | ✓             |
| **Test**       | leaderboard evaluation | 42 non-co-visible images | ✗             |

The test split is explicitly **non-co-visible** to enforce cold-start localisation.
The dataset is available on [Zenodo](https://zenodo.org/records/17644019)

### Components

#### **1. Airborne 3D Mesh**

* Derived from oblique imagery (UltraCam Osprey 4.1)
* ≈1550 m AGL
* 7.5 cm GSD (nadir)
* Georeferencing accuracy ≈1 GSD (XY) / 1.5 GSD (Z)

Provides a realistic, deployable reference model for cross-view localisation.

#### **2. CityGML LoD2 Model**

* Official city model of Braunschweig
* Footprints from cadastral data
* Generalised roof shapes
* Typical corner accuracy ≈10 cm relative to mesh

Represents textureless, low-detail geometry for object-based localisation.

#### **3. Smartphone Query Dataset**

* 2709 RGB images collected in January 2024
* Resampled to 960×1280 px (~4 cm GSD)
* PPK + GCP/CP-aided bundle adjustment
* Final pose accuracy:

  * **4 cm** (XY) / **7 cm** (Z) mean
  * **0.04°** mean orientation error



---
## Evaluation

The benchmark evaluates **6-DoF camera poses** predicted for each query image.

Participants submit a CSV file containing:

```
# Ground truth poses for validation images
# IMAGE_NAME qw qx qy qz UTMx UTMy alt
```

We use the same camera coordinate definition as Pix4D, for reference please look at the [documentation](https://support.pix4d.com/hc/en-us/articles/202559089).

### Metrics

We report:

* **Binned recall** at:

  * 0.5 m / 2°
  * 2 m / 5°
  * 5 m / 10°
* **Outliers**
* **Median translation error**
* **Median rotation error**
* **RMSE translation error**
* **RMSE rotation error**

Mesh-based and LoD2-based methods are evaluated **separately**.

### Running the evaluation script

We provide a lightweight Python evaluation script to self validate on the validation script, the same code will be used to evaluate the test split:

```bash
python eval.py \
    --pred poses.csv \
    --gt val/poses_gt.csv \
    --config eval_config.yaml \
    --visualize true
    --experiment debug
```

---

### Submissions

Submissions should be sent by email to **egeniouss@ait.ac.at**.  
Evaluation results will be returned via the same address. Multiple submissions are allowed, but only **one submission per day** will be evaluated per team.

By submitting, participants grant the organizers permission to publish the resulting scores on the public leaderboard.


---

### Notes

- We are aware that the orientation in the pose prior files `*_android_poses.csv` are uneliable. This is caused by the internal magnetometer of the smartphone converging to the wrong orientation. We suggest not to rely on the orientation priors to bootstrap the camera orientation. 

- We have extended the deadline for submission of the results to November 2026

---

## Citation

If you use egenioussBench in research, please consider citing:

```
@article{fanta-jende2025egenioussBench,
  title={egenioussBench: A New Dataset for Geospatial Visual Localisation},
  author={Fanta-Jende, Phillipp and Vultaggio, Francesco and Kern, Alexander and Loeper, Yasmin and Gerke, Markus},
  year={2025}
}
```

---

## Acknowledgements

<p align="center">
  <img src="assets/egeniouss_logo.svg" height="45">
  <img src="assets/ait_logo.jpg" height="45">
  <img src="assets/tu_bs_logo.gif" height="45">
  <img src="assets/eu_logo.png" height="45">
</p>

This work is part of the EU-Horizon **egeniouss** project.
