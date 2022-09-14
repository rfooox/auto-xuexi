import time
import uiautomator2 as u2
# import logging
# import time
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


if __name__ == '__main__':
    # 初始化数据库
    database = SqliteDatabase(db_name)
    database.create_tables([TiaoZhanQuestion],)

    # device = u2.connect(SN)
    device = u2.connect('10.0.51.134:6666')

    print(device.info)

    xpath_dict = dict()  # xpath路径
    # 判断设备型号
    if device.info['productName'] == 'SEA-AL10':
        print(device.info['productName'])
        # 我的
        xpath_dict['mine'] = '//*[@resource-id="cn.xuexi.android:id/comm_head_xuexi_mine"]'
        # 我的-我要答题
        xpath_dict['practice'] = '//*[@text="我要答题"]'
        xpath_dict['daily'] = '//*[@text="每日答题"]'
        xpath_dict['tiaozhan'] = '//*[@resource-id="app"]/android.view.View[1]/android.view.View[3]/android.view.View[11]'
        xpath_dict['shuangren'] = '//*[@resource-id="app"]/android.view.View[1]/android.view.View[3]/android.view.View[10]'
        xpath_dict['siren'] = '//*[@resource-id="app"]/android.view.View[1]/android.view.View[3]/android.view.View[9]'
        xpath_dict['tiaozhan_end'] = '//*[@text="挑战结束"]'

        # 挑战答题
        xpath_dict['tiaozhan_title'] = '//android.view.View/android.view.View[2]/android.view.View/android.view.View'
        xpath_dict['tiaozhan_answer'] = '//android.widget.ListView/android.view.View/android.view.View/android.view.View'

        # 双人答题
        xpath_dict['xuexi_tiaozhan_2_title'] = ''
        xpath_dict['xuexi_tiaozhan_2_answer'] = ''

        # 四人答题
        xpath_dict['xuexi_tiaozhan_4_title'] = ''
        xpath_dict['xuexi_tiaozhan_4_answer'] = ''

    else:
        exit(1)

    device.app_start('cn.xuexi.android', stop=True)

    # 打开挑战答题
    device.xpath(xpath_dict['mine']).click_exists()
    device.xpath(xpath_dict['practice']).click_exists()
    device.xpath(xpath_dict['tiaozhan']).click_exists()

    while True:
        if device.xpath(xpath_dict['tiaozhan_title']).click_exists():

            # 题目
            t_text = device.xpath(xpath_dict['tiaozhan_title']).get_text()

            # 选项
            answers_e = device.xpath(xpath_dict['tiaozhan_answer']).all()
            answer_list = [e.text for e in answers_e]
            answer_list.sort()  # 获取选项时排序

            # 读取或创建
            question_, create_status = TiaoZhanQuestion.get_or_create(title=t_text, answers='|'.join(answer_list))

            # 题目
            error_answers = []
            right_answer = ''

            # 创建新题目/读取项目内容
            if create_status:
                """创建新的条目"""
                print('创建一条新数据，记录对应选项')
                question_.answers = '|'.join(answer_list)
                temp_dict = json.loads(question_.description)
                temp_dict['times'] = 1
                question_.description = json.dumps(temp_dict)
                question_.save()
            else:
                """不是创建项目， 有记录"""
                print('读取数据库记录')
                if question_.right_answer is not None:
                    right_answer = question_.right_answer
                elif question_.error_answers is not None:
                    temp_str = question_.error_answers
                    error_answers = question_.error_answers.split('|')
                else:
                    error_answers = []

            # 更新次数内容
            if question_.description is None and not create_status:
                # question_.description 为空
                question_.description = json.dumps({'times': 1})
                question_.save()
                print(f'数据库中描述内容:为空, 重置为:{question_.description}')
            else:

                temp_dict = json.loads(question_.description)
                print(f'数据库中描述内容,字典化后:{temp_dict}')
                if type(temp_dict) != dict:
                    temp_dict = {'times': 0}
                    question_.description = json.dumps(temp_dict)
                    question_.save()
                    print(f"""{temp_dict}:不是字典, 重置为:{{'times': 0}}""")

                if 'times' not in temp_dict.keys() or type(temp_dict['times']) != int:
                    print(f'关键词 times 不在字典中, 添加 times: 1; 或者 times的值不为int类型')
                    temp_dict['times'] = 1
                    question_.description = json.dumps(temp_dict)
                    question_.save()
                else:
                    print('增加1')
                    temp_dict['times'] += 1
                    question_.description = json.dumps(temp_dict)
                    question_.save()

            # 确定点击谁
            right_button = None
            temp_right_button = None

            # 已知答案
            if right_answer != '' and right_answer is not None:
                print('已知答案：', right_answer)
                for answer_e in answers_e:
                    if answer_e.text == right_answer:
                        right_button = answer_e
                        temp_right_button = right_button
                    else:
                        continue

            # 已知部分错误选项
            else:
                for answer_e in answers_e:
                    if answer_e.text in error_answers:
                        continue
                    else:
                        temp_right_button = answer_e
                        break

            # 点击选项
            if right_button is None:
                temp_right_button.click()

                # 进入下一题
                time.sleep(time_dict['normal'])
                time.sleep(time_dict['normal'])
                if device.xpath(xpath_dict['tiaozhan_title']).exists \
                        and device.xpath(xpath_dict['tiaozhan_title']).get_text() != t_text:
                    question_.right_answer = temp_right_button.text
                    question_.error_answers = '|'.join([a for a in answer_list if a != temp_right_button.text])
                    question_.save()

                # 答题失败
                elif device.xpath(xpath_dict['tiaozhan_end']).click_exists():
                    error_answers.append(temp_right_button.text)
                    question_.error_answers = '|'.join(error_answers)
                    question_.save()
                    time.sleep(time_dict['long'])
                    time.sleep(time_dict['long'])
                    device.xpath('//*[@text="结束本局"]').click_exists()
                    device.xpath('//*[@text="再来一局"]').click_exists()
                    time.sleep(time_dict['long'])


            else:
                right_button.click()
                time.sleep(time_dict['long'])










