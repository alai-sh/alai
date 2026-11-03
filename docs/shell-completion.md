---
description: How to set up completion of alai's commands in your shell.
---

# Shell completion

alai can complete its commands and options in bash, zsh, fish, PowerShell
and tcsh. To set up completion, add the line for your shell to the file
the table names, and the line loads the script that
`alai generate-shell-completion <shell>` prints:

| Shell | Add to | Line |
|---|---|---|
| bash | `~/.bashrc`, or `~/.bash_profile` on macOS | `eval "$(alai generate-shell-completion bash)"` |
| zsh | `~/.zshrc`, after `compinit` | `eval "$(alai generate-shell-completion zsh)"` |
| fish | | Run `alai generate-shell-completion fish > ~/.config/fish/completions/alai.fish` once |
| PowerShell | `$PROFILE` | `alai generate-shell-completion powershell | Out-String | Invoke-Expression` |
| tcsh | `~/.tcshrc` | ``eval "`alai generate-shell-completion tcsh`"`` |

After adding the line, restart the shell, and completion works with your
shell's usual key, such as Tab.

!!! note "bash on macOS"

    Terminal and iTerm2 start bash as a login shell, which reads
    `~/.bash_profile` and not `~/.bashrc`. Use `~/.bash_profile`, unless it
    already sources `~/.bashrc`. Linux terminals start non-login shells, which
    read `~/.bashrc`.

!!! note "zsh needs compinit"

    The script registers alai with zsh's completion system, so the
    completion system has to be loaded first. Frameworks such as Oh My Zsh
    load it for you. Without one, put `autoload -Uz compinit && compinit`
    above the alai line. zsh is the
    default shell on macOS.

The script doesn't list alai's options but runs `alai` on each completion
request, so the script never needs regenerating when alai is upgraded.

Completion only works when `alai` is the command being run. When alai is
called through another command, such as `uv run alai ...`, the shell completes
`uv`'s arguments and not alai's.

## Other ways to set up completion

### bash-completion

[bash-completion](https://github.com/scop/bash-completion) loads a command's
completion script from a directory the first time you press Tab after that
command, rather than when the shell starts. Saving alai's script there means
nothing needs adding to `~/.bashrc`, and a new shell doesn't run alai until
you complete it:

```console
$ alai generate-shell-completion bash > ~/.local/share/bash-completion/completions/alai
```

Loading the script from that directory needs bash-completion version 2,
which most Linux distributions install with bash. macOS doesn't include
bash-completion, but Homebrew installs it as the `bash-completion@2`
package.

### argcomplete's global completion

alai's completion is built on
[argcomplete](https://github.com/kislyuk/argcomplete). If you already use its
[global completion](https://github.com/kislyuk/argcomplete#global-completion)
(`activate-global-python-argcomplete`, in bash and zsh), alai is completed
with no setup.
