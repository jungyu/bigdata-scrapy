# 本類依賴 LunarDate 函式庫
# 安裝指令： pip3 install lunardate

""" 測試實例
from date_converter import DateConverter

# 使用套件中的函式
year = 112
ad_year = DateConverter.roc_to_ad(year)
print(ad_year)  # 輸出: 2023

gan_zhi_year = "丙辰"
years = DateConverter.gan_zhi_to_lunar_years(gan_zhi_year)
print(years)  # 輸出: [1976, 1916, 1856, 1796]

date_str = "1976-10-10"
year, month, day = DateConverter.convert_to_int_date(date_str)
print(year, month, day)  # 輸出: 1976 10 10

"""
import datetime
from lunardate import LunarDate

class DateConverter:
    """
    將民國年轉換為西元年

    Args:
        year (int): 民國年份，例如110、101

    Returns:
        int: 西元年份
    """
    @staticmethod
    def roc_to_ad(year):
        if year <= 0:
            raise ValueError("無效的民國年份")
        return year + 1911

    """
    將西元年轉換為民國年

    Args:
        year (int): 西元年份

    Returns:
        str: 民國年份，例如 "110年"
    """
    @staticmethod
    def year_to_roc(year):
        if year < 1912:
            raise ValueError("年份不在有效範圍內")

        roc_year = year - 1911
        return f"{roc_year}年"

    """
    將各種日期格式的輸入轉換為整數型別的年、月、日

    Args:
        date_str (str): 日期字符串，可以接受多種日期格式，例如"2022-01-01"、"2022/01/01"、"2022年1月1日"等

    Returns:
        int: 年份
        int: 月份
        int: 日
    """
    @staticmethod
    def convert_to_int_date(date_str):
        date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']  # 定義支援的日期格式
        date = None
        for date_format in date_formats:
            try:
                date = datetime.datetime.strptime(date_str, date_format)
                break
            except ValueError:
                pass

        if date is None:
            raise ValueError("無法解析日期：{}".format(date_str))

        year = date.year
        month = date.month
        day = date.day

        return year, month, day
    
    """
    將農曆年轉換為天干地支年

    Args:
        year (int): 農曆年份

    Returns:
        str: 天干地支年份，例如 "甲午"
    """
    @staticmethod
    def lunar_year_to_gan_zhi(year):
        tian_gan = "甲乙丙丁戊己庚辛壬癸"
        di_zhi = "子丑寅卯辰巳午未申酉戌亥"

        gan_idx = (year - 4) % 10
        zhi_idx = (year - 4) % 12

        gan = tian_gan[gan_idx]
        zhi = di_zhi[zhi_idx]

        return gan + zhi
    
    """
    將天干地支年轉換為多個西元年份

    Args:
        gan_zhi_year (str): 天干地支年份，例如 "甲午"

    Returns:
        list: 多個西元年份
    """
    @staticmethod
    def gan_zhi_to_lunar_years(gan_zhi_year):
        tian_gan = "甲乙丙丁戊己庚辛壬癸"
        di_zhi = "子丑寅卯辰巳午未申酉戌亥"

        gan = gan_zhi_year[0]
        zhi = gan_zhi_year[1]

        gan_idx = tian_gan.index(gan)
        zhi_idx = di_zhi.index(zhi)

        current_year = datetime.datetime.now().year
        year_list = []
        for i in range(current_year, current_year - 241, -1):
            gan_idx_shift = (i - 4) % 10  # 根據天干的周期，向前位移4年
            zhi_idx_shift = (i - 4) % 12  # 根據地支的周期，向前位移4年
            if gan_idx_shift == gan_idx and zhi_idx_shift == zhi_idx:
                year_list.append(i)
            
        return year_list
    
    """
    將國曆日期轉換為農曆日期

    Args:
        year (int): 年份
        month (int): 月份
        day (int): 日

    Returns:
        LunarDate: 農曆日期
    """
    @staticmethod
    def convert_to_lunar_date(year, month, day):
        lunar_date = LunarDate.fromSolarDate(year, month, day)
        return lunar_date

    """
    將農曆日期轉換為國曆日期

    Args:
        year (int): 年份
        month (int): 月份
        day (int): 日

    Returns:
        SolarDate: 國曆日期
    """
    @staticmethod
    def convert_to_solar_date(year, month, day):
        lunar_date = LunarDate(year, month, day)
        solar_date = lunar_date.toSolarDate()
        return solar_date