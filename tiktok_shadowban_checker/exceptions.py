"""Exception classes for the TikTok Shadow Ban Checker SDK."""


class TikTokShadowBanError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(TikTokShadowBanError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(TikTokShadowBanError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(TikTokShadowBanError):
    """Raised when the actor run does not finish within the allowed timeout."""
