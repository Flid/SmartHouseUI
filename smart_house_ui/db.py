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
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return '<%s id=%s name=%s>' % (
            self.__class__.__name__,
            self.id,
            self.name,
        )


class WeightMeasure(Base):
    __tablename__ = 'weight_measures'
    id = Column(Integer, primary_key=True)
    user = ForeignKey('users.id')
    dt = Column(DateTime)
    value = Column(Float)

    def __repr__(self):
        return '<%s id=%s user=%s dt=%s value=%s>' % (
            self.__class__.__name__,
            self.id,
            self.user,
            self.dt,
            self.value
        )


def get_weights(since):
    return session.query(WeightMeasure).filter(
        WeightMeasure.dt >= since,
    ).order_by(
        WeightMeasure.dt,
    ).all()


def get_today_weights_query():
    day_start = datetime.combine(date.today(), datetime.min.time())
    day_end = day_start + timedelta(days=1)
    return session.query(WeightMeasure).filter(
        WeightMeasure.dt >= day_start,
        WeightMeasure.dt <= day_end,
    )


def add_weight(value):
    get_today_weights_query().delete()
    session.add(WeightMeasure(
        user=1,
        dt=datetime.now(),
        value=value,
    ))
    session.commit()
