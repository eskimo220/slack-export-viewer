import webbrowser

import click
import flask

from slackviewer.app import app
from slackviewer.archive import extract_archive
from slackviewer.reader import Reader
from slackviewer.utils.click import envvar, flag_ennvar

from slackviewer.data import *
from threading import Thread


def configure_app(app, archive, channels, no_sidebar, no_external_references,
                  debug):
    app.debug = debug
    app.no_sidebar = no_sidebar
    app.no_external_references = no_external_references
    if app.debug:
        print("WARNING: DEBUG MODE IS ENABLED!")
    app.config["PROPAGATE_EXCEPTIONS"] = True

    path = extract_archive(archive)

    for f in os.listdir(path):
        reader = Reader(os.path.join(path, f))

        top = flask._app_ctx_stack
        top.channels.update(reader.compile_channels(channels))
        top.groups.update(reader.compile_groups())
        top.dms.update(reader.compile_dm_messages())
        top.dm_users += reader.compile_dm_users()
        top.mpims.update(reader.compile_mpim_messages())
        top.mpim_users += reader.compile_mpim_users()


def empty_app():
    top = flask._app_ctx_stack
    top.channels = {}
    top.groups = {}
    top.dms = {}
    top.dm_users = []
    top.mpims = {}
    top.mpim_users = []


@click.command()
@click.option('-p',
              '--port',
              default=envvar('PORT', '5000'),
              type=click.INT,
              help="Host port to serve your content on")
@click.option("-z",
              "--archive",
              type=click.Path(),
              required=True,
              default=envvar('SEV_ARCHIVE', ''),
              help="Path to your Slack export archive (.zip file or directory)"
              )
@click.option('-I',
              '--ip',
              default=envvar('SEV_IP', '0.0.0.0'),
              type=click.STRING,
              help="Host IP to serve your content on")
@click.option('--no-browser',
              is_flag=True,
              default=flag_ennvar("SEV_NO_BROWSER"),
              help="If you do not want a browser to open "
              "automatically, set this.")
@click.option('--channels',
              type=click.STRING,
              default=envvar("SEV_CHANNELS", None),
              help="A comma separated list of channels to parse.")
@click.option('--no-sidebar',
              is_flag=True,
              default=flag_ennvar("SEV_NO_SIDEBAR"),
              help="Removes the sidebar.")
@click.option('--no-external-references',
              is_flag=True,
              default=flag_ennvar("SEV_NO_EXTERNAL_REFERENCES"),
              help="Removes all references to external css/js/images.")
@click.option(
    '--test',
    is_flag=True,
    default=flag_ennvar("SEV_TEST"),
    help=
    "Runs in 'test' mode, i.e., this will do an archive extract, but will not start the server,"
    " and immediately quit.")
@click.option('--debug', is_flag=True, default=flag_ennvar("FLASK_DEBUG"))
def main(port, archive, ip, no_browser, channels, no_sidebar,
         no_external_references, test, debug):
    # if not archive:
    #     raise ValueError("Empty path provided for archive")
    empty_app()
    if prepare():
        configure_app(app, "tmp", channels, no_sidebar, no_external_references,
                      debug)
    else:
        empty_app()

    def dl():
        for t in os.environ.get("SLACK_BOT_TOKEN").split(","):
            saveData(t)

        prepare()
        empty_app()
        configure_app(app, "tmp", channels, no_sidebar, no_external_references,
                      debug)

    Thread(target=dl).start()

    if not no_browser and not test:
        webbrowser.open("http://{}:{}".format(ip, port))

    if not test:
        app.run(host=ip, port=port)
