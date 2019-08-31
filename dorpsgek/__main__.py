import logging

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO)


if __name__ == "__main__":
    main()
