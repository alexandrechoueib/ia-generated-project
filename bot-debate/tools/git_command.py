#!/usr/bin/env python3

"""
git_command.py

Wrapper sécurisé autour de Git destiné à être utilisé par un agent.

Exemples :
    python git_command.py status
    python git_command.py log --oneline -10
    python git_command.py diff
    python git_command.py add fichier.py
    python git_command.py commit -m "Mon commit"

Options :
    --repo PATH       Répertoire du dépôt Git
    --timeout SECS    Timeout d'exécution (défaut: 30s)
    --allow-dangerous Autorise certaines commandes sensibles
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# Commandes que l'agent ne peut pas exécuter par défaut.
BLOCKED_COMMANDS = {
    "clean",
}

# Commandes nécessitant --allow-dangerous.
DANGEROUS_COMMANDS = {
    "reset",
    "push",
    "rebase",
    "checkout",
    "restore",
    "branch",
}

DEFAULT_TIMEOUT = 30


def output(success, returncode=0, stdout="", stderr="", error=None):
    """Retourne toujours une réponse JSON facilement exploitable par l'agent."""
    result = {
        "success": success,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
    }

    if error:
        result["error"] = error

    print(json.dumps(result, ensure_ascii=False, indent=2))


def get_command(args):
    """Retourne la première sous-commande Git."""
    if not args:
        return None

    # Ignore les éventuelles options globales Git.
    for arg in args:
        if not arg.startswith("-"):
            return arg

    return None


def validate_repo(repo):
    """Vérifie que le chemin existe et qu'il s'agit d'un dépôt Git."""
    path = Path(repo).resolve()

    if not path.exists():
        raise ValueError(f"Le répertoire n'existe pas : {path}")

    if not path.is_dir():
        raise ValueError(f"Ce chemin n'est pas un répertoire : {path}")

    # Vérification via git plutôt que de simplement tester .git,
    # car un worktree peut ne pas avoir de .git classique.
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        timeout=5,
    )

    if result.returncode != 0:
        raise ValueError(f"Ce répertoire n'est pas un dépôt Git : {path}")

    return path


def validate_command(args, allow_dangerous):
    """Applique les règles de sécurité sur la commande Git."""
    command = get_command(args)

    if not command:
        raise ValueError("Aucune commande Git fournie.")

    command = command.lower()

    if command in BLOCKED_COMMANDS:
        raise PermissionError(
            f"La commande 'git {command}' est interdite."
        )

    if command in DANGEROUS_COMMANDS and not allow_dangerous:
        raise PermissionError(
            f"La commande 'git {command}' est considérée comme sensible. "
            "Utilisez --allow-dangerous pour l'autoriser."
        )


def run_git(repo, args, timeout, allow_dangerous):
    """Exécute Git sans passer par un shell."""
    validate_command(args, allow_dangerous)

    command = ["git", "-C", str(repo), *args]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            env={
                **os.environ,
                # Évite certains prompts interactifs qui bloqueraient l'agent.
                "GIT_TERMINAL_PROMPT": "0",
            },
        )

        output(
            success=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )

        return result.returncode

    except subprocess.TimeoutExpired as exc:
        output(
            success=False,
            returncode=-1,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            error=f"Git a dépassé le timeout de {timeout} secondes.",
        )
        return 124

    except FileNotFoundError:
        output(
            success=False,
            returncode=-1,
            error="Git n'est pas installé ou n'est pas présent dans le PATH.",
        )
        return 127

    except Exception as exc:
        output(
            success=False,
            returncode=-1,
            error=f"Erreur inattendue : {exc}",
        )
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Wrapper sécurisé pour exécuter des commandes Git."
    )

    parser.add_argument(
        "--repo",
        default=".",
        help="Répertoire du dépôt Git (défaut: répertoire courant).",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout en secondes (défaut: {DEFAULT_TIMEOUT}).",
    )

    parser.add_argument(
        "--allow-dangerous",
        action="store_true",
        help="Autorise les commandes Git sensibles.",
    )

    parser.add_argument(
        "git_args",
        nargs=argparse.REMAINDER,
        help="Arguments à transmettre à Git.",
    )

    args = parser.parse_args()

    try:
        repo = validate_repo(args.repo)

        if args.timeout <= 0:
            raise ValueError("Le timeout doit être supérieur à 0.")

        if not args.git_args:
            raise ValueError("Aucune commande Git fournie.")

        return run_git(
            repo=repo,
            args=args.git_args,
            timeout=args.timeout,
            allow_dangerous=args.allow_dangerous,
        )

    except (ValueError, PermissionError) as exc:
        output(
            success=False,
            returncode=1,
            error=str(exc),
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())

