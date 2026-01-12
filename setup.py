from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in customer_portal_manager/__init__.py
from customer_portal_manager import __version__ as version

setup(
    name="customer_portal_manager",
    version=version,
    description="Customer Portal Management - Single-screen management portal for customer users",
    author="ITQAN LLC",
    author_email="info@itqan-kw.net",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
