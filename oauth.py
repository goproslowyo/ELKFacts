import os
import time
import json
import logging
import aiohttp
import asyncio
from aiohttp import web
from typing import Optional, Dict
from pathlib import Path
from urllib.parse import urlencode
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TwitchOAuth:
    """Handles Twitch OAuth authentication using authorization code flow."""

    TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"
    USER_URL = "https://api.twitch.tv/helix/users"

    def __init__(self, client_id: str, client_secret: str, cache_file: Optional[str] = None):
        """
        Initialize the OAuth handler.

        Args:
            client_id: Twitch application client ID
            client_secret: Twitch application client secret
            cache_file: Optional path to cache the token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.cache_file = cache_file
        self._token_data = None
        self._code_future = None

    def get_auth_url(self) -> str:
        """
        Get the authorization URL for the Twitch OAuth flow.
        Returns:
            URL string that user needs to visit to authorize the bot
        """
        scopes = [
            'chat:read',
            'chat:edit'
        ]

        params = {
            'client_id': self.client_id,
            'redirect_uri': 'http://localhost:3000/callback',
            'response_type': 'code',
            'scope': ' '.join(scopes)
        }

        return f"https://id.twitch.tv/oauth2/authorize?{urlencode(params)}"

    async def start_callback_server(self):
        """Start local server to handle OAuth callback."""
        self._code_future = asyncio.Future()
        app = web.Application()
        app.router.add_get('/callback', self._handle_callback)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 3000)
        await site.start()
        return runner

    async def _handle_callback(self, request: web.Request) -> web.Response:
        """Handle the OAuth callback request."""
        try:
            code = request.query.get('code')
            if code:
                if not self._code_future.done():
                    self._code_future.set_result(code)
                return web.Response(text="Authorization successful! You can close this window.")
            else:
                error = request.query.get('error', 'No code received')
                if not self._code_future.done():
                    self._code_future.set_exception(Exception(error))
                return web.Response(text=f"Authorization failed: {error}", status=400)
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            return web.Response(text="Internal error", status=500)

    def _log_token_status(self, token_data: Dict[str, str], status: str):
        """Log detailed token status information."""
        if not token_data:
            return

        expires_at = token_data.get('expires_at', 0)
        expiry_time = datetime.fromtimestamp(expires_at)
        now = datetime.now()
        time_until_expiry = expiry_time - now

        logger.info(f"Token Status: {status}")
        logger.info(f"Token User: {token_data.get('login', 'unknown')}")
        logger.info(f"Token Expiry: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')} ({time_until_expiry})")

        # Add warning if token is close to expiry
        if time_until_expiry <= timedelta(minutes=30):
            logger.warning(f"Token expires soon! Only {time_until_expiry} remaining")

    async def _load_cached_token(self) -> None:
        """Load token data from cache file if it exists and is valid."""
        self._token_data = None
        try:
            if not os.path.exists(self.cache_file):
                logger.info("No token cache file found")
                return

            with open(self.cache_file, 'r') as f:
                cached = json.load(f)

            # Check if token is still valid (with 5 minute buffer)
            if cached.get('expires_at', 0) > time.time() + 300:
                # Validate token with Twitch and get user info
                headers = {
                    'Authorization': f'Bearer {cached["access_token"]}',
                    'Client-Id': self.client_id
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(self.VALIDATE_URL, headers=headers) as response:
                        if response.status == 200:
                            validation_data = await response.json()
                            cached['login'] = validation_data['login']
                            self._token_data = cached
                            self._log_token_status(cached, "Loaded valid token from cache")
                            return

            self._log_token_status(cached, "Cached token invalid or expired")

        except Exception as e:
            logger.warning(f"Error loading cached token: {e}")

    def _save_token_to_cache(self) -> None:
        """Save current token data to cache file."""
        if not self.cache_file or not self._token_data:
            return

        try:
            # Ensure directory exists
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_file, 'w') as f:
                json.dump(self._token_data, f)

            self._log_token_status(self._token_data, "Saved new token to cache")

        except Exception as e:
            logger.warning(f"Error saving token to cache: {e}")

    async def _get_new_token(self, code: str) -> Dict[str, str]:
        """
        Get a new access token from Twitch using authorization code.
        Args:
            code: Authorization code from OAuth redirect
        Returns:
            Dict containing token data
        """
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://localhost:3000/callback'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.TOKEN_URL, data=data) as response:
                    if response.status != 200:
                        error_data = await response.text()
                        raise Exception(f"Failed to get token: {error_data}")

                    token_data = await response.json()
                    token_data['expires_at'] = time.time() + token_data['expires_in']

                    # Get user info from validation
                    headers = {
                        'Authorization': f'Bearer {token_data["access_token"]}',
                        'Client-Id': self.client_id
                    }

                    async with session.get(self.VALIDATE_URL, headers=headers) as validate_response:
                        if validate_response.status != 200:
                            raise Exception(f"Failed to validate token: {await validate_response.text()}")

                        validation_data = await validate_response.json()
                        token_data['login'] = validation_data['login']

                    self._token_data = token_data
                    self._save_token_to_cache()
                    self._log_token_status(token_data, "Generated new token")
                    return token_data

        except Exception as e:
            logger.error(f"Error in _get_new_token: {e}")
            raise

    async def get_token(self) -> Dict[str, str]:
        """
        Get a valid token, either from cache or through the OAuth flow.
        Returns:
            Dict containing token data
        """
        try:
            # Try to load from cache first
            if self.cache_file:
                await self._load_cached_token()

            # Check if we have a valid cached token
            if self._token_data:
                if self._token_data['expires_at'] > time.time() + 300:  # 5 minute buffer
                    return self._token_data

            # Start local server to handle callback
            runner = await self.start_callback_server()

            try:
                # Print authorization instructions
                auth_url = self.get_auth_url()
                print("\nAuthorization needed. Please follow these steps:")
                print("1. Visit this URL in your browser:")
                print(auth_url)
                print("\n2. Authorize the application")
                print("3. Wait for the automatic redirect...")

                # Wait for the callback to receive the code
                code = await self._code_future
                token_data = await self._get_new_token(code)
                return token_data

            finally:
                # Clean up the server
                await runner.cleanup()

        except Exception as e:
            logger.error(f"Error getting token: {e}")
            raise
