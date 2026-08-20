#  florence2.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php

from enum import StrEnum
from typing import Any

import torch
from PIL.Image import Image
from torch import dtype
from transformers import AutoProcessor, Florence2ForConditionalGeneration

from .subprocess import subprocess


class CaptionLevel(StrEnum):
    NORMAL = "<CAPTION>"
    DETAILED = "<DETAILED_CAPTION>"
    MORE_DETAILED = "<MORE_DETAILED_CAPTION>"


class Florence2:
    device: str
    torch_dtype: dtype
    model: Any
    processor: Any

    def __init__(self, model_id: str) -> None:
        if torch.backends.mps.is_available():
            self.device = "mps:0"
            self.torch_dtype = torch.float16
        elif torch.cuda.is_available():
            self.device = "cuda"
            self.torch_dtype = torch.float32
        else:
            self.device = "cpu"
            self.torch_dtype = torch.float32

        self.model = Florence2ForConditionalGeneration.from_pretrained(
            model_id, dtype=self.torch_dtype, trust_remote_code=True
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(
            model_id, trust_remote_code=True, clean_up_tokenization_spaces=True
        )

    def ocr(self, images: list[Image]) -> list[str]:
        return self.generate("<OCR>", images)

    def caption(self, images: list[Image], level: CaptionLevel = CaptionLevel.NORMAL) -> list[str]:
        return self.generate(str(level.value), images)

    def detect_objects(self, images: list[Image], object_name: str) -> list[dict[str, Any]]:
        return self.generate_structured("<CAPTION_TO_PHRASE_GROUNDING>", images, text=object_name)

    def point_objects(self, images: list[Image], object_name: str) -> list[dict[str, Any]]:
        grounded = self.generate_structured("<CAPTION_TO_PHRASE_GROUNDING>", images, text=object_name)
        return [_bboxes_to_points(region) for region in grounded]

    def dense_region_caption(self, images: list[Image]) -> list[dict[str, Any]]:
        return self.generate_structured("<DENSE_REGION_CAPTION>", images)

    def generate(self, prompt: str, images: list[Image]) -> list[str]:
        res = []
        for parsed in self._run(prompt, images):
            res.append(parsed.strip())
        return res

    def generate_structured(self, task: str, images: list[Image], text: str | None = None) -> list[dict[str, Any]]:
        prompt = task if text is None else task + text
        return list(self._run(prompt, images, task=task))

    def _run(self, prompt: str, images: list[Image], task: str | None = None) -> list[Any]:
        task = task or prompt
        res = []
        for img in images:
            with img.convert("RGB") as rgb_img:
                inputs = self.processor(text=prompt, images=rgb_img, return_tensors="pt").to(
                    self.device, self.torch_dtype
                )

                generated_ids = self.model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    num_beams=3,
                    do_sample=False,
                )
                generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

                parsed_answer = self.processor.post_process_generation(
                    generated_text, task=task, image_size=(rgb_img.width, rgb_img.height)
                )

                res.append(parsed_answer[task])

        return res


def _bboxes_to_points(region: dict[str, Any]) -> dict[str, Any]:
    """Converts a Florence-2 bboxes/labels region result into center-point/labels form."""
    points = [[(x1 + x2) / 2, (y1 + y2) / 2] for x1, y1, x2, y2 in region.get("bboxes", [])]
    return {"points": points, "labels": region.get("labels", [])}


class Florence2SP:
    model_id: str

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    @subprocess
    def ocr(self, images: list[Image]) -> list[str]:
        return Florence2(self.model_id).ocr(images)

    @subprocess
    def caption(self, images: list[Image], level: CaptionLevel = CaptionLevel.NORMAL) -> list[str]:
        return Florence2(self.model_id).caption(images, level)

    @subprocess
    def detect_objects(self, images: list[Image], object_name: str) -> list[dict[str, Any]]:
        return Florence2(self.model_id).detect_objects(images, object_name)

    @subprocess
    def point_objects(self, images: list[Image], object_name: str) -> list[dict[str, Any]]:
        return Florence2(self.model_id).point_objects(images, object_name)

    @subprocess
    def dense_region_caption(self, images: list[Image]) -> list[dict[str, Any]]:
        return Florence2(self.model_id).dense_region_caption(images)

    @subprocess
    def generate(self, prompt: str, images: list[Image]) -> list[str]:
        return Florence2(self.model_id).generate(prompt, images)
