from setuptools import find_packages, setup


def get_version() -> str:
    return "0.1.35"

install_requires = [
    "requests",
    "tqdm",
    "getmac>=0.8.3",
    "pyyaml>=5.1",
    "importlib_metadata;python_version<'3.8'",
    "packaging>=20.9",
    "Pillow==8.4"
]

extras = {}

setup(
    name="sharpai_hub",
    version=get_version(),
    author="SharpAI LLC",
    author_email="simba@sharpai.org",
    description=(
        "Client library to download application from sharpai hub"
    ),
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords=(
        "model-hub machine-learning models natural-language-processing deep-learning"
        " Edge AI"
    ),
    license="MIT",
    url="https://github.com/SharpAI/sharpai_hub",
    package_dir={"": "src"},
    packages=find_packages("src"),
    extras_require=extras,
    entry_points={
        "console_scripts": [
            "sharpai-cli=sharpai_hub.cli:main"
        ]
    },
    python_requires=">=3.6.0",
    install_requires=install_requires,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
