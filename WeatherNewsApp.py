import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import os
from io import BytesIO
import ttkbootstrap


class WeatherTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # Function to get weather information from OpenWeatherMap API
        def get_weather(city):
            API_key = "1b2f8c4cbcbd0ee0ce628c4130e28dc2"
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"
            res = requests.get(url)

            if res.status_code == 404:
                messagebox.showerror("Error", "City not found")
                return None

            # Parse the response JSON to get weather information
            weather = res.json()
            icon_id = weather['weather'][0]['icon']
            temperature = weather['main']['temp'] - 273.15
            description = weather['weather'][0]['description']
            city = weather['name']
            country = weather['sys']['country']

            # Get the icon URL and return all the weather information
            icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
            return (icon_url, temperature, description, city, country)

        # Function to search weather for a city
        def search():
            city = city_entry.get()
            result = get_weather(city)
            if result is None:
                return

            # If the city is found, unpack the weather information
            icon_url, temperature, description, city, country = result
            location_label.configure(text=f"{city}, {country}")

            # Get the weather icon image from the URL and update the icon label
            image = Image.open(requests.get(icon_url, stream=True).raw)
            icon = ImageTk.PhotoImage(image)
            icon_label.configure(image=icon)
            icon_label.image = icon

            # Update the temperature and description labels
            temperature_label.configure(text=f"Temperature: {temperature:.2f}°C")
            description_label.configure(text=f"Description: {description}")

            # Fetch and display news for the entered city
            fetch_and_display_news(city)

        # Function to fetch and display news for a city
        def fetch_and_display_news(city):
            news_text.delete(1.0, tk.END)  # Clear existing text

            # Function to scrape news search results from Kompas
            def scrape_kompas_search_results(query):
                url = f'https://search.kompas.com/search/?q={query}&submit=Submit+Query#gsc.tab=0&gsc.q={query}&gsc.sort=date'

                # Set up the Selenium webdriver with Firefox
                options = webdriver.FirefoxOptions()
                options.add_argument('--headless')  # Optional: run in headless mode to hide the browser window
                driver = webdriver.Firefox(options=options)

                # Navigate to the search results page
                driver.get(url)

                # Wait for the page to load (you might need to adjust the waiting time)
                driver.implicitly_wait(10)

                # Extract relevant information
                search_results = driver.find_elements(By.CSS_SELECTOR, 'div.gsc-thumbnail-inside')  # Adjust based on the website's structure

                # Display the extracted search results
                for index, result in enumerate(search_results, start=1):
                    title = result.find_element(By.CSS_SELECTOR, 'a.gs-title').text.strip()
                    link_element = result.find_element(By.CSS_SELECTOR, 'a.gs-title')
                    link = link_element.get_attribute('href') if link_element else None

                    if link:
                        news_text.insert(tk.END, f"{index}. {title} \n Link: {link}\n\n")

                # Close the webdriver
                driver.quit()

            # Call the function to scrape news search results
            scrape_kompas_search_results(city)

        # Create an entry widget -> to enter the city name
        city_entry = ttkbootstrap.Entry(self, font="Helvetica, 18")
        city_entry.pack(pady=10)

        # Create a button widget -> to search for the weather information
        search_button = ttkbootstrap.Button(self, text="Search", command=search, bootstyle="warning")
        search_button.pack(pady=10)

        # Create a label widget -> to show the city/country name
        location_label = tk.Label(self, font="Helvetica, 25")
        location_label.pack(pady=20)

        # Create a label widget -> to show the weather icon
        icon_label = tk.Label(self)
        icon_label.pack()

        # Create a label widget -> to show the temperature
        temperature_label = tk.Label(self, font="Helvetica, 20")
        temperature_label.pack()

        # Create a label widget -> to show the weather description
        description_label = tk.Label(self, font="Helvetica, 20")
        description_label.pack()

        # Create a text widget -> to display news results
        news_text = tk.Text(self, wrap="word", font="Helvetica, 14", height=15, width=70)
        news_text.pack(pady=20)

class NewsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # Function to scrape news search results from Kompas
        def scrape_kompas_search_results(query):
            url = f'https://search.kompas.com/search/?q={query}&submit=Submit+Query#gsc.tab=0&gsc.q={query}&gsc.sort=date'

            # Set up the Selenium webdriver with Firefox
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')  # Optional: run in headless mode to hide the browser window
            driver = webdriver.Firefox(options=options)

            # Navigate to the search results page
            driver.get(url)

            # Wait for the page to load (you might need to adjust the waiting time)
            driver.implicitly_wait(10)

            # Extract relevant information
            search_results = driver.find_elements(By.CSS_SELECTOR, 'div.gsc-thumbnail-inside')  # Adjust based on the website's structure

            # Display the extracted search results
            for index, result in enumerate(search_results, start=1):
                title = result.find_element(By.CSS_SELECTOR, 'a.gs-title').text.strip()
                link_element = result.find_element(By.CSS_SELECTOR, 'a.gs-title')
                link = link_element.get_attribute('href') if link_element else None

                if link:
                    news_text.insert(tk.END, f"{index}. {title} \n Link: {link}\n\n")

            # Close the webdriver
            driver.quit()

        # Create an entry widget -> to enter the news query
        query_entry = ttkbootstrap.Entry(self, font="Helvetica, 18")
        query_entry.pack(pady=10)

        # Create a button widget -> to search for news
        search_news_button = ttkbootstrap.Button(self, text="Search News", command=lambda: scrape_kompas_search_results(query_entry.get()), bootstyle="warning")
        search_news_button.pack(pady=10)

        # Create a text widget -> to display news results
        news_text = tk.Text(self, wrap="word", font="Helvetica, 18", height=25, width=70)
        news_text.pack(pady=20)

class PictureOfDayTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # Function to download an image from a given URL
        def download_image(url, save_path):
            response = requests.get(url)
            with open(save_path, 'wb') as f:
                f.write(response.content)

        # Function to update the displayed image
        def update_image():
            global absolute_image_url
            global image_path

            # Download the image
            download_image(absolute_image_url, image_path)

            # Update the displayed image
            image = Image.open(image_path)
            image = image.resize((400, 400), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            image_label.config(image=photo)
            image_label.image = photo

        # Function to get image links from NASA APOD website
        def get_image_links():
            try:
                url = 'https://apod.nasa.gov/apod/astropix.html'
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                image_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                return image_links
            except Exception as e:
                print(f"Error fetching image links: {e}")
                return None

        # Create a label widget -> to show the images from links
        if image_links := get_image_links():
            absolute_image_url = urljoin('https://apod.nasa.gov/apod/', image_links[0])
            os.makedirs('downloaded_images', exist_ok=True)
            image_path = os.path.join('downloaded_images', 'apod_image.jpg')

            # Display the image
            image = Image.open(requests.get(absolute_image_url, stream=True).raw)
            image = image.resize((400, 400), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            image_label = tk.Label(self, image=photo)
            image_label.image = photo
            image_label.pack(pady=10)

            # Download button
            download_button = ttk.Button(self, text="Download Image", command=update_image)
            download_button.pack(pady=10)

        else:
            # Show a message if no image links are found
            no_image_label = tk.Label(self, text="No image links found", font="Helvetica, 18")
            no_image_label.pack(pady=20)

class MainApplication(ttkbootstrap.Window):
    def __init__(self):
        super().__init__(themename="morph")
        self.title("Weather App")
        self.geometry("800x800")

        # Create a notebook for managing tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Create WeatherTab instance
        weather_tab = WeatherTab(self.notebook)
        self.notebook.add(weather_tab, text="Weather")

        # Create NewsTab instance
        news_tab = NewsTab(self.notebook)
        self.notebook.add(news_tab, text="News")

        # Create PictureOfDayTab instance
        picture_of_day_tab = PictureOfDayTab(self.notebook)
        self.notebook.add(picture_of_day_tab, text="Picture of the Day")

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
