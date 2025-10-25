def register_commands(app):
    from .generate_users import generate_users
    from .generate_products import generate_products
    from .generate_interactions import  generate_interactions
    
    app.cli.add_command(generate_users)
    app.cli.add_command(generate_products)

__all__ = ["register_commands"]