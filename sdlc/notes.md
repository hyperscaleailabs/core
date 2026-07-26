# SDLC notes

Working practices assumed across hsailabs repositories.

## Companion private repo

It is assumed as the best practice for a public repo to have a private companion repo
holding its specific private workflows: deployment configurations, environment
definitions, internal operations, and any information that has no place in a public
repository. The public repo stays a deployable product; the companion is the private
layer on top of it, and the default destination whenever it is unclear where a piece
of internal information belongs.
