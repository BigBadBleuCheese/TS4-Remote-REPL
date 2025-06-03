TOC
- [Description](#description)
- [How to Use](#how-to-use)
  - [Have PlumbBuddy 1.5 or later](#have-plumbbuddy-15-or-later)
  - [Enable Runtime Mod Integration in PlumbBuddy](#enable-runtime-mod-integration-in-plumbbuddy)
  - [Download and Install this mod](#download-and-install-this-mod)
  - [Use the Cheat Console](#use-the-cheat-console)
  - [Python interpretation](#python-interpretation)
    - [Evaluation](#evaluation)
    - [Execution](#execution)

# Description

Remote REPL is a PlumbBuddy UI Bridge mod for The Sims 4 which allows you to execute ad-hoc Python code in the game's environment while it's running, which can be useful for experimentation and debugging purposes.

<!-- ![GitHub Release Date](https://img.shields.io/github/release-date/BigBadBleuCheese/TS4-Remote-REPL) -->
![GitHub last commit](https://img.shields.io/github/last-commit/BigBadBleuCheese/TS4-Remote-REPL)
![GitHub top language](https://img.shields.io/github/languages/top/BigBadBleuCheese/TS4-Remote-Repl)
![GitHub contributors](https://img.shields.io/github/contributors/BigBadBleuCheese/TS4-Remote-REPL)
![GitHub Issues](https://img.shields.io/github/issues/BigBadBleuCheese/TS4-Remote-REPL)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/BigBadBleuCheese/TS4-Remote-REPL)

# How to Use

## Have PlumbBuddy 1.5 or later
This hasn't become generally available yet, so... I don't know... sweet talk Amethyst and maybe she'll slip you a file which *she really shouldn't*.
Look, just don't tell me about it.

## Enable Runtime Mod Integration in PlumbBuddy
This should be turned on by default, but in case it isn't...
1. open PlumbBuddy's menu
2. select **Settings**
3. on the **General** tab, switch on **Enable runtime mod integration**

## Download and Install this mod
Probably should go with [the latest release](releases) for this, but if you're particularly adventurous, you can download a [GitHub Actions workflow artifact](actions) for any commit you want.
Each time a commit make it to the `master` branch in this repo, GitHub will build a complete, production-ready version of the `.ts4script` file for use by the game.

## Use the Cheat Console
The Cheat Console command to get the REPL to appear in PlumbBuddy is:
```
remote_repl.launch
```
PlumbBuddy will grab foreground app focus to ask your permission to launch the REPL's UI.
Give consent and you're off to the races.

## Python interpretation
The REPL is capable of both **evaluation** and **execution**, which behave slightly differently.

*Implementation note: For those to whom those seem familiar, yes, the REPL is using [`eval`](https://docs.python.org/3.7/library/functions.html#eval) and [`exec`](https://docs.python.org/3.7/library/functions.html#exec), respectively.*

The REPL *always interprets your Python code starting from the context of its own module*.
This means that you need to import other modules to interact with the structures and objects of your own mod (or of the game).

The REPL's effects are "as good as" if it were a compiled script mod performing the actions *you tell it to perform*.
If you inject into EA code or alter tuning... whatever... that will stick around until the game is closed, *even if you close the REPL's bridged UI*.

### Evaluation
This is just a single Python expression.
As long as it's valid, the REPL will give you the result of evaluating your expression in the game.
If you fat-fingered something, the REPL will give you the message for the error it caught while trying to evaluate the expression.
Also, importantly: *only one Python expression is allowed in this mode*.

### Execution
This can be... whatever you want.
You could stuff an entire script mod into a single execution.
That's probably a bad idea, but *you could*.
The real purpose here is to give you the ability to provide complex logic, up to and including whole functions or even classes, if you need them.

Because execution doesn't inherently have a result, but you might want to have results, two magical variables are put in the local scope of each of your executions by the REPL:
* `__EXEC_RESULTS_LIST__`: a list to which you can do whatever you like, but most likely [append](https://docs.python.org/3.7/tutorial/datastructures.html?highlight=append)
* `__EXEC_RESULTS_DICT__`: a dictionary, the key/value pairs of which are... entirely up to you

When your execution finishes, the contents of both of the above will be transmitted to the REPL's interface and displayed along with the status of the execution itself (i.e. any error information if one was thrown).

---

That's about it.
Have fun being a script mod with a life all its own, because that's what you are when you're using the REPL.