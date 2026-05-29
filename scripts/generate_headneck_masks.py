"""
CranioCapture

Head-neck foreground mask generation.

This script combines:

1. ONNX-based foreground segmentation
2. MediaPipe face detection
3. Automatic head-neck region extraction

The generated masks are used for
COLMAP reconstruction and 2D Gaussian Splatting.

Dependencies:
- OpenCV
- ONNX Runtime
- MediaPipe
- NumPy

Author:
Richard LYU
"""
