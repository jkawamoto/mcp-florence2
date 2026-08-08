#  __main__.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
from typing import cast

from rich_click import Command

from mcp_florence2.cli import main

command = cast(Command, main)
command.main()
