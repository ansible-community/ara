#!/usr/bin/env python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager

from ara import app, db

manager = Manager(app)


def main():
    manager.run()


if __name__ == '__main__':
    main()
