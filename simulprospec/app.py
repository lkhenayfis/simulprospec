import click
import simulprospec.montadeck as md
import simulprospec.extraisaidas as es

@click.group()
def cli():

    """
    Ferramenta de linha de comando para automatizacao da simulacao de cenarios
    """

    pass

@click.command()
@click.argument("dir_deck")
@click.argument("modo")
def montaentradas(dir_deck, modo):

    """
    Modificacao dos arquivos dger.dat e vazoes.dat para simulacao final com cenarios
    externos

    Argumentos

    dir_deck: diretorio contendo os arquivos do deck a ser rodado
    modo: Modo de execucao -> 1 prepara dger para simulacao historica; 2 p consistencia de dados
    """

    modo = int(modo)

    md.modifica_dger(dir_deck, modo)
    md.modifica_vazoes(dir_deck)

    pass

@click.command()
@click.argument("dir_saidas")
def extraisaidas(dir_saidas):

    """
    Extracao estruturada dos arquivos de saida da simulacao final

    Argumentos
    
    dir_saidas: diretorio contendo os arquivos de saida da simulacao final
    """

    es.le_saidas(dir_saidas)

    pass

cli.add_command(montaentradas)
cli.add_command(extraisaidas)
