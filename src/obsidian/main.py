import fire

from obsidian.daily import daily
from obsidian.lib import console
from obsidian.publisher import publish


class CLI:
    @staticmethod
    def daily():
        console.print("Daily update")
        daily()

    @staticmethod
    def publish():
        console.print("Publishing...")
        publish()
        console.print("Done!")


def main():
    fire.Fire(CLI)


if __name__ == "__main__":
    main()
