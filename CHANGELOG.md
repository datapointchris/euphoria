## Misc
1. [X] Take code out of `__init__.py` files
   1. [X] Put them in `main.py` for the module or name of module
   2. [X] Import the names in the `__init__.py` file for better top level imports
2. [X] Main Site Navigation
   1. [X] Put this on base page that all pages inherit from
   2. [X] Inherit CSS as well
3. [ ] Restructure site so that all apps are top level
      1. [X] events
      2. [X] countdowns
      3. [X] journal
      4. [x] habits



# v0.3.0 --> Get rid of Flask-SQLAlchemy
- [X] Use regular SQLAlchemy instead.


# v0.2.0 --> Move databases (Postgres, MongoDB, DynamoDB) to their own Servers
---
Prod only, further ahead will figure out how to sync dev and "testing" (god help me) to the prod environment
- [X] pg_cron and update task priorities
- [X] MongoDB move to Atlas