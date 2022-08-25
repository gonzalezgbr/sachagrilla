# models.py

from peewee import SqliteDatabase, Model, CharField, DateTimeField, ForeignKeyField, IntegerField

from sachagrilla import MAIN_MODULE_BASEPATH


def get_db():
    db_path = MAIN_MODULE_BASEPATH / 'sachagrilla.db'
    db = SqliteDatabase(db_path, pragmas={'journal_mode': 'wal',
                                                   'cache_size': -1 * 64000,  # 64MB
                                                   'foreign_keys': 1,
                                                   'ignore_check_constraints': 0})
    return db


class BaseModel(Model):
    created_at = DateTimeField()

    class Meta:
        database = get_db()


class Word(BaseModel):
    content = CharField(unique=True)
    length = IntegerField()
    last_used = DateTimeField(null=True)
    times_used = IntegerField(default=0)


class Clue(BaseModel):
    content = CharField(unique=True)
    word_id = ForeignKeyField(Word, backref='clues')
    last_used = DateTimeField(null=True)
    times_used = IntegerField(default=0)


class Quote(BaseModel):
    content = CharField(unique=True)
    author = CharField()
    extra = CharField(null=True)
    last_used = DateTimeField(null=True)
    times_used = IntegerField(default=0)


class Control(BaseModel):
    last_grid_nbr = IntegerField()


class Grid(BaseModel):
    quote_id = ForeignKeyField(Quote, backref='grids')
    position1 = IntegerField()
    position2 = IntegerField()


class GridLine(BaseModel):
    grid_id = ForeignKeyField(Grid, backref='lines')
    row_nbr = IntegerField()
    word_id = ForeignKeyField(Word, backref='gridlines')
    clue_id = ForeignKeyField(Clue, backref='gridLines')
