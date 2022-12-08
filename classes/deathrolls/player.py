from __future__ import annotations

from dataclasses    import dataclass
from discord        import EmbedField
from typing         import (
    TYPE_CHECKING,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union
)

from utils  import connection, make_embed

if TYPE_CHECKING:
    from discord    import Bot, Embed, Guild, Member, User
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
        "longest_streak",
        "current_streak"
    )

    user: Union[Member, User]
    total_games: int
    wins: int
    longest_streak: int
    current_streak: int

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
            longest_streak=0,
            current_streak=0
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
            longest_streak=data[3],
            current_streak=data[4]
        )

######################################################################
    @property
    def name(self) -> str:

        return self.user.display_name

######################################################################
    @property
    def losses(self) -> int:

        return self.total_games - self.wins

######################################################################
    def stats(self) -> Embed:

        fields = [
            EmbedField("__Total Games__", f"`{self.total_games}`", True),
            EmbedField("__Wins__", f"`{self.wins}`", True),
            EmbedField("__Losses__", f"`{self.losses}`", True),
            EmbedField("__Current Win Streak__", f"`{self.current_streak} games`", True),
            EmbedField("__Longest Win Streak__", f"`{self.longest_streak} games`", True)
        ]

        return make_embed(
            title=f"Deathroll Stats for {self.user.name}",
            fields=fields,
            timestamp=True
        )

######################################################################
    def update(self, won_game: bool = False) -> None:

        self.total_games += 1

        if won_game is True:
            self.wins += 1
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 0

        c = connection.cursor()
        c.execute(
            "UPDATE deathroll_players SET games = %s, wins = %s, "
            "longest_streak = %s, current_streak = %s WHERE user_id = %s",
            (
                self.total_games, self.wins, self.longest_streak,
                self.current_streak, self.user.id
            )
        )

        connection.commit()
        c.close()

        return

######################################################################
