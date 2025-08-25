import sys
from app.cli import main as cli
from app.cli import click

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage : python main.py [commande]")
#     else:
#         command_name = sys.argv[1]
#         try:
#             command_func = getattr(cli, command_name)
#             try:
#                 command_func(*sys.argv[2:])
#             except TypeError as e:
#                 print(f"Erreur : Vérifiez les arguments de la commande '{command_name}'.")
#         except AttributeError:
#             print(f"Erreur : la commande '{command_name}' n'existe pas.")

if __name__ == "__main__":
    click.cli()