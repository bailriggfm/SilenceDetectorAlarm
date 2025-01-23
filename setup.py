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
