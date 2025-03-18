import argparse
import asyncio
import logging

from aiopath import AsyncPath
from aioshutil import copyfile


parser = argparse.ArgumentParser(description="Sorting folder")
parser.add_argument("--source", "-S", help="Source folder", required=True)
parser.add_argument("--output", "-O", help="Output folder", default="dist")

args = vars(parser.parse_args())

source = AsyncPath(args.get("source"))
output = AsyncPath(args.get("output"))

folders = []


async def read_folder(path: AsyncPath) -> None:
    async for el in path.iterdir():
        if await el.is_dir():
            await read_folder(el)
        else:
            await copy_file(el)


async def copy_file(file: AsyncPath) -> None:
    ext = file.suffix.lstrip(".") or "no_extension"
    new_path: AsyncPath = output / ext
    try:
        await new_path.mkdir(exist_ok=True, parents=True)
        await copyfile(file, new_path / file.name)
        logging.info("Copied %s to %s", file, new_path)
    except OSError as err:
        logging.error("Error copying %s: %s", file, err)


if __name__ == "__main__":
    if not asyncio.run(source.exists()):
        logging.error("Source folder %s does not exist.", source)
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
        asyncio.run(read_folder(source))
