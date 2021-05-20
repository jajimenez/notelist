"""Notelist Setup script."""

import setuptools as st


if __name__ == "__main__":
    # Long description
    with open("README.md") as f:
        long_desc = f.read()

    # Requirements
    with open("requirements.txt") as f:
        install_req = [i.replace("\n", "") for i in f.readlines()]

    # Setup
    st.setup(
        name="notelist",
        version="0.1.0",
        description="Note taking REST API",
        author="Jose A. Jimenez",
        author_email="jajimenezcarm@gmail.com",
        license="MIT",
        long_description=long_desc,
        long_description_content_type="text/markdown",
        url="https://github.com/jajimenez/notelist",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: MIT License"],
        python_requires=">=3.9.2",
        install_requires=install_req,
        packages=[
            "notelist", "notelist.models", "notelist.schemas",
            "notelist.resources", "notelist.migrations",
            "notelist.migrations.versions"],
        package_dir={
            "notelist": "src/notelist",
            "notelist.models": "src/notelist/models",
            "notelist.schemas": "src/notelist/schemas",
            "notelist.resources": "src/notelist/resources",
            "notelist.migrations": "src/notelist/migrations",
            "notelist.migrations.versions":
                "src/notelist/migrations/versions"},
        package_data={
            "notelist": ["templates/*.html"],
            "notelist.migrations": ["README", "*.ini", "*.mako"]}
    )
