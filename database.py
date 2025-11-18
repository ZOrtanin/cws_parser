from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import model


class BaseDB:
    def __init__(self, arg):
        self.arg = arg
        self.Session = sessionmaker(bind=model.engine)

    def addTable(self,  link, name, autor, rating, description, app_link, len_ratings, len_users) -> bool:
        ''' Запись одной строки в базу '''

        # Открываем сессию
        session = self.Session()

        # Добавляем запись
        try:            
            item = model.Tentacles(
                    link=link, 
                    name=name,
                    autor=autor,
                    rating=rating, 
                    description=description,
                    app_link=app_link,
                    len_ratings=len_ratings,
                    len_users=len_users,

                    )

            session.add(item)
            session.commit()
            # print(f"line: {self.name}, {self.my_time}, {self.link}, {self.price}")
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()
        return True

    def addTableArr(self, arr) -> bool:
        ''' Запись списка объектов в базу '''

        session = self.Session()

        try:
            # Пакетная вставка
            session.bulk_save_objects(arr)

            # Фиксируем изменения
            session.commit()
            result = f" {len(arr)} line added" if len(arr) == 1 else f" {len(arr)} lines added"
            print(result)

        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def dataGet(self, filters=None, custom_filters=None, order=None) -> list[model.Tentacles]:
        ''' Получаем составной запрос к базе в ответ объекты 
            filters = {
                        'cover_letter': 'value'
                        }

        '''

        # Открываем сессию
        session = self.Session()

        # Собираем запрос
        query = session.query(model.Tentacles)

        if filters:
            query = query.filter_by(**filters)

        if custom_filters:
            query = query.filter(*custom_filters)

        if order:
            query = query.order_by(*order)

        result = query.all()

        # Закрываем сессию
        session.close()

        return result

    def dataGetRaw(self, column_name=None, value=None) -> tuple:
        ''' Получаем параметры для поиска по базе в ответ кортедж '''

        # Открываем сессию
        session = self.Session()

        # Собераем запрос
        if column_name and value:
            query = text(f"SELECT * FROM template WHERE {column_name} = :value")
            result = session.execute(query, {'value': value})
        else:
            query = text("SELECT * FROM template")
            result = session.execute(query)

        rows = result.fetchall()

        # Закрываем сессию
        session.close()

        return rows

    def editLinkDescription(self, link_id, name, autor, rating, description, app_link, len_ratings, len_users) -> bool:
        ''' Записываем описание вакансии '''

        session = self.Session()

        link = session.query(model.Tentacles).filter_by(id=link_id).first()

        # Добавляем запись
        try:            
            if description:
                link.description = description
            if name:
                link.name = name
            if autor:
                link.autor = autor
            if rating:
                link.rating = rating
            if app_link:
                link.app_link = app_link
            if len_ratings:
                link.len_ratings = len_ratings
            if len_users:
                link.len_users = len_users           
            
            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def findNewLinksBase(self) -> tuple:
        ''' Берем ссылки у которых нет описания '''

        # Открываем сессию
        session = self.Session()

        # Собираем запрос
        query = session.query(model.Tentacles)

        query = query.filter_by(description='Описание пока не получено')

        result = query.all() 

        # Закрываем сессию
        session.close()
        
        return result

    def findNewLinkBase(self) -> tuple:
        ''' Берем ссылки у которых нет описания '''

        try:
            with self.Session() as session:
                query = session.query(model.Tentacles).filter_by(description=None)
                result = query.first()
                if result:
                    pass
                else:
                    result = None
        except Exception as e:
            print(f"Ошибка при работе с базой данных: {e}")
            result = None

        
        return result

    def findLinkBase(self, new_link) -> bool:
        ''' Смотрим ссылки в базе '''

        # Открываем сессию
        session = self.Session()

        # Собираем запрос
        query = session.query(model.Tentacles)

        query = query.filter_by(link=new_link)

        result = query.count() == 0

        # Закрываем сессию
        session.close()
        
        return result

    def getAllData(self) -> list[model.Tentacles]:
        ''' Получаем все записи из базы '''
        session = self.Session()
        try:
            all_data = session.query(model.Tentacles).all()
            return all_data
        except Exception as e:
            print(f"Ошибка при получении всех данных: {e}")
            return []
        finally:
            session.close()

    def getCountAll(self) -> int:
        # Открываем сессию
        session = self.Session()

        # Собираем запрос
        query = session.query(model.Tentacles)

        # query = query.all()

        result = query.count()

        # Закрываем сессию
        session.close()
        
        return result