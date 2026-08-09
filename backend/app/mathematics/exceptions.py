from app.shared.exceptions import NotFoundError


class PlayerNotFoundError(NotFoundError):
    def __init__(self, player_id: object) -> None:
        super().__init__("PLAYER_NOT_FOUND", f"Player '{player_id}' not found.")
