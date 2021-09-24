import feedparser
import os
from pyasn1_modules.rfc2459 import CommonName
from twython import Twython, TwythonError
from Config import Config as conf


Config=conf()


def rss_to_twitter(url: str):
    """Read rss feed and post it as a twitter post

    ------------
    url: str
        URL to RSS feed.
    ------------
    """
    for i in Config.twit_details:
        feed = feedparser.parse(url)
        if feed:
            for item in feed["items"]:
                link = item["link"]

                if already_logged(link, i.get("log_file")):
                    print("Already Tweeted:", link)
                else:
                    post_tweet(message=compose_message(item), acc=i)
                    write_log(link, i.get("log_file"))
                    print("Posted:", link)
                    break
    return


def already_logged(url: str, filename: str) -> bool:
    """Does the content exist on any line in the log file?

    Parameters
    ----------
    url: str
        Content to search file for.
    filename: str
        Full path to file to search.

    Returns
    -------
    bool
        Returns `True` if content is found in file, otherwise `False`.

    """
    if os.path.isfile(filename):
        with open(filename, "r+") as f:
            lines = f.readlines()
        if (url + "\n" or url) in lines:
            return True
    return False


def write_log(url: str, filename: str):
    """Append content to log file, on one line.

    Parameters
    ----------
    url: str
        Content to append to file.
    filename: str
        Full path to file that should be appended.
    """
    try:
        with open(filename, "a+") as f:
            f.write(url + "\n")
    except IOError as e:
        print(e)


def compose_message(item: feedparser.FeedParserDict) -> str:
    """Compose a tweet from an RSS item (title, link, description)
    and return final tweet message.

    Parameters
    ----------
    item: feedparser.FeedParserDict
        An RSS item.

    Returns
    -------
    str
        Returns a message suited for a Twitter status update.
    """
    title, link, _, tags = (
        item["title"],
        item["link"],
        item["description"],
        [f"#{(t.term).replace(' ','')}" for t in item.get("tags", [])],
    )
    if len(tags) > 6:
        tags = tags[:5]
    tags = " ".join(tags)
    print(tags)
    message = shorten_text(title, maxlength=250 - len(tags)) + "\n" + tags + " " + link
    # print(message)
    return message


def shorten_text(text: str, maxlength: int) -> str:
    """Truncate text and append three dots (...) at the end if length exceeds
    maxlength chars.

    Parameters
    ----------
    text: str
        The text you want to shorten.
    maxlength: int
        The maximum character length of the text string.

    Returns
    -------
    str
        Returns a shortened text string.
    """
    return (text[:maxlength] + "...") if len(text) > maxlength else text


def post_tweet(message: str, acc: dict):
    """Post tweet message to account.

    Parameters
    ----------
    message: str
        Message to post on Twitter.
    acc: str
        Account to use
    """
    try:
        twitter = Twython(
            acc.get("client_key"),
            acc.get("client_secret"),
            acc.get("access_token"),
            acc.get("access_token_secret"),
        )
        twitter.update_status(status=message)
    except TwythonError as e:
        print(e)


if __name__ == "__main__":

    rss_to_twitter("https://bitcoinist.com/feed/")