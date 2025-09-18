#  florence2.py
#
#  Copyright (c) 2025 Junpei Kawamoto
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

    def generate(self, prompt: str, images: list[Image]) -> list[str]:
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
                    generated_text, task=prompt, image_size=(rgb_img.width, rgb_img.height)
                )

                res.append(parsed_answer[prompt].strip())

        return res


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
