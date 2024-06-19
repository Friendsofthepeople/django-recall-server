# django-recall-server
A Django server to managing the verification of constituents, publishing of representative information, and signing to recall them. 

### About Repo
- This repo hosts the open-source server powering Public Gavel.
- It exposes APIs to facilitate verification and registration of constituents in a credible and secure way.

### Stack
- Django Rest framework
- PostgreSQL
- Docker
- JWT

### Join the Community
- [Discord server](https://discord.gg/v6TYzfuZc8)
- [Twitter]()

Happy hacking with you!

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
  - [Running the Server](#running-the-server)
  - [API Documentation](#api-documentation)
- [Contributing](#contributing)
  - [Getting Started](#getting-started)
  - [Code of Conduct](#code-of-conduct)
  - [How to Contribute](#how-to-contribute)
- [Join the Community](#join-the-community)
- [License](#license)

## Installation

### Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Docker
- Docker Compose
- Python 3.8 or higher
- PostgreSQL

### Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/Friendsofthepeople/django-recall-server.git
   cd django-recall-server
   ```

2. **Create and activate a virtual environment:**

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file in the project root and add the following variables:

   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_NAME=your_db_name
   DATABASE_USER=your_db_user
   DATABASE_PASSWORD=your_db_password
   DATABASE_HOST=db
   DATABASE_PORT=5432
   ```

5. **Build and start the Docker containers:**

   ```sh
   docker-compose up --build
   ```

6. **Apply database migrations:**

   ```sh
   docker-compose exec web python manage.py migrate
   ```

7. **Create a superuser:**

   ```sh
   docker-compose exec web python manage.py createsuperuser
   ```

## Usage

### Running the Server

Start the development server:

```sh
docker-compose up
```

Access the server at `http://localhost:8000`.

### API Documentation

API documentation is available at `http://localhost:8000/api/docs/` (configure as needed).

## Contributing

We welcome contributions from the community! Here’s how you can get involved:

### Getting Started

1. Fork the repository.
2. Clone your fork:

   ```sh
   git clone https://github.com/yourusername/django-recall-server.git
   cd django-recall-server
   ```

3. Create a branch for your feature or bug fix:

   ```sh
   git checkout -b feature/your-feature-name
   ```

4. Make your changes and commit them:

   ```sh
   git commit -m "Description of your changes"
   ```

5. Push your changes to your fork:

   ```sh
   git push origin feature/your-feature-name
   ```

6. Create a pull request on the main repository.

### Code of Conduct

We adhere to the Contributor Covenant Code of Conduct. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for more information.

### How to Contribute

1. **Report Bugs:**

   Use GitHub issues to report bugs. Make sure to provide detailed information about the issue and steps to reproduce it.

2. **Suggest Features:**

   Use GitHub issues to suggest new features. Describe your idea and how it can benefit the project.

3. **Write Code:**

   - Follow the project’s coding standards.
   - Write tests for your code.
   - Ensure your code passes all tests before submitting a pull request.

4. **Review Pull Requests:**

   - Help review and test pull requests submitted by others.

## Join the Community

- [Discord server](https://discord.gg/ZyCfgAQ6)
- [Twitter]()

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
