#  moondream.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
from typing import Any

import torch
from PIL.Image import Image
from transformers import AutoModelForCausalLM

DEFAULT_MOONDREAM_MODEL: str = "vikhyatk/moondream2"
DEFAULT_MOONDREAM_REVISION: str = "2025-01-09"


class Moondream:
    """Wraps Moondream2 for free-form visual question answering (VQA).

    Florence-2 has no open-ended VQA task token, so this second, smaller
    model is kept loaded alongside Florence2 specifically for `query`.
    """

    device: str
    model: Any

    def __init__(self, model_id: str = DEFAULT_MOONDREAM_MODEL, revision: str = DEFAULT_MOONDREAM_REVISION) -> None:
        if torch.backends.mps.is_available():
            self.device = "mps:0"
            torch_dtype = torch.float16
        elif torch.cuda.is_available():
            self.device = "cuda"
            torch_dtype = torch.float16
        else:
            self.device = "cpu"
            torch_dtype = torch.float32

        # `transformers` wraps the auto classes in a decorator that mypy reads as taking a
        # model instance in the first slot, so the model id below looks like the wrong type.
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            revision=revision,
            trust_remote_code=True,
            torch_dtype=torch_dtype,
        ).to(self.device)  # type: ignore[arg-type]

    def query(self, images: list[Image], question: str) -> list[str]:
        res = []
        for img in images:
            with img.convert("RGB") as rgb_img:
                answer = self.model.query(rgb_img, question)["answer"]
                res.append(answer)
        return res
