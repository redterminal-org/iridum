# Welcome to Iridum, the interactive virtual text environment!

A highly experimental, interactive virtual text environment build by its users!
Its built on the [Evennia MUD/MUSH Creation System](https://www.evennia.com/),
which also has in depth
[documentation](https://www.evennia.com/docs/latest/index.html), which you
should read and consult.

## Early ALPHA stage

I've been working on this for a long time now (with a break of 6 month) to make
at least a starting environment. There are still a lot of bugs and I have lot of
things to do but I hope for vivid participation and contributions.

**MIRRORS** \
https://github.com/redterminal-org/iridum \
https://codeberg.org/fab/iridum

---

## Another MUD/MUSH?

Yes and No. Its not a MUD in the classical adventure or RPG sense. Its not even
a real game, at least until games are built in by the users.

It is a virtual text environment where the users are also **builders** who can
create Objects, Rooms, Scripts and Characters, which are created by the builders
who are also **developers** who send in **Pull Requests**, which you are highly
encouraged to send in. But because everything is built by its users, there have
to be a quite a few rules to keep everything as clean and tidy as possible. This
has still to be worked out and exactly planned.

---

## How to connect

There are several ways to connect to the Iridum world:

1. With your webbrowser: https://iridum.redterminal.org
2. With SSH by running `ssh iridum.redterminal.org`. For the password simply hit
   enter with an empty password.
3. Over Telnet+SSL to `iridum.redterminal.org` on port `4444` with a dedicated
   MUD/MUSH client. There are several different MUD clients out there (TUI or
   GUI) which differ in features and operation. I hope there will be
   installation instructions provided by the users in future, but here we'll
   start with the `tintin++` CLI client with installation instructions.

---

## How to build a test/development environment

This is for the people who wish to unleash the full powers of the Iridum
development. The whole codebase is in Python3 and runs under Python3.13 on a
Debian GNU/Linux 13 (trixie) system. So Python3.13 is regarded as the minimum
version for Iridum. Here are the steps to build a local development environment.

1. Choose a location in your home folder which holds two directories: The Iridum
   git repository and the Evennia MUD/MUSH Creation System virtual environment.
   We'll use the directory `~/dev` for that, so create that first.
   ```bash
   mkdir ~/dev
   ```

2. Change into the `~/dev` directory and clone original repository (which we'll
   use here) or your fork on Codeberg.org. Then you need to copy the
   `settings_localhost.py` to `settings.py`, to use the localhost settings and
   not the original server settings, which won't work.
   ```bash
   cd ~/dev
   git clone https://codeberg.org/fab/iridum
   cd ~/iridum/server/conf/
   cp settings_localhost.py settings.py
   cd ~/dev
   ```

3. Create the virtual Python3 environment and start it:
   ```bash
   python3 -m venv evennia
   source evennia/bin/activate
   # Upgrade pip to the newest version if neccessary
   pip install --upgrade pip
   # now move into the repositories directory
   cd iridum
   # install Evennia and all the needed dependencies
   pip install -r requirements.txt
   ```

4. Migrate the database, start Iridum and create the *superuser*:
   ```bash
   evennia migrate # Create the initial database, which will be empty
   
   # This will start the Iridum Evennia Environment and ask for the *superuser*
   # credentials, you'll need to log in: A username, an email address and a
   # password.
   evennia start
   ```

5. Now Iridum is running (of course with an empty database, a @batch script to
   give you a starting environment in your virtual text matrix is planned). You
   can now connect to it with your webbrowser at `http://localhost:4001/` or you
   can use `ssh -p 8022 localhost` to enter it with SSH, or you can connect over
   Telnet+SSL with a dedicated MUD/MUSH client. There are a lot of MUD/MUSH
   clients out there, but we'll show here how to use the `tintin++` terminal MUD
   client in the next section.

6. Now you can create a starting environment and if you're ready you can shut
   down Iridum and the Python virtual environment:
   ```bash
   # Stop the Iridum Evennia server
   cd ~/dev/iridum/
   evennia stop
   deactivate # deactivates the Python3 environment
   ```

This is the general way to set up a development environment, where you can
create Objects, Scripts, Rooms and other game mechanics with the underlying
Iridum and Evennia System.

---

## Set up the 'tintin++' MUD client.

This describes how to setup the `tintin++` MUD client, which is also the package
name of the client on Debian 13 Trixie:

### Installation
Because `tintin++` may be not available on all Linux/BSD distributions, you may
have to compile it yourself eventually. I won't go into detail here, for now
it's up to you to install `tintin++` on your Distro. Here we'll go with Debian
13 Trixie, which has it as a package in the stable repository.

```bash
# as root
apt install tintin++
```

### Create a config file

After you managed to install the `tintin++` MUD client, you have to set up a
configuration file under `~/.tintin/iridum.cfg`. Commands to the `tintin++`
client itself begin with a `#`, so to exit the client you have to enter `#END`.
The configuration file is just a script of these `#` commands:

```
#CONFIG {AUTO TAB} {5000}
#CONFIG {BUFFER SIZE} {10000}
#CONFIG {CHARSET} {UTF-8}
#CONFIG {COLOR MODE} {TRUE}
#CONFIG {COLOR PATCH} {ON}
#CONFIG {COMMAND COLOR} {\e[0;37m}
#CONFIG {COMMAND ECHO} {OFF}
#CONFIG {CONNECT RETRY} {0.0}
#CONFIG {HISTORY SIZE} {1000}
#CONFIG {LOG MODE} {RAW}
#CONFIG {MOUSE} {OFF}
#CONFIG {PACKET PATCH} {AUTO OFF}
#CONFIG {RANDOM SEED} {7305759848}
#CONFIG {REPEAT CHAR} {!}
#CONFIG {REPEAT ENTER} {OFF}
#CONFIG {SCREEN READER} {OFF}
#CONFIG {SCROLL LOCK} {ON}
#CONFIG {SPEEDWALK} {OFF}
#CONFIG {TAB WIDTH} {8}
#CONFIG {TELNET} {ON}
#CONFIG {TINTIN CHAR} {#}
#CONFIG {VERBATIM} {ON}
#CONFIG {VERBATIM CHAR} {\}
#CONFIG {VERBOSE} {OFF}
#CONFIG {WORDWRAP} {ON}

#PROMPT {| [%*]%!{( \(.*\))?}%!{( \[.*\])?}%!{( '.*')?} |} {<039>[%1]<019>%2<069>%3<029>%4<099>} {} {10}
#SPLIT

#ACTION {| [%*]%* |} {#DRAW HORIZONTAL LINE -2 1 -2 -1} {3}

#EVENT {SESSION CONNECTED}
{
	#SEND {connect <username> <Passw0rd>}
}

#SSL Iridum iridum.redterminal.org 4444
```

Place this file as `~/.tintin/iridum.cfg`, so you'll also have a little status
bar showing information about your character, away status, location and if there
are any mails. The [tintin++ documentation](https://tintin.mudhalla.net/) may
help you on your first steps.

You can create a `username` and a `password` with the webclient or over SSH, so
you don't need to change the configuration file after removing the `#EVENT
{SESSION CONNECTED}` to get access to the login screen. If you put the right
`<username>` and `<password>` into the `#SEND` command, you'll be logged in
automatically on every start of `tintin++`.

To start `tintin++` with the created configuration file run:
```bash
tt++ -G ~/.tintin/iridum.cfg
```
You could create an alias for this command in your `.bashrc`, `.zshrc` or
whatever shell you use.

---

## Pull Requests and send in Patches

You are highly encouraged to make source code contributions. Codeberg.org or
Github PRs are preferred, but if you don't have or want a Codeberg.org account,
you can send in your commits with [git send-email](https://git-send-email.io/)
if you're able to create a good formatted set of emails with `git
format-patch`. I prefer as less commit emails as possible which are all under
the same *main* email and not commits below other commits. But if you've
set up your git to use `git send-email` you can send in your commits to
`-fab- <fab@redterminal.org>`.

---

## LICENSE

The source code is provided under the terms of the
[MIT](LICENSE) license. All contributions have to be compatible with this
license.
