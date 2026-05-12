# Book Recommendation System (API-Based)

## 📖 Introduction

This project is a web-based **Book Recommendation System** that provides personalized book suggestions. Unlike traditional systems that rely solely on static CSV datasets, this system integrates an external **API** to fetch real-time book metadata, including descriptions, authors, and high-quality cover images.

## 🚀 Key Features

* **Search Functionality:** Users can search for any book title to get instant details.
* **API Integration:** Real-time data fetching using an external Books API.
* **Aesthetic UI:** Designed with a modern, responsive interface using HTML/CSS and Jinja2 templates.
* **Fast Implementation:** Minimal storage requirements as data is fetched dynamically.

## 🛠️ Tech Stack

* **Backend:** Python 3.x, Flask
* **API:** [Google Books API / Open Library API]
* **Frontend:** HTML5, CSS3 (Grey/Minimalist Aesthetics)
* **Libraries:** Requests, Pandas, Jinja2

## 📂 Project Structure

```text
├── app.py              # Main Flask server and API routing logic
├── static/
│   ├── css/
│   │   └── style.css   # Custom styling (Grey/Modern theme)
│   └── js/             # Frontend interactivity
├── templates/
│   ├── index.html      # Landing page / Search bar
│   └── results.html    # Recommendation display page
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation

```

## ⚙️ Installation & Setup

1. **Clone the Repository:**
```bash
git clone https://github.com/themehmi/Book-Recommendation-System-Using-API.git
cd Book-Recommendation-System-Using-API

```


2. **Create a Virtual Environment:**

```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    
```bash
    pip install -r requirements.txt
    ```
4.  **Run the App:**
    ```bash
    python app.py
    ```
    Access the app at `[http://127.0.0.1:5000/](http://127.0.0.1:5000/)`.

## 🧠 How It Works
1.  **User Input:** The user enters a book title or genre into the search form.
2.  **Request Handling:** Flask captures the input and sends a GET request to the Books API.
3.  **Data Processing:** The system filters the JSON response to extract the title, author, description, and thumbnail.
4.  **Display:** The results are rendered dynamically on the results page using Jinja2 templates.

## 🔮 Future Improvements
*   Implement **Collaborative Filtering** using a hybrid approach (API + ML Model).
*   Add a **User Authentication** system to save favorite books.
*   Integrate a **Reading Progress Tracker**.

***

*Developed by Narinder Singh*

```
