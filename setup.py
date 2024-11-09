from setuptools import setup, find_packages

setup(
    name="server-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    author="geek2geeks",
    description="High-performance AI server infrastructure optimized for RTX 3090",
    keywords="AI, GPU, PyTorch, CUDA, RTX3090",
    url="https://github.com/geek2geeks/server-ai",
    python_requires=">=3.10",
)