# Final Project
![Frontend CI](https://github.com/software-students-spring2025/5-final-project2/actions/workflows/frontend-ci-cd.yml/badge.svg)
![AI Backend CI](https://github.com/software-students-spring2025/5-final-project2/actions/workflows/ai-backend-ci-cd.yml/badge.svg)

# Description
The Dream Journal Web App is a full-stack platform that allows users to register, log in, and record their dreams securely. After submitting a dream, users receive an AI-generated interpretation powered by an OpenAI backend. Dreams are stored in a personal journal using MongoDB, letting users view, export as a pdf, and reflect on their dream entries over time. Built with Python/Flask, HTML/CSS, and Docker, the app emphasizes user authentication, secure data handling, and creative self-exploration.
[Link to Deployed App](http://161.35.189.175:8080/)

# Team
* [Josh Lavroff](https://github.com/joshlavroff)
* [Andrew Jung](https://github.com/AndrewJung03)
* [Keith Dusling](https://github.com/kdusling56)
* [Krish Kothari](https://github.com/krish-nyu)

# User Stories
- As a new user, I want to register an account so that I can save my dream entries privately.

-  As a returning user, I want to log in securely so that I can access my personal dream journal.

- As a logged-in user, I want to input a description of a dream I had so that I can record and reflect on it later.

- As a logged-in user, I want to receive an AI-generated interpretation after submitting a dream so that I can gain new insights into its meaning.

- As a logged-in user, I want to view all my past dream entries so that I can track patterns or recurring themes over time.

- As a user, I want my dream entries to be private and linked only to my account so that I feel secure recording personal thoughts.

- As a logged-in user, I want to log out of my account securely when I am finished using the app.

# Instructions 

Clone repository:

```bash
git clone https://github.com/software-students-spring2025/5-final-project2.git
```

To launch the application, run the following command in your terminal from the project root:

```bash
docker-compose up --build
```

## 🔧 Environment Setup

Place the .env file in the root directory. .env was sent in the team's discord channel.