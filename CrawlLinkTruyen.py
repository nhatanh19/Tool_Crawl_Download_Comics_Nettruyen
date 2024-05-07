import os
import time

from selenium import webdriver
import threading
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor


# Hàm để lấy các liên kết chương truyện từ trang web
def get_comic_links(url):
    driver = webdriver.Firefox()
    driver.get(url)
    chapter = 1;
    comic_links = []

    # Lặp qua các chỉ số li tăng dần lên
    for i in range(1, 500):  # Chỉ số li tăng dần từ 1 đến 100 (hoặc số lớn hơn tùy vào trang web của bạn)
        xpath = f'//*[@id="nt_listchapter"]/nav/ul/li[{i}]/div[1]/a'
        elements = driver.find_elements(By.XPATH, xpath)
        if not elements:
            break

        for element in elements:
            href = element.get_attribute("href")
            if href:
                comic_links.append(href)
                print("Chapter [" ,chapter , "]: "+ href)
                chapter +=  1;

    # Đóng trình duyệt
    driver.quit()
    return comic_links

# Hàm để lấy các liên kết ảnh từ trang chương truyện
def get_image_links(comic_links, chapter_number):
    # Khởi tạo trình duyệt Firefox
    driver = webdriver.Firefox()
    driver.set_window_size(400, 400)

    # Mở trang web
    driver.get(comic_links)

    # Số lượng trang bạn muốn lặp qua
    num_pages = 100

    # Danh sách để lưu trữ tất cả các URL hình ảnh
    image_urls = []

    # Lặp qua các trang
    for i in range(1, num_pages + 1):
        # Lấy các phần tử <img> với XPath tương ứng
        img_elements = driver.find_elements(By.XPATH, f'//*[@id="page_{i}"]/img')
        # Lặp qua từng phần tử <img> và lấy thuộc tính 'src'
        for img in img_elements:
            src = img.get_attribute('src')
            if src:
                image_urls.append(src)

    # Đóng trình duyệt sau khi hoàn thành
    driver.quit()

    file_name = os.path.join(folder_name, f"Chapter_{chapter_number}.txt")
    try:
        # Ghi các URL hình ảnh vào tệp văn bản trong thư mục mới
        with open(file_name, 'w') as file:
            for url in image_urls:
                file.write(url + '\n')
        print(f"Image URLs saved to {file_name}")
    except Exception as e:
        print(f"Error occurred while saving image URLs: {str(e)}")



# URL của trang web chứa các chương truyện
comic_url = input("Nhập URL của trang web chứa truyện: ")

#comic_url = "https://www.nettruyenbb.com/truyen-tranh/du-bao-khai-huyen-100000"
# Tạo tên thư mục mới dựa trên số chương
folder_name = input("Nhập thư mục muốn lưu file: ")
MultiThread = int(input("Số luồng: "))
# Tạo thư mục mới nếu chưa tồn tại
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

#Lấy list link chapter
comic_links = get_comic_links(comic_url)

# Hàm để chạy các luồng
def run_threads(links):
    chapter_number = 1
    # Giới hạn số luồng đồng thời là MultiThread:
    with ThreadPoolExecutor(max_workers=MultiThread) as executor:
        # Lặp qua các liên kết và thực hiện trong các luồng
        for link in reversed(links):
            executor.submit(get_image_links, link, chapter_number)
            chapter_number += 1

# Kiểm tra xem có liên kết truyện không
if comic_links:
    run_threads(comic_links)
else:
    print("Không tìm thấy liên kết truyện trên trang web.")