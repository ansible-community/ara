from ara import models


def configure_context_processors(app):

    @app.context_processor
    def ctx_add_nav_data():
        '''Makes some standard data from the database available in the
        template context.'''

        playbook_item_limit = app.config.get('NAV_MENU_MAX_PLAYBOOKS', 10)
        host_item_limit = app.config.get('NAV_MENU_MAX_HOSTS', 10)

        return dict(hosts=models.Host.query
                    .order_by(models.Host.name)
                    .limit(host_item_limit),
                    playbooks=models.Playbook.query
                    .order_by(models.Playbook.time_start.desc())
                    .limit(playbook_item_limit))
