# Godzilla Movie Tracker Discord Bot

A Discord bot for Godzilla fans to **track which Godzilla movies you own** and quickly search your collection.

---

## Features

- **Track movies**: Use a `.ods` file to mark which Godzilla movies you own.
- **Search your collection**: `!movies <keyword>` searches your collection by title. If no keyword is provided, it lists all movies.
- **Customizable**: Add your own movies, descriptions, and eras.

---

## `.ods` File Setup

The bot uses a **LibreOffice / Excel `.ods` file** as its database. You need to create this file yourself.

1. Create a new spreadsheet in LibreOffice or Excel.
2. Use the following columns (first row as headers):

| Own | Title | Year | Movie Era | Description |
| --- | ----- | ---- | --------- | ----------- |

3. **Column descriptions:**
   - `Own`: Mark with `Yes` if you own the movie, `No` if you don’t.
   - `Title`: The official movie title.
   - `Year`: Release year of the movie.
   - `Movie Era`: Example: “Showa”, “Heisei”, “Millennium”, etc.
   - `Description`: Any notes or details about the movie.

4. Save the file as `.ods` in the location configured in the bot.

---

## Commands

### `!movies <keyword>`

- **Purpose**: Search your Godzilla collection.
- **Behavior**:
  - If `<keyword>` is provided: returns only movies containing that keyword in the title.
  - If left blank: returns all movies in your collection.
- **Example Usage**:

```
!movies
!movies Ghidorah
```

### `!own <movie name> <year>`

- Purpose: Marks the Godzilla Movie as owned

```
!own Godzilla Raids Again 1955
```

### `!notown <movie name> <year>`

- purpose: Marks the Godzilla movie as not owned.

```
!notown Godzilla Raids Again 1955
```

---

## Setup

1. Clone this repository

```

git clone git@github.com:username/godzilladiscordbot.git
cd godzilladiscordbot

```

2. Install dependencies

```

pip install -r requirements.txt

```

3. Create a .env file with your Discord bot token:

```

DISCORD_TOKEN=your_bot_token_here

```

4. Run the bot

```

python main.py

```

### Notes

- The bot reads the .ods file on startup. Make sure your file path is correct.
- The Own column is case-insensitive (yes / no).
- You can expand the collection by adding more movies with the required columns.
