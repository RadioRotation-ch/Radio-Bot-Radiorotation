import asyncio

import discord as pycord
import dotenv

from _helpers import _InvalidArgumentError, _MissingRequiredArgument, validate_url

# no usage of os.environ because this should work multiple times on the same machine

bot = pycord.Bot()


@bot.event
async def on_ready():
    channel_id: int | None = dotenv.get_key(".env", "CHANNEL_ID")
    url: str | None = dotenv.get_key(".env", "URL")

    if not channel_id:
        _missing = ["Channel ID"]
        if not url:
            _missing.append("URL")

        raise _MissingRequiredArgument(_missing)

    elif not url:
        _missing = ["URL"]
        raise _MissingRequiredArgument(_missing)

    if not validate_url(url):
        raise _InvalidArgumentError("URL", "valid URL", url)

    channel: pycord.VoiceChannel | pycord.StageChannel = await bot.fetch_channel(channel_id)  # type: ignore
    if channel.type not in {pycord.ChannelType.stage_voice, pycord.ChannelType.voice}:
        raise _InvalidArgumentError(
            "CHANNEL_ID",
            "channel_id pointing to a voice channel",
            f"ChannelType.{str(channel.type)}",
        )

    # if isinstance(channel, pycord.StageChannel):
    # channel.

    conn: pycord.VoiceClient = await channel.connect()
    conn.play(pycord.FFmpegPCMAudio(url))


if __name__ == "__main__":
    token: str | None = dotenv.get_key(".env", "TOKEN")

    if not token:
        raise _MissingRequiredArgument(["TOKEN"])

    async def start_helper():
        await bot.start(token)

    asyncio.run(start_helper())
