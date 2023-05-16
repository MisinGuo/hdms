import re
import sys
import time

# 数据提取模块
# 自动化测试工具selenium
import random

import jsonpath
import pymysql
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

a = 0
b = 0
num = 0
# 代理IP配置
# 'http://101.6.35.104:4780','http://118.31.2.38:8999',http://113.237.185.59:4314',
proxy = []


def get_proxy():  # 仅在获得代理IP时候调用即可
    # 代理配置设置为空
    proxy = []
    # y = []
    #     # 获得代理IP的链接
    body = requests.get(
        "http://http.tiqu.alibabaapi.com/getip3?num=10&type=2&pack=112647&port=1&ts=1&ys=1&cs=1&lb=1&pb=4&gm=4&regions=",
        verify=False).json()
    # 循环data的数量次
    for i in range(len(jsonpath.jsonpath(body, '$.data.*'))):
        http_ip_port = 'http://' + jsonpath.jsonpath(body, '$..ip')[i] + ':' + \
                       jsonpath.jsonpath(body, '$..port')[i]
        proxy.append(http_ip_port)
    print(proxy)
    return proxy


# 51job的滑块验证函数
# 在使用此函数之前需要将Chrome Driver文件用sublime搜索24 6364 63替换为24 6358 58（58即为x也可以为其他字符）或$cdc-->$cxx(hexediter中)
# 参考文献：https://blog.csdn.net/weixin_41712499/article/details/127488038
def certify(driver, url, module_string):
    # 获取0.2至0.8以内的小数
    t = random.uniform(0.2, 0.8)
    # 放慢速度，防止IP被封，5-30秒随机请求一次页面
    wait = random.randint(5, 10)
    time.sleep(wait)
    time.sleep(t)
    global a, b
    # 判断当前页面是否已经为405提示被封IP页面，如果已经被封则更换为下一个代理IP并再次请求主页
    while driver.title == "405":
        print("恭喜你，你的IP被该网站封掉了")
        print("你可以尝试使用其他IP或者提高你的技术使用代理IP，或者等半天或一天再试")
        print("你已经入库了所有模块的数据,共计成功{}条。".format(num))

        # b += 1
        # driver.quit()
        # module_list = []
        # # 切换后重新请求主页
        # driver = get_start(module_list, b)
        # 退出或执行其他操作
        sys.exit()
    # 在滑动验证页面则滑动
    while driver.title == "滑动验证页面":
        time.sleep(t)
        button = None
        # 能否获取到当前页面下的滑动按钮，若找不到按钮即认为是验证失败
        if not (driver.find_elements(By.XPATH, '//*[@id="nc_1_n1z"]')):
            time.sleep(t)
            a += 1
            print("共验证失败{}次".format(a))
            # 关闭浏览器并重新打开再次获取模块列表检测
            driver.quit()
            module_list = []
            driver = get_start(module_list, b, module_string)
            driver = certify(driver, url, module_string)
        # 验证失败则刷新页面递归调用该页面，验证并记录打印本次验证失败记录
        else:
            # 找到该元素并开始点击并保持
            button = driver.find_element(By.XPATH, '//*[@id="nc_1_n1z"]')
            ActionChains(driver).click_and_hold(button).perform()
            total = 255
            x = random.randint(1, 254)
            # 移动两次，第一次随机，第二次将剩余的距离移动完
            ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
            total = total - x
            ActionChains(driver).move_by_offset(xoffset=total, yoffset=0).perform()
            # 松开鼠标，这里不需要
            # ActionChains(driver).release(button).perform()
            time.sleep(t)
            # 滑块已经拉动但仍卡在加载中状态等待一个随机时间后再次刷新并重新验证
            if driver.find_elements(By.XPATH, '//*[@id="nc_1__scale_text"]/span/b'):
                time.sleep(t)
                if driver.find_elements(By.XPATH, '//*[@id="nc_1__scale_text"]/span/b'):
                    a += 1
                    print("共验证失败{}次，本次原因为卡在加载中状态".format(a))
                    # 关闭浏览器并重新打开再次获取模块列表检测
                    driver.quit()
                    module_list = []
                    driver = get_start(module_list, b, module_string)
                    driver = certify(driver, url, module_string)
            time.sleep(t)
    time.sleep(t)
    if driver.title == "405":
        print("恭喜你，你的IP被该网站封掉了")
        print("你可以尝试使用其他IP或者提高你的技术使用代理IP，或者等半天或一天再试")
        print("你已经入库了所有模块的数据,共计成功{}条。".format(num))
        # b += 1
        # driver.quit()
        # module_list = []
        # # 切换后重新请求主页
        # driver = get_start(module_list, b)
        sys.exit()
    return driver


# 声明
def init(i):
    options = webdriver.EdgeOptions()  # 创建一个配置对象
    # 设置User-agent
    options.add_argument(
        '--user-agent=Mozilla/5.0 ( NT 8.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')  # 替换User-Agent
    # # 效果是关闭浏览器的界面显示
    options.add_argument("--headless")  # 开启无界面模式
    options.add_argument("--disable-gpu")  # 禁用gpu

    # options.add_argument('--proxy-server={}'.format(proxy[i]))
    # 解决selenium遇到的滑块界面，不论是用代码模拟滑动还是你自己用手去滑动，都会出现上述失败图片
    options.add_argument("--disable-blink-features=AutomationControlled")
    # 效果是关闭浏览器上方显示的正在使用自动化测试工具的提示
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    return options


def get_start(module_list, i, module_string):
    options = init(i)
    driver = webdriver.Edge(service=Service(r'./msedgedriver.exe'),
                            options=options)
    driver.get("https://jobs.51job.com")
    driver = certify(driver, "https://jobs.51job.com", module_string)

    key = driver.find_elements(By.XPATH, module_string)  # 大模块

    if key:
        module_list_obj = key
        for i in range(len(module_list_obj)):
            module = []
            if key:
                module.append(key[i].text)
                module.append(module_list_obj[i].get_attribute("href"))
                module_list.append(module)
                i += 1
    else:
        print("未获取到首页")
        sys.exit()
    return driver


# 获取开始页面存放的数据列表链接 ,抓取模块中的第i+1个模块
def get_job(driver, module_list, job_list, i, module_string):
    # 待抓取数据模块的链接存放列表
    driver.get(module_list[i][1])
    driver = certify(driver, module_list[i][1], module_string)
    print("开始爬取模块链接：{}".format(module_list[i]))
    job_list_obj = driver.find_elements(By.XPATH, '//div[2]/div/p/span[1]/a')
    if job_list_obj:
        for i in range(len(job_list_obj)):
            job_list.append(job_list_obj[i].get_attribute("href"))
            i += 1
    print("待爬取数据列表:{}".format(job_list))
    return driver


# 爬取第i个模块中的数据
def spider(driver, module_list, i, p, module_string):
    # 用于存放待爬取的本页数据的列表
    job_list = []
    driver = get_job(driver, module_list, job_list, i, module_string)
    # 用于存放下一页数据的链接
    next_page = module_list[i][1]
    list_pages = etree.HTML(driver.page_source)
    if driver.find_elements(By.XPATH, "/html/body//a[text()='下一页']"):
        next_page = driver.find_elements(By.XPATH, "/html/body//a[text()='下一页']")[0].get_attribute("href")
    j = 0
    # 取p条数据
    end = False
    for k in range(p):
        # 暂时获取不到页面数据，反爬但是未提示，封的时间较短一般一个小时不到就可以再次使用
        if len(job_list) == 0:
            driver.quit()
            global b
            b += 1
            module_list = []
            driver = get_start(module_list, b, module_string)
            print("暂时获取不到页面数据，要不稍等一会再爬吧,系统设置的是半小时后再次请求但是有时候他不会等直接进入了下一个模块，算是一个BUG不过能爬俺就不动它了")
            time.sleep(1800)
        # 本页数据已经全部爬取或比对数据库结束，切换为下一页并重置坐标为0
        if j >= len(job_list):
            j = 0
            print("开始爬取数据链接：{}".format(next_page))
            driver.get(next_page)
            driver = certify(driver, next_page, module_string)

            job_list = []
            job_list_obj = driver.find_elements(By.XPATH, '//div[2]/div/p/span[1]/a')
            if job_list_obj:
                for job_obj in job_list_obj:
                    job_list.append(job_obj.get_attribute("href"))
            print("待爬取数据列表:{}".format(job_list))
            if driver.find_elements(By.XPATH, "/html/body//a[text()='下一页']"):
                next_page = driver.find_elements(By.XPATH, "/html/body//a[text()='下一页']")[0].get_attribute("href")
            if not (driver.find_elements(By.XPATH, "/html/body//a[text()='下一页']")):
                end = True
            list_pages = etree.HTML(driver.page_source)
        else:
            data = None
            try:
                data_link = job_list[j]
                connection = pymysql.connect(host='116.63.167.124',  # host属性
                                             user='root',  # 用户名
                                             password='',  # 此处填登录数据库的密码
                                             db='job_database'  # 数据库名
                                             )
                # 使用 cursor() 方法创建一个游标对象 cursor
                cursor = connection.cursor()
                # 使用 execute()  方法执行 SQL 查询
                cursor.execute("SELECT * FROM job_table WHERE data_link='{}'".format(data_link))
                # 使用 fetchone() 方法获取单条数据.
                data = cursor.fetchmany()
                connection.close()
            except:
                # 发生错误时回滚
                print("time_out错误,这条数据不要了")
                continue
            if len(data) > 0:
                print("该条数据已经存在，将自动跳过")
                j += 1
            else:
                driver.get(job_list[j])
                driver = certify(driver, job_list[j], module_string)
                # 此职位目前已经暂停招聘
                if driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[1]/div[1]/p'):
                    # if driver.find_elements(By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[1]/p')[0].text == "很抱歉，你选择的职位目前已经暂停招聘":
                    j += 1
                    print("此职位目前已经暂停招聘")
                    continue
                if driver.find_elements(By.XPATH, '/html/body'):
                    job_detail_html = etree.HTML(driver.page_source)
                    # 数据唯一标识符,这里使用链接的域名的片段标识
                    unique_key = re.search("jobs.*$", job_detail_html.xpath("//link[@rel='alternate']/@href")[0]).group(
                        0).strip("jobs/") if len(job_detail_html.xpath("//link[@rel='alternate']/@href")) > 0 else None
                    # 职位名称
                    job_name = job_detail_html.xpath("//div/div/h1/text()")[0] if len(
                        job_detail_html.xpath("//div/div/h1/text()")) > 0 else None
                    # 职位详情
                    job_detail = ""
                    if len(job_detail_html.xpath("/html/body/div[2]/div[2]/div[3]/div[1]/div//text()")) > 0:
                        job_detail_old = job_detail_html.xpath("/html/body/div[2]/div[2]/div[3]/div[1]/div//text()")
                        for detail in job_detail_old:
                            job_detail = job_detail + " " + detail.replace("\n", " ")
                    else:
                        job_detail = None
                    # if job_detail is None or len(job_detail) <= 20:
                    #     if len(job_detail_html.xpath("/html/body/div[2]/div[2]/div[3]/div[1]/div//p/text()")) > 0:
                    #         job_detail_old = job_detail_html.xpath(
                    #             "/html/body/div[2]/div[2]/div[3]/div[1]/div//p/text()")
                    #         for detail in job_detail_old:
                    #             job_detail = job_detail + detail.replace("\n", "")
                    # else:
                    #     job_detail = job_detail
                    # 所需技能
                    job_skills = None
                    # 学历要求
                    job_academic = list_pages.xpath("//div[1]/div[2]/div[{}]/p[2]/text()[1]".format(j + 1))[0].replace(
                        "学历要求：", "") if len(
                        list_pages.xpath("//div[1]/div[2]/div[{}]/p[2]/text()[1]".format(j + 1))) > 0 else None
                    # 工作经验要求
                    job_year = list_pages.xpath("//div[1]/div[2]/div[{}]/p[2]/text()[2]".format(j + 1))[0].replace(
                        "工作经验：",
                        "") if len(
                        list_pages.xpath("//div[1]/div[2]/div[{}]/p[2]/text()[2]".format(j + 1))) > 0 else None
                    # 工作福利
                    job_welfare = ""
                    if len(job_detail_html.xpath("/html/body/div[2]/div[2]/div[2]/div/div[1]/div/div/span/text()")) > 0:
                        for welfare in job_detail_html.xpath(
                                "/html/body/div[2]/div[2]/div[2]/div/div[1]/div/div/span/text()"):
                            job_welfare = job_welfare + " " + welfare
                    else:
                        job_welfare = None

                    # 工作薪资
                    job_compensation = \
                    job_detail_html.xpath("/html/body/div[2]/div[2]/div[2]/div/div[1]/strong/text()")[
                        0] if len(
                        job_detail_html.xpath("/html/body/div[2]/div[2]/div[2]/div/div[1]/strong/text()")) > 0 else None
                    # 工作城市
                    job_city = job_detail_html.xpath("/html/body/div[2]/div[2]/div[2]/div/div[1]/p/text()[1]")[
                        0].replace(
                        "\xa0", "") if len(
                        job_detail_html.xpath("/html/body/div[2]/div[2]/div[2]/div/div[1]/p/text()[1]")) > 0 else None
                    # 工作地址
                    job_adress = job_detail_html.xpath("/html/body/div[2]/div[2]/div[3]/div[2]/div/p/text()")[0] if len(
                        job_detail_html.xpath("/html/body/div[2]/div[2]/div[3]/div[2]/div/p/text()")) > 0 else None
                    # 招聘公司
                    jcompany_name = job_detail_html.xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div[1]/a/p/text()")[
                        0] if len(
                        job_detail_html.xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div[1]/a/p/text()")) > 0 else None
                    # 公司类型
                    company_type = job_detail_html.xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div[2]/p[1]/text()")[
                        0] if len(
                        job_detail_html.xpath(
                            "/html/body/div[2]/div[2]/div[4]/div[2]/div[2]/p[1]/text()")) > 0 else None
                    # 公司行业
                    company_industry = \
                        job_detail_html.xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div[2]/p[3]/@title")[
                            0] if len(
                            job_detail_html.xpath(
                                "/html/body/div[2]/div[2]/div[4]/div[2]/div[2]/p[3]/@title")) > 0 else None
                    # 发布时间
                    release_time = list_pages.xpath("//div[{}]/p[1]/span[@class='time']/text()".format(j + 1))[
                        0] if len(
                        list_pages.xpath("//div[{}]/p[1]/span[@class='time']/text()".format(j + 1))) > 0 else None
                    # 招聘数据链接
                    data_link = job_list[j]
                    # 数据来源网站
                    data_source = "51JOB"
                    job_module = module_list[i][0]
                    job = [unique_key, job_name, job_detail, job_skills, job_academic,
                           job_year, job_welfare, job_city, job_adress, jcompany_name, company_type, company_industry,
                           release_time, data_link, data_source, job_module]

                    try:
                        # 连接对象作用是：连接数据库、发送数据库信息、处理回滚操作（查询中断时，数据库回到最初状态）、创建新的光标对象
                        connection = pymysql.connect(host='116.63.167.124',  # host属性
                                                     user='root',  # 用户名
                                                     password='',  # 此处填登录数据库的密码
                                                     db='job_database'  # 数据库名
                                                     )
                        # 使用 cursor() 方法创建一个游标对象 cursor
                        cursor = connection.cursor()
                        # 使用 execute()  方法执行 SQL 查询
                        cursor.execute("SELECT * FROM job_table WHERE unique_key='{}'".format(unique_key))
                        # 使用 fetchone() 方法获取单条数据.
                        data = cursor.fetchmany()
                    except:
                        print("time_out错误，这条数据不要了")
                        continue
                    if not (len(data) > 0):
                        try:
                            # 执行sql语句
                            result = cursor.execute(
                                "INSERT INTO job_table VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}',null)".format(
                                    unique_key, job_name, job_detail, job_skills, job_academic, job_year, job_welfare,
                                    job_compensation, job_city,
                                    job_adress, jcompany_name, company_type, company_industry, release_time, data_link,
                                    data_source, job_module))
                            print("插入成功{}".format(job))
                            global num
                            num += 1
                            # 执行sql语句
                            connection.commit()
                        except Exception as e:
                            # 发生错误时回滚
                            connection.rollback()
                            print(job)
                            print("插入失败", e)
                    else:
                        print("该条数据已经存在，将自动跳过")
                        # 关闭数据库连接
                    connection.close()
                    j += 1
                else:
                    print("未获取到页面")
        if end is True and j >= len(job_list):
            print("本模块已经没数据了")
            break
    print("本模块已经完成")


# proxy = get_proxy()

# 用于存放待爬取模块的列表
module_list = []
list = ['/html/body/div[3]/div[2]/div[12]/div[1]/a', '//div[3]/div[2]/div[17]//div[1]/a', '//div[3]/div[2]/div[16]//div[1]/a',
        '//div[3]/div[2]/div[18]//div[1]/a', '//div[3]/div[2]/div[62]//div[1]/a',
        '//div[3]/div[2]/div[19]//div[1]/a', '//div[3]/div[2]/div[20]//div[1]/a', '//div[3]/div[2]/div[13]//div[1]/a']
while True:
    print("大模块(小模块数量/数量多的多跑几次，一次可能会爬不完)-------输入数字")
    print("后端开发大模块(23)----------1")
    print("前端开发大模块(2)-----------2")
    print("人工智能大模块(11)----------3")
    print("数据开发大模块(11)----------4")
    print("半导体/芯片大模块(28)--------5")
    print("移动端开发大模块(4)----------6")
    print("游戏开发大模块(22)-----------7")
    print("运维/技术支持大模块(18)------8")
    print("退出----------------------0")
    module_num = input("请输入一个你要爬取的模块：")

    total = input("请输入每个小模块爬取数据条数:")
    if 1 <= int(module_num) <= 8 and 1 <= int(total) <= 500:
        driver = get_start(module_list, b, list[int(module_num) - 1])
        driver.quit()
        for i in range(len(module_list)):
            driver = get_start(module_list, b, list[int(module_num) - 1])
            spider(driver, module_list, i, int(total), list[int(module_num) - 1])
            driver.quit()
        print("如果你到达了这里，那么你已经入库了所有小模块的数据,共计成功{}条。".format(num))
    elif int(module_num) == 0:
        sys.exit()
    else:
        print("输入有误")
