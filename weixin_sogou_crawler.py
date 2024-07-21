import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from urllib.parse import urljoin


def get_article_info(driver, keyword, num_pages=2):
    articles = []
    driver.get("https://weixin.sogou.com/")

    # 输入关键词并搜索
    search_box = driver.find_element(By.ID, "query")
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)

    for page in range(num_pages):
        # 等待搜索结果加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "news-box"))
        )

        # 解析页面
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for item in soup.select('.news-box .news-list li'):
            title = item.select_one('.txt-box h3 a').text.strip()
            summary = item.select_one('.txt-box p').text.strip()
            link = urljoin("https://weixin.sogou.com", item.select_one('.txt-box h3 a')['href'])
            time_str = item.select_one('.txt-box .s2').text.strip()

            articles.append({
                'title': title,
                'summary': summary,
                'link': link,
                'time': time_str
            })

        # 如果不是最后一页,点击下一页
        if page < num_pages - 1:
            next_button = driver.find_element(By.ID, "sogou_next")
            next_button.click()
            time.sleep(5)  # 等待页面加载

    return articles


def save_to_markdown(articles, keyword):
    md_content = f"# 搜狗微信搜索结果: {keyword}\n\n"

    for i, article in enumerate(articles, 1):
        md_content += f"## {i}. [{article['title']}]({article['link']})\n\n"
        md_content += f"**摘要**: {article['summary']}\n\n"
        md_content += f"**时间**: {article['time']}\n\n"
        md_content += "---\n\n"  # 添加分隔线

    with open(f"{keyword}_weixin_articles.md", "w", encoding="utf-8") as f:
        f.write(md_content)


def main():
    # 设置ChromeDriver路径
    chrome_driver_path = r"D:\0\chromedriver.exe"  # 替换为您的ChromeDriver路径
    service = Service(chrome_driver_path)

    # 创建Chrome选项
    options = webdriver.ChromeOptions()

    # 初始化WebDriver
    driver = webdriver.Chrome(service=service, options=options)

    keyword = input("请输入搜索关键词: ")
    articles = get_article_info(driver, keyword, num_pages=5)
    driver.quit()

    save_to_markdown(articles, keyword)
    print(f"已将搜索结果保存到 {keyword}_weixin_articles.md")


if __name__ == "__main__":
    main()