#!/usr/bin/env py
"""Collect backups of selected directories and Docker volumes.
"""
import getpass
import hashlib
import hmac
import logging
import os
import pathlib
import sys
import subprocess

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)

PASSWORD_HEXDIGEST = "54701ee8dca633bc72d64ceba2013f105b801c96716dea77907965d173767520"
BACKUPS_DIR = pathlib.Path(__file__).parent.absolute()
REPO_PATH = BACKUPS_DIR / "restic-repo"

assert (
    REPO_PATH.exists() and REPO_PATH.is_dir()
), f"Expected a directory at {REPO_PATH=}"
os.environ["RESTIC_REPOSITORY"] = str(REPO_PATH)


def collect_restic_password() -> None:
    if "RESTIC_PASSWORD" in os.environ:
        log.info("Password alredady set")
        return
    password = getpass.getpass()
    hash = hashlib.sha3_256(password.encode("utf8")).hexdigest()
    if hmac.compare_digest(hash, PASSWORD_HEXDIGEST):
        log.info("Password matches hash.")
        os.environ["RESTIC_PASSWORD"] = password
    else:
        log.warning("Password doesn't match hash")
        sys.exit(2)


def check_restic_cmd() -> None:
    try:
        log.info("Checking restic command")
        subprocess.run(["restic", "version"]).check_returncode()
    except:
        log.error("Error running 'restic'; is it installed?")
        sys.exit(1)


def check_repo() -> None:
    try:
        log.info("Checking repository integrity")
        subprocess.run(["restic", "check"]).check_returncode()
    except:
        log.error("Error checking Restic Repo; aborting.")
        sys.exit(3)


BACKED_UP_FOLDERS = [
    pathlib.Path("~/projects"),
    pathlib.Path("~/services"),
]


def backup_folders() -> None:
    log.info("Taking backups")
    exclude_file = pathlib.Path(__file__).parent / "restic-excludes"
    cmd = ["restic", "backup", f"--exclude-file={exclude_file.absolute()}"]
    cmd.extend(str(p.expanduser().absolute()) for p in BACKED_UP_FOLDERS)
    subprocess.run(cmd).check_returncode()


def forget_old_backups() -> None:
    log.info("Forgetting old backups")
    cmd = [
        "restic",
        "forget",
        "--keep-daily=8",
        "--keep-weekly=16",
        "--keep-monthly=64",
        "--keep-yearly=9999",
    ]
    subprocess.run(cmd).check_returncode()


def sync_to_onedrive() -> None:
    log.info("Syncing to OneDrive")
    cmd = [
        "rclone",
        "copy",
        str(REPO_PATH),
        "onedrive:restic-repo",
    ]
    subprocess.run(cmd).check_returncode()



if __name__ == "__main__":
    check_restic_cmd()
    collect_restic_password()
    check_repo()
    backup_folders()
    forget_old_backups()
    sync_to_onedrive()
