Title: Dotfile Management & Git Tricks
Date: 2024-11-20 12:00
Tags: Technical, Musings


<style>
mark{
    background: linear-gradient(to right, #6666ff, #0099ff , #00ff00, #ff3399, #6666ff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: rainbow_animation 6s ease-in-out infinite;
    background-size: 400% 100%;
}

@keyframes rainbow_animation {
    0%,100% {
        background-position: 0 0;
    }

    50% {
        background-position: 100% 0;
    }
}
</style>

# TL;DR
 * [Preamble](#Preamble)
     * [GNU-Stow](#GNU-Stow)
     * [The Idea](#TheIdea)
 * [Tangent Time!](#Tangent-Time)
 * [Managing Dotfiles](#Managing-Dotfiles)
 * [Amuse Bouche, Repo Specific Git Configs](#AmuseBouche)


# <a id="Preamble"></a>Preamble<hr/>

I am using [GNU STOW](https://www.gnu.org/software/stow/) with [git](https://git-scm.com/) to manage [my dotfiles](https://github.com/shiddy/dot). This means that all I have to do on a new machine is access my git repo, install stow, and pitter patter - let's get att'er. After many years of manually managing these files, using different migration tools, and writing a tool myself, I can confidently say that stow is the best solution I've used.

The readme on my dotfiles should be easy enough to follow, but <mark style="padding-top:0;">the shiddy blog</mark> is where I take the time to talk through some of the more interesting bits, updating your files, security considerations, and if you ask nicely some useful quality of life pieces. Join me will you?

## <a id="GNU-Stow"></a>GNU-Stow<hr/>

GNU Stow is a really nice piece of software that does not get enough attention. It's also getting up there in years, [with its initial release in 2001](https://git.savannah.gnu.org/cgit/stow.git/commit/?id=1b3b46907af7f23032645f14c27778cf77eae4dd) it's had enough eyes on it that it will work for my use case.

The basic premise is that you can set up a slightly strange directory structure, call `stow` within the root of that directory and stow will create symlinks that the rest of your system will see and treat as regular files.

This works quite well within git, where we can archive our stow configuration, but also because our configuration files are symlinks, whenever we change any of our configuration files (since they are symlinks), we can see all the changes as git changes natively and commit them without extra fuss!

## <a id="TheIdea"></a>The Idea<hr/>

The basic premise is that we want to create our directory with paths that reflect the paths to our configuration files.

```log
$HOME/.zshrc => $HOME/DOTFILEREPO/zsh/.zshrc
```

# <a id="Tangent-Time"></a>Tangent time!<hr/>

I was lucky enough to start using linux around Canonical's Precise Pangolin (12.04) release. If you ask me it was the perfect time to get serious because I was so late to the game. A ton of the bullshit was solved by smarter people than me. I could reasonably start learning with things that were in a functional state.

Many of my future co-workers and co-horts would wax on about the nightmarish ages of old, and how easy I had it in comparison. Some of the more notable examples:

 * Buying a new laptop after fighting with ndiswrapper and a random broadcom nic longer than the cost of hours lost to it not working.
 * Trying to quit cigarettes when the company needed you to deploy iptables before firewalld existed.
 * wicd and iwlconfig for setting up wireless devices before NetworkManager, and only having one laptop without an ethernet port.
 * Running an isolinux memdisk kernel to install because many BIOSes didn't support usb booting, and praying that the myriad of tunables to whatever incantation your conputer's firmware would be accepted before el torito cd extensions.
 * Buying an nvidia graphics card and having to have a seperate windows machine to install the driver on, copying the needed files back to linux and running the "NVIDIA X Server Settings" gui to get a wildly inconsistent kernel interface to a busted driver so the nvidia module compilation would fail and you would have to spend weeks old manually compiled kernels waiting for upstream fixes.

To be fair, I rarely get to use SIMD as much as I'd like. I hardly get to use compiled languaged as much as I'd like. But I've never been told by the guy who made my operating system that I should be retroactively aborted for using an enumerable for a system call read. If that did happen I have a feeling I would probably just install windows and get a job in finance or something idk.

I feel like I lost the plot in this tangent a bit, but my point is that there has never been a better time to be getting into computing. The only real problem at this point is the curation of quality content. There is a decent amount of amazing material, and a seemingly infinite amount of absolute slop. Honestly, one of the best skills in comp-sci is just being around and paying attention while things are happening. Then you at least know what things felt like when computers were a hundred times slower, and why opening a random program shouldn't take 40 seconds long.

People in those positions don't often praise the progress we have made, we don't often tell the stories where a bunch of people got together and cleaned up an utter shit-fest and left us with a better strategy.

Think of this, how many common places exist for executables?

```log
/bin
/sbin
/usr/bin
/usr/sbin
/usr/local/bin
macos has bin and sbin directories for homebrew and a few for [Cryptex](https://support.apple.com/guide/security/apple-security-research-device-seca7ff718d2/1/web/1)
random install dirs for things like node where they want you have to update your path after install
~/Downloads  that one time you downloaded an .exe from your work email that strangely did nothing but open the commandline for a second.
```

To me, this list feels excessive... But don't get it twisted, **at least** there is a known and defined place for executables. Until **very** recently, configuration files were an absolute shit-show. Everyone who made a program that would have user specific configs would put them wherever they could. You want to put all your user specific data, configs, and state in a place specific to the user? `$HOME` is good enough. Then your `$HOME` directory looked like an ADHD teen's bedroom and you had to just let it fester over time.

Or... hear me out, you could just sweep all the clutter under the rug by hiding the files from your default file program.

![eyebrows.gif]({static}/images/eyebrows.gif)

I know that sounds stupid, because it is. But the reason flags like `-a` exist on `ls`, and some files are hidden by default is because it makes finding the random file in your home directory harder. Until the X11 Desktop Group [proposed a standard on base directories in 2003](https://specifications.freedesktop.org/basedir-spec/latest/index.html) there was not a place other than random dotfiles in your home directory. It's one of the main reasons that we call our user configuration files dotfiles in the first place.

This standard means that we are able to move all our files to a directory where they belong, so long as the programs are written to respect the XDG standards (the number of which is growing pretty steadily)

As we can see on their docs:

> "`$XDG_CONFIG_HOME` defines the base directory relative to which user-specific configuration files should be stored. If `$XDG_CONFIG_HOME` is either not set or empty, a default equal to `$HOME`/.config should be used."


I don't have a great reason for deviating from the default `$HOME/.config` path so that is what I will use the rest of this article

So cheers to you XDG Standard writers. Let's hope this becomes popular enough that people in the future don't even know what hidden files are, and we can add a new mitre attack group for gen alpha.

# <a id="Managing-Dotfiles"></a>Tangent Time Over, Managing Dotfiles<hr/>

You will need to make a new repository in your version control software; Fill it with directories of the programs you want to manage the dotfiles for

Worth pointing out that since we are setting up our dotfiles to be managed to the XDG_CONFIG_HOME standard we can add a .config directory here as well.

```
dot
 |-nvim
 |--.config
 |-tmux
 |--.config
 |-zsh
 |--.config (* you will have do add a .zshenv 'export ZDOTDIR="$HOME/.config"')
 |--.zshenv
 | ...
```

Then we need to start moving our configs there. This works quite well if you are running on a new machine, lest you accidentally kill what you have in the process of copying things over...otherwise be careful.

once you have moved everything over your directories should be populated with some of your dotfiles. It should look something like this

```
dot
 |-nvim
 |--.config
 |---(imagine some LUA or something stupid)
 |-tmux
 |--.config
 |---.tmux.conf
 |-zsh
 |--.config
 |---.zshrc
 |--.zshenv
 | ...
```

Now you are ready to use stow to link everything! The basic command looks like this:

`stow -d PATH/TO/YOUR/REPO -t ~ YOURPROGRAMNAME`

 * `-d` is the directory your stow should be running from, in this case we set it to the directory of our repo, variable expansion works fine btw
 * `-t` is the target where we want to write symlinks to, in our case I use `~` which means our home directory of our current user
 * `YOURPROGRAMNAME` would refer to the directories that we created for each of our programs. `nvim`, `zsh`, `tmux` or whatever you specified.

If you are feeling really randy, you can also just make a shell script that has all these commands ready for a fresh install, or even a blog post so that you don't have to do that until you get to this part of the blog!

```bash
#!/bin/bash

# I'm assuming you are using git, so I ignore .git and the current directory here, I assume you can change it if you need to.
for line in $(find . -type d -maxdepth 1 | sed "s|.\/||" | grep -v -e .git -e "\."); do
        stow -d $(pwd) -t ~ $line
done
```

Then you can install everything with `/bin/bash whateveryounamethatthing.sh`

Now you can see any config changes you make with your version control, and updating it is as simple as committing your changes and fetching whatever changes you want on whatever machine you are using. Different branches can work for OS changes or local stack changes for me, but the sky is the limit.

...and that's pretty much it...


# <a id="AmuseBouche"></a>Multiple Git SSH configs on one machine<hr/>

Now for an adjacent idea that I want to treat you to... like a blog amuse bouche

Somehow I find myself with a many to many relationship between git accounts and git servers with different auth schemes. This is very annoying since you can't use the same ssh pub keys on multiple accounts, this is why git@github.com allows you to test auth to it without a tty and github does not have to do weird pathing.

also, did you know that you can get anyone's public keys off of github?
[The Primagen's Public RSA Keys](https://github.com/theprimeagen.keys)

See? This is an intentional design choice but can lead to some unintentional data loss. \*The Primagen does not know that he has root access to my machines... yet\* So it's not uncommon to generate and revoke keys often if you are being serious about security and what you put online... perhaps that's an indicator of something I'm working on, perhaps it's not.

So if you find yourself in the same situation you might have some random directory need to use a different ssh key for authing to your git server, while also using a completely different key for another repo on the same computer, this is the section that helps you.

Remember that .git directory I ignored in my dotfiles before? that has all the information of what's happening to the files on your repo, local and remote. If you look at a "normal" repository, there is a `.git/config` file that shows these connections to a local user.

```ini
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
	ignorecase = true
	precomposeunicode = true
[remote "origin"]
	url = git@github.com:idk/something.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
	remote = origin
	merge = refs/heads/main
```

Recall, we know that we have git@github.com as the remote user/host info in this file. So we need to configure the ssh connection information to something else. We can do so by adding a host to `~/.ssh/config` so that we can then edit the connection information in our repo's `.git/conffig` and have it route somewhere else. That looks like this:

```
# $HOME/.ssh/config
Host shiddy
    HostName github.com
    User git
    IdentityFile /Users/user/.ssh/your-private-key-for-this-user
```

What we are essentially saying is that we should make a fake host (in my case called shiddy) that should be handled differently. So now we can update our `.git/config` file in our repo to use this fake host

```ini
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
	ignorecase = true
	precomposeunicode = true
[remote "origin"]
	url = git@shiddy:idk/something.git # NOTE THE DOMAIN CHANGE
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
	remote = origin
	merge = refs/heads/main
```

This will work all well and good, but also would mean that every commit you make will be for whatever your global git user is, which can be another data loss that you can run into committing to different git repos as same user. So we have one final change we should make to our local git config:

```ini
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
	ignorecase = true
	precomposeunicode = true
[remote "origin"]
	url = git@personal-github:shiddy/dot.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
	remote = origin
	merge = refs/heads/main
[user] # This tells git to use the following user for git changes to all it manages in this .git repo
	name = shiddy
	email = shiddy@shiddy.io
```

And would you guess, the changes to `.ssh/config` are also dotfiles? So minding all of the ways you can passively leak information, you can add the `.ssh/config` changes to your stow repo. I'll leave that as an exercise for the reader if you are so inclined.

Thanks for reading! Hopefully you learned something, and if you have anything to say I guess you can find my contact links at the bottom of the page.

OK BYE |o･-･)ﾉ
