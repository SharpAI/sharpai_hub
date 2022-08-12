from setuptools import find_packages, setup


def get_version() -> str:
    return "0.1.0"


install_requires = [
    "requests",
    "tqdm",
    "pyyaml>=5.1",
    "importlib_metadata;python_version<'3.8'",
    "packaging>=20.9",
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
    license="Apache",
    url="https://github.com/SharpAI/sharpai_hub",
    package_dir={"": "src"},
    packages=find_packages("src"),
    extras_require=extras,
    entry_points={
        "console_scripts": [
            "sharpai-cli=sharpai_hub.cli:main"
        ]
    },
    python_requires=">=3.7.0",
    install_requires=install_requires,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
