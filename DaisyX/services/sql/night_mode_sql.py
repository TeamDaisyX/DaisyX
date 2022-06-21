#    Copyright (C) Midhun KM 2020-2021
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sqlalchemy import Column, String

from DaisyX.services.sql import BASE, SESSION


class Nightmode(BASE):
    __tablename__ = "nightmode"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


Nightmode.__table__.create(checkfirst=True)


def add_nightmode(chat_id: str):
    nightmoddy = Nightmode(chat_id)
    SESSION.add(nightmoddy)
    SESSION.commit()


def rmnightmode(chat_id: str):
    if rmnightmoddy := SESSION.query(Nightmode).get(chat_id):
        SESSION.delete(rmnightmoddy)
        SESSION.commit()


def get_all_chat_id():
    stark = SESSION.query(Nightmode).all()
    SESSION.close()
    return stark


def is_nightmode_indb(chat_id: str):
    try:
        if s__ := SESSION.query(Nightmode).get(chat_id):
            return str(s__.chat_id)
    finally:
        SESSION.close()
