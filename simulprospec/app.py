import click
import simulprospec.montadeck as md
import simulprospec.extraisaidas as es

@click.group()
def cli():
    pass

@click.command()
@click.argument("dir_deck")
def montaentradas(dir_deck):
    md.modifica_dger(dir_deck)
    md.modifica_vazoes(dir_deck)

@click.command()
@click.argument("dir_saidas")
def extraisaidas(dir_saidas):
    es.le_saidas(dir_saidas)

cli.add_command(montaentradas)
cli.add_command(extraisaidas)
