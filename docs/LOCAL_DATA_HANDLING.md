# Local Data Handling

The reference runtime reads user-supplied local files and writes artifacts to the selected local output directory. Its core normalization, validation, policy, reporting, Decision Pack, integrity, and handoff modules make no application network calls and include no telemetry, analytics, account, database, or cloud integration.

Package installation may contact a package source depending on how the user invokes `pip`; that behavior belongs to the package installer, not the toolkit runtime.

Users remain responsible for authorization to process inventory data, local file permissions, retention, backups, sharing, and deletion. Generated artifacts may contain the inventory values supplied by the user. This repository does not claim host isolation, encryption, secure deletion, or protection from other software on the same machine.
