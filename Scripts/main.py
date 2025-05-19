import flet as ft
from flet import Page
from FletPages import AppController

def main(page: Page) -> None:
    AppController(page)

if __name__ == '__main__':
    ft.app(target=main)