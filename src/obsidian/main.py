import fire
import rich.console

from obsidian.daily import daily
from obsidian.publish import publish

console = rich.console.Console()


class CLI:
    def daily(self):
        console.print("Daily update")
        daily()

    def publish(self):
        console.print("Publishing")
        publish()


def main():
    fire.Fire(CLI)


if __name__ == "__main__":
    main()
