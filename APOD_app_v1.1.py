import pandas as pd
import requests
import datetime
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # For handling images

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('NASA_API_KEY')


def fetch_apod(date):
    """Fetch the Astronomy Picture of the Day (APOD) data from NASA API."""
    url = f"https://api.nasa.gov/planetary/apod?date={date}&api_key={API_KEY}"
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        apod_data = response.json()
        
        # Debugging: Print the fetched data
        print("Fetched APOD data:", apod_data)

        # Ensure the expected keys are in the response
        if 'date' in apod_data:
            return apod_data
        else:
            print(f"Error: 'date' key not found in APOD data for date: {date}")
            return {}
    else:
        print(f"Error fetching APOD: {response.status_code} - {response.text}")
        return {}


def update_apod_db(data, db_file='nasa_apod.csv'):
    """Update the APOD database CSV file with the new data."""
    new_data = pd.DataFrame({
        'date': [data['date']],
        'title': [data['title']],
        'explanation': [data['explanation']],
        'copyright': [data.get('copyright', 'No copyright info')],  # Handle missing copyright info
        'media_type': [data['media_type']],
        'url': [data['url']],
        'hdurl': [data.get('hdurl', '')]  # Some entries may not have 'hdurl'
    })

    # If file exists, load the existing DataFrame, else create a new one
    if os.path.exists(db_file):
        apod_df = pd.read_csv(db_file)
        # Check if today's data is already in the database
        if not (apod_df['date'] == data['date']).any():
            # Append new data if it's not already present
            apod_df = pd.concat([apod_df, new_data], ignore_index=True)
    else:
        # No existing data, create a new DataFrame
        apod_df = new_data

    # Save the updated DataFrame to the CSV file
    apod_df.to_csv(db_file, index=False)
    return apod_df

def display_apod():
    """Fetch and display the APOD based on the selected date."""
    selected_date = f"{year_var.get()}-{month_var.get()}-{day_var.get()}"
    apod_data = fetch_apod(selected_date)

    if not apod_data:  # Check if apod_data is empty
        title_label.config(text="Failed to fetch data.")
        explanation_label.config(text="Please check the date and try again.")
        image_label.config(image='')  # Clear image
        return

    # Update the title and explanation
    title_label.config(text=apod_data.get("title", "No Title"))
    explanation_label.config(text=apod_data.get("explanation", "No Explanation"))

    # Update the image
    image_url = apod_data.get("url")
    if image_url:
        image_response = requests.get(image_url)
        image_data = Image.open(requests.get(image_url, stream=True).raw)
        image_data = image_data.resize((400, 400))  # Resize image to fit the GUI
        photo = ImageTk.PhotoImage(image_data)
        image_label.config(image=photo)
        image_label.image = photo  # Keep a reference to avoid garbage collection

    # Update the database
    update_apod_db(apod_data)


def gui_launch():
    """Launch the main GUI application."""
    global month_var, day_var, year_var, title_label, explanation_label, image_label

    root = tk.Tk()
    root.title("Astronomy Picture of The Day")

    # Application Instructions
    instructions = (
        "Welcome to the NASA Astronomy Picture of the Day (APOD) viewer\n\n"
        "Instructions:\n"
        "1. Use the dropdown menus to select a date (Year, Month, Day).\n"
        "2. Click 'Get APOD' to fetch and display the APOD for the selected date.\n"
        "3. The title, image, and description will be shown below.\n"
    )
    instruction_label = tk.Label(root, text=instructions, font=("Arial", 12), justify="left")
    instruction_label.grid(row=0, column=0, columnspan=5, padx=10, pady=10)

    # Dropdown for month
    month_options = [str(i).zfill(2) for i in range(1, 13)]
    month_var = tk.StringVar(root)
    month_dropdown = ttk.Combobox(root, textvariable=month_var, values=month_options, state="readonly", width=5)
    month_dropdown.grid(row=1, column=1, padx=10, pady=5)
    month_dropdown.set("MM")

    # Dropdown for day
    day_options = [str(i).zfill(2) for i in range(1, 32)]
    day_var = tk.StringVar(root)
    day_dropdown = ttk.Combobox(root, textvariable=day_var, values=day_options, state="readonly", width=5)
    day_dropdown.grid(row=1, column=2, padx=10, pady=5)
    day_dropdown.set("DD")

    # Dropdown for year
    year_options = [str(i) for i in range(1995, datetime.datetime.now().year + 1)]  # APOD starts from 1995
    year_var = tk.StringVar(root)
    year_dropdown = ttk.Combobox(root, textvariable=year_var, values=year_options, state="readonly", width=6)
    year_dropdown.grid(row=1, column=3, padx=10, pady=5)
    year_dropdown.set("YYYY")

    # Button to fetch APOD
    fetch_button = tk.Button(root, text="Get APOD", command=display_apod)
    fetch_button.grid(row=1, column=4, padx=10, pady=5)

    # Label for title
    title_label = tk.Label(root, text="", font=("Arial", 16, "bold"), wraplength=400, justify="center")
    title_label.grid(row=2, column=0, columnspan=5, pady=10)

    # Label for image
    image_label = tk.Label(root)
    image_label.grid(row=3, column=0, columnspan=5)

    # Label for explanation
    explanation_label = tk.Label(root, text="", wraplength=400, justify="left")
    explanation_label.grid(row=4, column=0, columnspan=5, pady=10)

    # Start the GUI event loop
    root.mainloop()

gui_launch()


