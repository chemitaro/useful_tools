from setuptools import find_packages, setup

setup(
    name="useful_tools",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "import_collector=apps.import_collector:main",
            "s2t=apps.s2t:app_run",
            "scrape_web=apps.scrape_web:run_from_cli",
            "git_diff=apps.git_diff:main",
            "class_diagram=apps.class_diagram:run_from_cli",
        ]
    },
    install_requires=[
        # 依存関係をリストアップ
        "argparse",
    ],
    author="Chemitaro",
    author_email="iwasi_44@hotmail.com",
    description="This package provides tools for dependency analysis and speech-to-text conversion.",
    keywords="dependency analysis, speech-to-text",
    url="http://example.com/YourProjectHome",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
)
