# Movie Organizer (UTN-TUPaD Integrator)

This program processes an initial list of movies stored in `movies/movies_unscrapped.csv` and organizes them into multiple CSV files saved in nested folders by genre, year, and duration category. It also provides basic CRUD (Create, Read, Update, Delete) functionality for managing the movie records.

## What it does

- Reads the initial movie data from `movies/movies_unscrapped.csv`.
- Normalizes and splits the movies into separate CSV files placed in a nested folder structure: first by genre, then by year, and then by duration category (for example: `movies/Action/2020/short/`).
- Each CSV contains the subset of movies that match that genre/year/duration category.
- Offers CRUD operations so you can add, list, modify, or remove movie entries either through the provided scripts or the main program interface.

## Input

- Primary input: `movies/movies_unscrapped.csv`.
- Optional configuration: `config.ini` can hold runtime options used by the scripts.

## Output structure

The organizer creates a nested folder tree under the `movies/` directory with CSV files grouped like:

- `movies/<Genre>/<Year>/<DurationCategory>/movies.csv`

Where `<DurationCategory>` refers to categories such as `short` for a duration less than 90 minutes, `medium` for a duration between 90 and 120 minutes, and `long` for a duration more than 120 minutes.

Example:

- `movies/Action/2019/short/movies.csv`
- `movies/Drama/2021/long/movies.csv`

Each CSV contains the movie rows that belong to that particular genre/year/duration group.

## CRUD functionality

The project provides basic Create, Read, Update and Delete operations for movie entries. You can:

- Add new movie records (which will be placed into the proper folder and CSV according to their metadata).
- Read/list movies from the organized CSVs.
- Update existing movie entries (modify metadata such as title, year, genre, duration, etc.).
- Delete movie entries (remove from the appropriate CSV).

CRUD operations are exposed via the included scripts and/or the `main.py` entry point; consult the script docstrings or open the source files in `scripts/` for exact usage.

## How to run

Requirements:

- Python 3.8+ (recommended).

Typical usage from the project root (Windows PowerShell example):

```powershell
python main.py
```

## Files of interest

- `main.py` — program entry point.
- `config.ini` — configuration.
- `movies/movies_unscrapped.csv` — initial dataset.
- `scripts/load.py`, `scripts/organize.py`, `scripts/show.py` — utility scripts for loading, organizing and viewing movies.

---