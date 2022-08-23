import click
import simulprospec.montadeck as md

@click.group()
def cli():
    pass

@click.command()
@click.argument("dir_deck")
def montaentradas(dir_deck):
    md.modifica_dger(dir_deck)
    md.modifica_vazoes(dir_deck)

cli.add_command(montaentradas)
