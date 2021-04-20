# COPYRIGHT (C) 2021 BY LEGENDX22 AND PROBOYX

# MADE BY LEGEND X AND TEAM LEGEND
# MADE FOR LEGEND ROBOT & DAISYX
# FULL CREDITS TEAM LEGEND🔥🔥🔥
# IF YOU KANG THIS THAN KEEP CREDITS
# 1ST UPDATER FOR GROUP MANAGEMENT BOTS

# PLEASE KEEP CREDITS PLEASE 🥺🥺🥺


# I KNOW YOU ARE GOOD YOU KEEP MY CREDITS 😘


import asyncio
import sys
from os import environ, execle, path, remove

import heroku3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from DaisyX import OWNER_ID
from DaisyX.config import get_str_key
from DaisyX.services.events import register
from DaisyX.services.telethon import tbot as update

HEROKU_APP_NAME = get_str_key("HEROKU_APP_NAME", None)
HEROKU_API_KEY = get_str_key("HEROKU_API_KEY", None)
UPSTREAM_REPO_URL = get_str_key("UPSTREAM_REPO_URL", None)
if not UPSTREAM_REPO_URL:
    UPSTREAM_REPO_URL = "https://github.com/atleastskem/skem"

requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "requirements.txt"
)


async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"•[{c.committed_datetime.strftime(d_form)}]: {c.summary} by <{c.author}>\n"
        )
    return ch_log


async def updateme_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


@register(pattern="^/update(?: |$)(.*)")
async def upstream(ups):
    global UPSTREAM_REPO_URL
    check = ups.message.sender_id
    OK = int(OWNER_ID)
    if int(check) != OK:
        if int(check) == 1141839926 or int(check) == 1759123364:
            pass
        else:
            return
    lol = await ups.reply("`Checking for updates, please wait....`")
    conf = ups.pattern_match.group(1)
    off_repo = UPSTREAM_REPO_URL
    force_update = False

    try:
        txt = "`Oops.. Updater cannot continue "
        txt += "please add heroku apikey, name`\n\n**LOGTRACE:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await lol.edit(f"{txt}\n`directory {error} is not found`")
        repo.__del__()
        return
    except GitCommandError as error:
        await lol.edit(f"{txt}\n`Early failure! {error}`")
        repo.__del__()
        return
    except InvalidGitRepositoryError as error:
        if conf != "now":
            await lol.edit(
                f"**Unfortunately, the directory {error} does not seem to be a git repository.\
            \nBut we can fix that by force updating the bot using** `/update now`"
            )
            return
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        force_update = True
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)

    ac_br = repo.active_branch.name
    if ac_br != "main":
        await lol.edit(
            f"**[UPDATER]:**` Looks like you are using your own custom branch ({ac_br}). "
            "in that case, Updater is unable to identify "
            "which branch is to be merged. "
            "please checkout to any official branch`"
        )
        repo.__del__()
        return

    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)

    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")

    if not changelog and not force_update:
        await lol.edit("\nYour DaisyX  >>  **up-to-date**  \n")
        repo.__del__()
        return

    if conf != "now" and not force_update:
        changelog_str = (
            f"**New UPDATE available for {ac_br}\n\nCHANGELOG:**\n`{changelog}`"
        )
        if len(changelog_str) > 4096:
            await lol.edit("`Changelog is too big, view the file to see it.`")
            file = open("output.txt", "w+")
            file.write(changelog_str)
            file.close()
            await update.send_file(
                ups.chat_id,
                "output.txt",
                reply_to=ups.id,
            )
            remove("output.txt")
        else:
            await lol.edit(changelog_str)
        await ups.respond("**do** `/update now` **to update**")
        return

    if force_update:
        await lol.edit("`Force-Syncing to latest main bot code, please wait...`")
    else:
        await lol.edit("`Still Running ....`")
    if conf == "deploy":
        if HEROKU_API_KEY is not None:
            heroku = heroku3.from_key(HEROKU_API_KEY)
            heroku_app = None
            heroku_applications = heroku.apps()
            if not HEROKU_APP_NAME:
                await lol.edit(
                    "`Please set up the HEROKU_APP_NAME variable to be able to update your bot.`"
                )
                repo.__del__()
                return
            for app in heroku_applications:
                if app.name == HEROKU_APP_NAME:
                    heroku_app = app
                    break
            if heroku_app is None:
                await lol.edit(
                    f"{txt}\n`Invalid Heroku credentials for updating bot dyno.`"
                )
                repo.__del__()
                return
            await lol.edit(
                "`[Updater]\
                            Your bot is being deployed, please wait for it to complete.\nIt may take upto 5 minutes `"
            )
            ups_rem.fetch(ac_br)
            repo.git.reset("--hard", "FETCH_HEAD")
            heroku_git_url = heroku_app.git_url.replace(
                "https://", "https://api:" + HEROKU_API_KEY + "@"
            )
            if "heroku" in repo.remotes:
                remote = repo.remote("heroku")
                remote.set_url(heroku_git_url)
            else:
                remote = repo.create_remote("heroku", heroku_git_url)
            try:
                remote.push(refspec="HEAD:refs/heads/main", force=True)
            except GitCommandError as error:
                await lol.edit(f"{txt}\n`Here is the error log:\n{error}`")
                repo.__del__()
                return
            await lol.edit("Successfully Updated!\n" "Restarting.......")
    else:
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await lol.edit("`Successfully Updated!\n" "restarting......`")
        args = [sys.executable, "-m", "DaisyX"]
        execle(sys.executable, *args, environ)
        return
