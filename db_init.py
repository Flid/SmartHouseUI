# -*- coding: utf-8 -*-
from __future__ import unicode_literals


if __name__ == "__main__":
    from smart_house_ui.db import session, User, Base, engine

    Base.metadata.create_all(engine)
    session.add(User(id=1, name="User1"))

    session.commit()
