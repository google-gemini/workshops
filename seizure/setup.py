from setuptools import setup, find_packages

setup(
    name="seizure_score_ai",
    version="0.1.0",
    description="AI-powered ILAE seizure score calculator",
    author="Vineet Reddy",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.40.0",
        "google-adk>=0.3.0",
        "python-dotenv>=1.0.0",
        "pillow>=10.0.0",
    ],
)

