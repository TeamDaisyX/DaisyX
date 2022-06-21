from sqlalchemy import BigInteger, Boolean, Column, String, UnicodeText

from DaisyX.services.sql import BASE, SESSION


class Goodbye(BASE):
    __tablename__ = "goodbye"
    chat_id = Column(String(14), primary_key=True)
    custom_goodbye_message = Column(UnicodeText)
    media_file_id = Column(UnicodeText)
    should_clean_goodbye = Column(Boolean, default=False)
    previous_goodbye = Column(BigInteger)

    def __init__(
        self,
        chat_id,
        custom_goodbye_message,
        should_clean_goodbye,
        previous_goodbye,
        media_file_id=None,
    ):
        self.chat_id = chat_id
        self.custom_goodbye_message = custom_goodbye_message
        self.media_file_id = media_file_id
        self.should_clean_goodbye = should_clean_goodbye
        self.previous_goodbye = previous_goodbye


Goodbye.__table__.create(checkfirst=True)


def get_current_goodbye_settings(chat_id):
    try:
        return SESSION.query(Goodbye).filter(Goodbye.chat_id == str(chat_id)).one()
    except:
        return None
    finally:
        SESSION.close()


def add_goodbye_setting(
    chat_id,
    custom_goodbye_message,
    should_clean_goodbye,
    previous_goodbye,
    media_file_id,
):
    # adder = SESSION.query(Goodbye).get(chat_id)
    adder = Goodbye(
        chat_id,
        custom_goodbye_message,
        should_clean_goodbye,
        previous_goodbye,
        media_file_id,
    )
    SESSION.add(adder)
    SESSION.commit()


def rm_goodbye_setting(chat_id):
    if rem := SESSION.query(Goodbye).get(str(chat_id)):
        SESSION.delete(rem)
        SESSION.commit()


def update_previous_goodbye(chat_id, previous_goodbye):
    row = SESSION.query(Goodbye).get(str(chat_id))
    row.previous_goodbye = previous_goodbye
    # commit the changes to the DB
    SESSION.commit()
