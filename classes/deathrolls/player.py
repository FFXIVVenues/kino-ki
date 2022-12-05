from __future__ import annotations

from dataclasses    import dataclass
from typing         import (
    TYPE_CHECKING,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union
)

from utils  import connection

if TYPE_CHECKING:
    from discord    import Bot, Guild, Member, User
######################################################################

__all__ = (
    "DeathrollPlayer",
)

DP = TypeVar("DP", bound="DeathrollPlayer")

######################################################################
@dataclass
class DeathrollPlayer:

    __slots__ = (
        "user",
        "total_games",
        "wins",
        "streak"
    )

    user: Union[Member, User]
    total_games: int
    wins: int
    streak: int

######################################################################
    @classmethod
    def new(cls: Type[DP], user: Member) -> DP:

        c = connection.cursor()
        c.execute(
            "INSERT INTO deathroll_players (user_id) VALUES (%s)",
            (user.id, )
        )

        connection.commit()
        c.close()

        return cls(
            user=user,
            total_games=0,
            wins=0,
            streak=0
        )

######################################################################
    @classmethod
    async def from_data(
        cls: Type[DP], bot: Bot, *, data: Tuple[int, int, int, int]
    ) -> DP:

        user = bot.get_user(data[0])
        if user is None:
            try:
                user = await bot.fetch_user(data[0])
            except:
                pass

        return cls(
            user=user,
            total_games=data[1],
            wins=data[2],
            streak=data[3]
        )

######################################################################
    @property
    def name(self) -> str:

        return self.user.display_name

######################################################################
    def update(self, won_game: bool = False) -> None:

        self.total_games += 1

        if won_game is True:
            self.wins += 1
            self.streak += 1
        else:
            self.streak = 0

        c = connection.cursor()
        c.execute(
            "UPDATE deathroll_players SET games = %s, wins = %s, "
            "streak = %s WHERE user_id = %s",
            (self.total_games, self.wins, self.streak, self.user.id)
        )

        connection.commit()
        c.close()

        return

######################################################################
