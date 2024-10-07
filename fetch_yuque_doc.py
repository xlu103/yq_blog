import requests
from bs4 import BeautifulSoup
import json
import os
import re
import urllib.parse

# 全局变量
YUQUE_COOKIE = os.environ.get('YUQUE_COOKIE', 'eceive-cookie-deprecation=1; lang=zh-cn; _yuque_session=GjmDSBKgdOqFpJrwqFMTeQ00Yt59oPlmsMbrZvWCabhz0RWlkGWnm4GMcgL5Dvb8mnmjHYHwbev64sQSWoi5BA==; _uab_collina=172554126784662255176215; aliyungf_tc=2b9b9559f1f36209b3dd089d48b929e384ff870b1b0df064dbd7bcf7fe43fc11; yuque_ctoken=6wcI5a0YBCK0bplhQ8HenRbk; receive-cookie-deprecation=1; current_theme=default; acw_tc=ac11000117282889338291382ec239feece1dfac4d6f07aac96b55c9b85a50')
BASE_URL = 'https://www.yuque.com/api/modules/table/doc/TableRecordController/show?docId=188343884&docType=Doc&limit=5000&offset=0&sheetId=efe4g4rgg2qk8kaz1qmavg60zhho10np'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
OUTPUT_FILE = 'yuque_doc.js'
YUQUE_USER_ID = 'xlu103'
def fetch_yuque_doc():
    import random
    random_number = random.randint(1, 1000000)
    url = f'{BASE_URL}'
    headers = {
        'User-Agent': USER_AGENT,
        'Cookie': YUQUE_COOKIE
    }
 
    
    try:
        if not YUQUE_COOKIE:
            print("错误:未能从 GitHub Actions 的 secrets 中获取 YUQUE_COOKIE")
            return
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)
        
        # 已移除规则判断
        article_list = []
        data = json.loads(soup.text)
        links = [record['data'] for record in data['records']]
        links = [json.loads(link)['fldpkay4ggz7gro1yvnv455fqa3qmt3a']['value']['src'] for link in links]
        print(links)
        # 去重链接
        links = list(set(links))
        for link in links:
            print(link)
            try:
                response = requests.get(link, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                article_data = extract_article_data(soup, link)
                article_list.append(article_data)
                print(f"已添加文章: {article_data['title']}")
            except requests.RequestException as e:
                print(f"获取文章 {link} 时出错: {e}")
            except ValueError as e:
                print(f"处理文章 {link} 数据时出错: {e}")
            except Exception as e:
                print(f"处理文章 {link} 时发生未知错误: {e}")
        
        if not article_list:
            print("未找到符合格式的链接")
        else:
            save_article_list(article_list)
    except requests.RequestException as e:
        print(f"获取文档时出错: {e}")

def extract_article_data(soup, link):
    article_title = soup.find('meta', property='og:title')
    if not article_title:
        raise ValueError("未找到文章标题")
    
    article_description = soup.find('meta', property='og:description')
    article_url = soup.find('meta', property='og:url')
    article_image = soup.find('meta', property='og:image')
    article_create_time = soup.find('meta', attrs={'name': 'weibo:article:create_at'})
    article_update_time = soup.find('meta', attrs={'name': 'weibo:article:update_at'})
    
    return {
        "title": article_title['content'],
        "description": article_description['content'] if article_description else "无描述",
        "url": article_url['content'] if article_url else link,
        "image": article_image['content'] if article_image else "无图片",
        "create_time": article_create_time['content'] if article_create_time else "未知",
        "update_time": article_update_time['content'] if article_update_time else "未知",
        "link": link
    }

def save_article_list(article_list):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"const articleList = {json.dumps(article_list, ensure_ascii=False, indent=2)};")
    print(f"article_list已保存到 {OUTPUT_FILE} 文件中")

if __name__ == "__main__":
    fetch_yuque_doc()