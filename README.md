# TGChannelIndex

A web application that generates public HTTP links for accessing media files from private Telegram channels. Share files securely without exposing sensitive chat or message identifiers—perfect for distributing content while maintaining channel privacy.

## Features

- **User Authentication**: Login with username and password
- **Token Generation**: Generate secure, unique tokens for specific Telegram messages
- **Media Streaming**: Stream media files from Telegram with Range request support
- **Rate Limiting**: 1 request per minute per IP address to prevent abuse
- **Session Management**: Secure cookie-based authentication
- **Redis Integration**: Token storage and validation using Redis
- **Environment Configuration**: All sensitive configuration via `.env` file

## Prerequisites

- Python 3.8+
- Telegram API credentials (API ID and API Hash)
- Redis server
- Docker (optional)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AnjanaMadu/TGChannelIndex.git
cd TGChannelIndex
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` File

Copy the template below and create a `.env` file in the project root:

```env
# Telegram API Credentials
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Redis Connection URL
REDIS_URL=redis://default:your_password@host:6379/0

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# Logging Level (INFO, DEBUG, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 4. Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Select "API development tools"
4. Fill in the form to create a new application
5. Copy your **API ID** and **API Hash** to the `.env` file

## Usage

### Running Locally

```bash
python main.py
```

The application will start at `http://localhost:8080` by default.

### Running with Docker

```bash
docker build -t tgchannelindex .
docker run -p 8080:8080 --env-file .env tgchannelindex
```

## API Endpoints

### Authentication

**GET `/login`**
- Display login page

**POST `/login`**
- Login with username and password
- Required parameters:
  - `username`: Admin username
  - `password`: Admin password
- Returns: Sets authentication cookie, redirects to `/`

**GET `/logout`**
- Logout and clear authentication cookie

### Content

**GET `/`**
- Display index page (requires authentication)

**GET `/generate`**
- Generate a secure token for a Telegram message
- Requires authentication
- Query parameters:
  - `chatId`: Telegram chat ID (required)
  - `messageId`: Telegram message ID (required)
- Returns: JSON with generated token
- Example: `/generate?chatId=123456&messageId=789`

**GET `/stream/{token}`**
- Stream media file from Telegram
- Path parameters:
  - `token`: Token generated from `/generate` endpoint
- Supports HTTP Range requests for partial content
- Returns: Media file stream (document, video, or audio)

## Configuration

All configuration is managed through environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | - |
| `API_HASH` | Telegram API Hash | - |
| `REDIS_URL` | Redis connection URL | - |
| `ADMIN_USERNAME` | Admin username for login | - |
| `ADMIN_PASSWORD` | Admin password for login | - |
| `SERVER_HOST` | Server host address | `0.0.0.0` |
| `SERVER_PORT` | Server port | `8080` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Security Considerations

- ⚠️ **Never commit the `.env` file** to version control
- The `.env` file is included in `.gitignore` to prevent accidental commits
- Use strong, unique passwords for the admin account
- Keep your Telegram API credentials confidential
- Tokens are stored in Redis with no expiration by default (consider adding TTL)
- Rate limiting is enforced (1 request per minute per IP)
- Authentication cookies are httponly and secure

## Project Structure

```
TGChannelIndex/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── myacc.session       # Telegram session file (auto-generated)
└── templates/
    ├── index.html      # Main page template
    └── login.html      # Login page template
```

## Requirements

See `requirements.txt` for the complete list of dependencies:

- `aiohttp` - Async HTTP web framework
- `pyrofork` - Telegram client library
- `tgcrypto` - Telegram encryption library
- `redis` - Redis client
- `python-dotenv` - Environment variable loader

## Troubleshooting

### Connection Issues

- Ensure Redis server is running and accessible at the `REDIS_URL`
- Verify Telegram API credentials are correct
- Check internet connectivity for Telegram API calls

### Authentication Issues

- Verify `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env` file
- Clear browser cookies and try logging in again
- Check server logs for authentication errors

### File Streaming Issues

- Ensure the message contains media (document, video, or audio)
- Verify the token is valid and has not been invalidated
- Check that the file exists on Telegram servers

## Logging

The application logs all important events and errors. Set `LOG_LEVEL` in `.env` to control verbosity:

- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages only

## License

This project is provided as-is for personal use.

## Support

For issues or questions, please open an issue on GitHub or contact the repository owner.

---

**Note**: This application requires a valid Telegram account and API credentials to function properly.
