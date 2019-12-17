import os
import time

from sqlalchemy import create_engine, BigInteger, UnicodeText, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import ChatNotFound
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB = os.getenv('DB_ADDR')
ENGINE = create_engine(DB)
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=ENGINE))


class Msg(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    text = Column(UnicodeText(4096))
    

# Bot configuration
USAGE = """\
/status -- show how many messages are pending
/receive -- receive pending messages
/send [user_id] -- reply to message to send it to given user
/drop -- drop all pending messages
"""
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['send'])
async def send_msg(message: types.Message):
    if message.chat.type == 'private':
        session = Session()
        args = message.get_args().split()
        if len(args) >= 1:
            try:
                receiver = int(args[0])
            except ValueError:
                await message.reply('You need to specify a Telegram id as the receiver.')
                return
            if message.reply_to_message is not None:
                msg = Msg(user_id=receiver, text=message.reply_to_message.text)
                try:
                    session.add(msg)
                    session.commit()
                    try:
                        await bot.send_message(receiver, 'You have a new message!')
                        await message.reply('Message was sent.')
                    except ChatNotFound:
                        session.flush()
                        await message.reply('This user id does not exist.')
                except SQLAlchemyError as err:
                    session.rollback()
                    print(f'[{time.asctime()}]: {err}')
                    await message.reply('Something happened, message could not be sent.\nTry sending the message again.')
            else:
                await message.reply('You must reply to the message you want to send.')
        else:
            await message.reply('You must provide a receiver to the message.')


@dp.message_handler(commands=['receive'])
async def receive_msg(message: types.Message):
    if message.chat.type == 'private':
        session = Session()
        msgs = session.query(Msg).filter_by(user_id=message.from_user.id).all()
        if msgs is not None:
            for i, msg in enumerate(msgs, 1):
                text = f'#{i}: {msg.text}'
                await message.reply(text, parse_mode=types.message.ParseMode.MARKDOWN, reply=False)
            try:
                session.query(Msg).filter(Msg.user_id == message.from_user.id).delete()
            except SQLAlchemyError as err:
                print(f'[{time.asctime()}]: {err}')
                await message.reply('Something happened, could not drop messages.')
        else:
            await message.reply('Your inbox is currently empty.')


@dp.message_handler(commands=['drop'])
async def drop_msg(message: types.Message):
    if message.chat.type == 'private':
        session = Session()
        msgs = session.query(Msg).filter_by(user_id=message.from_user.id).count()
        try:
            session.query(Msg).filter(Msg.user_id == message.from_user.id).delete()
            await message.reply(f'Dropped {msgs} messages.')
        except SQLAlchemyError as err:
            session.rollback()
            print(f'[{time.asctime()}]: {err}')
            await message.reply(f'Something happened, could not drop messages.')


@dp.message_handler(commands=['status'])
async def status(message: types.Message):
    if message.chat.type == 'private':
        session = Session()
        msgs = session.query(Msg).filter_by(user_id=message.from_user.id).count()
        text = f'You have {msgs} pending messages.'
        await message.reply(text)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        text = f'Hello, this is Anonybot.\n'+USAGE
        session = Session()
        msgs = session.query(Msg).filter_by(user_id=message.from_user.id).count()
        text += f'\nYou have {msgs} pending messages.'
        await message.reply(text=text, reply=False)


if __name__ == '__main__':
    Base.metadata.create_all(ENGINE)
    executor.start_polling(dp)
