## Getting Started

### Prerequisites

Ensure you have the following installed on your system:

- Docker
- Docker Compose

### Installation

1. **Clone the repository:**

```bash
git clone <repository_url>
cd greenguardian
```

2. **Build and start the Docker containers:**
```bash
docker-compose up --build 
```
3. **Access the application:**  
Open your browser and navigate to http://localhost:5001.

### Database Setup
After building and starting the Docker containers, set up the database by running the following command:  
```bash
docker-compose exec web flask db upgrade
```