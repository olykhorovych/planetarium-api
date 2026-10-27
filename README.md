# Planetarium API Service

A RESTful API service for managing planetarium shows, dome seating, and online ticket reservations.

---

## Tech Stack

* **Python** 3.15
* **Django** 6.1.2
* **Django REST Framework** 3.18.3
* **Django Filter** 26.2
* **Development Tools:** Django Debug Toolbar 8.0.0, Django Extensions 4.1

---

## Getting Started

1. **Clone the repository:**
    ```bash
    git clone https://github.com/olykhorovych/planetarium-api.git
    cd planetarium-api
    ```
2. **Set up virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Apply migrations:**
    ```bash
    python manage.py migrate
    ```
5. **Run the development server:**
    ```bash
    python manage.py runserver
    ```
