# Imports
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL for postgresql database
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Creating an engine
engine = create_engine(DATABASE_URL)

# Making session instance
session_local = sessionmaker(autoflush = False, autocommit = False, bind = engine)

# Creating a base class for models
Base = declarative_base()