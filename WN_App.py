# Import required modules
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import os 
import ttkbootstrap
from io import BytesIO

def get_weather(city):
    API_key = "1b2f8c4cbcbd0ee0ce628c4130e28dc2"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"
    res = requests.get(url)

    if res.status_code == 404:
        messagebox.showerror("Error", "City not found")
        return None
    
    weather = res.json()
    try:
        icon_id = weather['weather'][0]['icon']
        temperature = weather['main']['temp'] - 273.15
        description = weather['weather'][0]['description']
        city = weather['name']
        country = weather['sys']['country']

        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        return (icon_url, temperature, description, city, country)
    except KeyError:
        messagebox.showerror("Error", "Failed to fetch weather information")
        return None

def search():
    city = city_entry.get()
    weather_result = get_weather(city)
    if weather_result is None:
        return

    icon_url, temperature, description, city, country = weather_result
    location_label.configure(text=f"{city}, {country}")

    image = Image.open(requests.get(icon_url, stream=True).raw)
    icon = ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image = icon

    temperature_label.configure(text=f"Temperature: {temperature:.2f}°C")
    description_label.configure(text=f"Description: {description}")

    news_data = get_news_from_web(city)
    if news_data is not None:
        news_text = "\n".join([f"{index}. {title}\n   Link: {link}\n" for index, title, link in news_data])
        news_textbox.configure(state='normal')
        news_textbox.delete(1.0, tk.END)
        news_textbox.insert(tk.END, news_text)
        news_textbox.configure(state='disabled')
    else:
        news_textbox.configure(state='normal')
        news_textbox.delete(1.0, tk.END)
        news_textbox.insert(tk.END, "News: No news available")
        news_textbox.configure(state='disabled')

def get_news_from_web(city):
    try:
        query = city

        url = f'https://search.kompas.com/search/?q={query}&submit=Submit+Query#gsc.tab=0&gsc.q={query}&gsc.sort=date'
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox()
        driver.get(url)
        driver.implicitly_wait(10)
        search_results = driver.find_elements(By.CSS_SELECTOR, 'div.gsc-thumbnail-inside')

        news_data = []
        for index, result in enumerate(search_results, start=1):
            title = result.find_element(By.CSS_SELECTOR, 'a.gs-title').text.strip()
            link_element = result.find_element(By.CSS_SELECTOR, 'a.gs-title')
            link = link_element.get_attribute('href') if link_element else None

            if link:
                news_data.append((index, title, link))

        return news_data if news_data else None

    except Exception as e:
        print(f"Error during web scraping: {e}")
        return None
    finally:
        driver.quit()

def get_image_links():
    try:
        url = "https://apod.nasa.gov/apod/astropix.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        image_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

        return image_links
    except Exception as e:
        print(f"Error fetching image links: {e}")
        return None

def download_image(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def update_image():
    global absolute_image_url
    global image_path

    download_image(absolute_image_url, image_path)

    image = Image.open(image_path)
    image = image.resize((400, 400), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)

    image_label.config(image=photo)
    image_label.image = photo

root = ttkbootstrap.Window(themename="morph")
root.title("Weather App")
root.geometry("800x800")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

weather_frame = ttk.Frame(notebook)
notebook.add(weather_frame, text="Weather")

city_entry = ttkbootstrap.Entry(weather_frame, font="Helvetica, 18")
city_entry.pack(pady=10)

search_button = ttkbootstrap.Button(weather_frame, text="Search", command=search, bootstyle="warning")
search_button.pack(pady=10)

location_label = tk.Label(weather_frame, font="Helvetica, 25")
location_label.pack(pady=20)

icon_label = tk.Label(weather_frame)
icon_label.pack()

temperature_label = tk.Label(weather_frame, font="Helvetica, 20")
temperature_label.pack()

description_label = tk.Label(weather_frame, font="Helvetica, 20")
description_label.pack()

news_textbox = tk.Text(weather_frame, font="Helvetica, 20", wrap=tk.WORD, state='disabled', height=10, width=50)
news_textbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(news_textbox)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
news_textbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=news_textbox.yview)

picture_frame = ttk.Frame(notebook)
notebook.add(picture_frame, text="Picture of the Day")

title_label = ttk.Label(picture_frame, text="NASA APOD", font="Helvetica, 20")
title_label.pack(pady=10)

image_links = get_image_links()

if image_links is not None and image_links:
    absolute_image_url = urljoin("https://apod.nasa.gov/apod/", image_links[0])
    os.makedirs('downloaded_images', exist_ok=True)
    image_path = os.path.join('downloaded_images', 'apod_image.jpg')

    image = Image.open(requests.get(absolute_image_url, stream=True).raw)
    image = image.resize((650, 650), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)

    image_label = tk.Label(picture_frame, image=photo)
    image_label.image = photo
    image_label.pack(pady=10)

    download_button = ttk.Button(picture_frame, text="Download Image", command=update_image)
    download_button.pack(pady=10)

else:
    no_image_label = tk.Label(picture_frame, text="No image links found", font="Helvetica, 18")
    no_image_label.pack(pady=20)

root.mainloop()
