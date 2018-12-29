# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker

from prod_config import DB_URI


engine = create_engine(DB_URI, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<%s id=%s name=%s>" % (self.__class__.__name__, self.id, self.name)
