# Web Reader

A minimal web reader for following RSS feeds.

This web reader is designed to be run at specific intervals of the day.

For example, you can poll feeds every hour, or every day.

This project is intentionally not designed to be a real-time reader.

Web Reader supports the following feed formats:

- RSS
- Atom
- JSON Feed
- microformats2

## Installation

First, clone this repository and install the required dependencies:

```
git clone https://github.com/capjamesg/web-reader
cd web-reader
pip install -r requirements.txt
```

Then, update `feeds.txt` with the URLs of the feeds you want to follow.

Every feed should be on its own line in `feeds.txt`.

To poll for new posts, run:

```
python3 poll.py
```

To generate a site from the posts, run:

```
aurora build
```

## License

This project is licensed under an [MIT license](LICENSE).