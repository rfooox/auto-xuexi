import time
import uiautomator2 as u2
import logging
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
    # 初始化logging
    log = logging.getLogger('log')
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter(fmt='%(asctime)s - %(levelname)-9s-%(filename)-8s: %(lineno)s line - %(message)s')

    log_screen_out = logging.StreamHandler()
    log_screen_out.setLevel(logging.DEBUG)
    log_screen_out.setFormatter(fmt)

    log_file_out = logging.FileHandler(filename='debug.log', mode='a', encoding='utf-8')
    log_file_out.setFormatter(fmt)

    log.addHandler(log_screen_out)
    log.addHandler(log_file_out)

    # 初始化数据库
    log.debug('连接数据库')
    database = SqliteDatabase(db_name)
    log.debug('初始化数据表：【TiaoZhanQuestion】')
    database.create_tables([TiaoZhanQuestion],)

    # device = u2.connect(SN)
    log.debug('连接手机："10.0.51.134:6666"')
    device = u2.connect('10.0.51.134:6666')

    xpath_dict = dict()  # xpath路径
    # 判断设备型号
    if device.info['productName'] == 'SEA-AL10':
        log.debug('匹配型号成功：SEA-AL10')
        log.debug('初始化xpath_dict')
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
        log.info('机型不匹配，退出程序')
        exit(1)

    # TODO: 改为恢复到初始界面，停用 重新打开
    log.debug('停止并重新打开应用：cn.xuexi.android')
    device.app_start('cn.xuexi.android', stop=True)

    # 打开挑战答题

    log.debug('点击【我的】')
    device.xpath(xpath_dict['mine']).click_exists()
    log.debug('点击【我要答题】')
    device.xpath(xpath_dict['practice']).click_exists()
    log.debug('点击【挑战答题】')
    device.xpath(xpath_dict['tiaozhan']).click_exists()

    log.info('获取题库模式')
    while True:
        # TODO: 读题
        log.debug('判断题目是否正常出现')
        if device.xpath(xpath_dict['tiaozhan_title']).exists and device.xpath(xpath_dict['tiaozhan_answer']).exists \
                and device.xpath(xpath_dict['tiaozhan_title']).get_text() != '' \
                and device.xpath(xpath_dict['tiaozhan_answer']).get_text() != '':
            # 若题目存在
            log.debug('题目正常读取')
            # 题目
            t_text = device.xpath(xpath_dict['tiaozhan_title']).get_text()

            # 选项
            answers_e = device.xpath(xpath_dict['tiaozhan_answer']).all()
            answer_list = [e.text for e in answers_e]
            log.debug('选项排序')
            answer_list.sort()  # 获取选项时排序

            log.debug(f'题目：{t_text}')
            log.debug(f'选项：{answer_list}')

            # 读取或创建
            log.debug('查询数据库是否有此题')
            question_, create_status = TiaoZhanQuestion.get_or_create(title=t_text, answers='|'.join(answer_list))

            temp_dict = dict()
            # 题目
            error_answers = []
            right_answer = ''

            # 创建新题目/读取项目内容
            if create_status:
                """创建新的条目"""
                temp_dict['times'] = 1
                log.debug('第一次遇到此题，计次初始化为1')
                question_.description = json.dumps(temp_dict)
            else:
                """不是创建项目， 有记录"""
                temp_dict = json.loads(question_.description)
                log.debug(f'数据库中描述内容,字典化后:{temp_dict}')
                if type(temp_dict) != dict:
                    log.debug(f"""{temp_dict}:不是字典, 重置为:{{'times': 0}}""")
                    temp_dict = {'times': 0}
                    question_.description = json.dumps(temp_dict)

                if 'times' not in temp_dict.keys() or type(temp_dict['times']) != int:
                    log.debug(f'关键词 times 不在字典中, 添加 times: 1; 或者 times的值不为int类型')
                    temp_dict['times'] = 1
                    question_.description = json.dumps(temp_dict)
                else:

                    temp_dict['times'] += 1
                    question_.description = json.dumps(temp_dict)
                    log.debug(f'遇题次数加1：{temp_dict}')

                log.info('读取数据库记录选项情况')
                if question_.right_answer is not None:

                    right_answer = question_.right_answer
                    log.debug(f'读取正确答案：{right_answer}')

                if question_.error_answers is not None:
                    temp_str = question_.error_answers
                    error_answers = question_.error_answers.split('|')
                    log.debug(f'读取错误答案：{error_answers}')
                else:
                    log.debug('错误答案无记录，初始化error_answers')
                    error_answers = []

            # 确定点击谁
            log.debug('初始化：正确按钮与可能正确按钮')
            right_button = None
            temp_right_button = None

            # 已知答案
            if right_answer != '' and right_answer is not None:
                log.info(f'已知答案：{right_answer}')
                log.debug('确认与正确答案匹配按钮元素')
                for answer_e in answers_e:
                    if answer_e.text == right_answer:
                        right_button = answer_e
                        temp_right_button = right_button
                        question_.update_time = datetime.datetime.now()
                        question_.save()
                        log.debug(f'正确选项为：{right_button.text}')
                    else:
                        continue

            # 已知部分错误选项
            else:
                log.debug('未知正确答案，读取错误选项记录')
                for answer_e in answers_e:
                    if answer_e.text in error_answers:
                        log.debug(f'选项：{answer_e.text}，包含在错误选记录中（{error_answers}）')
                        continue
                    else:
                        temp_right_button = answer_e
                        log.debug(f'可能正确选项为：{temp_right_button.text}')
                        break

            # 点击选项
            log.info('点击选项')
            if right_button is None:
                log.debug('不知道正确答案，点击【可能正确】选项')
                temp_right_button.click()

                t_time = 0
                while True:
                    # TODO: 循环检测点击后情况
                    # TODO: 加入时间检测
                    log.debug(f'点击后等待时长：{t_time}')
                    time.sleep(2)
                    if t_time > 20:
                        # 超时
                        log.debug('超时退出')
                        exit('timeout')
                        # break
                    t_time += 2

                    # 进入下一题
                    if device.xpath(xpath_dict['tiaozhan_title']).exists \
                            and device.xpath(xpath_dict['tiaozhan_title']).get_text() != t_text:
                        log.info('成功进入下一题')
                        # 更新数据库
                        log.debug('将正确选项写入数据库')
                        question_.right_answer = temp_right_button.text
                        question_.error_answers = '|'.join([a for a in answer_list if a != temp_right_button.text])
                        question_.update_time = datetime.datetime.now()
                        question_.save()
                        log.debug('写入成功，进入下一题')
                        break

                    # 答题失败
                    elif device.xpath(xpath_dict['tiaozhan_end']).exists:
                        error_answers.append(temp_right_button.text)
                        log.debug('点击错误选项，更新至数据库')
                        question_.error_answers = '|'.join(error_answers)
                        question_.update_time = datetime.datetime.now()
                        question_.save()
                        device.xpath('//*[@text="结束本局"]').click_exists()
                        time.sleep(time_dict['long'])
                        device.xpath('//*[@text="再来一局"]').click_exists()
                        log.debug('点击错误选项，进入下一题')
                        break

            else:
                log.debug('已知正确答案，点击【正确】选项')
                right_button.click()

                while True:
                    # TODO: 加入超时计时
                    # TODO: 更新次数
                    if device.xpath(xpath_dict['tiaozhan_title']).exists \
                            and device.xpath(xpath_dict['tiaozhan_title']).get_text() != t_text:
                        log.debug('点击正确选项，进入下一题')
                        break

            # 异常情况处理
            if device.xpath('//*[@text="结束本局"]').exists:
                log.debug('异常发现结束本局')
                device.xpath('//*[@text="结束本局"]').click_exists()
            if device.xpath('//*[@text="再来一局"]').exists:
                log.debug('异常发现再来一局')
                device.xpath('//*[@text="再来一局"]').click_exists()









