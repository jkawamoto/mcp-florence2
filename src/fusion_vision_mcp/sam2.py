#  sam2.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
"""SAM2-backed segmentation: turns a bounding box into the object's silhouette."""

from typing import Any, Final

import numpy as np
import torch
from numpy.typing import NDArray
from PIL.Image import Image
from transformers import Sam2Model, Sam2Processor

from .device import resolve_device

#: Measured on CPU over tiny/small/base-plus: `small` costs ~0.06s more per call
#: and ~34MB more than `tiny` for a better mask, while `base-plus` roughly doubles
#: inference time for a marginal gain. `small` is the middle that earns its keep.
DEFAULT_SAM2_MODEL: Final[str] = "facebook/sam2.1-hiera-small"

#: SAM2 decodes masks on a fixed grid regardless of input size. Masks are upscaled
#: to the image's own pixels for reporting, but detail finer than
#: `max(image side) / MASK_DECODE_RESOLUTION` pixels is not actually resolved.
MASK_DECODE_RESOLUTION: Final[int] = 256


class Sam2:
    """Wraps SAM2 for prompted segmentation.

    Florence-2 locates objects but only as bounding boxes, which cannot say
    whether two things touch: any two boxes overlap as soon as one object is in
    front of another. Segmentation gives the actual silhouette, which is what the
    measurements in `geometry` need.
    """

    device: str
    torch_dtype: torch.dtype
    model: Any
    processor: Any

    def __init__(self, model_id: str = DEFAULT_SAM2_MODEL, device: str | None = None) -> None:
        self.device = resolve_device(device)
        self.torch_dtype = torch.float32 if self.device == "cpu" else torch.float16

        self.processor = Sam2Processor.from_pretrained(model_id)
        self.model = Sam2Model.from_pretrained(model_id, dtype=self.torch_dtype).to(self.device)
        self.model.eval()

    def segment(self, image: Image, boxes: list[list[int]]) -> list[NDArray[np.bool_]]:
        """Return one mask per input box, on the image's own pixel grid.

        SAM2 proposes several candidate masks per box; the one it scores highest
        is kept. Candidate logits are upscaled before thresholding rather than
        after, so the boundary follows the object rather than the decode grid.
        """
        if not boxes:
            return []

        with image.convert("RGB") as rgb:
            inputs = self.processor(images=rgb, input_boxes=[boxes], return_tensors="pt").to(
                self.device, self.torch_dtype
            )
            with torch.no_grad():
                outputs = self.model(**inputs)

            masks: list[NDArray[np.bool_]] = []
            for index in range(len(boxes)):
                best = int(outputs.iou_scores[0, index].argmax())
                logits = outputs.pred_masks[0, index, best][None, None]
                upscaled = torch.nn.functional.interpolate(
                    logits.float(), size=(rgb.height, rgb.width), mode="bilinear", align_corners=False
                )
                masks.append((upscaled[0, 0] > 0).cpu().numpy())
            return masks
