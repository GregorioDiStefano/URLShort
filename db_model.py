import peewee

database = peewee.SqliteDatabase("urls.db")


class BaseModel(peewee.Model):
    class Meta:
        database = database


class User(BaseModel):
    username = peewee.CharField(unique=True)
    password = peewee.CharField()
    email = peewee.CharField()
    join_date = peewee.DateTimeField()

    class Meta:
        order_by = ('username',)


class Shorturls(BaseModel):
    url = peewee.CharField()
    uid = peewee.CharField()
    created = peewee.DateTimeField()
    accessed = peewee.IntegerField()
    user = peewee.ForeignKeyField(User, null=True)


    def __str__(self):
        return "url: %s ==> %s" % (self.url, self.uid)


try:
    Shorturls.create_table()
except peewee.OperationalError:
    pass
