# 📱 TGChannelIndex

Generate secure HTTP links for Telegram channel media. Share files in private channels without needing to join them!

![](collage.jpg)

## ✨ Features

- 🔐 User authentication with secure cookies
- 🎟️ Generate unique tokens for Telegram messages
- 📹 Stream media (documents, videos, audio)
- ⚡ Rate limiting (1 req/min per IP)
- 💾 Redis-backed token storage
- 🔑 Environment-based configuration

## 📋 Prerequisites

- Python 3.8+
- Telegram API credentials
- Redis server

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/IMXD20/TGChannelIndex.git
cd TGChannelIndex
pip install -r requirements.txt
```

### 2. Set Up `.env`

```env
API_ID=your_api_id
API_HASH=your_api_hash
REDIS_URL=redis://default:password@host:6379/0
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
LOG_LEVEL=INFO
```

### 3. Run

```bash
python main.py
```

Visit `http://localhost:8080` 🎉

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/login` | GET/POST | 🔓 User login |
| `/logout` | GET | 🚪 Logout |
| `/` | GET | 📄 Dashboard (auth required) |
| `/generate?chatId=X&messageId=Y` | GET | 🎟️ Generate token (auth required) |
| `/stream/{token}` | GET | 📹 Stream media file |

## 🔒 Security

- ⚠️ Never commit `.env` file
- Use strong passwords
- Keep API credentials confidential
- Rate limiting enabled
- HttpOnly secure cookies

## 📦 Project Structure

```
TGChannelIndex/
├── main.py           # Application logic
├── requirements.txt  # Dependencies
├── Dockerfile        # Docker setup
├── .env             # Configuration (create this!)
├── templates/
│   ├── index.html
│   └── login.html
└── README.md
```

## 🛠️ Docker

```bash
docker build -t tgchannelindex .
docker run -p 8080:8080 --env-file .env tgchannelindex
```

## 🆘 Troubleshooting

- **Redis connection fails**: Check `REDIS_URL` is correct
- **Login fails**: Verify credentials in `.env`
- **File streaming fails**: Ensure message has media attached

## 📝 License

Personal use only. See repository for details.

---

**Made with ❤️ for Telegram**
