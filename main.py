"""Точка входа в игру"""
from game import Game


def main():
    """Запуск игры"""
    print("Запуск градостроительного симулятора...")
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
