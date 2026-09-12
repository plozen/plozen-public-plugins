# YouTube API setup

Read the current Google documentation before the first live authorization:

- [YouTube Data API OAuth 2.0 authentication](https://developers.google.com/youtube/v3/guides/authentication)
- [YouTube `videos` resource and `status.publishAt`](https://developers.google.com/youtube/v3/docs/videos)
- [YouTube `videos.insert`](https://developers.google.com/youtube/v3/docs/videos/insert)

## One-time setup

1. Create or select a Google Cloud project.
2. Enable YouTube Data API v3.
3. Create an OAuth client for a desktop/installed application and download the client-secret JSON to a local ignored path.
4. Confirm Python 3 and the local client-secret JSON are available. The bundled scripts use only the Python standard library; no third-party package installation is required.
5. Run `youtube_auth.py` interactively and complete Google consent in the user-visible browser.
6. Keep the resulting token file outside the repository and outside the Obsidian Vault.

The auth script requests `https://www.googleapis.com/auth/youtube.upload` for upload and `https://www.googleapis.com/auth/youtube.readonly` for post-upload `videos.list` readback. A schedule is sent with `privacyStatus=private` and a future ISO 8601 `publishAt`; the API does not allow setting `publishAt` on an already-published video.
