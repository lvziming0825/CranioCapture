This repository provides the implementation and supplementary materials associated with the manuscript:

**A Locally Deployable Smartphone-Video Pipeline for Scalable 3D Craniofacial Assessment in Low-Resource Clinical Settings**

The workflow includes:

1. Smartphone video acquisition
2. Frame extraction
3. Foreground masking
4. COLMAP reconstruction
5. 2D Gaussian Splatting
6. Metric calibration
7. Quantitative evaluation


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

