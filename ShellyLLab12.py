# Name: Luke Shelly
# Class: CSEC 1437
# Assignment: Lab 12

import urllib.request
import json
import csv
import random
import xml.etree.ElementTree as ET
from html.parser import HTMLParser


class WebTextParser(HTMLParser):
    """Gets readable text from an HTML page."""

    def __init__(self):
        """Initialize the objects and the data that their methods will use."""
        super().__init__()
        self.text_parts = []
        self.skip_tag = None

    def handle_starttag(self, tag, attrs):
        """Remember when script or style content begins so it is not added to readable page text."""
        if tag in ("script", "style"):
            self.skip_tag = tag

    def handle_endtag(self, tag):
        """Stop skipping text when the matching script or style element ends."""
        if tag == self.skip_tag:
            self.skip_tag = None

    def handle_data(self, data):
        """Collect visible page text while ignoring script and style contents."""
        if self.skip_tag is None:
            self.text_parts.append(data)

    def get_text(self):
        """Return all collected page text as one string."""
        return " ".join(self.text_parts)


class ShellyL_GetSearchWeb:
    """Downloads web pages and searches their words."""

    def __init__(self):
        # These are the same default and custom sources used in Lab 10.
        """Initialize the objects and the data that their methods will use."""
        self.SourcesDnary = {
            "Python": "https://www.python.org/",
            "NIST": "https://www.nist.gov/"
        }

        self.Custom1List = [
            ("NASA", "https://www.nasa.gov/"),
            ("NOAA", "https://www.noaa.gov/"),
            ("National Archives", "https://www.archives.gov/")
        ]

        self.Custom2List = [
            ("CISA", "https://www.cisa.gov/"),
            ("FBI", "https://www.fbi.gov/"),
            ("USA.gov", "https://www.usa.gov/")
        ]

        Custom1 = random.choice(self.Custom1List)
        Custom2 = random.choice(self.Custom2List)

        self.SourcesDnary[Custom1[0]] = Custom1[1]
        self.SourcesDnary[Custom2[0]] = Custom2[1]

        # Start with the four Lab 10 sources.
        self.urls = list(self.SourcesDnary.items())
        self.search_words = []
        self.results = []

    def ask_for_urls(self):
        """Ask for a source name and its URL."""
        self.urls = []

        while True:
            source = input("Enter the website source name: ").strip()
            url = input("Enter the website URL: ").strip()

            if source and url:
                self.urls.append((source, url))
            else:
                print("Both the source and URL are required.")

            again = input("Would you like to enter another URL? (y/n): ")
            if again.lower() != "y":
                break

    def read_urls_from_file(self):
        """Read source and URL pairs from a file."""
        filename = input("Enter the URL file name: ").strip()

        try:
            loaded_urls = []

            with open(filename, "r", encoding="utf-8") as file:
                reader = csv.reader(file)

                for row in reader:
                    if len(row) >= 2:
                        source = row[0].strip()
                        url = row[1].strip()

                        # Ignore a heading row, if the file has one.
                        if source.lower() == "source":
                            continue

                        if source and url:
                            loaded_urls.append((source, url))

            self.urls = loaded_urls
            print("URLs successfully loaded:", len(self.urls))

            if not self.urls:
                print("No valid source and URL pairs were found.")

        except FileNotFoundError:
            print("File was not found. Check the file name and try again.")
        except Exception as error:
            print("Error reading URL file:", error)

    def ask_for_search_words(self):
        """Ask for up to 10 comma-separated search words."""
        answer = input(
            "Enter up to 10 search words separated by commas: "
        )

        self.search_words = []

        for word in answer.split(","):
            clean_word = ""

            # This follows Lab 10 by keeping alphabetic characters only.
            for letter in word.strip().lower():
                if "a" <= letter <= "z":
                    clean_word += letter

            if clean_word and clean_word not in self.search_words:
                self.search_words.append(clean_word)

            if len(self.search_words) == 10:
                break

        print("Search words:", self.search_words)

    def get_web_page(self, source, url):
        """Download a web page and return its readable text."""
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(request, timeout=20) as response:
                html = response.read().decode("utf-8", errors="ignore")

            parser = WebTextParser()
            parser.feed(html)
            return parser.get_text()

        except Exception as error:
            print("Could not open website:", source)
            print(error)
            return None

    def make_word_lists(self, page_text):
        """
        Use the Lab 10 method: find non-alphabetic characters,
        build a word list, remove duplicates, and sort the words.
        """
        lower_text = page_text.lower()
        lines = lower_text.splitlines()

        non_alpha_list = []

        for line in lines:
            for character in line:
                if character < "a" or character > "z":
                    if character.isprintable():
                        if character not in non_alpha_list:
                            non_alpha_list.append(character)

        alpha_words_list = []

        for line in lines:
            word = ""

            for character in line:
                if character in non_alpha_list:
                    if word != "":
                        alpha_words_list.append(word)
                        word = ""
                else:
                    word += character

            if word != "":
                alpha_words_list.append(word)

        unique_words = []

        for word in alpha_words_list:
            if word not in unique_words:
                unique_words.append(word)

        unique_words.sort()

        return non_alpha_list, alpha_words_list, unique_words

    def run_search(self):
        """Download each page and count the requested words."""
        self.results = []

        if not self.urls:
            print("Please enter URLs or read URLs from a file first.")
            return

        if not self.search_words:
            print("Please enter search words first.")
            return

        for source, url in self.urls:
            print("\nProcessing:", source)
            page_text = self.get_web_page(source, url)

            if page_text is None:
                continue

            non_alpha, all_words, unique_words = self.make_word_lists(
                page_text
            )

            word_counts = {}

            for word in self.search_words:
                # Count complete words, like Lab 10, not partial matches.
                word_counts[word] = all_words.count(word)

            self.results.append({
                "source": source,
                "url": url,
                "non_alpha": non_alpha,
                "unique_count": len(unique_words),
                "unique_words": unique_words,
                "word_counts": word_counts
            })

            print("Finished:", source)

        print("\nWebsite search completed.")

    def create_report(self):
        """Create an aligned table and detailed website results."""
        lines = []
        lines.append("WEBSITE WORD SEARCH RESULTS")
        lines.append("-" * 100)

        if not self.results:
            lines.append("No results are available.")
            return "\n".join(lines)

        header = f"{'Source':<22}{'Unique Words':>15}"
        for word in self.search_words:
            header += f"{word[:12]:>15}"
        lines.append(header)
        lines.append("-" * 100)

        for result in self.results:
            row = (
                f"{result['source'][:21]:<22}"
                f"{result['unique_count']:>15}"
            )

            for word in self.search_words:
                row += f"{result['word_counts'].get(word, 0):>15}"

            lines.append(row)

        lines.append("\nWEBSITE LINKS")
        for result in self.results:
            lines.append(
                result["source"] + ": " + result["url"]
            )

        lines.append("\nUNIQUE ALPHABETIC WORDS")
        for result in self.results:
            lines.append("\nWebsite: " + result["source"])
            lines.append(
                "Number of unique words: "
                + str(result["unique_count"])
            )
            lines.append(", ".join(result["unique_words"]))

        return "\n".join(lines)

    def display_results(self):
        """Display the tabulated results on the screen."""
        print(self.create_report())

    def save_results(self):
        """Save the tabulated results to a text file."""
        if not self.results:
            print("Run a website search before saving results.")
            return

        filename = input("Enter a name for the results file: ").strip()

        if not filename:
            print("A file name is required.")
            return

        try:
            if __import__("os").path.exists(filename):
                replace_file = input(
                    "This file already exists. Replace it? (y/n): "
                ).strip().lower()
                if replace_file != "y":
                    print("File was not changed.")
                    return

            with open(filename, "w", encoding="utf-8") as file:
                file.write(self.create_report())

            print("Results successfully saved to", filename)

        except Exception as error:
            print("Could not save results:", error)


class ShellyL_Vulnerabilities:
    """Downloads and searches the CISA known exploited vulnerabilities."""

    def __init__(self):
        """Initialize the objects and the data that their methods will use."""
        self.vulnerabilities = []
        self.json_url = (
            "https://www.cisa.gov/sites/default/files/feeds/"
            "known_exploited_vulnerabilities.json"
        )

    def get_vulnerabilities(self):
        """Download the CISA JSON feed and store its vulnerability list."""
        try:
            request = urllib.request.Request(
                self.json_url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            self.vulnerabilities = data.get("vulnerabilities", [])

            output_name = "CISA_Vulnerabilities.json"
            if Path(output_name).exists():
                replace_file = input(
                    output_name + " already exists. Replace it? (y/n): "
                ).strip().lower()
                if replace_file != "y":
                    print("Existing CISA file was not changed.")
                    return True

            with open(output_name, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            print("\nCISA vulnerability data obtained successfully.")
            print(
                "Number of vulnerabilities:",
                len(self.vulnerabilities)
            )
            return True

        except Exception as error:
            print("Could not get CISA data:", error)
            return False

    def search_vulnerabilities_by_year(self):
        """Search descriptions without case sensitivity and group by year."""
        if not self.vulnerabilities:
            print("Please download the CISA data first.")
            return

        phrase = input(
            "\nEnter one search word or phrase: "
        ).strip().lower()

        if not phrase:
            print("Please enter a search word or phrase.")
            return

        yearly_results = {}

        for vulnerability in self.vulnerabilities:
            description = vulnerability.get("shortDescription", "")

            if phrase in description.lower():
                date_added = vulnerability.get("dateAdded", "")
                cve_id = vulnerability.get("cveID", "Unknown")

                if len(date_added) >= 4:
                    year = date_added[:4]

                    if year not in yearly_results:
                        yearly_results[year] = []

                    yearly_results[year].append(cve_id)

        print("\n========== CISA Search Results ==========")
        print("Search phrase:", phrase)
        print(f"\n{'Year':<12}{'Number Found':<18}CVE IDs")
        print("-" * 75)

        if not yearly_results:
            print("No matching vulnerabilities were found.")
            return

        for year in sorted(yearly_results):
            cve_ids = ", ".join(yearly_results[year])
            print(
                f"{year:<12}{len(yearly_results[year]):<18}{cve_ids}"
            )

        print("\nSearch completed.")



class ShellyL_XMLFeedClass:
    """Reads XML feeds, searches them, displays matches, and saves results."""

    def __init__(self):
        """Initialize the objects and the data that their methods will use."""
        self.feed_urls = []
        self.feed_data = []
        self.search_words = []
        self.search_results = []

    def read_feed_urls(self):
        """Read one XML feed URL from each line of a text file."""
        filename = input("Enter the XML URL file name: ").strip()

        if not filename:
            print("A file name is required.")
            return

        try:
            urls = []
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    url = line.strip()
                    if url and not url.startswith("#"):
                        urls.append(url)

            if len(urls) < 5:
                print("The file must contain at least 5 XML feed URLs.")
                return

            self.feed_urls = urls
            self.feed_data = []
            self.search_results = []
            print("XML feed URLs loaded:", len(self.feed_urls))

        except FileNotFoundError:
            print("File was not found. Check the name and try again.")
        except Exception as error:
            print("Could not read the URL file:", error)

    def get_tag_text(self, element, names):
        """Find text in an XML tag, including namespaced tags."""
        for child in element.iter():
            tag_name = child.tag.split("}")[-1].lower()
            if tag_name in names and child.text:
                return child.text.strip()
        return ""

    def get_entry_links(self, entry):
        """Get every web link from one feed entry."""
        links = []
        for child in entry.iter():
            if child.tag.split("}")[-1].lower() == "link":
                link = child.attrib.get("href", "").strip()
                if not link and child.text:
                    link = child.text.strip()
                if link and link not in links:
                    links.append(link)
        return links

    def get_feed_from_url(self, url):
        """Download one XML feed and turn its entries into dictionaries."""
        request = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(request, timeout=25) as response:
            xml_text = response.read()

        root = ET.fromstring(xml_text)
        feed_name = self.get_tag_text(root, {"title"})
        if not feed_name:
            feed_name = url

        entries = []
        for element in root.iter():
            tag_name = element.tag.split("}")[-1].lower()
            if tag_name in {"item", "entry"}:
                title = self.get_tag_text(element, {"title"})
                pub_date = self.get_tag_text(
                    element, {"pubdate", "published", "updated", "date"}
                )
                description_parts = []
                for child in element.iter():
                    child_name = child.tag.split("}")[-1].lower()
                    if child_name in {"description", "summary", "content", "encoded"}:
                        if child.text:
                            description_parts.append(child.text.strip())
                entries.append({
                    "title": title or "No title",
                    "publication_date": pub_date or "Unknown",
                    "links": self.get_entry_links(element),
                    "description": " ".join(description_parts)
                })

        return {"feed_name": feed_name, "feed_url": url, "entries": entries}

    def get_xml_feed_data(self):
        """Download each URL and store its feed name and entries."""
        if not self.feed_urls:
            print("Read an XML URL file first.")
            return

        self.feed_data = []
        for url in self.feed_urls:
            print("\nDownloading XML feed:", url)
            try:
                feed = self.get_feed_from_url(url)
                self.feed_data.append(feed)
                print("Loaded:", feed["feed_name"])
                print("Entries:", len(feed["entries"]))
            except Exception as error:
                print("Could not read this XML feed:", error)

        print("\nXML feed download finished.")
        print("Feeds loaded:", len(self.feed_data))

    def search_feeds_for_text(self):
        """Find entries that contain one or more of up to 10 search words."""
        if not self.feed_data:
            print("Get the XML feed data first.")
            return

        answer = input(
            "Enter up to 10 words or phrases separated by commas: "
        ).strip()
        words = []
        for part in answer.split(","):
            word = part.strip()
            if word and word.lower() not in [item.lower() for item in words]:
                words.append(word)
            if len(words) == 10:
                break

        if not words:
            print("Enter at least one search word or phrase.")
            return

        self.search_words = words
        self.search_results = []

        for feed in self.feed_data:
            for entry in feed["entries"]:
                searchable_text = (
                    feed["feed_name"] + " " + entry["title"] + " "
                    + entry["publication_date"] + " "
                    + entry["description"] + " "
                    + " ".join(entry["links"])
                ).lower()

                found_words = []
                for word in self.search_words:
                    if word.lower() in searchable_text:
                        found_words.append(word)

                if found_words:
                    links = entry["links"] if entry["links"] else ["No link"]
                    for link in links:
                        self.search_results.append({
                            "feed_name": feed["feed_name"],
                            "words_found": found_words,
                            "publication_date": entry["publication_date"],
                            "title": entry["title"],
                            "link": link
                        })

        print("Search completed.")
        print("Matching feed entries:", len(self.search_results))

    def display_feed_search_data(self):
        """Display all matches in a numbered table."""
        if not self.search_results:
            print("No search results are available.")
            return

        print("\nXML FEED SEARCH RESULTS")
        print("-" * 125)
        print(
            f"{'No.':<6}{'Feed Name':<24}{'Words Found':<22}"
            f"{'Publication Date':<22}{'Feed Title':<28}Web Link"
        )
        print("-" * 125)

        for number, result in enumerate(self.search_results, start=1):
            print(
                f"{number:<6}{result['feed_name'][:23]:<24}"
                f"{', '.join(result['words_found'])[:21]:<22}"
                f"{result['publication_date'][:21]:<22}"
                f"{result['title'][:27]:<28}{result['link']}"
            )

    def save_feed_search_data(self):
        """Save matching feed data as JSON with four spaces of indentation."""
        if not self.search_results:
            print("Run a feed search before saving.")
            return

        filename = input("Enter a name for the JSON file: ").strip()
        if not filename:
            print("A file name is required.")
            return
        if not filename.lower().endswith(".json"):
            filename += ".json"

        try:
            file_path = filename
            if __import__("os").path.exists(file_path):
                answer = input(
                    "This file already exists. Replace it? (y/n): "
                ).strip().lower()
                if answer != "y":
                    print("File was not changed.")
                    return

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.search_results, file, indent=4)

            print("Search data saved to:", file_path)
        except Exception as error:
            print("Could not save the JSON file:", error)


class ShellyL_Menu:
    """Displays menus and controls the program's menu navigation."""

    def show_main_menu(self):
        """Display the main choices and return the user selection."""
        print("\n========== Main Menu ==========")
        print("1. Network Menu")
        print("2. Forensics Menu")
        print("3. Get Web Data Menu")
        print("4. Quit the program")
        return input("Enter menu choice between 1 and 4: ").strip()

    def show_web_menu(self):
        """Display the Get Web Data choices and return the user selection."""
        print("\n======= Get Web Data Menu =======")
        print("1. Get Web HTML Pages")
        print("2. Check Vulnerabilities Data")
        print("3. Get Web XML Pages")
        print("4. Go Back To Main Menu")
        return input("Enter menu choice between 1 and 4: ").strip()

    def show_html_menu(self):
        """Display the HTML tools and return the user selection."""
        print("\n========== Web HTML Menu ==========")
        print("1. Ask for a URL Interactively")
        print("2. Reading URLs From File")
        print("3. Asking for Search Words")
        print("4. Run the Search")
        print("5. Display Results")
        print("6. Saving Results to a File")
        print("7. Go Back to Web Data Menu")
        return input("Enter menu choice between 1 and 7: ").strip()

    def show_vulnerability_menu(self):
        """Display the vulnerability tools and return the user selection."""
        print("\n======= Vulnerabilities Menu =======")
        print("1. Search Vulnerabilities by Year")
        print("2. Go Back to Web Data Menu")
        return input("Enter menu choice between 1 and 2: ").strip()

    def show_xml_menu(self):
        """Display the XML feed tools and return the user selection."""
        print("\n======= Get Web XML Pages =======")
        print("1. Read XML Feed URLs File")
        print("2. Get XML Feeds Data")
        print("3. Search Feeds Data for Text")
        print("4. Display Feeds Search Data")
        print("5. Save Feeds Data to File")
        print("6. Go Back to Web Data Menu")
        return input("Enter menu choice between 1 and 6: ").strip()

    def html_menu(self, web):
        """Control all choices in the HTML submenu."""
        while True:
            choice = self.show_html_menu()
            if choice == "1":
                web.ask_for_urls()
            elif choice == "2":
                web.read_urls_from_file()
            elif choice == "3":
                web.ask_for_search_words()
            elif choice == "4":
                web.run_search()
            elif choice == "5":
                web.display_results()
            elif choice == "6":
                web.save_results()
            elif choice == "7":
                break
            else:
                print("Invalid choice. Try again.")

    def vulnerability_menu(self, vulnerabilities):
        """Control the CISA vulnerability submenu."""
        if not vulnerabilities.get_vulnerabilities():
            return
        while True:
            choice = self.show_vulnerability_menu()
            if choice == "1":
                vulnerabilities.search_vulnerabilities_by_year()
            elif choice == "2":
                break
            else:
                print("Invalid choice. Try again.")

    def xml_menu(self, xml_feeds):
        """Control all choices in the XML feed submenu."""
        while True:
            choice = self.show_xml_menu()
            if choice == "1":
                xml_feeds.read_feed_urls()
            elif choice == "2":
                xml_feeds.get_xml_feed_data()
            elif choice == "3":
                xml_feeds.search_feeds_for_text()
            elif choice == "4":
                xml_feeds.display_feed_search_data()
            elif choice == "5":
                xml_feeds.save_feed_search_data()
            elif choice == "6":
                break
            else:
                print("Invalid choice. Try again.")

    def web_data_menu(self, web, vulnerabilities, xml_feeds):
        """Control the Get Web Data submenu."""
        while True:
            choice = self.show_web_menu()
            if choice == "1":
                self.html_menu(web)
            elif choice == "2":
                self.vulnerability_menu(vulnerabilities)
            elif choice == "3":
                self.xml_menu(xml_feeds)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Try again.")

    def main_menu(self, web, vulnerabilities, xml_feeds):
        """Keep the main menu running until the user chooses Quit."""
        while True:
            choice = self.show_main_menu()
            if choice == "1":
                print("Network Menu is not included in this lab version.")
            elif choice == "2":
                print("Forensics Menu is not included in this lab version.")
            elif choice == "3":
                self.web_data_menu(web, vulnerabilities, xml_feeds)
            elif choice == "4":
                print("\nThank you for using the program!")
                break
            else:
                print("Invalid choice. Enter 1, 2, 3, or 4.")


def main():
    """Create the program objects and start the main menu."""
    menu = ShellyL_Menu()
    web = ShellyL_GetSearchWeb()
    vulnerabilities = ShellyL_Vulnerabilities()
    xml_feeds = ShellyL_XMLFeedClass()
    menu.main_menu(web, vulnerabilities, xml_feeds)


if __name__ == "__main__":
    main()
