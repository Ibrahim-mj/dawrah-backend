# Event Management App

An application designed to streamline event registration, payment processing, and participant management. This app is equipped with robust features for both participants and organizers, making event management efficient and user-friendly.

---

## Features

### Participant Features

- **Event Registration**:  
  Register for the event seamlessly by providing personal details.

- **Payment Integration**:  
  Integrated with **Paystack** for secure and reliable payment processing.

- **Retry Payment**:  
  If a payment fails, participants receive an email containing a link to retry the payment.

- **Payment Confirmation**:  
  On successful payment, participants receive a confirmation email with a unique **Event ID**.

---

### Organizer Features

- **Authentication**:  
  Organizers can sign in using:
  - **Email and Password**
  - **Google Sign-In**

- **Participant Management**:  
  - View the list of all registered participants.
  - Identify which participants have completed their payments.

- **Donation Management**:  
  Organizers can receive and manage donations for the event.

- **Payment Management**:  
  View and track all payments received, including registration fees and donations.

---

### Communication Features

- **Email Notifications**:  
  - Notify participants of payment failures with a link to retry the payment.  
  - Confirm successful payments with an email containing the **Event ID**.

---

## Technologies Used

- **Backend**: Django, Django REST Framework (DRF)
- **Payment Gateway**: Paystack
- **Authentication**: Google OAuth, JWT

---

## Installation

1. Clone the repository:

   ```bash
   https://github.com/Ibrahim-mj/dawrah-backend.git

    ```

2. Change the directory:

    ```bash
    cd core
    ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```

4. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Use the .evn.example file to create a .env file:

    ```bash
    cp .env.example .env
    ```

6. run migrations:

    ```bash
    python manage.py migrate
    ```

7. Run the development server:

    ```bash
    python manage.py runserver
    ```