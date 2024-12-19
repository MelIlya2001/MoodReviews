import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Укажите путь к вашему ChromeDriver
service = Service('C:/Users/Kanat/chromedriver-win64/chromedriver.exe')  # Замените на ваш путь к ChromeDriver

def get_reviews(url, max_reviews=600, report_interval=10):
    print("Начинаем извлечение отзывов с URL:", url)  # Отладочное сообщение
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(url)
        time.sleep(10)

        reviews_data = []
        seen_reviews = set()  # Для хранения уникальных отзывов
        last_review_count = 0  # Для отслеживания количества отзывов
        start_time = time.time()  # Запоминаем время начала

        while len(reviews_data) < max_reviews:
            # Получаем отзывы и рейтинги
            reviews = driver.find_elements(By.CLASS_NAME, 'feedback__content')
            ratings = driver.find_elements(By.CLASS_NAME, 'feedback__rating.stars-line')  # Обновляем рейтинги здесь

            # Удаляем каждый второй рейтинг
            ratings = [rating for index, rating in enumerate(ratings) if index % 2 == 0]
           

            for review, rating in zip(reviews, ratings):  # Используем zip для сопоставления
                review_text = ""
                review_class = review.get_attribute('class')

                # Проверяем наличие текстовых классов внутри 'feedback__content'
                pros = review.find_elements(By.CLASS_NAME, 'feedback__text--item-pro')
                cons = review.find_elements(By.CLASS_NAME, 'feedback__text--item-con')
                comments = review.find_elements(By.CLASS_NAME, 'feedback__text--item')

                # Если нет текста, пропускаем отзыв
                if not (pros or cons or comments):
                    continue

                # Извлечение текста "достоинств"
                pros_text = " ".join([pro.text.strip() for pro in pros])
                # Извлечение текста "недостатков"
                cons_text = " ".join([con.text.strip() for con in cons])
                # Извлечение текста комментариев
                comments_text = " ".join(
                    [comment.text.strip() for comment in comments if comment not in pros and comment not in cons])

                # Формирование текста отзыва
                review_text = f"{pros_text} {cons_text} {comments_text}".strip()

                # Проверка на уникальность
                if review_text and review_text not in seen_reviews:
                    seen_reviews.add(review_text)  # Добавляем текст отзыва в множество

                    # Получаем класс рейтинга
                    rating_class = rating.get_attribute('class')

                    # Получаем количество звезд
                    if "star5" in rating_class:
                        star_count = 5
                    elif "star4" in rating_class:
                        star_count = 4
                    elif "star3" in rating_class:
                        star_count = 3
                    elif "star2" in rating_class:
                        star_count = 2
                    elif "star1" in rating_class:
                        star_count = 1
                    else:
                        star_count = 0

                    # Добавляем отзыв только если есть текст
                    if review_text:  # Проверяем наличие текста
                        reviews_data.append(
                            {'id': len(reviews_data) + 1, 'text': review_text, 'stars': star_count,'mood': ''})

            # Проверка на количество собранных отзывов
            if len(reviews_data) >= max_reviews:
                break

            # Прокручиваем страницу вниз, чтобы загрузить новые отзывы
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Увеличьте время ожидания, если необходимо

            # Проверка на зависание
            if len(reviews_data) == last_review_count:
                print("Не удалось загрузить новые отзывы, выходим из цикла.")
                break
            last_review_count = len(reviews_data)  # Обновляем количество собранных отзывов

            # Выводим количество собранных отзывов каждые report_interval секунд
            elapsed_time = time.time() - start_time
            if elapsed_time >= report_interval:
                print(f"Собрано {len(reviews_data)} отзывов за {int(elapsed_time)} секунд.")
                start_time = time.time()  # Сбрасываем таймер

        return reviews_data[:max_reviews]  # Возвращаем только первые max_reviews

    finally:
        driver.quit()

def save_reviews_to_csv(reviews_data, filename):
    # Сохраняем данные в CSV файл
    with open(filename, mode='w', newline='', encoding='utf-16') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'text', 'stars', 'mood'])
        writer.writeheader()
        writer.writerows(reviews_data)
