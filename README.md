# QuizMaster

A dynamic quiz application built with Python Flask that allows users to create, manage, and participate in quizzes.

## Features

- Create and manage quizzes
- Multiple choice questions support
- User authentication and authorization
- Score tracking and history
- Responsive web interface
- SQLite database for data persistence

## Technologies Used

- Python 3.x
- Flask (Web Framework)
- SQLite (Database)
- HTML/CSS/JavaScript (Frontend)
- Bootstrap (UI Framework)

## Project Structure

```
QuizMaster/
├── app.py              # Main application file
├── model.py            # Database models
├── database.sqllite3   # SQLite database
├── templates/          # HTML templates
├── .env/               # Virtual environment
└── README.md          # Project documentation
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sriisty/dummy_project.git
   cd dummy_project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .env
   .env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install flask
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Register a new account or login with existing credentials
2. Create new quizzes or participate in existing ones
3. View your quiz history and scores
4. Manage your created quizzes

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).
