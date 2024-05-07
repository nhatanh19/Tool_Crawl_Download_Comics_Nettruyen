import os
import requests
import threading
import re
from urllib.parse import urlparse
from queue import Queue



def download_images_from_txt(folder_path, referer_url):
    # Lặp qua tất cả các file trong thư mục
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            txt_file_path = os.path.join(folder_path, filename)
            image_folder_path = os.path.splitext(txt_file_path)[0]  # Tên thư mục ảnh sẽ trùng với tên file txt
            os.makedirs(image_folder_path, exist_ok=True)  # Tạo thư mục ảnh nếu chưa tồn tại
            #print(f"Tạo thư mục {image_folder_path} thành công!")
            with open(txt_file_path, "r") as file:
                lines = file.readlines()
                # Lặp qua từng dòng trong file txt
                for line in lines:
                    image_url = line.strip()  # Loại bỏ ký tự trắng và dấu xuống dòng
                    if image_url:
                        image_name = generate_valid_filename(image_url)
                        image_path = os.path.join(image_folder_path, image_name)

                        # Thêm nhiệm vụ tải xuống vào hàng đợi
                        download_queue.put((image_url, image_path, referer_url))

    # Đánh dấu kết thúc của hàng đợi
    for _ in range(NUM_THREADS):
        download_queue.put(None)

def download_image_worker():
    while True:
        task = download_queue.get()
        if task is None:
            # Kết thúc khi nhận được thông báo từ hàng đợi
            break
        image_url, image_path, referer_url = task
        download_image(image_url, image_path, referer_url)
        download_queue.task_done()

def download_image(image_url, image_path, referer_url):
    # Tạo header với referer là nội dung được yêu cầu
    headers = {
        'referer': referer_url
    }

    # Tải file ảnh từ URL và lưu vào đường dẫn chỉ định
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Đã tải xuống: {image_url}")
    else:
        print(f"Lỗi {response.status_code} khi tải xuống: {image_url}")

def generate_valid_filename(url):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)
    return filename

if __name__ == "__main__":
    # Thư mục chứa các file txt
    folder_path = input("Nhập đường dẫn đến thư mục chứa các file txt: ")
    # Số lượng luồng tải xuống ảnh
    NUM_THREADS = int(input("Số luồng: "))
	

    # URL referer
    referer_url = "https://www.nettruyentt.com"

    # Hàng đợi nhiệm vụ tải xuống
    download_queue = Queue()

    # Tạo và khởi chạy các luồng tải xuống ảnh
    threads = []
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=download_image_worker)
        thread.start()
        threads.append(thread)

    # Thực hiện tải các ảnh từ các file txt trong thư mục chỉ định
    download_images_from_txt(folder_path, referer_url)

    # Chờ tất cả các luồng hoàn thành
    for thread in threads:
        thread.join()

    # Đảm bảo rằng tất cả các nhiệm vụ đã được hoàn thành
    download_queue.join()
    
    print("Tải xuống hoàn tất!")
