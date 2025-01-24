#  SPDX-License-Identifier: GPL-3.0-or-later
#  Copyright (C) 2025 Bailrigg FM
#  All rights reserved.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name="BFM_Silence_Detector",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "RPi.GPIO",
        "requests",
        "python-dotenv"
    ],
    entry_points={
        'console_scripts': [
            'SilenceDetector=BFM_Silence_Detector.main:main',  # Run the main function
        ],
    },
)
