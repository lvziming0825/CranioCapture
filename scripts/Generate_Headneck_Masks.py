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


import os
import cv2
import numpy as np
import onnxruntime as ort
import mediapipe as mp


INPUT_DIR = "path/to/images"

OUTPUT_DIR = "path/to/masks"

MODEL_PATH = "path/to/model.onnx"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

SAVE_WHITE_BG_PREVIEW = True

MASK_THRESHOLD = 127

NECK_MARGIN_RATIO = 0.5

FEATHER_BLUR = 9

USE_PREVIOUS_FACE_BOX = True


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def list_images(folder):
    files = []
    for name in os.listdir(folder):
        ext = os.path.splitext(name)[1].lower()
        if ext in IMAGE_EXTS:
            files.append(os.path.join(folder, name))
    files.sort()
    return files


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def normalize_to_uint8(arr):
    arr = arr.astype(np.float32)
    arr = np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=0.0)

    if arr.min() < 0.0 or arr.max() > 1.0:
        arr = sigmoid(arr)

    vmin = float(arr.min())
    vmax = float(arr.max())

    if vmax - vmin < 1e-6:
        return np.zeros_like(arr, dtype=np.uint8)

    arr = (arr - vmin) / (vmax - vmin)
    arr = np.clip(arr, 0.0, 1.0)

    return (arr * 255.0).round().astype(np.uint8)


def extract_mask_from_output(output_array):

    arr = np.array(output_array)

    if arr.ndim == 4:
        if arr.shape[0] == 1 and arr.shape[1] >= 1:
            arr = arr[0, 0]

        elif arr.shape[0] == 1 and arr.shape[-1] >= 1:
            arr = arr[0, :, :, 0]

        else:
            raise ValueError(f"Unexpected 4D output shape: {arr.shape}")

    elif arr.ndim == 3:

        if arr.shape[0] == 1:
            arr = arr[0]

        elif arr.shape[-1] == 1:
            arr = arr[:, :, 0]

        else:
            arr = arr[0]

    elif arr.ndim == 2:
        pass

    else:
        raise ValueError(f"Unexpected output ndim: {arr.ndim}")

    return arr


def prepare_input_bgr(image_bgr, input_h, input_w):

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    resized = cv2.resize(
        image_rgb,
        (input_w, input_h),
        interpolation=cv2.INTER_LINEAR
    )

    x = resized.astype(np.float32) / 255.0

    x = np.transpose(x, (2, 0, 1))
    x = np.expand_dims(x, axis=0)

    return x


mp_face_detection = mp.solutions.face_detection

face_detector = mp_face_detection.FaceDetection(
    model_selection=1,
    min_detection_confidence=0.35
)


def find_face_box_bgr(image_bgr):

    h, w = image_bgr.shape[:2]

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    result = face_detector.process(image_rgb)

    if not result.detections:
        return None

    best_det = max(
        result.detections,
        key=lambda d: d.score[0] if d.score else 0
    )

    bbox = best_det.location_data.relative_bounding_box

    x1 = int(bbox.xmin * w)
    y1 = int(bbox.ymin * h)

    x2 = int((bbox.xmin + bbox.width) * w)
    y2 = int((bbox.ymin + bbox.height) * h)

    x1 = max(0, min(w - 1, x1))
    y1 = max(0, min(h - 1, y1))
    x2 = max(0, min(w - 1, x2))
    y2 = max(0, min(h - 1, y2))

    if x2 <= x1 or y2 <= y1:
        return None

    return x1, y1, x2, y2


def get_largest_component(mask_bin):

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask_bin.astype(np.uint8),
        connectivity=8
    )

    if num_labels <= 1:
        return mask_bin

    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])

    largest = (labels == largest_label).astype(np.uint8) * 255

    return largest


def make_headneck_mask(person_mask, face_box):

    h, w = person_mask.shape[:2]

    x1, y1, x2, y2 = face_box

    face_h = y2 - y1

    cutoff_y = int(y2 + NECK_MARGIN_RATIO * face_h)

    cutoff_y = max(0, min(h - 1, cutoff_y))

    roi = np.zeros((h, w), dtype=np.uint8)

    roi[:cutoff_y, :] = 255

    final_mask = cv2.bitwise_and(person_mask, roi)

    final_mask = get_largest_component(final_mask)

    kernel_close = np.ones((11, 11), np.uint8)
    kernel_open = np.ones((3, 3), np.uint8)

    final_mask = cv2.morphologyEx(
        final_mask,
        cv2.MORPH_CLOSE,
        kernel_close
    )

    final_mask = cv2.morphologyEx(
        final_mask,
        cv2.MORPH_OPEN,
        kernel_open
    )

    if FEATHER_BLUR > 0:

        blur_size = FEATHER_BLUR

        if blur_size % 2 == 0:
            blur_size += 1

        final_mask = cv2.GaussianBlur(
            final_mask,
            (blur_size, blur_size),
            0
        )

    return final_mask


def make_white_bg_preview(image_bgr, mask_u8):

    alpha = mask_u8.astype(np.float32) / 255.0

    alpha_3 = np.stack([alpha, alpha, alpha], axis=-1)

    fg = image_bgr.astype(np.float32)

    white_bg = np.ones_like(fg, dtype=np.float32) * 255.0

    composite = fg * alpha_3 + white_bg * (1.0 - alpha_3)

    composite = np.clip(composite, 0, 255).astype(np.uint8)

    return composite


def main():

    ensure_dir(OUTPUT_DIR)

    image_paths = list_images(INPUT_DIR)

    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

    session = ort.InferenceSession(
        MODEL_PATH,
        providers=providers
    )

    input_meta = session.get_inputs()[0]

    input_name = input_meta.name
    input_shape = input_meta.shape

    input_h = input_shape[2]
    input_w = input_shape[3]

    if isinstance(input_h, str) or input_h is None:
        input_h, input_w = 384, 384

    previous_face_box = None

    for idx, img_path in enumerate(image_paths, start=1):

        stem = os.path.splitext(os.path.basename(img_path))[0]

        print(f"[{idx}/{len(image_paths)}] {stem}")

        image_bgr = cv2.imread(img_path)

        if image_bgr is None:
            continue

        orig_h, orig_w = image_bgr.shape[:2]

        # =================================================
        # ONNX matting
        # =================================================

        x = prepare_input_bgr(
            image_bgr,
            input_h,
            input_w
        )

        outputs = session.run(None, {input_name: x})

        raw_mask = extract_mask_from_output(outputs[0])

        raw_mask_resized = cv2.resize(
            raw_mask,
            (orig_w, orig_h),
            interpolation=cv2.INTER_LINEAR
        )

        soft_mask = normalize_to_uint8(raw_mask_resized)

        # =================================================
        # binary person mask
        # =================================================

        person_mask = (
            soft_mask > MASK_THRESHOLD
        ).astype(np.uint8) * 255

        # =================================================
        # face detection
        # =================================================

        face_box = find_face_box_bgr(image_bgr)

        if face_box is None:

            if USE_PREVIOUS_FACE_BOX and previous_face_box is not None:

                face_box = previous_face_box

                print("Using previous face box")

            else:
                print("Face detection failed")
                continue

        else:
            previous_face_box = face_box


        final_mask_soft = make_headneck_mask(
            soft_mask,
            face_box
        )

        final_mask_bin = (
            final_mask_soft > 127
        ).astype(np.uint8) * 255


        out_bin = os.path.join(
            OUTPUT_DIR,
            f"{stem}_mask_bin.png"
        )

        cv2.imwrite(out_bin, final_mask_bin)


        if SAVE_WHITE_BG_PREVIEW:

            preview = make_white_bg_preview(
                image_bgr,
                final_mask_soft
            )

            out_preview = os.path.join(
                OUTPUT_DIR,
                f"{stem}_whitebg.png"
            )

            cv2.imwrite(out_preview, preview)

    print("Done.")


if __name__ == "__main__":
    main()
