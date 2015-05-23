import peewee

database = peewee.SqliteDatabase("urls.db")


class BaseModel(peewee.Model):
    class Meta:
        database = database


class User(BaseModel):
    email = peewee.CharField(unique=True)
    password = peewee.CharField()
    join_date = peewee.DateTimeField()

    class Meta:
        order_by = ('email',)


class Shorturls(BaseModel):
    url = peewee.CharField()
    uid = peewee.CharField()
    created = peewee.DateTimeField()
    accessed = peewee.IntegerField()
    user = peewee.ForeignKeyField(User, null=True)


    def __str__(self):
        return "user: %s url: %s ==> %s" % (self.user, self.url, self.uid)


try:
    Shorturls.create_table()
    User.create_table()
except peewee.OperationalError:
    pass
