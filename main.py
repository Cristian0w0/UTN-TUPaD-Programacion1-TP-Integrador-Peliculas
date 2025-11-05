import os, sys, configparser
from scripts import organize, load, show

# Initial program configuration
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8-sig")

# Constants definition
HEADER = ["name", "genre", "year", "duration", "rating", "director", "language"]
GENRES = ["Action", "Adventure", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "History", 
        "Horror", "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western"]
LANGUAGES = ["English", "Spanish", "German", "Italian", "French", 
            "Portuguese", "Russian", "Korean", "Chinese", "Japanese"]

def main():
    # Main program menu
    all_movies = load.get_all_movies()
    while True:
        print("\n--- Main Menu ---\n"
        "1. Show all movies with path\n"
        "2. Show total number of movies\n"
        "3. Show total number of movies by genre\n"
        "4. Show average duration of all movies\n"
        "5. Show average duration of all movies by genre\n"
        "6. Show movies sorted by attribute\n"
        "7. Show movies filtered by attribute\n"
        "8. Add new movie\n"
        "9. Update movie\n"
        "10. Delete movie\n"
        "0. Exit")
        option = insert_option(range_max=10)
        match option:
            case 0:
                print("\nExiting...")
                break
            case 1:
                show.show_movies(all_movies)
            case 2:
                show.show_movie_amount(all_movies)
            case 3:
                show.show_movie_amount_genre(all_movies)
            case 4:
                show.show_average_duration(all_movies)
            case 5:
                show.show_average_duration_genre(all_movies)
            case 6:
                show.show_sorted_movies(all_movies)
            case 7:
                show.show_filtered_movies(all_movies)
            case 8:
                all_movies = load.add_new_movie(all_movies)
            case 9:
                all_movies = load.update_movie(all_movies)
            case 10:
                all_movies = load.delete_movie(all_movies)



def insert_option(text:str = "\nEnter option: ", 
                range_max:int = sys.maxsize, 
                range_min:int = 0,
                value_type = int):
    # Function to validate user option input
    try:
        option = value_type(input(text))
        if (not range_min <= option <= range_max):
            raise ValueError
    except ValueError:
        print("Invalid option")
        option = None
    finally:
        return option



# Define duration categories
def get_duration_category(duration):
    duration = int(duration)
    if duration < 90:
        return "short"
    elif duration <= 120:
        return "medium"
    else:
        return "long"



if (__name__ == "__main__"):
    # Program initialization - CSV files organization
    csv_paths = organize.organize_files()
    print("\n" + "="*60)
    print("ORGANIZED CSV FILE PATHS:")
    print("="*60)
    for name, path in sorted(csv_paths.items()):
        print(f"  {name:20} -> {path}")
    stats = load.categorize_movies()
    print(stats)
    main()