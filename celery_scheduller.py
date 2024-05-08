from tasks import yesterday_from_db


# ежедневаня выгрузка из БД
yesterday_from_db.delay()
