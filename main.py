from pyrogram import Client
from aiohttp import web
import asyncio
import secrets
import base64
import redis
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
redis_url = os.getenv('REDIS_URL')
admin_username = os.getenv('ADMIN_USERNAME')
admin_password = os.getenv('ADMIN_PASSWORD')
server_host = os.getenv('SERVER_HOST', '0.0.0.0')
server_port = int(os.getenv('SERVER_PORT', 8080))

app = Client("myacc", api_id=api_id, api_hash=api_hash)
redis_client = redis.from_url(redis_url)

users = {admin_username: admin_password}
rate_limiter = {}
sessions = {}

def check_rate_limit(ip):
    now = datetime.now()
    if ip in rate_limiter:
        last_attempt = rate_limiter[ip]
        if (now - last_attempt).total_seconds() < 60:
            return False
    rate_limiter[ip] = now
    return True

def verify_token(token):
    try:
        data = redis_client.get(f"token:{token}")
        if data:
            chat_id, message_id = data.decode('utf-8').split(':')
            return chat_id, message_id
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
    return None, None

def generate_token(chat_id, message_id):
    token = secrets.token_hex(16)
    try:
        redis_client.set(f"token:{token}", f"{chat_id}:{message_id}")
        logger.info(f"Token generated for chat_id={chat_id}, message_id={message_id}")
    except Exception as e:
        logger.error(f"Error generating token: {e}")
    return token

def verify_auth_cookie(request):
    cookie = request.cookies.get('auth')
    if not cookie:
        return None
    try:
        decoded = base64.b64decode(cookie).decode('utf-8')
        username, password = decoded.split(':', 1)
        if username in users and users[username] == password:
            return username
    except Exception:
        pass
    return None

routes = web.RouteTableDef()

@routes.get('/login')
async def show_login(request):
    with open('templates/login.html', 'r') as f:
        html = f.read()
    html = html.replace('{{if .Error}}', '').replace('{{.Error}}', '').replace('{{end}}', '')
    return web.Response(text=html, content_type='text/html')

@routes.post('/login')
async def perform_login(request):
    ip = request.remote or 'unknown'
    if not check_rate_limit(ip):
        logger.warning(f"Rate limit exceeded for IP: {ip}")
        return web.json_response({"error": "Rate limit exceeded. Please wait 1 minute."}, status=429)
    
    data = await request.post()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username in users and users[username] == password:
        value = base64.b64encode(f"{username}:{password}".encode()).decode()
        response = web.HTTPFound('/')
        response.set_cookie('auth', value, max_age=86400, httponly=True)
        logger.info(f"Login successful for user: {username}")
        return response
    
    logger.warning(f"Failed login attempt for user: {username} from IP: {ip}")
    with open('templates/login.html', 'r') as f:
        html = f.read()
    html = html.replace('{{if .Error}}', '').replace('{{.Error}}', 'Invalid username or password').replace('{{end}}', '')
    return web.Response(text=html, content_type='text/html', status=401)

@routes.get('/logout')
async def perform_logout(request):
    response = web.HTTPFound('/login')
    response.del_cookie('auth')
    return response

@routes.get('/')
async def index(request):
    username = verify_auth_cookie(request)
    if not username:
        return web.HTTPFound('/login')
    with open('templates/index.html', 'r') as f:
        html = f.read()
    return web.Response(text=html, content_type='text/html')

@routes.get('/generate')
async def generate_link(request):
    username = verify_auth_cookie(request)
    if not username:
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    chat_id = request.query.get('chatId')
    message_id = request.query.get('messageId')
    
    if not chat_id or not message_id:
        return web.json_response({"error": "Missing chatId or messageId"}, status=400)
    
    try:
        int(chat_id)
        int(message_id)
    except ValueError:
        return web.json_response({"error": "Invalid chatId or messageId"}, status=400)
    
    token = generate_token(chat_id, message_id)
    return web.json_response({"token": token})

@routes.get('/stream/{token}')
async def stream_file(request):
    token = request.match_info['token']
    chat_id_str, message_id_str = verify_token(token)
    
    if not chat_id_str or not message_id_str:
        logger.warning(f"Invalid token attempt: {token}")
        return web.json_response({"error": "Invalid or missing token"}, status=401)
    
    try:
        chat_id_int = int(chat_id_str)
        message_id = int(message_id_str)
        chat_id = -(100 * 1_000_000_0000 + chat_id_int)
        
        message = await app.get_messages(chat_id, message_id)
        
        if not message.document and not message.video and not message.audio:
            return web.json_response({"error": "No media found"}, status=404)
        
        media = message.document or message.video or message.audio
        file_size = media.file_size
        file_name = getattr(media, 'file_name', 'file')
        mime_type = getattr(media, 'mime_type', 'application/octet-stream')
        
        logger.info(f"Streaming file: {file_name} ({file_size} bytes)")
        
        range_header = request.headers.get('Range')
        if range_header:
            range_str = range_header.replace('bytes=', '')
            parts = range_str.split('-')
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else file_size - 1
            
            if start >= file_size or end >= file_size or start > end:
                response = web.Response(status=416)
                response.headers['Content-Range'] = f'bytes */{file_size}'
                return response
            status = 206
        else:
            start = 0
            end = file_size - 1
            status = 200
        
        content_length = end - start + 1
        
        response = web.StreamResponse(
            status=status,
            headers={
                'Content-Type': mime_type,
                'Content-Disposition': f'inline; filename="{file_name}"',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(content_length),
                'Cache-Control': 'public, max-age=31536000',
                'Content-Range': f'bytes {start}-{end}/{file_size}',
            }
        )
        
        await response.prepare(request)
        
        CHUNK_SIZE = 1024 * 1024
        start_chunk = start // CHUNK_SIZE
        end_chunk = end // CHUNK_SIZE
        offset_in_first_chunk = start % CHUNK_SIZE
        bytes_in_last_chunk = (end % CHUNK_SIZE) + 1
        
        bytes_sent = 0
        current_chunk = start_chunk
        
        async for chunk_data in app.stream_media(message, offset=start_chunk):
            chunk_to_send = chunk_data
            
            if current_chunk == start_chunk:
                chunk_to_send = chunk_to_send[offset_in_first_chunk:]
            
            if current_chunk == end_chunk:
                if current_chunk == start_chunk:
                    chunk_to_send = chunk_to_send[:bytes_in_last_chunk - offset_in_first_chunk]
                else:
                    chunk_to_send = chunk_to_send[:bytes_in_last_chunk]
            
            if bytes_sent + len(chunk_to_send) > content_length:
                chunk_to_send = chunk_to_send[:content_length - bytes_sent]
            
            if len(chunk_to_send) > 0:
                await response.write(chunk_to_send)
                bytes_sent += len(chunk_to_send)
            
            current_chunk += 1
            
            if bytes_sent >= content_length or current_chunk > end_chunk:
                break
        
        await response.write_eof()
        return response
        
    except Exception as e:
        logger.error(f"Error streaming file: {e}")
        return web.json_response({"error": f"Failed to stream file: {str(e)}"}, status=500)

async def start_server():
    await app.start()
    logger.info("Telegram client started")
    
    web_app = web.Application()
    web_app.add_routes(routes)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, server_host, server_port)
    await site.start()
    
    logger.info(f"Server started at http://{server_host}:{server_port}")
    logger.info(f"Login with username: {admin_username}, password: {admin_password}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()
