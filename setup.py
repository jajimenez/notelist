"""Notelist Setup script."""

import setuptools as st


if __name__ == "__main__":
    # Long description
    with open("README.md") as f:
        long_desc = f.read()

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
        install_requires=[
            "Flask==1.1.2",
            "flask-restx==0.4.0",
            "Flask-JWT-Extended==4.1.0",
            "Flask-SQLAlchemy==2.5.1",
            "Flask-Migrate==2.7.0",
            "flask-marshmallow==0.14.0",
            "marshmallow-sqlalchemy==0.24.3"],
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
        package_data={"notelist.migrations": ["README", "*.ini", "*.mako"]})
