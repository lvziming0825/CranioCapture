This repository provides the implementation and supplementary materials associated with the manuscript:

**A Locally Deployable Smartphone-Video Pipeline for Scalable 3D Craniofacial Assessment in Low-Resource Clinical Settings**

The workflow includes:

1. Smartphone video acquisition
2. Frame extraction & Foreground masking
3. COLMAP reconstruction
4. 2D Gaussian Splatting
5. Metric calibration
6. Quantitative evaluation


## Phase 1. Smartphone Video Acquisition
The patient is seated in a natural head position while a smartphone is moved along an inverse S-shaped trajectory around the face.

A 5-second demonstration of the smartphone video acquisition procedure.

<table border="0">
<tr>
<td width="75%" align="center">
<b>Workflow</b>
</td>

<td width="25%" align="center">
<b>5-second Demo</b>
</td>
</tr>

<tr>

<td width="75%" align="center" valign="middle">
<img src="docs/images/data_acquisition.jpg" width="100%">
</td>

<td width="25%" align="center" valign="middle">
<img src="docs/gifs/github_demo_5s.gif" width="200">
</td>

</tr>
</table>


## Phase 2. Frame Extraction & Foreground Masking

Video frames are extracted from the recorded smartphone video. A foreground matting model is subsequently applied to remove background structures and generate patient-specific facial masks.

<p align="center">
  <img src="docs/images/frame_masking.jpg" width="90%">
</p>

**Related Script**

[`Extract_Frames.py`](scripts/Extract_Frames.py)

[`Generate_Headneck_Masks.py`](scripts/Generate_Headneck_Masks.py)


## Phase 3. COLMAP-Based Camera Pose Estimation and Sparse Reconstruction

COLMAP is used to estimate camera poses and generate a sparse 3D reconstruction from multi-view facial images.

<table border="0">
<tr>

<td width="65%" align="center" valign="middle">
<img src="docs/images/colmap_reconstruction.jpg" width="100%">
</td>

<td width="35%" align="center" valign="middle">
<img src="docs/gifs/COLMAP_reconstruction_5s.gif" width="100%">
</td>

</tr>
</table>

<p align="center">
Feature Extraction → Feature Matching → Camera Pose Estimation → Sparse Reconstruction
</p>
