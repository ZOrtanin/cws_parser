# from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine, Column, String, Date, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from datetime import date

# Определяем базовую модель
Base = declarative_base()

# Определяем модель таблицы
class Tentacles(Base):
    __tablename__ = 'template'
    id = Column(Integer, primary_key=True)
    link = Column(String, nullable=True)
    name = Column(String, nullable=True)
    autor = Column(String, nullable=True)
    rating = Column(String, nullable=True)
    description = Column(String, nullable=True)
    app_link = Column(String, nullable=True)
    len_ratings = Column(String, nullable=True)
    len_users = Column(String, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "link": self.link, 
            "name": self.name,
            "autor": self.autor,
            "rating": self.rating, 
            "description": self.description,
            "app_link": self.app_link,
            "len_ratings": self.len_ratings,
            "len_users": self.len_users,
        }


# Создаём подключение к базе данных
new_sqlite = 'sqlite:///template.db'

# Обычный движок
engine = create_engine(new_sqlite)
Base.metadata.create_all(engine)
