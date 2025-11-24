# Cooked Roasted Life

A Flask-based web application that generates AI-powered roasts based on your digital lifestyle data from Spotify, AniList, and Valorant.

## Description

Cooked Life is an entertaining web application that analyzes your music taste, anime/manga preferences, and gaming statistics to generate humorous, personalized roasts using Google's Gemini AI. The application integrates with multiple APIs to gather comprehensive data about your digital footprint and transforms it into witty commentary that can be shared with friends.

### Key Features

- **Spotify Integration**: Analyzes your music listening habits, playlists, and favorite artists
- **AniList Integration**: Reviews your anime and manga statistics, favorites, and viewing patterns
- **Valorant Integration**: Examines your gaming performance and player statistics
- **Steam Integration**: Summarizes top games, recent playtime, and total hours
- **AI-Powered Roasts**: Utilizes Google Gemini AI to generate creative, personalized roasts
- **Shareable Results**: Generate unique links to share your roasts with others
- **Modern Web Interface**: Clean, responsive UI built with Flask templates

## Installation Instructions

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Git

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/SpreadSheets600/Cooked-Roasted-Life.git
   cd Cooked-Roasted-Life
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   Create a `.env` file in the root directory with the following variables:

   ```env
   # Flask Configuration
   PORT=8888
   SECRET_KEY=your_secret_key_here
   DEBUG=False

   # Database
   DATABASE_URL=sqlite:///roastmytaste.db

   # Google OAuth
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret

   # Spotify API
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

   # Valorant API
   HENRIK_API_KEY=your_henrik_api_key

   # Gemini API
   GEMINI_API_KEY=your_gemini_api_key
   
   # Steam API
   STEAM_API_KEY=your_steam_web_api_key
   ```

5. Initialize the database:

   ```bash
   python run.py
   ```

   The database will be automatically created on first run.

### API Keys Setup

- **Spotify API**: Register your application at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- **Google OAuth**: Create credentials at [Google Cloud Console](https://console.cloud.google.com/)
- **Gemini API**: Obtain an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Henrik API (Valorant)**: Get your API key from [Henrik's Valorant API](https://henrik-3.gitbook.io/hendrik-api)
- **Steam Web API**: Obtain a key from the [Steam Web API key page](https://steamcommunity.com/dev/apikey)

## Usage Instructions

### Running the Application

1. Activate your virtual environment (if not already activated):

   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Start the Flask development server:

   ```bash
   python run.py
   ```

3. Open your web browser and navigate to:

   ```bash
   http://localhost:8888
   ```

### Using the Application

1. **Home Page**: Navigate to the main page to get started
2. **Connect Services**: Authenticate with Spotify, AniList, Valorant, or provide Steam ID / vanity
3. **Generate Roast**: Click the roast button to analyze your data and generate a personalized roast
4. **Share**: Use the generated share link to show your roast to friends

### Steam Usage

To include Steam data, supply either `steam_id` (numeric) or `steam_vanity` in the roast request body. Vanity names are resolved automatically.

Example request payload:

```json
{
   "anilist_user": "YourAniListName",
   "valorant_name": "AgentSlayer",
   "valorant_tag": "1234",
   "steam_vanity": "yourVanityName"
}
```

If both are provided, `steam_id` takes precedence. Omit both to exclude Steam.

## Project Structure

```bash
Cooked-Life/
├── app/
│   ├── __init__.py           # Application factory
│   ├── config.py             # Configuration management
│   ├── models/               # Database models
│   │   ├── database.py
│   │   └── user_data.py
│   ├── routes/               # Application routes
│   │   ├── api_routes.py
│   │   ├── auth_routes.py
│   │   └── main_routes.py
│   ├── services/             # External API integrations
│   │   ├── anime.py
│   │   ├── gemini.py
│   │   ├── spotify.py
│   │   └── valorant.py
│   │   ├── steam.py
│   ├── static/               # CSS, JS, images
│   ├── templates/            # HTML templates
│   └── utils/                # Helper functions
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata
└── README.md                 # This file
```

## Contribution Guidelines

We welcome contributions to improve Cooked Life! Please follow these guidelines:

### How to Contribute

1. **Fork the Repository**: Click the 'Fork' button at the top right of the repository page

2. **Clone Your Fork**:

   ```bash
   git clone https://github.com/your-username/Cooked-Roasted-Life.git
   cd Cooked-Roasted-Life
   ```

3. **Create a Feature Branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**: Implement your feature or bug fix

5. **Test Your Changes**: Ensure all tests pass and add new tests if applicable

   ```bash
   python -m pytest tests/
   ```

6. **Commit Your Changes**:

   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

7. **Push to Your Fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

8. **Submit a Pull Request**: Go to the original repository and click 'New Pull Request'

### Coding Standards

- Follow PEP 8 style guidelines for Python code
- Write descriptive commit messages
- Add comments for complex logic
- Maintain existing code structure and patterns
- Update documentation for new features
- Ensure all tests pass before submitting PR

### Areas for Contribution

- Adding new service integrations (Steam, Discord, etc.)
- Improving AI roast quality and variety
- Enhancing UI/UX design
- Writing additional tests
- Fixing bugs and improving performance
- Documentation improvements

## License Information

This project is licensed under the MIT License. This means you are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the following conditions:

- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the software.
- The software is provided "as is", without warranty of any kind.

For more details, see the [LICENSE](LICENSE) file in the repository.

## Contact Information

**Project Maintainer**: SpreadSheets600

- **GitHub**: [@SpreadSheets600](https://github.com/SpreadSheets600)
- **Repository**: [Cooked-Roasted-Life](https://github.com/SpreadSheets600/Cooked-Roasted-Life)

For bug reports, feature requests, or general inquiries, please:

- Open an issue on [GitHub Issues](https://github.com/SpreadSheets600/Cooked-Roasted-Life/issues)
- Submit a pull request for contributions

## Acknowledgments

- Google Gemini AI for powering the roast generation
- Spotify Web API for music data
- AniList GraphQL API for anime/manga statistics
- Henrik's Valorant API for gaming statistics
