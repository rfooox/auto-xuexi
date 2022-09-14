import datetime
from peewee import *
import json


db_name = 'rDB.db'
SN = '6HJDU19926001808'  # huawei nova SEA-AL10
time_dict = {
    'fast': 0.5,
    'normal': 2,
    'long': 5,
}  # 舍


class TiaoZhanQuestion(Model):
    """挑战答题数据库

    """

    title = CharField(max_length=1000, null=True)
    answers = CharField(max_length=500, null=True)
    right_answer = CharField(max_length=200, null=True)
    error_answers = CharField(max_length=400, null=True)
    description = TextField(null=True, default=json.dumps({}))
    update_time = DateTimeField(null=True, default=datetime.datetime.now())
    create_time = DateTimeField(null=True, default=datetime.datetime.now())

    class Meta:
        database = SqliteDatabase(db_name)


def fix_tiao_zhan_question():
    tdb = SqliteDatabase(db_name)
    tdb.create_tables([TiaoZhanQuestion],)
    t_list = TiaoZhanQuestion.select()
    for temp_question in t_list:
        print(temp_question.id, temp_question.answers)
        t_str = temp_question.answers
        a_list = t_str.split('|')
        a_list.sort()
        temp_question.answers = '|'.join(a_list)
        temp_question.save()
        print(temp_question.id, temp_question.answers)


if __name__ == '__main__':
    fix_tiao_zhan_question()