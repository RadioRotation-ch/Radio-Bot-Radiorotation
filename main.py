from __future__ import annotations

import contextlib

import discord as pycord
import dotenv

from _helpers import _InvalidArgumentError, _MissingRequiredArgument, validate_url

# no usage of os.environ because this should work multiple times on the same machine

bot = pycord.Bot()
channel_id: int | None = dotenv.get_key(".env", "CHANNEL_ID")


@bot.event
async def on_ready():
    url: str | None = dotenv.get_key(".env", "URL")

    if not channel_id:
        _missing = ["CHANNEL_ID"]
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
    conn: pycord.VoiceClient = await channel.connect()

    if isinstance(channel, pycord.StageChannel):
        instance = None
        with contextlib.suppress(Exception):
            instance = await channel.fetch_instance()
        if not instance:
            if topic := dotenv.get_key(".env", "STAGE_INSTANCE_TOPIC"):
                await channel.create_instance(topic=topic, reason="RadioRotationStream")

            else:
                raise _MissingRequiredArgument(["STAGE_INSTANCE_TOPIC"])

    for member in channel.members:
        if member.id == bot.user.id:
            if member.voice.suppress:
                await member.edit(suppress=False)
            if member.voice.mute:
                await member.edit(mute=False)

    conn.play(pycord.FFmpegPCMAudio(url))


@bot.event
async def on_voice_state_update(
    member: pycord.Member,
    before: pycord.VoiceState,
    after: pycord.VoiceState,
):
    if after.channel.id != channel_id:
        return
    if member.id == bot.user.id:
        if after.mute:
            await member.edit(mute=False)
        if after.suppress and after.channel.type == pycord.ChannelType.stage_voice:
            await member.edit(suppress=False)
    else:
        if not after.mute and after.channel.type == pycord.ChannelType.voice:
            await member.edit(mute=True)
        if not after.suppress and after.channel.type == pycord.ChannelType.stage_voice:
            await member.edit(suppress=True)


if __name__ == "__main__":
    if token := dotenv.get_key(".env", "TOKEN"):
        bot.run(token)
    else:
        raise _MissingRequiredArgument(["TOKEN"])
