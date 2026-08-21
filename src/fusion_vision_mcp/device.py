#  device.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
"""Picks which torch device a model loads onto."""

import torch


def resolve_device(explicit: str | None = None) -> str:
    """Returns the torch device string to use.

    An explicit override (e.g. from --device) always wins, so an implementer can pin a
    model to a specific accelerator, force CPU on a shared GPU box, or point at a
    non-default device index -- auto-detection only runs when nothing was requested.
    """
    if explicit:
        return explicit
    if torch.backends.mps.is_available():
        return "mps:0"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
