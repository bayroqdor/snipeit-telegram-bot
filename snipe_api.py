import httpx 
import json
from config import SNIPEIT_URL, SNIPEIT_API_KEY

API_BASE_URL = f"{SNIPEIT_URL}/api/v1"
HEADERS = {
    "Authorization": f"Bearer {SNIPEIT_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def _handle_error(response):
    """API xatoliklarini chiroyli formatda qaytarish"""
    try:
        res_json = response.json()
        if 'messages' in res_json:
            return res_json['messages']
        if 'error' in res_json:
            return res_json['error']
    except json.JSONDecodeError:
        return response.text
    return "Noma'lum xatolik yuz berdi."

async def _request(method, url, **kwargs):
    """Umumiy so'rov funksiyasi"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, headers=HEADERS, **kwargs)
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {e.response.status_code} - {_handle_error(e.response)}")
            return {"status": "error", "messages": _handle_error(e.response)}
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            return {"status": "error", "messages": f"Ulanishda xatolik: {e}"}

async def get_assets(status=None, limit=10, offset=0, search=None):
    url = f"{API_BASE_URL}/hardware"
    params = {'limit': limit, 'offset': offset, 'sort': 'created_at', 'order': 'desc'}
    if status:
        params['status'] = status
    if search:
        params['search'] = search
    return await _request('get', url, params=params)

async def get_asset_by_id(asset_id):
    url = f"{API_BASE_URL}/hardware/{asset_id}"
    return await _request('get', url) 

async def get_users(limit=10, offset=0, search=None):
    url = f"{API_BASE_URL}/users"
    params = {'limit': limit, 'offset': offset}
    if search:
        params['search'] = search
    return await _request('get', url, params=params)

async def get_user_by_id(user_id):
    url = f"{API_BASE_URL}/users/{user_id}"
    return await _request('get', url) 

async def get_user_assets(user_id):
    url = f"{API_BASE_URL}/users/{user_id}/assets"
    return await _request('get', url)

async def get_models(search=None):
    url = f"{API_BASE_URL}/models"
    params = {'limit': 50, 'sort': 'name', 'order': 'asc'}
    if search:
        params['search'] = search
    return await _request('get', url, params=params) 

async def get_status_labels():
    url = f"{API_BASE_URL}/statuslabels"
    return await _request('get', url)

async def create_asset(payload):
    url = f"{API_BASE_URL}/hardware"
    return await _request('post', url, data=json.dumps(payload))

async def assign_asset(asset_id, user_id):
    url = f"{API_BASE_URL}/hardware/{asset_id}/checkout"
    payload = {"checkout_to_type": "user", "assigned_user_id": user_id, "note": "Telegram bot orqali biriktirildi"}
    return await _request('post', url, data=json.dumps(payload))

async def create_user(payload):
    url = f"{API_BASE_URL}/users"
    return await _request('post', url, data=json.dumps(payload))
