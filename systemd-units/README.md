# SystemD Units for this Backup Script

These two units should let you start and enable the backup script.

To install it:

- Copy these files into `$HOME/.config/systemd/user`
- Run `systemd --user daemon-reload` to add the files to SystemD
- Test the backup script with `systemd --user start backups`
- Run `systemd --user enable backups.service` and `systemd --user enable backups.timer`

