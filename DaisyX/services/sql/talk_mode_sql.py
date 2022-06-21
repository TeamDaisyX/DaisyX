#    Copyright (C) InukaAsith 2021
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


class Talkmode(BASE):
    __tablename__ = "talkmode"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


Talkmode.__table__.create(checkfirst=True)


def add_talkmode(chat_id: str):
    talkmoddy = Talkmode(chat_id)
    SESSION.add(talkmoddy)
    SESSION.commit()


def rmtalkmode(chat_id: str):
    if rmtalkmoddy := SESSION.query(Talkmode).get(chat_id):
        SESSION.delete(rmtalkmoddy)
        SESSION.commit()


def get_all_chat_id():
    stark = SESSION.query(Talkmode).all()
    SESSION.close()
    return stark


def is_talkmode_indb(chat_id: str):
    try:
        if s__ := SESSION.query(Talkmode).get(chat_id):
            return str(s__.chat_id)
    finally:
        SESSION.close()
