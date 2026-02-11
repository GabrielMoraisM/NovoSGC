from setuptools import setup, find_packages

setup(
    name="sgc-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.115.0",
        "uvicorn[standard]==0.30.1",
        "sqlalchemy==2.0.30",
        "alembic==1.13.1",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.0",
        "passlib[bcrypt]==1.7.4",
        "python-jose[cryptography]==3.3.0",
        "pydantic-settings==2.2.0",
    ],
)