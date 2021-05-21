# discord.ext.wizard

A [discord.py](https://discordpy.readthedocs.io/) extension for making wizards within Discord.

## What is a wizard?

Here's a good explanation from [Wikipedia](<https://en.wikipedia.org/wiki/Wizard_(software)):

> A software wizard or setup assistant is a user interface type that presents a user with a sequence of dialog boxes that lead the user through a series of well-defined steps. Tasks that are complex, infrequently performed or unfamiliar may be easier to perform using a wizard.
>
> _\- Wikipedia_

Basically, a wizard acts as a quick, understandable guide to accomplish a task. Instead of typing a bunch of commands to download a software, a installation wizard would ease the process of that.

In our case, we wanted to make a wizard-maker for [discord.py](https://discordpy.readthedocs.io/).

## Why discord.ext.wizard?

Well, making a wizard in discord.py is already hard, especially when having a lot of inputs/options.

Here's an example of a giveaway-maker wizard made by one of the maintainer's friends (which happens to be [a YouTuber with over 3 thousand subscribers](https://www.youtube.com/channel/UC2ITRZ4_Di-KMHSIylTQbBA)):

```py
def convert(time):
    pos = ["s","m","h","d"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2


    return val * time_dict[unit]

questions = ["Which channel should it be hosted in?",
            "What should be the duration of the giveaway? (s|m|h|d)",
            "What is the prize of the giveaway?"]

answers = []

def check(m):
    return m.author == ctx.author and m.channel == ctx.channel

for i in questions:
    await ctx.send(i)

    try:
        msg = await client.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('You didn\'t answer in time, please be quicker next time!')
        return
    else:
        answers.append(msg.content)

try:
    c_id = int(answers[0][2:-1])
except:
    await ctx.send(f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time.")
    return

channel = client.get_channel(c_id)

time = convert(answers[1])
if time == -1:
    await ctx.send(f"You didn't answer the time with a proper unit. Use (s|m|h|d) next time!")
    return
elif time == -2:
    await ctx.send(f"The time must be an integer. Please enter an integer next time")
    return
```

To summarize, the code given above is over 50 lines of code. I would like to chop that code down to two parts, the for loop and the checks.

The for loop is the part of the code where they ask the questions, aka the wizard itself which he [the person who made the code] actually did a good job on.

The checks part is the part where it checks if the given content is proper, or correct. As you can see, it's just full of raw `except` error catching.

Now, let's re-create this code using `discord.ext.wizard`:

```py
from discord.ext.wizard import Prompt
import discord.ext.wizard as wizard


def convert(time):

    pos = ["s","m","h","d"]
    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}
    unit = time[-1]

    if unit not in pos:
        return -1

    try:
        val = int(time[:-1])
    except (ValueError, IndexError):
        return -2

    return val * time_dict[unit]


questions = [Prompt(title="Which channel should it be hosted in?",
                    check=lamba m: all(maybe_num in (str(num) for num in range(10)) for maybe_num in m.content[0][2:-1]),  # scuffed way to check if it can be converted to int but works
                    res_type=lambda msg: int(msg[0][2:-1])
                    ),
            Prompt("What should be the duration of the giveaway? (s|m|h|d)", res_type=convert),
            Prompt("What is the prize of the giveaway?")]

giveaway_wizard = wizard.EmbedWizard(bot=client, channel=ctx.channel, user=ctx.author, prompts=questions, title="Giveaway Wizard", default_timeout=15)

answers = await giveaway_wizard.run()

if answers[1] == -1:
    return await ctx.send(f"You didn't answer the time with a proper unit. Use (s|m|h|d) next time!")
    return
elif answers[1] == -2:
    return await ctx.send(f"The time given must be in proper format.\nExample: `24h`  `1d`  `1440m`  `86400s`")

# then your actual giveaway timer here
```

The code given above has been chopped to just 30 lines of code, doing the same thing but with `discord.ext.wizard`.
